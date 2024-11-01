'''Camelot Endpoint
'''
import re
import logging
import time
import sys
from tng.api import creatable_device
from tng.api import until
from tng.device.endpoint.ciscophone import (CiscoPhoneAudioChannel,
                                            CiscoPhoneVideoChannel)
from tng.device.interfaces.cp_feedback_handler import CiscoPhoneFeedbackHandler
from tng.device.interfaces.cisco_phone_interface import CiscoPhoneInterface
from tng import media
from tng.device.endpoint.ciscophone import CiscoPhone
import ast
from collections import OrderedDict
import socket
from tng.plugins.plugin import DevicePlugin
import camelot
from camelot.tngdevice.plugins.camelot_feedback_plugin import (
    CamelotFeedbackPlugin)
from camelot.utils.vapi_ei_utils import VAPIEIUtils
from tng.frontend import timing
from tng.api import interface
from camelot.protocol.tcp.camelot_connection import ConnectionError
from camelot.tngdevice.tng_endpoint import CamelotTngEndpoint
from pyparsing import ParseException
from tng.frontend.setupfile_parser import SetupParserException
from tng.frontend import setupfile_parser
from tng.device_helpers.addresses import (
    DeviceAddrs, validate_and_classify_addr_str)
from camelot.utils.rawendpoint_helper import InActionObject
from camelot import CamelotError
from camelot.tngdevice.plugins.ssh_plugin import CamelotSshPlugin
from tng.plugins.scp_plugin import ScpPlugin
import tng
from camelot.utils import camelot_ep_template_file as template
log = logging.getLogger('Camelot')


class CamelotTTSParser(setupfile_parser.TtsFileParser):
    def parse(self, fp):
        devices = OrderedDict()
        used = set()
        test_members = set()
        try:
            tokens = self.parser.parseFile(fp)
        except ParseException as e:
            if hasattr(fp, 'name'):
                fname = fp.name
            else:
                fname = '?'
            msg = 'Parsing configfile %s failed because %s' % (fname, str(e))
            if hasattr(e, 'line'):
                msg = e.line + '\n' + ' ' * (e.column - 1) + '^\n' + msg

            raise SetupParserException(msg)

        for (objname, member), values in tokens:
            if objname == 'test':
                if member in ['targets', 'eps']:
                    test_members.add(member)
                    for val in values:
                        if val in devices:
                            devices[val]['target'] = (member == 'targets')
                            used.add(val)
                        else:
                            raise SetupParserException(
                                "Unknown device name '%s'" % val)
            else:
                if values:
                    value = values[-1]
                    if member in ['config_params', 'config_headers']:
                        value = ' '.join(values)
                    elif len(values) > 1:
                        log.warning("Config value %s.%s='%s' picking last one",
                                    objname, member, ' '.join(values))
                else:
                    # allow for empty passwords
                    if 'password' in member:
                        value = ''
                    else:
                        raise SetupParserException(
                            'Missing value for %s.%s' % (objname, member))

                if objname not in devices:
                    device = {
                        'name': objname,
                        'target': False,
                        'addrs': DeviceAddrs([{'name': 'TTS'}], [])}
                    devices[objname] = device
                    ip_protocol_specified = False
                else:
                    device = devices[objname]
                if value.lower() == 'none':
                    continue
                elif member == 'ip_protocol':
                    if value == 'both':
                        value = 'ipv4'
                    device['addrs'].default_mode = value
                    ip_protocol_specified = True
                elif member == 'ip':
                    addr_type, value = validate_and_classify_addr_str(value)
                    setattr(device['addrs'], addr_type, value)
                    if not ip_protocol_specified:
                        device['addrs'].default_mode = addr_type
                elif member in self.device_names:
                    device['device_type'] = member
                elif member in [
                        'username', 'password',
                        'rootusername', 'rootpassword']:
                    device[member] = value
                elif member == 'ipv4':
                    device['addrs'].ipv4 = value
                elif member == 'ipv6':
                    device['addrs'].ipv6 = value
                else:
                    device[member] = value

        if test_members != set(['targets', 'eps']):
            return devices.values()
        else:
            ret = OrderedDict()
            for key, value in devices.items():
                if key in used:
                    ret[key] = value
                else:
                    log.warning('Ignoring device %s which is neither in '
                                'test.eps or test.targets' % (key))
            return ret.values()


def camelot_get_parser(formatname):
    if formatname == 'tts':
        return CamelotTTSParser
    else:
        return l_get_parser(formatname)


l_get_parser = setupfile_parser.get_parser
setupfile_parser.get_parser = camelot_get_parser


@interface('vapi', 'CamelotEP')
class CamelotPhoneInterface(CiscoPhoneInterface):

    def dial(self, number, protocol=None, callrate=None,
             call_type=None):
        return self.device.vapi._device_dial(number)

    def disconnect(self, call_id=None):
        try:
            call_info = self.device.vapi.get_call_info(call_id)
            if call_info and call_info['state'] in [
                    'held', 'localheld', 'remoteheld']:
                self.device.vapi.resume(call_id)
                time.sleep(0.5)
        except Exception as e:
            log.info('resume failed:[%s]' % e)
        return self.device.vapi.endcall(call_id)

    def disconnect_all(self):
        self.device.vapi.release_calls()
        try:
            calls = self.device.vapi.get_calls()
            if calls is None or len(calls) < 1:
                return False
            for call in calls:
                if not isinstance(call, dict):
                    continue
                self.disconnect(call['Ref'])

                def __call_disconnected():
                    c_info = self.device.vapi.get_call_info(call['Ref'])
                    if c_info['state'] == 'disconnected':
                        return True
                timing.until(
                    __call_disconnected, True, 15, raise_on_timeout=False)
        except Exception as e:
            log.exception('Received exception: %s' % e)
            return

    def blind_transfer(self, call_id, protocol, number):
        def _get_call_id(callstate):
            calls = self.device.vapi.get_calls()
            for call in calls:
                if call['CallState'] == callstate:
                    call_ref = call['Ref']
                    return call_ref
            return False

        def _is_alerting():
            calls = self.device.vapi.get_calls()
            for call in calls:
                if call['CallState'] == 'alerting':
                    return True

        def _is_offhooked():
            calls = self.device.vapi.get_calls()
            for call in calls:
                if call['CallState'] == 'dialtone':

                    return True
            return False

        def _is_transfer_ready():
            calls = self.device.vapi.get_calls()
            for call in calls:
                if call['CallState'] == 'alerting':
                    return True
            return False

        if self.device.vapi.transfer(call_id):
            timing.until(_is_offhooked, True, 2, raise_on_timeout=True)
            transfer_callid = _get_call_id('dialtone')
            if transfer_callid:
                self.device.vapi.dial(number, transfer_callid)
            else:
                log.error('Unable to retrieve the call id of the dialing call')
                return
            timing.until(_is_transfer_ready, True, 2, raise_on_timeout=False)
            timing.until(_is_alerting, True, 30, raise_on_timeout=False)
            transfer_callid = _get_call_id('alerting')
            if transfer_callid:
                return self.device.vapi.transfer(transfer_callid)
            else:
                log.error('Unable to retrieve call id of the alerting call')
                return

    def join(self):
        def _get_call_id(callstate):
            calls = self.device.vapi.get_calls()
            for call in calls:
                if call['CallState'] == callstate:
                    call_ref = call['Ref']
                    return call_ref
            return False

        self.device.is_conf_initiator = True
        transfer_callid = _get_call_id('connected')
        self.device.vapi.conference(transfer_callid)


