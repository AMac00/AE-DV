import re
import logging
import sys
from tng.device.abc_device import ABCDevice
from tng.api import creatable_device
import socket
from tng.plugins.plugin import DevicePlugin
import camelot
from camelot.utils.vapi_ei_utils import VAPIEIUtils
from camelot.utils.rawendpoint_helper import (
    MsgObject, OutActionObject, InActionObject, SipTemplateMethods)
from camelot.protocol.tcp.camelot_connection import ConnectionError
from tng.device_helpers import addresses
from tng.device_helpers.addresses import AddressError
from twisted.internet.abstract import isIPAddress


log = logging.getLogger('CamelotServer')


# FIXME: timebeing overriding TNGpi as there are impacts to
# customers
def validate_camelot_mac_ipv4(addr):
    '''Validate a string containing an IPv4 address

    :returns: The normalised, validated address.
    '''
    if addr is None:
        return addr

    try:
        return addresses.validate_mac(addr)
    except AddressError:
        pass

    addr_list = addr.split(':')

    if len(addr_list) == 2 and isIPAddress(addr_list[0]):
        return addr
    else:
        raise AddressError('Invalid IPv4 address "{}"'.format(addr))


# FIXME: timebeing overriding TNGpi as there are impacts to
# customeres
addresses.InterfaceAddrs._validate_and_hook['mac'] = validate_camelot_mac_ipv4
addresses.ADDR_VALIDATORS['mac'] = validate_camelot_mac_ipv4


class CamelotServerPlugin(DevicePlugin):
    name = 'vapi'

    def __init__(self, host='', servers_list=None, version='', **kwargs):
        super(CamelotServerPlugin, self).__init__(**kwargs)
        self.version = version

    def setup(self):
        frontend = {}

        if (not hasattr(self.device, 'cam_servers') or
                not self.device.cam_servers):
            self.set_namespace(None)
            return

        def _create_camelot(ip, port, version):
            cam_obj = None
            try:
                cam_obj = camelot.create_camelot_server(
                    ip, port, version=version)
            except camelot.CamelotError as e:
                log.debug('Camelot Error: [%r], Error: %s' % (self.device, e))
                if e.e_type == 'Internal':
                    cam_obj = camelot.get_camelot_server(ip, port)
            except ConnectionError:
                raise
            except Exception as e:
                log.debug('Camelot Error: [%r], Error: %s' % (self.device, e))
                pass
            return cam_obj

        for ser_name, ser_port in self.device.cam_servers.items():
            obj = _create_camelot(
                self.device.cam_ip, int(ser_port), self.version)
            if obj:
                frontend[ser_name] = obj

        if len(frontend) != len(self.device.cam_servers):
            raise Exception('Failed to create all Camelot servers, '
                            'please refer to detailed logs')

        if frontend:
            if len(frontend) > 1:
                self.set_namespace(frontend)
            else:
                self.set_namespace(list(frontend.values())[0])
        else:
            self.set_namespace(frontend)

    def teardown(self):
        pass