class CamelotEndpoinPlugin(DevicePlugin):
    name = 'vapi'

    def __init__(self, host='', port='', ep_name='', ep_type=None, version='',
                 client_data=None, cas_protocol='', cas_board='',
                 cas_trunk='', cas_country='', cas_line='', **kwargs):
        super(CamelotEndpoinPlugin, self).__init__(**kwargs)
        self.host = host
        self.port = port
        self.ep_type = ep_type
        self.ep_name = ep_name
        self.version = version
        self.client_data = client_data
        self.cas_board = cas_board
        self.cas_trunk = cas_trunk
        self.cas_country = cas_country
        self.cas_protocol = cas_protocol
        self.cas_line = cas_line

    def setup(self):
        frontend = None
        cam_srv = None
        try:
            cam_srv = camelot.create_camelot_server(
                self.host, self.port, version=self.version)
            cam_srv._tng_cleanup_required = True
        except camelot.CamelotError as e:
            if e.e_type == 'Internal':
                cam_srv = camelot.get_camelot_server(self.host, self.port)
        except ConnectionError:
            raise
        except Exception as e:
            log.debug("warning::failed to create camelot"
                      "serverip:{} port:{} reason:{}".format(
                          self.host, self.port, e))
        if cam_srv:
            if self.client_data:
                frontend = cam_srv.attach_endpoint(
                    self.client_data, ep_class=CamelotTngEndpoint)
            else:
                if self.ep_type == 'cas':
                    log.debug('CamelotEndpointPlugin createendpoint cas')
                    frontend = cam_srv.create_new_endpoint(
                        self.ep_type, self.ep_name,
                        ep_class=CamelotTngEndpoint,
                        cas_board_id=self.cas_board,
                        cas_line_id=self.cas_trunk,
                        cas_country=self.cas_country,
                        cas_protocol=self.cas_protocol,
                        cas_line_num=self.cas_line)
                else:
                    log.debug('CamelotEndpointPlugin createendpoint not cas')
                    frontend = cam_srv.create_new_endpoint(
                        self.ep_type, self.ep_name,
                        ep_class=CamelotTngEndpoint)
        if frontend:
            frontend._device = self.device
            frontend.in_service = frontend.inservice
            frontend.out_of_service = frontend.outofservice
            frontend.init_ep = frontend.init
            frontend.uninit_ep = frontend.uninit
            frontend.transfer_VM = frontend.transfer_vm
        self.set_namespace(frontend)

    def teardown(self):
        pass


class CamelotPresentationChannel(CiscoPhoneVideoChannel):
    def __init__(self):
        super(CamelotPresentationChannel, self).__init__()

    def get_role(self):
        return media.PRESENTATION