@creatable_device()
class CamelotServer(ABCDevice):

    hardware = 'Camelot Server Machine'
    software = 'Camelot Server'
    platform = 'Camelot Server'
    version_regex = re.compile(
        '''
        (?P<product_code>\w+)\s(?P<major_version>(\d+)).
        (?P<minor_version>(\d+)).
        (?P<revision>(\d+)).(?P<build_num>(\d+))
        (?P<second_build_num>\.(\d+)\.(\d+))
        ''',
        re.I | re.VERBOSE)

    def __init__(self, ip, engine, username='root', password='cisco123',
                 cam_servers=None, version=VAPIEIUtils.CLIENT_VERSION,
                 **kwargs):
        super(CamelotServer, self).__init__(ip, engine, **kwargs)
        self.cam_ip = ip.addr
        self.cam_servers = cam_servers

        if self.addrs.default_mode == 'camelot_server':
            if ip.addr and ':' in ip.addr:
                self.cam_ip = ip.addr[:ip.addr.index(':')]
                port_str = ip.addr[ip.addr.index(':') + 1:]
                self.cam_servers = {'srv1': int(port_str)}
                self.cam_port = int(port_str)
        elif self.addrs.default_mode == 'mac':
            if ip.addr and ':' in ip.addr:
                if len(ip.addr.split(':')) == 2:
                    self.cam_ip = ip.addr[:ip.addr.index(':')]
                    port_str = ip.addr[ip.addr.index(':') + 1:]
                    self.cam_servers = {'srv1': int(port_str)}
                    self.cam_port = int(port_str)
        self.cli_version = version
        self.event_port = 0
        self.cam_feedback = None
        self.plugins |= {
            CamelotServerPlugin(
                version=version,
                check_target_match=self._check_target_match), }

    def _check_target_match(self, connection_namespace):
        if self.cam_ip and self.cam_servers:
            result = self._exec_command(
                self.cam_ip, int(list(self.cam_servers.values())[0]))
            return 'VAPIEI' in result

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
            log.debug('Camelot server failed to retrieve: {}'.format(e))

    # <FIXME:>
    def log_to_device(self, message):
        pass

    def _reset_config_action(self):
        raise NotImplementedError()

    def _upload_image(self, url):
        raise NotImplementedError()
    # </FIXME:>

    def check_is_available(self):
        '''Checks that the device is responding to basic network requests. This
        usually amounts to being able to access at least one device API.

        :returns: True if the device was successfully contacted, or False if
                  the device did not respond.
        '''
        if not self.vapi.get_server_version():
            return False
        return True

    def _boot_action(self):
        log.warning('This Action is not supported on Camelot Server.')
        return

    def _restart_action(self):
        log.warning('This Action is not supported on Camelot Server. To exit'
                    ' the camelot server use command server_exit() to exit'
                    ' camelot server')
        return

    def server_exit(self):
        '''serverexit Exit the camelot server remotely
        '''
        self.vapi.server_exit()

    def get_mac_address(self):
        '''Returns the MAC address for the device.
        '''
        log.warning('This Action is not supported on Camelot Server.')
        return

    def get_logs(self, local_log_path):
        '''Downloads the logs from the device to the given local path. It is
        entirely up to the device author to determine how and in what format
        the logs are retrieved.

        :parameter local_log_path: the path on the local machine to which the
            logs should be downloaded.
        '''
        log.debug('This Action is not supported on Camelot Server. To get '
                  'the get execution log file directory on camelot server '
                  'machine, execute  the camelot server command _log_dir()')
        return

    def _log_dir(self):
        '''Returns the executions logs directory path
        '''
        hex_len = self.get_message_length_hex('logdir@')
        send_msg = 'l:' + '00000000:' + hex_len + ':' + 'logdir@'
        try:
            result = self.vapi._camelot_query(send_msg)
            if result:
                res_list = result.split(":")
                msgobject = MsgObject(self.vapi, res_list[3])
                if msgobject:
                    return msgobject
        except Exception:
            log.error('Create Message Failed')
            return

    def get_version_string(self):
        '''Returns the version string for the device, e.g. X7.0RC3,
        X7.1PreAlpha6, TE2.1.0.2055743.
        '''
        return 'CAMELOT {}'.format(self.vapi.get_server_version())

    def get_system_name(self):
        '''Retrieves from the device the name that the device has been
        configured to identify itself with, for example ``'X201'``.

        ..note::
            Not all devices have a system name.
        '''
        return 'Camelot Server'

    def get_server_version(self):
        '''Fetches the camelot server version
        '''
        return self.vapi.get_server_version()

    def get_vapiei_version(self):
        '''Fetches the compatible vapiei version
        '''
        return self.vapi.get_vapiei_version()

    def get_server_os(self):
        return self.vapi.get_server_os()

    def get_compat_versions(self):
        '''
        Get the compability versions of various app servers

        Queries a running Camelot server for the compatiblity versions of
            various app servers.

        :returns: A string containing the versions of various app servrs that
            Camelot is compatible with.
        '''
        return self.vapi.get_compat_versions()

    def log_mask(self, level=None, moduleid=None, device=None, reset=False,
                 endpoint_level=None):
        ''' Set or get the current server logging level.

        :parameter moduleid: the functional component to which the setting is
                             being applied. Modules defined:\n
                             * cupc - CUPC endpoint related events
                             * cupcd - CUPC-Deskphone mode events
                             * csfd - Client Services Framework Deskphone mode
                               events
                             * http - HTTP related log events
                             * media - IP media related events
                             * mediatransp - IP media transport events.
                               Warning! enabling info
                               level logging or lower may result in huge amount
                               of log information and may impact server
                               performance.
                             * qbe - QBE related log events
                             * qbetransp - QBE line protocols related log
                               events
                             * sccp - SCCP endpoints related events
                             * sccptransp - SCCP protocol level events
                             * sip - SIP endpoints related events
                             * siptransp - SIP protocol level events
                             * tftp - TFTP protocol events
                             * tvs - Trust Verification Service client events
                             * vapi - VAPI client handler events
                             * '*' - global filter
                               Warning! enabling info level logging or lower
                               may result in huge amount of log information
                               and may impact server performance. log messages
                               that do not belong to any of the listed modules
                             * '~' - log messages that do not belong to any of
                               the listed modules

        :parameter level: the log level being applied to a specific module.
                          Levels defined:\n
                          * none - disable logging
                          * error - error level log events
                          * info - high level informational events
                          * debug_1 through debug_5 - debug information
                            (debug_5 being the most detailed)

        :parameter device: either file or console.

        :parameter reset: reset all log settings.

        :parameter endpoint_level: enable logs only for endpoint level.

        :returns: When trying to apply new settings a status string is
                  returned. On success Log Level Set is returned; otherwise an
                  informative exception raised.

        '''
        return self.vapi.log_mask(
            level=level, moduleid=moduleid, device=device, reset=reset,
            endpoint_level=endpoint_level)

    def get_client_version(self):
        return self.cli_version

    def _send_msg_to_server(self, msg_type, outmsg=None):
        if not outmsg:
            return
        if not msg_type:
            log.error('No message type passed to send to server, Returning..')
            return
        hex_len = self.get_message_length_hex(outmsg)
        send_msg = ('%s:00000000:%s:%s' % (msg_type, hex_len, outmsg))
        try:
            result = self.vapi._camelot_query(send_msg)
            ret_result = self.vapi._result_parse(result)
            return ret_result['result_msg']
        except Exception:
            log.error('Coulndnt send the message to Camelot server')
            return

    def get_message_length_hex(self, message):
        if message is None:
            log.warning('No message passed to get Hex length')
            return
        msg_len = len(message)
        hex_val_in_str = hex(msg_len)
        len_hex = len(hex_val_in_str)
        if len_hex == 3:
            hex_val_in_str = hex_val_in_str.replace('0x', '000')
        if len_hex == 4:
            hex_val_in_str = hex_val_in_str.replace('0x', '00')
        elif len_hex == 5:
            hex_val_in_str = hex_val_in_str.replace('0x', '0')
        len_hex = len(hex_val_in_str)
        return hex_val_in_str[(len_hex - 4):len_hex]

    def create_message(self, message, msgobj='', media=''):
        '''Creates a SIP message based on the given parameters. msgid and
        media parameters are optional.

        :parameter message: It can be a SIP message or any supported SIP
                            methods/responses. Currently supported SIP
                            methods/responses are "SIP_INVITE", "SIP_100",
                            "SIP_180", "SIP_200", "SIP_ACK", "SIP_BYE".
        :parameter msgobj:  Creates the current message based on given
                            msgobj. It replaces "To", "From", "Via", "CSeq",
                            and "Call-ID" headers from msgid to current
                            message.
        :parameter media: It can be audio/video

        :Returns: On success, it returns msgobj. On failure the exception
         will be thrown.

        Create a message with SIP message

        >>> msgobj = self.srv.create_message("INVITE sip:[sip.raw.dn]@
        [sip.cm.cm1ip]:[sip.cm.cm1port] SIP/2.0\\nVia: SIP/2.0/TCP
        [sip.phone.ip]:[auto.sip.signalling.port]:;branch=z9hG4bK2639a74d5\\n
        From: \"[sip.line.1]\" <sip:[sip.line.1]@[sip.cm.cm1ip]>;
        tag=52472e61-60466c25\\nTo: \"[sip.line.1]\" <sip:[sip.line.1]@
        [sip.cm.cm1ip]>\\nCall-ID: abcde@1.2.3.5\\nCSeq: 101 INVITE\\n
        Max-Forwards: 6\\n")

        Create a template message with SipTemplateMethods

        >>> msgobj = create_message(SipTemplateMethods.SIP_INVITE)

        Create a message with SIP response and based on another
        SIP message

        >>> msg_180 = create_message("SIP_180", msgobj)

        Create a message with SIP response with media and based on
        another SIP message

        >>> msg_200 = create_message("SIP_200", msg_180, media='audio')
        While creating message or adding sip header all configuration
        parameters can be used. Along with them few special purpose
        configuration parameters are also present
        1) auto.sip.call.newcallid: This tag will generate a new call-id
        2) auto.sip.time.currtime: This will be used to generate value
                                    for Date field
        3) auto.sip.signalling.port: This port will place endpoint signalling
                                    port, used in via and contact
        4) auto.sip.call.contentlen: This will calculate length of SDP and put
                                    that value here
        5) auto.sip.via.branch: This will generate new branch for via
        6) auto.sip.tag: This will generate new tag which can be used in To or
                                    From
        '''
        if msgobj == "":
            msgid = 'NONE'
        else:
            msgid = msgobj.msgid

        if media == "":
            media = 'NONE'

        createmsg = 'createtemplatemessage {0} {1} {2}@'.format(
            media, msgid, message)

        hex_len = self.get_message_length_hex(createmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, createmsg)
        try:
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                msgobject = MsgObject(self.vapi, with_new_line)
                if msgobject:
                    return msgobject
        except Exception:
            log.error('Create Message Failed')
            return

    def delete_message(self, msg):
        '''Delete a message object

        :parameter msg: message to be deleted

        :returns: On success, it returns True. On failure, exception will be
         thrown.

         >>> camelotserver.delete_message(msgobj)
         True
        '''
        delmsg = 'deletemessage {0}@'.format(msg.msgid)
        hex_len = self.get_message_length_hex(delmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, delmsg)
        return(self.vapi._camelot_query(rawmessage))

    def create_out_action_set(self):
        '''
        Note: This API is Obsolete.
        Please use create_out_action_set() API available on Server.

        Camelot Wiki link:

        http://10.106.248.246:8080/job/CAMELOT_PI_SDK_DEV/API_Doc/api/camelot_server.html?highlight=create_out_action_set#camelot.camelot_server.CamelotServer.create_out_action_set

        Create a blank set of actions as a place holder for all the messages.
        Then using different command one can keep on adding different action
        for addition/deletion or modification of original message.

        NOTE: This API can be used for Simulated Endpoints as well.
              i.e., the endpoint need not to be RawEndpoint.

        >>> out_action_valid_ep1 = self.srv.create_out_action_set()
        >>> out_action_valid_ep1.add_sdp_attrib(typestr='z', value='0 0')
        >>> out_action_valid_ep1.add_sdp_attrib('audio', 'a', 'ptime',
                                                 '100')
        >>> out_action_valid_ep1.add_sdp_attrib('audio', 'a', value='100')
        >>> out_action_valid_ep1.add_sdp_attrib('audio', 'a', value='200')
        >>> ep1.apply_out_action_set(out_action_valid_ep1,
                                      method='INVITE')
        '''
        createmsg = 'createtemplatemessage NONE NONE@'

        hex_len = self.get_message_length_hex(createmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, createmsg)
        try:
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                actionObject = OutActionObject(self.vapi, with_new_line)
                if actionObject:
                    return actionObject
        except Exception as e:
            log.error('Create out Action Object Failed reason:%s' % e)
            return

    def delete_out_action_set(self, actionObj):
        delmsg = 'deletemessage {0}@'.format(actionObj.msgid)
        hex_len = self.get_message_length_hex(delmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, delmsg)
        try:
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
        except Exception:
            log.error('Delete Action Set Failed')
            return

    def create_in_action_set(self):
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

        >>> in_action_ep1_ring = self.srv.create_in_action_set()
        >>> in_action_ep1_ring.add_verify_sip_header('Allow-Events',
                'telephone-event',mode=0)
        >>> in_action_ep1_ring.add_verify_sip_header('Server',
                'Cisco-SIPGateway',mode=0)
        >>> self.ep1.start_verify_event(self.verifyRing,
                in_action_ep1_ring,method='180')
        >>> self.ep1.stop_verify_event(in_action_ep1_ring,method='180')
        '''
        createmsg = 'createtemplatemessage NONE NONE@'

        hex_len = self.get_message_length_hex(createmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, createmsg)
        try:
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                actionObj = InActionObject(self.vapi, with_new_line)
                if actionObj:
                    return actionObj
        except Exception as e:
            log.error('Create in Action Object Failed=%s' % e)
            return

    def delete_in_action_set(self, validationObj):
        delmsg = 'deletemessage {0}@'.format(validationObj.msgid)
        hex_len = self.get_message_length_hex(delmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, delmsg)
        try:
            with_new_line = self.vapi._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
        except Exception:
            log.error('Delete Action Set Failed')
            return

    def clone(self, messageid):
        '''Create a copy of the given msgobj.

        :parameter messageid: msgobj to be cloned.

        :returns: On success, it returns msgobj of the new message.
         On failure, exception will be thrown.

        >>> msgobj_new = camelot.clone(msgobj)
        '''
        clonemsg = 'copymessage {0}@'.format(messageid.msgid)
        hex_len = self.get_message_length_hex(clonemsg)
        rawmsg = 'f:00000000:{0}:{1}'.format(hex_len, clonemsg)
        with_new_line = self.vapi._camelot_query(rawmsg)
        if with_new_line:
            msgobject = MsgObject(self.vapi, with_new_line)
            if msgobject:
                return msgobject
        else:
            log.error('clone message failed')
            return

    def create_tone_seq(self, addr, port, tone_list, codec='g711ulaw',
                        leader='~', duration='~', trailer='~'):
        return self.vapi._create_tone_seq(addr, port, tone_list, codec, leader,
                                          duration, trailer)