@creatable_device()
class Camelot(CiscoPhone):
    _model_number_regex = None
    version_regex = re.compile(
        '''
        (?P<product_code>\w+)\s(?P<major_version>(\d+)).
        (?P<minor_version>(\d+)).
        (?P<revision>(\d+)).(?P<build_num>(\d+))
        (?P<second_build_num>\.(\d+)\.(\d+))
        ''',
        re.I | re.VERBOSE)
    # <FIXME:> These were added for compliance with the ABCDevice definition

    def _boot_action(self):
        raise NotImplementedError()

    def _restart_action(self):
        raise NotImplementedError()
    # </FIXME:>

    def __init__(self, ip, engine, ep_type='sipx', camelot_ip='0.0.0.0',
                 camelot_port=9004, version=VAPIEIUtils.CLIENT_VERSION,
                 username='camuser', password='ciscocisco1',
                 config_params={}, config_headers={}, log_params={},
                 auto_register=True, inservice_timeout=100,
                 wait_to_register=True, station_event_callback=None,
                 client_data=None, log_src_dir=None, **kwargs):
        self.feedback_handler_cls = CamlotFeedbackHandler
        self.feedback_handler_classes = (CamlotFeedbackHandler,)
        self.ep_type = ep_type
        self.client_data = client_data
        self.ignore_complex_spontaneous_calls = True
        super(CiscoPhone, self).__init__(
            ip, engine, ep_type=ep_type, camelot_ip=camelot_ip,
            camelot_port=camelot_port, version=version,
            username=username, password=password,
            config_params=config_params, config_headers=config_headers,
            log_params=log_params, auto_register=auto_register,
            inservice_timeout=inservice_timeout,
            wait_to_register=wait_to_register,
            station_event_callback=station_event_callback, **kwargs)
        self.cli_version = version
        self.cam_ip = camelot_ip
        self.cam_port = int(camelot_port)
        if hasattr(ip, 'addr'):
            self.cam_mac = ip.addr
        else:
            self.cam_mac = ip
        self.audio_only = True
        self.config_params = self._validate_dict_args(config_params)
        self.config_headers = self._validate_dict_args(config_headers)
        if isinstance(auto_register, str):
            auto_register = eval(auto_register)
        self.auto_register = auto_register
        if isinstance(inservice_timeout, str):
            inservice_timeout = int(inservice_timeout)
        self.inservice_timeout = inservice_timeout
        if isinstance(wait_to_register, str):
            wait_to_register = eval(wait_to_register)
        self._wait_to_register = wait_to_register
        self._station_event_callback = station_event_callback
        self.ep_log_params = log_params

        if self.ep_type and not self.config_params:
            log.debug('IMP: in case of EP craetion failed: '
                      'Unable to read Config params, Invalid type')

        if self.ep_type and self.ep_log_params:
            self.ep_log_params = self._validate_dict_args(log_params)
            if not self.ep_log_params:
                log.debug('IMP: in case of EP craetion failed: '
                          'Unable to read endpoint log params, Invalid type')

        if self.ep_type and not self._validate_args():
            log.debug('IMP: in case of EP craetion failed: '
                      'Failed to validate args')

        self.hardware = 'Camelot Endpoint'
        self.platform = 'Camelot'
        self.feedback_receiver = None
        self.cam_feedback = None
        self.supported_protocols = ['sip']
        self.pending_feedback_handler = None
        self.is_conf_initiator = False
        self.log_src_dir = log_src_dir

    def _initialise(self, **kwargs):
        camelot_ip = kwargs.get('camelot_ip')
        camelot_port = kwargs.get('camelot_port')
        version = kwargs.get('version')
        cas_params = {}
        log.debug('_initialise kwargs is %s' % kwargs)
        if camelot_port:
            camelot_port = int(camelot_port)
        end_point_type = kwargs.get('ep_type')
        log.debug('_initialise eptype is %s len is %d' %
                  (end_point_type, len(end_point_type)))
        if end_point_type == 'cas':
            cas_params['board_id'] = kwargs.get('board_id', 1)
            cas_params['line_id'] = kwargs.get('line_id', 1)
            cas_params['country'] = kwargs.get('country', 'ind')
            cas_params['protocol'] = kwargs.get('protocol', 'nocc')
            cas_params['line_num'] = kwargs.get('line', '')
            log.debug('_initialise cas_params is %s' % cas_params)
            vapi_plugin = CamelotEndpoinPlugin(
                host=camelot_ip, port=camelot_port,
                ep_name=self.ip,
                ep_type=kwargs.get('ep_type'),
                version=version,
                check_target_match=self._check_target_match,
                setup_action=self._setup_camelot_device,
                client_data=self.client_data,
                cas_trunk=cas_params['line_id'],
                cas_board=cas_params['board_id'],
                cas_protocol=cas_params['protocol'],
                cas_country=cas_params['country'],
                cas_line=cas_params['line_num'])
        else:
            vapi_plugin = CamelotEndpoinPlugin(
                host=camelot_ip, port=camelot_port,
                ep_name=self.ip,
                ep_type=kwargs.get('ep_type'),
                version=version,
                check_target_match=self._check_target_match,
                setup_action=self._setup_camelot_device,
                client_data=self.client_data)
        feedback_plugin = CamelotFeedbackPlugin(vapi_plugin)
        log.debug(self.credentials['default'])
        ssh_plugin = CamelotSshPlugin(camelot_ip,
                                      credential=self.credentials['default'])
        self.plugins |= {
            vapi_plugin,
            feedback_plugin,
            ssh_plugin,
            ScpPlugin(ssh_plugin)}
        return feedback_plugin

    def _is_nogencert_key(self, parm_val):
        log.debug('in _is_nogencert_key')
        no_gen_cert = False
        call_gen_cert_key = False
        if parm_val and parm_val != '0':
            no_gen_cert = True
        else:
            log.debug('calling gen_cert_key reason:parm set')
            call_gen_cert_key = True
        return [no_gen_cert, call_gen_cert_key]

    def _configure_endpoint(self):
        '''
        This method decides to call gencertkey based on:
        1. nogencertkey parm, preference always is given to this parm
        2. isedge parm.
        Also this method sets audio_only flag based on parm, and sets hardware
        configs.
        '''
        if self.config_params:
            no_gen_cert = False
            call_gen_cert_key = False
            params = self.config_params
            for key in sorted(params):
                if 'nogencertkey' in key:
                    nogen_val = self.config_params.get(
                        key)
                    [no_gen_cert, call_gen_cert_key] = self._is_nogencert_key(
                        nogen_val)
                elif '.phone.isedge' in key:
                    log.debug('calling gen_cert_key reason:isedge')
                    call_gen_cert_key = True
                elif '.phone.secured' in key and (str(
                        params[key]) in ['1', '2']):
                    log.debug('calling gen_cert_key reason:secured')
                    call_gen_cert_key = True
                elif 'vidpayloadtype' in key or 'vidcodectype' in key:
                    log.debug('making audio_only false reason:parm set')
                    self.audio_only = False

            if not no_gen_cert:
                if self.ep_type in ['jabber', 'jabbermobile']:
                    log.debug('calling gen_cert_key reason:'
                              'jabber/jabbermobile')
                    call_gen_cert_key = True

                if call_gen_cert_key:
                    self.vapi.gen_cert_key()

            self._set_hardware_from_config(params)

    def _configure_config_headers(self):
        if self.config_headers:
            params = self.config_headers
            for key in sorted(params):
                result = self.config_header(key, str(params[key]))
                if result:
                    log.debug('config headers success %s:%s' % (
                        key, str(params[key])))
                    continue
                else:
                    log.error('_configure_config_headers:'
                              ' config %s failed.' % key)

    def _is_valid_integer(self, int_str):
        try:
            int(int_str)
            return True
        except ValueError:
            return False

    def _set_hardware_from_config(self, params):
        type_val = None
        if 'sip.phone.modelnumber' in params:
            value = params['sip.phone.modelnumber']
            if self._is_valid_integer(value):
                value = int(value)
                if value in VAPIEIUtils.model_number_map:
                    type_val = VAPIEIUtils.model_number_map[value]
        elif 'sip.phone.deviceid' in params:
            value = params['sip.phone.deviceid']
            if self._is_valid_integer(value):
                value = int(value)
                if value in VAPIEIUtils.device_id_map:
                    type_val = VAPIEIUtils.device_id_map[value]
        elif 'skinny.phone.devicetype' in params:
            value = params['skinny.phone.devicetype']
            if self._is_valid_integer(value):
                value = int(value)
                if value in VAPIEIUtils.skinny_device_type_map:
                    type_val = VAPIEIUtils.skinny_device_type_map[value]

        if type_val:
            self.hardware = "%s-%s" % (self.hardware, type_val)

    def _setup_camelot_device(self, namespace):
        log.info('Initializing Camelot Endpoint...')
        if not namespace:
            log.error('could not create endpoint object')
            return
        try:
            namespace.config_ep_dict(self.config_params)
        except Exception as e:
            log.warning('Failed to configure all parameters during '
                        'initialization: {}'.format(e))
        self._configure_config_headers()
        self._configure_endpoint()
        if self.auto_register:
            namespace.init()
            namespace.inservice()
            if self._wait_to_register:
                log.info('Waiting for the endpoint: [%r] inservice state' % (
                    self))

                def _is_registered():
                    if namespace.get_info()['state'] == 'inservice':
                        return True
                try:
                    timing.until(
                        _is_registered, timeout=self.inservice_timeout,
                        interval=3, raise_msg='timed out waiting for'
                                              ' in-service')
                except Exception:
                    log.error('Endpoint in-service failed, Info: {}'.format(
                        namespace.get_info()))
                    log.info('cleaning camelot endpoint')
                    self.camelot_endpoint_clean_exit()
                    raise
        log.info('Initialized Camelot Endpoint')

    def _prepare_config_param(self, conf_param):
        if 'camelot_ep_template_file' in conf_param:
            log.debug("camelot_ep_template_file:"
                      "{}".format(conf_param.get('camelot_ep_template_file')))
            import imp
            import os
            camelot_config_file = conf_param.get('camelot_ep_template_file')
            if os.path.exists(camelot_config_file) and \
                    camelot_config_file.endswith('.py'):
                template_obj = imp.load_source("camelot_config",
                                               camelot_config_file)
                phones_dict = template_obj.phones_camelot_params
                features_dict = template_obj.features_camelot_params
                del conf_param['camelot_ep_template_file']
            else:
                log.exception("File not found:{}".format(camelot_config_file))
                raise
        else:
            log.debug("Fetching phone models from "
                      "camelot-pi/camelot_param_template.")
            phones_dict = template.phones_camelot_params
            features_dict = template.features_camelot_params
        if 'phone_model' in conf_param:
            model = conf_param['phone_model']
            if model in phones_dict:
                phone_dict = phones_dict.get(model)
                for key, val in phone_dict.iteritems():
                    if key not in conf_param:
                        conf_param[key] = val
            else:
                log.warn("Phone model: {} not defined in "
                         "camelot_param_template file.".format(model))
            del conf_param['phone_model']
        if 'add_feature' in conf_param:
            feature = conf_param['add_feature']
            if isinstance(feature, list):
                for item in feature:
                    if item in features_dict:
                        feature_dict = features_dict.get(item)
                        for key, val in feature_dict.iteritems():
                            if key not in conf_param:
                                conf_param[key] = val
                    else:
                        log.warn("Feature: {} not defined in "
                                 "camelot_param_template file.".format(item))
            del conf_param['add_feature']
        if conf_param:
            log.debug("\nModified Config:{} \n{}\n".format(self.cam_mac,
                                                           conf_param))

    def _check_target_match(self, namespace):
        if self.cam_ip and self.cam_port:
            result = self._exec_command(self.cam_ip, self.cam_port)
            return ('VAPIEI' in result and
                    self.addrs._default_mode != 'camelot_server')

    def _exec_command(self, ip, port):
        result = ''
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, int(port)))
            if sys.version_info < (3, 5):
                s.send('cv')
                result = s.recv(1024)
                return result
            else:
                s.send('cv'.encode())
                result = s.recv(1024)
                return result.decode()
        except Exception as e:
            log.debug('Camelot endpoint failed to connect: {}'.format(e))

    def _validate_dict_args(self, dict_arg):
        if type(dict_arg) == str:
            dict_arg = ast.literal_eval(dict_arg)
        if type(dict_arg) == dict or type(dict_arg) == OrderedDict:
            self._prepare_config_param(dict_arg)
            return dict_arg

    def _is_valid_ip(self, ip):
        if not VAPIEIUtils.is_valid_ipv4(
                ip) and not VAPIEIUtils.is_valid_ipv6_address(
                ip):
            return False
        return True

    def _validate_args(self):
        # TODO: throw exception here
        try:
            if self.cam_ip == '0.0.0.0':
                return
            if not self._is_valid_ip(self.cam_ip):
                log.error('Not a valid camelot server ip[%s]'
                          % self.cam_ip)
                return
            if not isinstance(self.cam_port, int):
                log.error('Camelot port is not a valid integer')
                return
            params = self.config_params
            # TODO Detailed verification of parameters by maintaining a list
            if 'sip.phone.tftpip' in params:
                if not self._is_valid_ip(params.get(
                        'sip.phone.tftpip')):
                    log.error('Not a valid TFTP IP in config parameters')
                    return
            if not isinstance(params.get('sip.phone.deviceid'), int):
                log.debug('DEVICE_ID is not a valid integer')
            if 'sip.phone.ip' in params:
                if not self._is_valid_ip(params.get(
                        'sip.phone.ip')):
                    log.error('Not a valid PHONE_IP in config parameters')
                    return
            return True
        except Exception:
            log.exception('Un expected exception while _validate_args(): ')
            return

    def get_ipv6(self):
        '''Returns the ipv6 address for the device.
        '''
        camelot_ipv6 = self.vapi.get_info()['ipv6address']
        if not camelot_ipv6:
            camelot_ipv6 = self.cam_mac
        return camelot_ipv6

    def get_ip(self):
        '''
            Returns the ipv4 address for the device.
        '''
        camelot_ipv4 = self.vapi.get_info()['ipv4address']
        if not camelot_ipv4:
            camelot_ipv4 = self.cam_mac
        return camelot_ipv4

    def get_feedback_handler(self):
        return CamlotFeedbackHandler

    def get_number(self, protocol='sip', profile=1, e164=False):
        if self.ep_type == 'cas':
            log.debug('its cas endpoint is %s' % self.ep_type)
            result = self.vapi.get_lines()
            return result

        result = self.vapi.get_lines()
        if not result or len(result) < 0:
            log.debug('Empty get_lines output, no associated DN found')
            return

        primary_line = result[0]
        if primary_line.get('full_address'):
            full_address = primary_line.get('full_address')
        else:
            log.error('Line does not have attribute "full_address" ')
            return
        try:
            if '@' in full_address:
                ep_dn = full_address[:full_address.index('@')]
            else:
                ep_dn = full_address
            return ep_dn
        except Exception:
            log.error('No DN allocated to the Endpoint')

    def get_version_string(self):
        data = self.get_device_info()
        return 'CamelotEP {version}'.format(version=data['Version'])

    def get_device_info(self):
        ''' Fetches the Device Basic information '''
        data = {'DeviceInfo': self.get_system_name(),
                'PhoneDN': self.get_number(),
                'Version': self.cli_version,
                'MAC Address': self.cam_mac,
                'Model Name': 'Camelot Endpoint',
                'Camelot Server ip': self.cam_ip}
        return data

    def get_system_name(self):
        '''Returns the name of the device, e.g.
        ``'SEPBAACBAAC7001'``'''
        return self.cam_mac

    def log_to_device(self, message):
        pass

    def get_mac_address(self):
        '''Returns the MAC address for the device.
        '''
        return self.cam_mac

    def dial(self, receiver, **kwargs):
        '''Instruct the endpoint device to dial another endpoint device
        (the receiver) under the control of TNG pi. Protocol can be a string
        containing the word 'to', such as 'h323tosip', in which case we will
        try to establish an interworked call.

        The should_fail parameter is used to change the behaviour of the method
        in the case where we expect a call to fail. If should_fail is True and
        the call does indeed fail we swallow the CallError the failure raises
        and do not note the failure on the backend. If the call unexpectedly
        connects, we raise an AssertionError. If should_fail is False (ult)
        dial behaviour is completely normal.
        '''
        if not kwargs.get('audio_only'):
            kwargs['audio_only'] = self.audio_only

        return super(Camelot, self).dial(receiver, **kwargs)

    def dial_device_with_alias(self, receiver, alias, interface_name=None,
                               *args, **kwargs):
        if not kwargs.get('audio_only'):
            kwargs['audio_only'] = self.audio_only

        return super(Camelot, self).dial_device_with_alias(
            receiver, alias, interface_name=interface_name,
            *args, **kwargs)

    def dial_alias(self, alias, **kwargs):
        if not kwargs.get('audio_only'):
            kwargs['audio_only'] = self.audio_only

        return super(Camelot, self).dial_alias(alias, **kwargs)

    def answer_incoming(self, otherside, **kwargs):
        if not kwargs.get('audio_only'):
            kwargs['audio_only'] = self.audio_only

        return super(Camelot, self).answer_incoming(
            otherside, **kwargs)

    def blind_transfer(self, transferee, receiver, **kwargs):
        if not kwargs.get('audio_only'):
            kwargs['audio_only'] = self.audio_only

        return super(Camelot, self).blind_transfer(
            transferee, receiver, **kwargs)

    def blind_transfer_with_alias(self, transferee, receiver,
                                  receiver_alias, **kwargs):
        if not kwargs.get('audio_only'):
            kwargs['audio_only'] = self.audio_only

        return super(Camelot, self).blind_transfer_with_alias(
            transferee, receiver, receiver_alias, **kwargs)

    def consultative_transfer(self, transferee, receiver, **kwargs):
        if not kwargs.get('audio_only'):
            kwargs['audio_only'] = self.audio_only

        return super(Camelot, self).consultative_transfer(
            transferee, receiver, **kwargs)

    def consultative_transfer_with_alias(self, transferee, receiver,
                                         receiver_alias, **kwargs):
        if not kwargs.get('audio_only'):
            kwargs['audio_only'] = self.audio_only

        return super(Camelot, self).consultative_transfer_with_alias(
            transferee, receiver, receiver_alias, **kwargs)

    def join_ad_hoc(self, joinee1, joinee2, **kwargs):
        if not kwargs.get('audio_only'):
            kwargs['audio_only'] = self.audio_only

        return super(Camelot, self).join_ad_hoc(
            joinee1, joinee2, **kwargs)

    def join_ad_hoc_with_alias(self, joinee1, joinee2, joinee2_alias,
                               **kwargs):
        if not kwargs.get('audio_only'):
            kwargs['audio_only'] = self.audio_only

        return super(Camelot, self).join_ad_hoc_with_alias(
            joinee1, joinee2, joinee2_alias, **kwargs)

    def get_model_number(self, timeout=1):
        '''This method returns the Model number of the IOS device
        ''' '''Change this in future TO-DO'''
        return 'Camelot Endpoint'

    def _pre_deactivation(self):
        '''Overriden method. Stops the test case execution and puts the
         endpoint out of service

        :returns: None
        '''
        super(Camelot, self)._pre_deactivation()
        self.camelot_endpoint_clean_exit()

    def get_logs(self, log_dir):
        ep_log_dir = self.vapi.ep_log_dir()
        ep_sipx = self.vapi.ep_log_file_prefix()
        if self.log_src_dir and ep_log_dir:
            if ep_log_dir.endswith('/'):
                ep_log_dir_splt = ep_log_dir[:-1].split('/')
            else:
                ep_log_dir_splt = ep_log_dir.split('/')
            ep_log_dir = '{}/{}/{}/{}'.format(
                self.log_src_dir, ep_log_dir_splt[-3], ep_log_dir_splt[-2],
                ep_log_dir_splt[-1])
        if ep_log_dir and ep_sipx:
            if log_dir.endswith("/"):
                log_dir = '{}{}_{}'.format(log_dir, ep_sipx,
                                           self.ip)
            else:
                log_dir = '{}/{}_{}'.format(log_dir, ep_sipx,
                                            self.ip)
        log.info("camelot ep log: {}".format(log_dir))
        self.scp.get_dir(ep_log_dir, topath=log_dir)

    def is_outofservice(self):
        if self.vapi.get_info()['state'] == 'outofservice':
            return True
        else:
            return False

    def camelot_endpoint_clean_exit(self):
        '''Stops camelot endpoint on the server side.

        :returns: None
        '''
        log.debug('in camelot_endpoint_clean_exit...')
        if self.vapi:
            if (self.vapi.get_info()['state']
                    not in ['outofservice', 'uninitialized']):
                try:
                    self.disconnect_all()
                except Exception:
                    log.exception('Failed to call disconnect_all '
                                  'during cleanup')
                self.vapi.out_of_service()
                tng.api.until(func=self.is_outofservice,
                              timeout=10,
                              raise_on_timeout=False)
            self.vapi.uninit_ep()
            if self.ep_type in ['sipx', 'tandbergsip', 'siptrunk']:
                self.vapi._release_ep()
            serv = camelot.get_camelot_server(self.cam_ip, self.cam_port)
            if serv:
                serv._tng_cleanup_required = False

    def is_sip(self):
        '''Checks if the phone is a Sip phone'''
        return True

    def get_media(self, call_id):
        cm = media.CallMedia(self, call_id)
        streams_data = self.vapi.get_streams()
        call_ref = call_id
        call_id_streams = []
        if call_ref:
            for stream in streams_data:
                if 'StrmID' not in stream:
                    stream['StrmID'] = stream['stream_ref']
                if 'CallId' not in stream:
                    stream['CallId'] = stream['call_ref']
                if 'Type' not in stream:
                    stream['Type'] = stream['type']
                stream_info = self.vapi.get_stream_info(stream['StrmID'])
                stream['RemoteAddr'] = stream_info['address']
                if stream.get('state'):
                    if stream['state'] == 'open':
                        stream['StreamStatus'] = 'Active'
                    else:
                        stream['StreamStatus'] = 'Not Ready'
                if stream.get('direction'):
                    if stream['direction'] == 'inbound':
                        stream['Direction'] = 'Rx'
                        stream['RcvrCodec'] = stream_info.get('codec')
                    elif stream['direction'] == 'outbound':
                        stream['Direction'] = 'Tx'
                        stream['SenderCodec'] = stream_info.get('codec')
            for stream in streams_data:
                if stream['StreamStatus'] == 'Active':
                    stream['CallId'] = stream['CallId'].strip()
                    call_ref = call_ref.strip()
                    if int(stream['CallId'], 16) == int(call_ref, 16):
                        call_id_streams.append(stream)

            if call_id_streams:
                call_details = self.vapi.get_call_info(call_ref)
                cm.add(self._get_audio_in(call_id_streams, call_details))
                cm.add(self._get_audio_out(call_id_streams, call_details))
                video_chns = self._get_video_in(call_id_streams, call_details)
                for chn in video_chns:
                    cm.add(chn)
                video_chns = self._get_video_out(call_id_streams, call_details)
                for chn in video_chns:
                    cm.add(chn)
        return cm

    def _create_audio_channel(self, call_streams, call_details, media_direc):
        channel = CiscoPhoneAudioChannel()
        channel.media_type = media.AUDIO
        stream_active = False
        channel.encryption = False
        for stream in call_streams:
            if (stream['StreamStatus'] != 'Not Ready' and
                    stream['Type'] == 'audio'):
                stream_active = True
                stream_info = self.vapi.get_stream_info(stream['StrmID'])
                if media_direc == media.INCOMING:
                    channel.protocol = stream['RcvrCodec']
                    str_ext = self.vapi.get_stream_info_ext(stream['StrmID'])
                    if str_ext.get('packets received'):
                        channel.packet_count = str_ext['packets received']
                    else:
                        channel.packet_count = 0
                else:
                    channel.protocol = stream['SenderCodec']
                    str_ext = self.vapi.get_stream_info_ext(stream['StrmID'])
                    if str_ext.get('packets sent'):
                        channel.packet_count = str_ext['packets sent']
                    else:
                        channel.packet_count = 0
                if stream_info['transport'] == 'srtp':
                    channel.encryption = True
        if not channel.encryption:
            if stream_active:
                sec_state = call_details['call security status']
                if sec_state in ['unknown', 'not authenticated']:
                    channel.encryption = False
                elif sec_state in ['authenticated', 'encrypted',
                                   'secured media']:
                    channel.encryption = True
                else:
                    channel.encryption = None
            else:
                channel.protocol = None
                channel.encryption = None
        channel.role = media.MAIN
        channel.tag(channel.role, channel.media_type)
        return channel

    def _get_audio_in(self, call_streams, call_details):
        send_list = []
        for stream in call_streams:
            if stream['Direction'] == 'Rx':
                send_list.append(stream)
        if send_list:
            c = self._create_audio_channel(send_list, call_details,
                                           media.INCOMING)
            c.direction = media.INCOMING
            c.tag(c.direction)
            return c
        log.warning('No inbound stream on Camelot endpoint')
        return []

    def _get_audio_out(self, call_streams, call_details):
        send_list = []
        for stream in call_streams:
            if stream['Direction'] == 'Tx':
                send_list.append(stream)
        if send_list:
            c = self._create_audio_channel(send_list, call_details,
                                           media.OUTGOING)
            c.direction = media.OUTGOING
            c.tag(c.direction)
            return c
        log.warning('No outbound stream on Camelot endpoint')
        return []

    def _create_video_channel(self, call_stream, call_details, media_direc):
        channels = []
        stream_active = False
        video_active = False
        for stream in call_stream:
            stream_info = self.vapi.get_stream_info(stream['StrmID'])
            if (stream['StreamStatus'] != 'Not Ready' and
                    stream['Type'] == 'video'):
                if stream_info['content'] == 'slides':
                    channel = CamelotPresentationChannel()
                    channel.role = media.PRESENTATION
                else:
                    channel = CiscoPhoneVideoChannel()
                    channel.role = media.MAIN
                channel.encryption = False
                channel.media_type = media.VIDEO
                stream_active = True
                video_active = True
                if media_direc == media.INCOMING:
                    channel.protocol = stream['RcvrCodec']
                    channel.FrameRate = stream_info['frame rate']
                    channel.ResolutionX = stream_info.get(
                        'picture format customXMax', 0)
                    channel.ResolutionY = stream_info.get(
                        'picture format customYMax', 0)
                    str_ext = self.vapi.get_stream_info_ext(stream['StrmID'])
                    if str_ext.get('packets received'):
                        channel.packet_count = str_ext['packets received']
                    else:
                        channel.packet_count = 0
                else:
                    channel.protocol = stream['SenderCodec']
                    channel.FrameRate = stream_info['frame rate']
                    channel.ResolutionX = stream_info.get(
                        'picture format customXMax', 0)
                    channel.ResolutionY = stream_info.get(
                        'picture format customYMax', 0)
                    str_ext = self.vapi.get_stream_info_ext(stream['StrmID'])
                    if str_ext.get('packets sent'):
                        channel.packet_count = str_ext['packets sent']
                    else:
                        channel.packet_count = 0
                if stream_info['transport'] == 'srtp':
                    channel.encryption = True
                if not channel.encryption:
                    if stream_active and video_active:
                        sec_state = call_details['call security status']
                        if sec_state in ['unknown', 'not authenticated']:
                            channel.encryption = False
                        elif sec_state in ['authenticated', 'encrypted',
                                           'secured media']:
                            channel.encryption = True
                        else:
                            channel.encryption = None
                    else:
                        channel.protocol = None
                        channel.encryption = None
                channel.tag(channel.role, channel.media_type)
                channels.append(channel)
        return channels

    def _get_video_in(self, call_streams, call_details):
        send_list = []
        for stream in call_streams:
            if stream['Direction'] == 'Rx':
                send_list.append(stream)

        if send_list:
            chns = self._create_video_channel(send_list, call_details,
                                              media.INCOMING)
            for c in chns:
                c.direction = media.INCOMING
                c.tag(c.direction)
            return chns
        log.warning('No inbound stream on Camelot endpoint')
        return []

    def _get_video_out(self, call_streams, call_details):
        send_list = []
        for stream in call_streams:
            if stream['Direction'] == 'Tx':
                send_list.append(stream)
        if send_list:
            chns = self._create_video_channel(send_list, call_details,
                                              media.OUTGOING)
            for c in chns:
                c.direction = media.OUTGOING
                c.tag(c.direction)
            return chns
        log.warning('No outbound stream on Camelot endpoint')
        return []

    def send_message(self, msgobj, ip='', port=''):
        try:
            createmsg = 'sendrawmsg {0} {1} {2}@'.format(
                msgobj.msgid, ip, port)
            hex_len = self.vapi._get_message_length_hex(createmsg)
            rawmessage = 'm:{0}:{1}:{2}'.format(
                self.vapi.ep_id, hex_len, createmsg)
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
            else:
                log.error('Send message failed')
        except Exception:
            log.exception('send_message failed reason:')
            log.error('send_message request failed')
            return

    def fill_parm(self, msgobj):
        fillparm = 'fillrawparms {0}@'.format(msgobj.msgid)
        hex_len = self.vapi._get_message_length_hex(fillparm)
        rawmessage = 'm:{0}:{1}:{2}'.format(self.vapi.ep_id,
                                            hex_len, fillparm)
        try:
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
            else:
                log.error('Fill Parm failed')
        except Exception:
            log.error('fill_parm request failed')
            return

    def start_raw_event(self, call_back, event_sub_type='',
                        callid_filter='NONE', method_filter='NONE',
                        cseq_filter='NONE', assist='0'):
        '''
        Registers the event call back on the endpoint for the perticular
        requested event. Once the event has occured, the call back
        function will be invoked.
        From call back user will get event_object from there, user
        can get msgObj()as shown below

        NOTE: This API can be used for Simulated Endpoints as well.
              i.e., the endpoint need not to be RawEndpoint.

        :parameter station_call_back: call back function to get event_object
        :parameter event_sub_type: event sub type
        :parameter callid_filter: callid filter
        :parameter method_filter: method filter
        :parameter cseq_filter: cseq filter
        :parameter assist: '1' -parse msg at sip stack, '0'- no parse
        :returns: None

        Example:
              To get any 200 OK INVITE event

        >>> self.ep1.start_raw_event(self.station_call_back, method_filter=
                                 '200 OK',cseq_filter='INVITE', assist=1)

        >>> Where in definition of call back
        >>> station_call_back(self, event_object=None):
        >>> if not event_object:
        >>>     log.info('Event Object is Null')
        >>> else:
        >>>     msgObj = event_object['msgid']

        '''
        event_type = 'rawevent'
        if event_sub_type != '':
            event_sub = event_sub_type.split(' ')
            callid_filter = event_sub[0]
            method_filter = event_sub[1]
            cseq_filter = 'NONE'

        event_sub_type1 = '{0},{1},{2}'.format(callid_filter,
                                               method_filter.replace(' ', '_'),
                                               cseq_filter.replace(' ', '_'))
        self.vapi.register_to_event(event_type, event_sub_type1, call_back)

        return self.vapi.start_raw_events(
            callid_filter, method_filter, cseq_filter, str(assist))

    def stop_raw_event(self, call_back, event_sub_type='',
                       callid_filter='NONE', method_filter='NONE',
                       cseq_filter='NONE', assist='0'):
        '''
        Un-registers the event call back on the endpoint, which it is
        registered using start_raw_event. parameters are same as start

        NOTE: This API can be used for Simulated Endpoints as well.
              i.e., the endpoint need not to be RawEndpoint.

        :parameter station_call_back: call back function to get event_object
        :parameter event_sub_type: event sub type
        :parameter callid_filter: callid filter
        :parameter method_filter: method filter
        :parameter cseq_filter: cseq filter
        :parameter assist: '1' -parse msg at sip stack, '0'- no parse

        :returns: None
        '''
        self.vapi.stop_raw_events(callid_filter, method_filter, cseq_filter,
                                  str(assist))
        event_type = 'rawevent'
        event_sub_type1 = '{0},{1},{2}'.format(callid_filter,
                                               method_filter.replace(' ', '_'),
                                               cseq_filter.replace(' ', '_'))
        self.vapi.unregister_event(event_type, event_sub_type1)

    def apply_out_action_set(self, actionset, method='NONE', cseq='NONE'):
        '''
        This is used for addition, modification or removal of headers to any
        outgoing SIP message.

        :parameter actionset: out action object to be applied to endpoint.
        :parameter method: method filter
        :parameter cseq: cseq filter

        :returns: 'success' or 'failure'

        >>> out_action_valid_ep1 = self.srv.create_out_action_set()
        >>> out_action_valid_ep1.add_sdp_attrib(typestr='z', value='0 0')
        >>> out_action_valid_ep1.add_sdp_attrib('audio', 'a',
                'ptime','100')
        >>> out_action_valid_ep1.add_sdp_attrib('audio', 'a', value='100')
        >>> out_action_valid_ep1.add_sdp_attrib('audio', 'a', value='200')
        >>> self.ep1.apply_out_action_set(out_action_valid_ep1,
                method='INVITE')
        >>> 'success'
        '''
        msgid = actionset.msgid
        outmsg = 'mergemessage {0}\n{1}\n{2}@'.format(msgid, method, cseq)
        hex_len = self.vapi._get_message_length_hex(outmsg)
        rawmessage = 'm:{0}:{1}:{2}'.format(self.vapi.ep_id, hex_len,
                                            outmsg)

        if actionset.event_type != '':
            self.vapi.register_to_event(actionset.event_type,
                                        actionset.event_sub_type,
                                        actionset.call_back)

        try:
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
            else:
                log.error('apply_action_set failed')
        except Exception:
            log.error('apply_action_set request failed')
            return

    def remove_out_action_set(self, actionset, method='NONE', cseq='NONE'):
        '''
        This is used for removal of out_action_set linked to endpoint.
        This should contain same param values as in apply_out_action_set.

        :parameter actionset: out action object to be applied to endpoint.
        :parameter method: method filter
        :parameter cseq: cseq filter

        :returns: 'success' or 'failure'

        >>> ep1.apply_out_action_set(out_action_Obj, method='INVITE')
        'success'.
        >>> ep1.remove_out_action_set(out_action_Obj, method='INVITE')
        'success'.
        '''
        msgid = actionset.msgid
        outmsg = 'removemergemessage {0} {1} {2}@'.format(msgid, method,
                                                          cseq)
        hex_len = self.vapi._get_message_length_hex(outmsg)

        rawmessage = 'm:{0}:{1}:{2}'.format(self.vapi.ep_id, hex_len,
                                            outmsg)

        try:
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
            else:
                log.error('remove_action_set failed nul returned')
        except Exception as e:
            log.error('remove_action_set request failed reason:%s' % e)
            return

    def create_in_action_object(self):
        '''
        Note: This API is Obsolete.
        Please use create_in_action_set() API available on Server.

        Camelot Wiki link:

        http://10.106.248.246:8080/job/CAMELOT_PI_SDK_DEV/API_Doc/api/camelot_server.html?highlight=create_in_action_set#camelot.camelot_server.CamelotServer.create_in_action_set

        Create a blank set of verification as a place holder
        Then using different command one can keep on adding actions
        for veification of original message.

        NOTE: This API can be used for Simulated Endpoints as well.
              i.e., the endpoint need not to be RawEndpoint.

        >>> inActionObj = create_in_action_set()
        '''
        log.debug("in create_in_action_object method")
        res = self.vapi._query_camelot(camelot.CREATE_TEMPLATE_MSG)
        try:
            if res:
                actionObj = InActionObject(self.vapi, res)
                if actionObj:
                    return actionObj
        except Exception as e:
            log.error('create_in_action_object Failed=%s' % e)

    def remove_inaction_object(self, inaction_obj):
        '''
        Delete the inaction object. Internally, inaction_obj gets
        deleted based on the msgid.

        :parameter inaction_obj: inaction_obj returned by
                                 verify_request_send_response().

        :returns: Upon success, True is returned. Orelse, Exception
                  is thrown from the Camelot.

        >>> ep1.remove_inaction_object(inaction_obj)
            True
        >>> ep1.remove_inaction_object(inaction_obj)
            CamelotError: No match found
        '''
        log.debug("in remove_inaction_object method")
        event_type = 'verifyevent'
        if not isinstance(inaction_obj, InActionObject):
            log.error('invalid inaction object passed')
        if inaction_obj.sub_type:
            self.vapi.unregister_event(event_type, inaction_obj.sub_type)
        return self.vapi._query_camelot(
            camelot.REMOVE_INACTION_OBJ, inaction_obj.msgid)

    def _validate_init_verify_req(self,
                                  call_back,
                                  req_method,
                                  req_content_filter,
                                  req_header_filter):
        supported_methods = ['INVITE', 'UPDATE', 'REFER']
        if req_method not in supported_methods:
            log.error("incorrect method name passed!supported methods are:"
                      " {}".format(supported_methods))
            return
        event_type = 'verifyevent'
        # cseq is used to do a backward compatibility with
        # register_to_event.
        cseq = req_method
        sub_type = '{0},{1}'.format(req_method.replace(' ', '_'),
                                    cseq.replace(' ', '_'))
        verifyobj = self.create_in_action_object()
        if not verifyobj:
            raise CamelotError("in-action object creation failed")
        try:
            self.vapi.register_to_event(event_type, sub_type, call_back)
        except Exception as e:
            raise CamelotError('Failed to register_to_event in'
                               'verify_request_send_response,reason:{}'.
                               format(e))
        if req_content_filter and 'Content-Type' not in req_header_filter:
            raise CamelotError("content_type needs to be given when"
                               " content_filter is specified")
        if not req_header_filter or req_header_filter == {}:
            req_header_filter = 'ALL'
        if not req_content_filter or req_content_filter == {}:
            req_content_filter = 'ALL'
        verifyobj.sub_type = sub_type
        return verifyobj

    def verify_request_send_response(self, call_back,
                                     req_method,
                                     req_header_filter=None,
                                     req_content_filter=None,
                                     resp_status_code=None,
                                     resp_reason_phrase=None,
                                     resp_continue='yes'):
        '''
        This method allows to intercept the incoming SIP requests and
        alter their response. A callback method is registered internally,
        and once the filter matches the inbound SIP request in server, the
        callback method is invoked. This callback will be called for every
        SIP request that match, unless remove_inaction_object is called.

        :parameter call_back: call back method to be registered.
        :parameter req_method: This is the SIP request method to be matched.
         supported methods = ['INVITE', 'UPDATE', 'REFER'].
         It is a Mandatory parameter.
        :parameter req_header_filter: SIP headers to be matched.Default value
         is None. All incoming headers are accepted.
         eg - {"MIME-Version":"1.0", "Content-Type":"multipart/mixed;
         boundary=uniqueBoundary"}
        :parameter req_content_filter: This is the SIP sub-content-type to be
         matched. Default value is None, accepts anything coming inside the
         body.eg - {"application/x-cisco-remotecc-cm+xml":[
         "<ExecuteItem URL", "RTPMTx:Play"]}, matches the sub-content-type
         inside the xml body, sets filter and triggers the callback once SIP
         message is received.
         values possible:\n
         * Default: None. Accepts anything in incoming SIP message's body.
         * set filter for multipart/mixed: {SUB-CONTENT-TYPE:
           ['string1','string2']}.\n
           eg - {"application/x-cisco-remotecc-cm+xml":[
           "<ExecuteItem URL", "RTPMTx:Play"]}. Matches the SUB-CONTENT-TYPE
           and strings in its boundary.\n
         * set filter for other content-types:\n
           {"application/sdp":["media"]}. Matches strings in the entire body.
         Note: If req_header_filter doesnot contain Content-Type, then setting
         req_content_filter will throw exception.\n
        :parameter resp_status_code: This is the response status code to the
         SIP request that has been captured. Default value is None. For None,
         the response is not altered. eg - '202', '200',etc...
        :parameter resp_status_phrase: This is the SIP response phrase to the
         SIP request that has been captured. Default value is None. For None,
         the response is not altered. eg - 'Accepted','OK',etc..
        :parameter resp_continue: This is the flag tells to the camelot that
         response should be sent or not after receiving the incoming request.

        :returns: Upon success, in-action object is returned. On Failure,
         Exception will be thrown.

        :Note: As of now, Camelot supports verify_request_send_response only
         for REFER and Notify scenario.

        >>> in_action_valid_ep1
            = ep1.verify_request_send_response(
                            self.verify_CB_1,
                            req_method='REFER',
                            req_header_filter={"MIME-Version":"1.0", "
                                    Content-Type":"multipart/mixed;boundary=uniqueBoundary"},
                            req_content_filter={"application/x-cisco-remotecc-cm+xml":
                                    ["<ExecuteItem URL", "RTPMTx:Play"]},
                            resp_status_code='480',
                            resp_reason_phrase='Temporarily not availiable')
        '''
        log.debug("in method verify_request_send_response")
        req_method = req_method.upper()
        verifyobj = self._validate_init_verify_req(call_back,
                                                   req_method,
                                                   req_content_filter,
                                                   req_header_filter)
        kwargs = {'header_filter': req_header_filter,
                  'msgid': verifyobj.msgid,
                  'method': req_method,
                  'content_filter': req_content_filter,
                  'status_code': resp_status_code,
                  'reason_phrase': resp_reason_phrase,
                  'resp_continue': resp_continue}
        log.debug("in method verify_request_send_response"
                  "kwargs:{}".format(kwargs))
        res = self.vapi._query_camelot(camelot.VERIFY_REQ_SEND_RESP, **kwargs)
        if res:
            return verifyobj
        else:
            log.error('verify_request_send_resp failed camelot'
                      'returned null')

    def send_request(self, call_handler, subscription_handler, method,
                     body_xml, withsdp=None):
        '''
        This method allows to send a customized SIP request.
        eg- Used to send a NOTIFY request once the callback is triggered
        by verify_request_send_response upon receiving  REFER request.

        :parameter call_handler: call_handler returned by the callback in
         msgObj['call_handler'].
        :parameter subscription_handler: subscription_handler returned by the
         callback in msgObj['subscription_handler'].
        :parameter method: SIP request method that has to be sent. eg-'NOTIFY',
         'INVITE', etc...
        :parameter body_xml: xml body to be sent along with the request.
         eg - '<tag1>xmlbeingsent</tag1>'
        :parameter withsdp: Functionality not yet supported.

        :returns: Upon success, True is returned. On Failure,
         Exception will be thrown. Exceptions such as "invalid CCB or
         SCB passed","request sending in camelot failed" and
         "internal error".

        :Note: As of now, Camelot supports verify_request_send_response only
         REFER and Notify scenario.

        >>> in_action_valid_ep1
            = ep1.verify_request_send_response(
                            self.verify_CB_1,
                            req_method='REFER',
                            req_header_filter='{"MIME-Version":"1.0"}',
                            req_content_type='XML',
                            req_content_filter='ALL',
                            resp_status_code='480',
                            resp_reason_phrase='Temporarily not available')

        >>> def verify_CB_1(msg_obj):
                ep2.send_request(ccb = msgObj['call_handler'],
                                 scb = msgObj['subscription_handler'],
                                 method = "NOTIFY",
                                 body_xml = "with-xml-body",
                                 withsdp = "with-sdp")
        '''
        log.debug("in method send_request")
        kwargs = {'ccb': call_handler,
                  'scb': subscription_handler,
                  'method': method,
                  'body_xml': body_xml,
                  'withsdp': withsdp}
        return self.vapi._query_camelot(camelot.SEND_RAW_REQUEST, **kwargs)

    def start_verify_event(self, call_back, verifyobj,
                           method='ALL', cseq='ALL'):
        event_type = 'verifyevent'
        sub_type = '{0},{1}'.format(method.replace(' ', '_'),
                                    cseq.replace(' ', '_'))
        msgid = verifyobj.msgid
        outmsg = 'startverifyevent {0}\n{1}\n{2}@'.format(
            msgid, method, cseq)
        hex_len = self.vapi._get_message_length_hex(outmsg)
        rawmessage = 'm:{0}:{1}:{2}'.format(
            self.vapi.ep_id, hex_len, outmsg)
        try:
            self.vapi.register_to_event(event_type, sub_type, call_back)
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
            else:
                log.error('start_verify_event failed camelot returned null')
        except Exception as e:
            log.error('start_verify_event failed %s' % e)
            return

    def stop_verify_event(self, verifyobj, method='ALL', cseq='ALL'):
        event_type = 'verifyevent'
        sub_type = '{0},{1}'.format(method, cseq)
        # msgid = verifyobj.msgid
        outmsg = 'stopverifyevent {0}\n{1}@'.format(method, cseq)
        hex_len = self.vapi._get_message_length_hex(outmsg)

        rawmessage = 'm:{}:{}:{}'.format(self.vapi.ep_id, hex_len, outmsg)

        try:
            self.vapi.unregister_event(event_type, sub_type)
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
            else:
                log.error('stop_verify_event returned NULL')
        except Exception as e:
            log.error('stop_verify_event failed reason:%s',
                      e)
            return


class CamlotFeedbackHandler(CiscoPhoneFeedbackHandler):

    def __call__(self, owner, call_info, state_machine):
        if self.owner or self.call_info or self.state_machine:
            raise Exception('Duplicate registration on feedback handler')
        else:
            self.owner = owner
            self.call_info = call_info
            self.state_machine = state_machine
        return self

    def received_event(self, event):
        log.debug('Received event: %s' % event)
        for call in event:
            time.sleep(0.5)
            call_id = call['ref']
            if not call_id:
                continue
            if 'alerting' in call['status']:
                if call_id in self.connected_calls:
                    if self.device.ignore_complex_spontaneous_calls:
                        continue
                    self.push_new_state('disconnected', call_id)
                    self.connected_calls.remove(call_id)
                    time.sleep(1)
                if call_id not in self.initialized_calls:
                    self.initialized_calls.append(call_id)
                self.push_new_state('dialing', call_id)
            elif 'incoming' in call['status']:
                self.initialized_calls.append(call_id)
                self.push_new_state('ringing', call_id)
            elif 'connected' in call['status']:
                if call_id not in self.initialized_calls:
                    self._send_initialization_event(call_id)
                try:
                    call = self.device.get_call_to(self.device)
                    call.set_expecting_disconnect()
                except Exception:
                    pass
                self.push_new_state('connected', call_id)
            elif ('ONHOOK' in call['status'] or
                  'disconnected' in call['status']):
                self.push_new_state('disconnected', call_id)
            elif 'REMOTEHOLD' in call['status']:
                self.calls_on_remotehold.append(call_id)
                self.push_new_state('remote', call_id)
            elif 'held' in call['status']:
                self.calls_on_localhold.append(call_id)
                self.push_new_state('local_hold', call_id)
            elif 'TRANSFERRED' in call['status']:
                if self.device.ignore_complex_spontaneous_calls:
                    if call_id in self.calls_on_localhold:
                        self.calls_on_localhold.remove(call_id)
                        self.push_new_state('local_hold', call_id)
                    elif call_id in self.calls_on_remotehold:
                        self.calls_on_remotehold.remove(call_id)
                        self.push_new_state('remote_hold', call_id)
                    continue
                self._check_CCT_case(call_id)

    def _send_initialization_event(self, call_id):
        matched_call = self.device.vapi.get_call_info(call_id)
        if not matched_call:
            log.error('Unexpected call-id:%s' % call_id)
            return
        if matched_call['direction'] == 'outbound':
            self.push_new_state('dialing', call_id)
        elif matched_call['direction'] == 'inbound':
            self.push_new_state('ringing', call_id)
        self.initialized_calls.append(call_id)

    def _check_CCT_case(self, callid):
        if callid:
            call_info = self.device.vapi._get_call_info(callid)
            if (call_info and call_info['Call State'] == 'connected' and
                    callid in self.connected_calls):
                calls = self.device.vapi.get_calls()
                matched_call = None
                for call in calls:
                    if call['Ref'] == callid:
                        matched_call = call
                        break
                if matched_call:
                    try:
                        matched_call_info = self.device.vapi._get_call_info(
                            matched_call.get('Id'))
                        calling_part = matched_call_info['Calling Party Name']
                        called_part = matched_call_info['Called Party Name']
                        if ('Conference' in called_part or
                                'Conference' in calling_part):
                            log.debug('Conference call on: %s' % self.device)
                            self.push_new_state('local_hold', callid)
                            time.sleep(0.5)
                            self.push_new_state('local_hold', callid)
                            return
                    except Exception:
                        pass
                    self.push_new_state('disconnected', callid)
                    time.sleep(1)
                    if matched_call_info['Type'] == 'OUTBOUND':
                        self.push_new_state('dialing', callid)
                    elif matched_call_info['Type'] == 'INBOUND':
                        self.push_new_state('ringing', callid)
                    self.push_new_state('connected', callid)
                    try:
                        call = self.device.get_call_to(self.device)
                        call.set_expecting_disconnect()
                    except Exception:
                        pass
                else:
                    log.error('No Call found with the passed call-id')

    def register(self, feedback_receiver):
        self.connected_calls = []
        self.initialized_calls = []
        self.calls_on_localhold = []
        self.calls_on_remotehold = []
        self.device.feedback_receiver = feedback_receiver
        self.device.vapi.register_event_callback(
            self.device.vapi._generic_callback_function)
        self.device.vapi.fb_receiver = feedback_receiver
        self.device.vapi.start_info_events()
        self.device.vapi.start_info_events('calls')
        self.device.vapi.start_station_events()
        feedback_receiver.subscribe(self.received_event)
