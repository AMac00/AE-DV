import camelot
from camelot import camlogger, FaxProfile, DivaFaxOptions, DivaFaxMaxSpeed
import inspect
from camelot.utils import common_utils
from camelot.vapi.vapi_endpoint_query_control import CamelotEndpointControl
from camelot.vapi.vapi_call_control import CamelotCallControl
from camelot.vapi.vapi_supplementary_features import CamelotSFeatureControl
from camelot.vapi.vapi_auto_operations import CamelotAutoOperation
from camelot.vapi.vapi_imp_uds_control import CamelotIMPUdsControl
from camelot.vapi.vapi_media_control import CamelotMediaControl
from camelot.vapi.vapi_vvm_features import CamelotVVMFeatures
from camelot.vapi.vapi_button import CamelotButtonOperation
from camelot.vapi.vapi_ippservices import CamelotIPPServices
from camelot.vapi.vapi_xmpp_operation import CamelotXMPPOperations
from camelot.vapi.vapi_cti_feature import CamelotCTIFeature
from camelot.vapi.vapi_cas_features import CamelotCasOperation
from camelot.utils.rawendpoint_helper import InActionObject
from camelot.utils.customheader_helper import CustomHeadersObject
from camelot.vapi.vapi_headset_operations import CamelotHeadsetOperation
import string


log = camlogger.getLogger(__name__)


class CamelotEndpoint(CamelotEndpointControl, CamelotCallControl,
                      CamelotSFeatureControl, CamelotAutoOperation,
                      CamelotIMPUdsControl, CamelotMediaControl,
                      CamelotVVMFeatures, CamelotButtonOperation,
                      CamelotIPPServices, CamelotXMPPOperations,
                      CamelotCasOperation, CamelotCTIFeature,
                      CamelotHeadsetOperation, object):

    def __init__(self, ep_id, camelot_server_conn):
        self.server_conn = camelot_server_conn
        self.ep_id = ep_id
        self._callback = None
        self._callbackdict = {}
        self._is_valid = True
        self._callbackarg = {}
        self.func_generic_cmd = None
        self.args_generic_cmd = {}

    def reset_to_default(self, camelot_server_conn):
        '''This resets the endpoint to default when connection
        to camelot is restablised , It can be overridden by the user
        to reset the endpoint to default'''
        self.server_conn = camelot_server_conn
        self._callback = None
        self._callbackdict = {}
        self._is_valid = True
        self._callbackarg = {}

    def run_bcg_auto_cmd(self):
        if not self.func_generic_cmd:
            raise camelot.CamelotError('function not set in endpoint')
        self.func_generic_cmd(**self.args_generic_cmd)

    def _is_valid_object(self):
        if self._is_valid:
            return True
        else:
            raise camelot.CamelotError('invalid endpoint address')

    @property
    def ip(self):
        self._is_valid_object()
        return self._get_server_conn().server_ip

    @property
    def port(self):
        self._is_valid_object()
        return self._get_server_conn().server_port

    def _get_server_conn(self):
        if (self.server_conn._stopped):
            log.debug('connection to camelot is stopped')
            serv = camelot.get_camelot_server(self.server_conn.server_ip,
                                              self.server_conn.server_port)
            log.debug('trying to re-establish server connection')
            self.server_conn = serv._get_server_conn()
            return serv._get_server_conn()
        return self.server_conn

    def config_ep_dict(self, param_value_dict):
        '''Set's list of parameters to the Endpoint
        Passed dictionary will be used as param:value pair and all the params
        will be set on the Endpoint , if there is any invalid param or error in
        setting the params exception will be raised

        :parameter param_value_dict: dictionary of the param:value pairs

        :returns: Returns the dictionary of results returned for each set

        >>> import camelot
        >>> params = {'sip.phone.ip':'10.20.1.3',
        ...           'sip.phone.tftpip':'10.20.1.21',
        ...           'sip.phone.deviceid':'1'}
        >>> ep1 = camelot.create_new_endpoint('10.106.248.199', 5004, 'sipx',
        ...                                   'SEPBAACBAAC7001')
        >>> ep1.config_ep_dict(params)
        {'sip.phone.deviceid': '1', 'sip.phone.ip': '10.20.1.3',
         'sip.phone.tftpip': '10.20.1.21'}
        '''
        if not param_value_dict or not isinstance(param_value_dict, dict):
            raise camelot.CamelotError(
                'Pass {parameter: value} dictionary for configuring endpoint')
        ret = {}
        ret_error = {}
        is_errored = False
        order_h264 = 'skinny.cap.vidcaps.0.payloadcapability'
        if order_h264 in param_value_dict.keys():
            result = self._send_config_param(order_h264, param_value_dict[
                                             order_h264])
            del param_value_dict[order_h264]
            if result[0]:
                is_errored = True
                ret_error[order_h264] = result[1]
            else:
                ret[order_h264] = result[1]
        param_value_list = sorted(param_value_dict)
        for param in param_value_list:
            if 'nogencertkey' not in param:
                result = self._send_config_param(
                    param, param_value_dict[param])
            else:
                log.debug('nogencertkey config not send to camelot')
            if result[0]:
                is_errored = True
                ret_error[param] = result[1]
            else:
                ret[param] = result[1]
        if is_errored:
            raise camelot.CamelotError('Failed to configure one or more '
                                       'config params: \n\t%s' % ret_error)
        return ret

    def _send_config_param(self, param, param_value):
        try:
            result = self._query_camelot(camelot.CONFIG, param,
                                         str(param_value))
        except camelot.CamelotError as ce:
            log.error('Failed to configure ==%s==' % param)
            return [True, ce.message]
        return [False, result]

    def config(self, param, value=None):
        '''Set or get the value of a configuration parameter

        If the "value" is specified, the parameter is set to the new specified
        value, else this will return the configured value on Endpoint.

        :parameter param: name of the configuration parameter
        :parameter value: value to set

        :returns: If the "value" is specified, the parameter is set to the new
         specified value, else this will return the configured value on
         Endpoint.

        Setting a param for endpoint

        >>> import camelot
        >>> ep1 = camelot.create_new_endpoint('10.106.248.199', 5004, 'sipx',
        ...                                   'SEPBAACBAAC7001')
        >>> ep1.config('sip.phone.ip', '10.20.1.3')
        '10.20.1.3'

        Getting a param value of endpoint

        >>> import camelot
        >>> ep1 = camelot.create_new_endpoint('10.106.248.199', 5004, 'sipx',
        ...                                   'SEPBAACBAAC7001')
        >>> ep1.config('sip.phone.deviceid', '1')
        '1'
        >>> ep1.config('sip.phone.sip_call_features.meetme_service_uri', '')
        ''
        '''
        log.debug('Entering config function : '
                  'param{}\n value{}\n'.format(param, value))
        if value == '':
            value = 'none'
        return self._query_camelot(camelot.CONFIG, param, value)

    def init(self):
        '''If the endpoint is in the uninitialized state, this method will
        read the endpoint's configuration and initialize the endpoint.

        :returns: The new state of the endpoint.  If the endpoint is in the
         uninitialized state, initpending or outofservice will be returned
         indicating successful start of initialization or successful completion
         of initialization.  If initialization is not successfully started,
         camelot.CamelotError will be raised.\n
         If initialization successfully starts (i.e. initpending is returned),
         but is unable to complete, the endpoint ultimately returns to the u
         ninitialized state.  Use the getinfo method to retrieve status
         information regarding why the endpoint could not be initialized.\n
         If the endpoint is already initialized then no initialization will
         take place, and the current state of the endpoint will be returned.

        >>> import camelot
        >>> params = {'sip.phone.ip':'10.20.1.3',
        ...           'sip.phone.tftpip':'10.20.1.21',
        ...           'sip.phone.deviceid':'1'}
        >>> ep1 = camelot.create_new_endpoint('10.106.248.199', 5004, 'sipx',
        ...                                   'SEPBAACBAAC7001')
        >>> ep1.config_ep_dict(params)
        {'sip.phone.deviceid': '1', 'sip.phone.ip': '10.20.1.3',
         'sip.phone.tftpip': '10.20.1.21'}
        >>> ep1.init()
        'outofservice'
        '''
        log.debug('Entering init function')
        return self._query_camelot(camelot.INIT)

    def _release_ep(self):
        return self._query_camelot(camelot.RELEASE_EP)

    def inservice(self):
        '''Attempts to bring an out of service endpoint in service.

        :returns: The new state of the endpoint.  If the endpoint is in any
         state other than outofservice, no attempt will be made to
         place the endpoint in service, and the endpoint's current
         state will be returned.\n\n
         If the endpoint is in the outofservice state, and the in
         service process can be successfully started or completed,
         this method returns either inservicepending or inservice.
         If the in service process successfully starts
         (i.e. inservicepending is returned) but does not complete,
         the endpoint returns to the outofservice state.  Use the
         getinfo method to get status information regarding the
         problem.

        >>> import camelot
        >>> params = {'sip.phone.ip':'10.20.1.3',
        ...           'sip.phone.tftpip':'10.20.1.21',
        ...           'sip.phone.deviceid':'1'}
        >>> ep1 = camelot.create_new_endpoint('10.106.248.199', 5004, 'sipx',
        ...                                   'SEPBAACBAAC7001')
        >>> ep1.config_ep_dict(params)
        {'sip.phone.deviceid': '1', 'sip.phone.ip': '10.20.1.3',
         'sip.phone.tftpip': '10.20.1.21'}
        >>> ep1.init()
        'outofservice'
        >>> ep1.inservice()
        'inservicepending'
        '''
        log.debug('Entering inservice function')
        return self._query_camelot(camelot.IN_SERVICE)

    def client_suspend(self):
        '''Attempts to bring an inservice endpoint to suspended state.
        This API can be used only for JabberMobile endpoint.

        :returns: The endpoint state as inservice_suspended.

        >>> ep1.client_suspend()
        'inservice_suspended'
        '''
        log.debug('Entering client_suspend function')
        return self._query_camelot(camelot.CLIENT_SUSPEND)

    def client_foreground(self, cucm_info={}):
        '''Attempts to bring a suspended endpoint to in service.
        This API can be used only for JabberMobile endpoint. If the endpoint
        state is not inservice_suspended it will not act anything.

        :parameter cucm_info: new cucm ip info where endpoint need to
         REGISTER as part of foreground(). This optional parameter can
         be omitted in case for REGISTER to the same cucm of before suspened.
         This cucm_info dictionary will have 'type' and 'value' keys in it.
         Below are the possible values of 'type' key are: \n
         * 'IP'   - for ip addr as a value.
         * 'HOST' - for hostname as a value.
         * 'FQDN' - for FQDN hostname as a value.
         * 'PRIORITY' - for cucm priority number as a value
                        same from Device config file.

         These hostname/FQDN value should be any one of the CUCMs
         received in device config file.

        :returns: endpoint state. If the endpoint is inservice_suspended then
                    it will return inservice_foregroundpending and then after
                    register complete endpoint will move to inservice
        For any missing/invalid arguments, exception will be thrown and can
        be referred camelot logs for more information.
        For other Registration issues, endpoint will be moved to outofservice.

        >>> Foreground to the same cucm of before suspended
        >>> ep1.client_foreground()
        'inservice_foregroundpending'

        >>> Foreground to the new cucm
        mydict = {'type':'FQDN', 'value':'cam-ccm-117.camelot.test'}
        OR
        mydict = {'type':'HOST', 'value':'cam-ccm-117'}
        OR
        mydict = {'type':'IP', 'value':'10.12.10.84'}
        OR
        mydict = {'type':'PRIORITY', 'value':'1'}
        >>> ep1.client_foreground(cucm_info=mydict)
        'inservice_foregroundpending'

        >>> Error cases:
        >>> mydict = {'type':'TESTING', 'value':'cam-ccm-117'}
        >>> ep1.client_foreground(cucm_info=mydict)
        Exception: invalid type for cucm info dict
        >>> FQDN not found in device config file
           mydict = {'type':'FQDN', 'value':'cam-ccm-117'}
        >>> ep1.client_foreground(cucm_info=mydict)
        CamelotError: client_foreground failed: invalid argument
        >>> ipaddr not found in any resolved hostname from device config file
           mydict = {'type':'IP', 'value':'10.12.10.230'}
        >>> ep1.client_foreground(cucm_info=mydict)
        CamelotError: client_foreground failed: invalid argument
        '''
        log.debug('Entering client_foreground function')

        if (len(cucm_info)):
            cucm_type = cucm_info.get('type', None)
            cucm_value = cucm_info.get('value', None)
            key_list = ['IP', 'HOST', 'FQDN', 'PRIORITY']
            if not cucm_type:
                raise Exception('no type key for cucm info dict')
            if not cucm_value:
                raise Exception('no value key for cucm info dict')
            if cucm_type not in key_list:
                raise Exception('invalid type for cucm info dict')
            return self._query_camelot(camelot.CLIENT_FOREGROUND,
                                       None, **cucm_info)
        return self._query_camelot(camelot.CLIENT_FOREGROUND)

    def uninit(self):
        '''Put an endpoint into uninitialized state

        :returns: The new state of the endpoint.  If the endpoint is currently
                    in service, then outofservicepending will be returned.  If
                    the endpoint is out of service, uninitialized will be
                    returned.

        >>> import camelot
        >>> params = {'sip.phone.ip':'10.20.1.3',
        ...           'sip.phone.tftpip':'10.20.1.21',
        ...           'sip.phone.deviceid':'1'}
        >>> ep1 = camelot.create_new_endpoint('10.106.248.199', 5004, 'sipx',
        ...                                   'SEPBAACBAAC7001')
        >>> ep1.config_ep_dict(params)
        {'sip.phone.deviceid': '1', 'sip.phone.ip': '10.20.1.3',
         'sip.phone.tftpip': '10.20.1.21'}
        >>> ep1.init()
        'outofservice'
        >>> import time
        >>> time.sleep(5)
        >>> ep1.un_init()
        'uninitialized'
        '''
        log.debug('Entering un_init function')
        return self._query_camelot(camelot.UNINIT)

    def outofservice(self):
        '''Place an endpoint out of service

        :returns: If the endpoint is in service, outofservicepending or
                    outofservice will be returned. Otherwise, the current
                    state of the endpoint will be returned.

        >>> import camelot
        >>> params = {'sip.phone.ip':'10.20.1.3',
        ...           'sip.phone.tftpip':'10.20.1.21',
        ...           'sip.phone.deviceid':'1'}
        >>> ep1 = camelot.create_new_endpoint('10.106.248.199', 5004, 'sipx',
        ...                                   'SEPBAACBAAC7001')
        >>> ep1.config_ep_dict(params)
        {'sip.phone.deviceid': '1', 'sip.phone.ip': '10.20.1.3',
         'sip.phone.tftpip': '10.20.1.21'}
        >>> ep1.init()
        'outofservice'
        >>> ep1.inservice()
        'inservicepending'
        >>> import time
        >>> time.sleep(5)
        >>> ep1.inservice()
        'inservice'
        >>> ep1.out_of_service()
        'outofservicepending'
        '''
        log.debug('Entering out_of_service function')
        return self._query_camelot(camelot.OUT_OF_SERVICE)

    def get_info(self):
        '''Get information about an endpoint

        :returns: returns a dictionary with following fields :\n
                  * state - current state of endpoint, uninitialized,
                    outofservice,inservice, initpending, inservicepending,
                    outofservicepending, client_suspended,
                    client_foregroundpending.
                  * type - type of endpoint, sccp, sip, h323, pri, cas, raw,
                    jabber.
                  * description - description of the endpoint.
                  * overall state - It is a mirror of state field till it
                    comes to inservice. After inservice if any of the
                    refreshes on endpoint fails then this field will display
                    with inservicepending otherwise it will display state
                    field value.
                    Below are the type of refreshes will be invoked on the
                    Jabber:\n
                    * auth cookie refresh
                    * config refresh
                    * auth token refresh (cucm/unity)
                    * uds server refresh
                    * buddy list refresh
                  * current login - This field will display with type of
                    login/process which is in-progress during inservice on
                    endpoint at the time getinfo command is invoked. if
                    endpoint state is inservice or not initiated the
                    inservice process, this field will display as empty.
                    Below are the possible values:\n
                    * edge config
                    * uds
                    * cucm sso
                    * unity sso
                    * imp
                    * device config
                    * registration
                  * lines - number of lines associated with endpoint.
                  * calls - number of call references currently associated
                    with endpoint.
                  * streams - number of media streams currently associated
                    with endpoint
                  * primary cm - IP of the current primary call manager.
                  * backup cm - IP address of the current backup call manager.
                  * status - string describing the temorary errors on the
                    endpoint, e.g.if endpoint received an error response an
                    error response while downloading CTL/ITL file.
                  * registration error - This field will display any error
                    which is making endpoint to go outofservice.
                  * last error - string describing the previous value of
                    field of get_info() API.\n
                    https://wiki.cisco.com/display/CAMELOT/Configuration+files+download#Configurationfilesdownload-CTL/ITLDownloadFailureHandlingandTFTPfailover
                  * delay offer - false if offer is going with Invite true
                    otherwise.
                  * Voice Mail client status - The current status of the
                    voicemail client (where available). Possible values:
                    disconnected, connecting,connected, disconnecting.
                  * primary cti - IP address of the primary CTI manager, if the
                    endpoint is a CUPC-Deskphone. For all other endpoint types
                    this would be empty.Please note, primary cm information in
                    the getinfo will be empty for a CUPC-Deskphone.
                  * backup cti - IP address of the backup CTImanager, if the
                    endpoint is a CUPC-Deskphone. For all other endpoint types
                    this would be empty. Please note, backup cm information in
                    the getinfo will be empty for a CUPC-Deskphone.
                  * current cti - IP address of the current logged in CTI
                    manager, if the endpoint is a CUPC-Deskphone. For all
                    other endpoint types this would be empty.
                  * id - Internal server generated endpoint id
                  * userid - userid of the user associated with the endpoint
                  * preferred mode - Displays the DMC phone preferredmode
                    configured for incoming calls and the same is sent in
                    registration.
                  * call type - Displays the DMC phone calltype configured for
                    outgoing calls.
                  * domain - This displays the Organization Top Level Domain of
                    the cluster which is read from tftp config file. The
                    setting is being read from the organization top level
                    domain enterprise parameter.
                  * sip port - This displays the local port of the end point
                    for the SIP messages.
                  * ixenabled - This field displays the endpoint IX channel
                    feature negotiation status after registration complete. The
                    possible values are yes or no.
                  * esrstvernego - This field displays the endpoint ESRST
                    Version Negotiation feature negotiation status after
                    registration complete. The possible values are <versiontag>
                    or null.
                  * login type - This field displays the type of login incase
                    of jabber endpoint. The possible values are :
                    *sso: sso based login
                    * uc-directory: directory based login
                  * deploymentmodel: type of deployment model possible values
                    are:
                    * on-premise
                    * hedge
                    * edge
                  * privacy - This field displays the privacy information of an
                    endpoint.The possible values are:
                    * enabled
                    * disabled
                  * By default the value is disabled
                  * tlscipher - Negotiated TLS cipher for SIP signalling.
                  * config version stamp -This field displays the version stamp
                    downloaded from the <MAC>.cnf.xml file of the endpoint. The
                    value will be updated only if the endpoint has successfully
                    inservice/registred. If the endpoint goes to out of service
                    then this field value will be cleared.
                  * config file version refer response - response code of the
                    Out of dialog REFER message sent for the version stamp
                    reporting. The value will be updated only if the endpoint
                    has successful inservice/registration. If the endpoint goes
                    to out of service, then this field value will be cleared.
                    Note: This field will not have significance for skinny
                    endpoints.
                  * register_supported - list of supported tags received in
                    200 OK response for initial register message.
                  * voicepush_delete_code - contains the HTTP response code
                    received for the DELETE devicetoken api
                  * voicepush_delete_error - the text contained in
                    error_description, if any, received for the DELETE
                    devicetoken api. For code 200, this is an empty string.
                  * voicepush_token_code - contains the HTTP response code
                    received for the PUT devicetoken api.
                  * voicepush_token_error - the text contained in
                    error_description, if any, received for the PUT
                    devicetoken api.For code 200, this is an empty string.
                  * last_lifecycle_event - this shows service control
                    notification actions.
                    `refer wiki doc <https://wiki.cisco.com/display/CAMELOT/
                    Service+Control+Notification#ServiceControlNotification-
                    Featuredescription>`_
                  * last_lifecycle_timestamp - time stamp of service control
                    notification actions.
                  * last SSL error - this shows most recent SSL error message
                    thrown for while making SSL connection
                  * negotiated_curves - this shows the most recent curve
                    negotiated for SSL connection.
                    `refer wiki doc <https://wiki.cisco.com/display/CAMELOT/
                    Elliptic+Curve+Cryptography%28ECC%29+Support>`_
                  * register_callid - callid used for active sip registration
                  * register_warning - displays the warning message received
                    from the 403 sip response msg for active sip registration
                  * register_reason - displays the reason message received
                  * sip_remote_port - displays the ccm remote port information
                    for on-premise deployment for sip registrations
                    possible cases and values are:\n
                    * oAuth Enabled(5090)
                    * oAuth disabled and secure registration enabled(5061)
                    * oAuth disabled and non secure registration enabled(5060)

        >>> import camelot
        >>> params = {'sip.phone.ip':'10.20.1.3',
                      'sip.phone.tftpip':'10.20.1.21',
                      'sip.phone.deviceid':'1'}
        >>> ep1 = camelot.create_new_endpoint('10.106.248.199', 5004, 'sipx',
                                              'SEPBAACBAAC7001')
        >>> ep1.config_ep_dict(params)
        {'sip.phone.deviceid': '1', 'sip.phone.ip': '10.20.1.3',
         'sip.phone.tftpip': '10.20.1.21'}
        >>> ep1.get_info()
        {'backup_cm': None,
         'backup_cti': None,
         'call_type': None,
         'calls': '1',
         'central uds':'',
         'config download cipher':'ECDHE-RSA-AES256-GCM-SHA384',
         'config file version refer response': '481',
         'config file version stamp' : '',
         'current_cti': None,
         'current login': '',
         'deploymentmodel': 'on-premise',
         'description': 'SEPBAACBAAC7003,10.20.1.3,tcp;(tnp)',
         'domain': None,
         'esrstvernego': 'null',
         'id': 'sipx1',
         'ipv4_address': '10.20.1.3',
         'ipv6_address': None,
         'ix_enabled': 'no',
         'last_error': None,
         'lines': '1',
         'preferred_mode': None,
         'primary_cm': '10.20.1.21',
         'primary_cti': None,
         'sip_port': '51789',
         'state': 'inservice',
         'status': None,
         'streams': '2',
         'type': 'sipx',
         'userid': 'phoneuser',
         'voice_mail_client_status': 'inactive',
         'register_supported': ['X-cisco-voicepush-enabled'],
         'voicepush_delete_code': '204',
         'voicepush_delete_error': '',
         'voicepush_token_code': '200',
         'voicepush_token_error': '',
         'last SSL error': '',
         'negotiated_curves': 'P-256',
         'last_lifecycle_event': 'service control action=reset',
         'last_lifecycle_timestamp': '2017-01-24T18:37:56.943-05:30',
         'register_callid': '2685789952040493@10.12.10.224',
         'register_warning': '399 cam-ccm-99 "Registration is active
          for another client"',
         'register_reason': '',
         'sip_remote_port;: '5061'}
        '''
        return self._query_camelot(camelot.GET_INFO)

    def get_unity_info(self):
        '''Get information about an endpoint

        :returns: unity server information

        >>> ep1.get_unity_info()
        {'vvm subscription failurereason': '',
        'jsessionidsso': 'FBD3F308D5D7707E871EBC93A1AB362D',
        'backup2 server port': '0', 'backup2 server': '',
        'jsessionid': 'E9411EC633B0BFA93C09D987D8B1CC6C',
        'primary server': 'cam-unity-2.camelot.test',
        'primary server port': '8443', 'active server':
        'cam-unity-2.camelot.test', 'backup1 server port': '0',
        'vvm subscription status': 'active',
        'backup1 server': '', 'active server port': '8443'}
        '''
        return self._query_camelot(camelot.GET_UNITY_INFO)

    def get_tftp_info(self):
        '''
        Get detailed informations about the tftp download operation.

        :returns: dictionary of tftp file download informations.\n
                  * downloaded - List of tftp files downloaded successfully.
                  * remote_port - List of tftp files downloaded successfully
                    and their remote ports.
                  * jabber_profile - Any error inforamtion in case
                    jabberProfile download failed:\n
                    * response - response info\n
                      * status_code - http error response code
                      * reason_phrase - http error response "reason phrase"
                        or "connection failure" for server connection fail
                        or "reponse timeout" for response timeout
                    * sign_algorithm - jabberProfile signed file
                      algorithm like "MD-5"/"SHA-256" etc.,
                      "not avail" if file not downloaded
                    * sign_verification - jabberProfile signed file
                      verfication state. like "done"/"not done"/"errored"
                      etc.,
                    * advanced_encryption_algorithms - values are as below\n
                      ITL file and finds 0x1c tag:\n
                      |  <version>      |  <aea>   |\n
                      |  >= 0x01 0x01   |  True    |\n
                      |  < 0x01 0x01    |  False   |\n
                      ITL file and finds no 0x1c tag:\n
                      set to "not found"
                    * ctl_checksum - Returns both MD5 and SHA1 checksum of the
                      CTL file downloaded
                    * itl_checksum - Returns both MD5 and SHA1 checksum of the
                      ITL file downloaded
                    * ext_itl_checksum - Returns both MD5 and SHA1 checksum of
                      the extended ITL file downloaded
                  * xmldefault - information on default config file download:\n
                    * error - error encountered\n
                    * response_code - status code of response\n
                    * response_phrase - reason phrase of response\n
                    * state - possible values are "none","inprogress", and\n
                      "success"\n
                      and "failed"
                    * url - absolute url of XMLDefault file\n
                    * warning - warning header if present in the response\n


        >>> ep1.get_tftp_info()
        Example is given below.
        {'userLocalWinChar': 'iso-8859-1',
        'load': 'sip9971.9-4-2SR2-2',
        'CTLparsing': 'done',
        'protocol': 'tftp',
        'version': '1459274194-6b4e3f15-66b5-440a-9055-5eb396c5dff6',
        'fp_sign_verification': 'done',
        'primary': '10.12.10.74',
        'time elapsed': '83 ms',
        'cfg_sign_verification': 'done',
        'userLocalName': 'English_United_States',
        'state': 'tftp done',
        'dialplan_sign_verification': 'done',
        'ctl_sign_verification': 'done',
        'softkey_sign_algorithm': 'SHA-512',
        'dialplan_sign_algorithm': 'SHA-512',
        'itl_sign_verification': 'not done',
        'downloaded': 'CTLFile.tlv SEPABBA99711001.cnf.xml
        sip9971.9-4-2SR2-2.loads DefaultFP0000000000-c7a6c673-7479
        -46b0-839e-014d3d093963.xml DR684abde0-6dbc-9515-dbab-
        b3b740147286.xml
        SK50719900-3bee-4594-bc3f-6400e1a33bf0.xml',
        'cfg_sign_algorithm': 'SHA-512',
        'networkLocal': 'United_States',
        'ctl_sign_algorithm': 'SHA-512',
        'remote_port': {'CTLSEP886588656002.tlv': '6970',
        'ITLSEP886588656002.tlv': '6970',
        'SEP886588656002.cnf.xml.sgn': '6971',
        'SK93886772-e459-a46f-ff8d-e15df16797e8.xml.sgn': '6970',
        'ext_ITLSEP886588656002.tlv': '6971',
        'sip8845_65.12-1-1SR1-4.loads': '6970'},
        'ctl_checksum': {'MD5': '516bd856a24e86a0e397396fe4e36175',
          'SHA1': '663846e9c81f10607e186ded77fbc4940926eac1'},
        'ext_itl_checksum': {'MD5': '84f957595ed53b9deb3b841e08ff6383',
          'SHA1': '519e55826dc2cd632914104f5b2907e66760a344'},
        'itl_checksum': {'MD5': '445a02684c228200aee59bdb8c351adf',
          'SHA1': '56789a614b951326d033c99c7e7cae0b57dd8d71'},
        'secondary': '',
        'config used': 'primary',
        'fp_sign_algorithm': 'SHA-512',
        'itl_sign_algorithm': 'not avail',
        'softkey_sign_verification': 'done',
        'tftp_encrypted': 'yes',
        'jabber_profile': {'response' :{'reason_phrase': 'Not Found',
        'status_code': '404'},'sign_algorithm': 'not avail',
        'sign_verification': 'not done'},
        'XMLparsing': 'done',
        'xmldefault': {'error': '',
        'response_code': '200',
        'response_phrase': 'OK',
        'state': 'success',
        'url': 'http://10.12.10.9:6970/XMLDefault.cnf.xml',
        'warning': ''}
        }"

        >>> ep1.get_tftp_info()['jabber_profile']
        Example "response timeout"
        {'response':{'reason_phrase': 'response timeout', 'status_code': ''},
        'sign_algorithm': 'not avail',
        'sign_verification': 'not done'},

        >>> ep1.get_tftp_info()['jabber_profile']
        Example "connection failed"
        {'response':{'reason_phrase': 'connection failed', 'status_code': ''},
        'sign_algorithm': 'not avail',
        'sign_verification': 'not done'},

        >>> ep1.get_tftp_info()['jabber_profile']
        Example "200 OK"
        {'response':{'reason_phrase': 'OK', 'status_code': '200'},
        'sign_algorithm': 'SHA-512',
        'sign_verification': 'done'},

        '''

        return self._query_camelot(camelot.GET_TFTP_INFO)

    def get_location(self):
        '''
        Get detailed informations about the location based Refer response.

        :returns: dictionary of Refer Msg response paramters.\n
                  * backofftimer - used to give information about backofftimer.
                  * callid - callid of the Refer Msg
                  * state - Refer Msg current state
                  * sessionid - gives local and remote session id values
                  * response - Refer Msg output
                     * status-code: Refer Msg response code
                     * status-text: Refer Msg response status
                     * warning:Refer msg Warning header value if present
                     * Reason: Refer Msg Reason header value if present

        >>> ep1.get_location()[0]
        [{u'backoffTimer': u'60',
          u'callid': u'f1a5e2cc-fc3323e-0-47d5cdd6@10.12.10.224',
            u'response': {u'reason': u'',
            u'status_code': u'202',
            u'status_text': u'Accepted',
            u'warning': u''},
            u'sessionid': {u'local': u'', u'remote': u''},
            u'state': u'complete'}]
        '''

        return self._query_camelot(camelot.GET_LOCATION)

    def get_sip_register(self):
        '''
        Get detailed information about sip registration request/response
        status of the primary/backup nodes.

        :returns:  List of entries of Sip Register Message of primary/backup
                   nodes\n
                  * address - Ipaddress of the register message.
                  * callid - callid of the Register message.
                  * cseq - cseq no of the Register message.
                  * hostname - hostname of the active CUCM node registered
                  * priority - registration priority of the node
                  * camelot_reason - connection down event because of
                    tcp Connection error/TLS negotiation failure/
                    Registration transaction timeout
                    Error reason with error code is updated in the field.
                  * response - Register Message Response output
                     * status-code: Register message response code
                     * status-text: Register message response status
                     * warning:Register msg response warning header if present
                     * reason:Register msg response reason header if present
                  * state - Sip Registration state.Possible values are
                    As soon as sip registration is triggered then 'state'
                    value will be "inservicepending.
                    When 200 ok received for register move the state to
                    "inservice".
                    when Refresh register is triggered then state will be same
                    as "inservice"
                    When SIP De-Register is triggered move the state to
                    "outofservicepending".
                    Move to "outofservice" when ever the register received
                    failure response,connection failed(or down),TLS negotiation
                    failed.(during initial connect time)
                    Move to "outofservice" to "token_registration when Camelot
                    sends keep alive message or token_registration message
                    Whenregistration not invoked but in service called and
                    endpoint is doing login procedures then the state will be
                    empty.

        >>> ep1.get_sip_register()
        [{u'address': u'',
          u'callid': u'106312335049562@10.12.10.224',
          u'camelot_reason': u'',
          u'cseq': u'101',
          u'hostname': u'cam-ccm-57.camsso.test',
          u'port': u'5061',
          u'priority': u'1',
          u'response': {u'reason': u'',
          u'status_code': u'200',
          u'status_text': u'OK',
          u'warning': u''},
          u'sessionid': u'6432c5e5004050008000berep1200001;
          remote=00000000000000000000000000000000',
          u'state': u'inservice'},

        '''
        return self._query_camelot(camelot.GET_SIP_REGISTER)

    def get_bfcp_info(self, call_ref):
        '''it retrives the bfcp protocol specific statistics
           information associated to the call reference.

        The following field/values are defined:
            * floor id - identifier of the floor
            * state - state of the floor. state value can be any one of the
              below strings.
              * ""
              * "floor request sent"
              * "floor release request sent"
              * "floor pending status received"
              * "floor accepted status received"
              * "floor granted status received"
              * "floor denied status received"
              * "floor cancelled status received"
              * "floor released status received"
              * "floor revoked status received"
              * "floor request received"
              * "floor granted status sent"
              * "floor release request received"
              * "floor released status sent"
              * "floor pending status sent"
              * "floor accepted status sent"
            * sent floorrequest primitives - overall sent floorrequest
              primitives associated to the call.
            * sent floorrelease primitives - overall sent floorrelease
              primitives associated to the call.
            * sent floorrequeststatus primitives - overall sent
              floorrequeststatus primitives associated to the call.
            * received floorrequest primitives - overall received floorrequest
              primitives associated to the call.
            * received floorrelease primitives - overall received floorrelease
              primitives associated to the call.
            * received floorrequeststatus primitives - overall received
              floorrequeststatus primitives associated to the call.
            * sent hello primitives - sent hello primitives
              associated to the call.
            * sent helloack primitives - sent helloack primitives
              associated to the call.
            * sent floorstatus primitives - sent floorstatus primitives
              associated to the call.
            * sent floorstatusack primitives - sent floorstatusack primitives
              associated to the call.
            * sent floorrequeststatusack primitives - sent
              floorrequeststatusack primitives
              associated to the call.
            * received hello primitives -  received hello primitives
              associated to the call.
            * received helloack primitives - received helloack
              primitives associated to the call.
            * received floorstatus primitives - received
              floorstatus primitives associated to the call.
            * received floorstatusack primitives - received
              floorstatusack primitives associated to the call.
            * received floorrequeststatusack primitives - received
              floorrequeststatusack primitives
              associated to the call.

        :parameter call_ref: call reference

        :returns: information about the bfcp protocol.

        >>> ep1.get_bfcp_info('0xf4063230')
        {'floor id': '1',
         'state': 'floor granted status received',
         'sent floorrequest primitives': '1',
         'sent floorrelease primitives': '0',
         'sent floorrequeststatus primitives': '0',
         'received floorrequest primitives': '0',
         'received floorrelease primitives': '0',
         'received floorrequeststatus primitives': '1',
         ....,
         ....}
         '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('get_bfcp_info: Invalid Call-reference passed')
            return

        return self._query_camelot(camelot.GET_BFCP_INFO, call_ref)

    def get_call_crypto_info(self, call_ref, mtype='audio', tag='all',
                             local=False):
        '''Displays the remote and local crypto line information sent/rcvd.
        from CUCM Displays the remote and local crypto line information
        sent/rcvd from CUCM.

        :parameter call_ref:  call reference
        :parameter mtype:  type audio or video or fecc, default audio
        :parameter tag:  tag crypto to be displayed, default is all cryptos
        :parameter local:  if need to display configured cryptos

        :returns: Upon success, A dictionary of field:value pairs.
            Otherwise returns None.\n
            The current fields are support:\n
            * suite - local/remote SRTP crypto suite
            * tag - local/remote SRTP crypto tag
            * key salt - local/remote SRTP crypto key salt value
            * kdr - local/remote SRTP crypto session param kdr value
            * wsh - local/remote SRTP crypto session param wsh value
            * fec order - local/remote SRTP crypto session parm value
                            'FEC_SRTP' or 'SRTP_FEC' or None
            * fec key - local/remote SRTP crypto session param fec key string
            * unencrypted srtp - local/remote SRTP crypto session param
                            present status in SDP.
                            '1' or ''
                            '1' means UNENCRYPTED-SRTP param is present in SDP.
            * unencrypted srtcp - local/remote SRTP crypto session param
                            present status in SDP.
                            '1' or ''
                            '1' means UNENCRYPTED-SRTCP param is present
                            in SDP.
            * unautheticated srtp - local/remote SRTP crypto session param
                            present status in SDP.
                            '1' or ''
                            '1' means UNAUTHENTICATED-SRTP param is present
                            in SDP.

        >>> ep1.get_call_crypto_info('0xabcdabcd', mtype='audio', tag='2')
        {'fec key': '',
         'fec order': 'FEC_SRTP',
         'kdr': '',
         'key salt': '3c68af0c6f0492729bc2...65eec3f1baf1677ca223',
         'suite': 'AES_CM_128_HMAC_SHA1_32',
         'tag': '2',
         'unauthenticated srtp': '',
         'unencrypted srtcp': '',
         'unencrypted srtp': '',
         'wsh': ''}
        >>> ep1.get_call_crypto_info('0xabcdabcd', mtype='audio') OR
        >>> ep1.get_call_crypto_info('0xabcdabcd', mtype='audio', tag='all')
        [{'fec key': '',
          'fec order': '',
          'kdr': '',
          'key salt': 'd3752308fac46ebc8acb...6f8b07098d879a3f59e1',
          'suite': 'AEAD_AES_128_GCM',
          'tag': '1',
          'unauthenticated srtp': '',
          'unencrypted srtcp': '',
          'unencrypted srtp': '',
          'wsh': '128'},
         {'fec key': '',
          'fec order': '',
          'kdr': '',
          'key salt': '067f0d27597adcbc2c66...5c8edae2948c711676fe',
          'suite': 'AES_CM_128_HMAC_SHA1_32',
          'tag': '2',
          'unauthenticated srtp': '',
          'unencrypted srtcp': '',
          'unencrypted srtp': '',
          'wsh': ''}]
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return

        kwargs = {'mtype': mtype,
                  'tag': tag,
                  'local': local}
        return self._query_camelot(
            camelot.GET_CALL_CRYPTO_INFO, call_ref, **kwargs)

    def get_info_ext(self):
        '''Retrieve current extended information about an endpoint.

        :returns: a list of extended information as following:\n
            * softkeys - list of currently available softkey labels.\n
            * prompt - last non call display prompt text.\n
            * notify - last display notify text. Note: in case of park notify
              display the parked number. In case SIPX: "Parked At 88888".
              Incase Jabber Mobile: "Parked On 88888".\n
            * speeddials - list of speed dial labels currently
              configured.\n
            * buttons -  list of labels/features currently configured on a
              79XXs line/feature buttons.\n
            * intercom - list of intercom button labels currently configured\n
            * mobileconnect - Displays the mobileconnect status of that
              endpoint.\n
            * mwi - state of message waiting indicator (lamp on or off).\n
            * mwi line - state of message waiting indicator per line.\n
            * mwistats - number of lamp on, lamp off, icon on, icon off
              messages received.\n
            * presence interface status - Gives the status of the presence
              interface.\n
            * Voice Mail client info - Extended protocol specific state
              information of the voice mail client.
            * mediastate - Gives the media state for an IP-STE endpoint.
              Possible values are:
                * audio (audio mode)
                * vbd (voice band data)
                * mr (modem relay).\n
            * mrstate - Gives the remote modem state for an IP-STE endpoint.
              Possible values are:\n
                * n/a - not applicable (media stream not in modem relay state)
                * init - remote transport protocol has been initialized
                * phyup - remote modem physical layer is up
                * connect - remote modem has connected
                * ratereg - remote modem renegotiating rate
                * retrain - remote modem retraining
            * ctrldevices - List of control devices configured in CUCM for
              the user associated with a CUPC-Deskphone. For all other
              endpoint types this information will be empty.
            * cumcopmode - Operational mode of the CUMC endpoint. Possible
              values are:\n
                * cuma -  CUMC endpoint will have CUMA server in the
                  middle.
                * standalone - CUMC endpoint communicates directly with
                  CUCM, no CUMA server in the middle.\n
            * mobileconnect - Displays the mobileconnect status of that
              endpoint. Supported values are: "on", "off", "".\n
            * subsevtdialog - Displays the status of explicit subscribe of
              dialog event. possible values: "active", "terminated", "pending"
              Default value is "".\n
            * subsevtpresence - Displays the status of explicit subscribe of
              dialog event. possible values: "active", "terminated", "pending"
              Default value is "".\n
            * Feature Control Policy - Displays the status of parsing of
              feature control policy xml file. Possible values are:
              enabled/disabled.\n

        >>> ep1.get_info_ext()
        {
         'softkeys': ['Redial', 'NewCall', 'CfwdAll'],
         'prompt': '',
         'notify': '',
         'speeddials': ['@@SPEED_DIAL_6002_MOD', '@@6003-BLF_SD'],
         'buttons': ['6001', '6101', 'SPEED_DIAL_6002_MOD', '6003-BLF_SD'],
         'intercom': '',
         'mwi': '',
         'mwi line': ['6001 off terminated', '6101 off terminated'],
         'presence interface status': '',
         'mediastate': '',
         'mrstate': '',
         'localmdm': '',
         'remotemdm': '',
         'orclc': '',
         'smtlc': '',
         'subsevtdialog': '',
         'subsevtpresence': '',
         'Voice Mail client info': '',
         'ctrldevices': '',
         'cumcopmode': '',
         'mobileconnect': '',
         'Feature Control Policy': '',
         'mwi stats': {
         'lamp on': 0,
         'lamp off': 0,
         'icon on': 0,
         'icon off': 0,
        },
        }
        '''
        log.debug('Entering get_info_ext function')
        return self._query_camelot(camelot.GET_INFO_EXT)

    def get_srst_info(self):
        '''Retrieves srst information from downloaded config file.

        :returns: a list of information as following:\n
            * ipv4 address1 - SRST node1 ipv4 address.\n
            * ipv6 address1 - SRST node1 ipv6 address.\n
            * port1 - SRST port1.
            * ipv4 address2 - SRST node2 ipv4 address.\n
            * ipv6 address2 - SRST node2 ipv6 address.\n
            * port2 - SRST port2.
            * ipv4 address3 - SRST node3 ipv4 address.\n
            * ipv6 address3 - SRST node3 ipv6 address.\n
            * port3 - SRST port3.\n
            * secure - yes if received isSecure is true otherwise no.\n

        >>> ep1.get_srst_info()
        {'ipv4 address1': '10.12.10.68',
         'ipv6 address2': '2002:db8:c18:1:1001:1001:1001:68',
         'port1': '5060',
         'ipv4 address2': '',
         'ipv6 address2': '',
         'port2': '',
         'secure': 'no',
         'ipv4 address3': '',
         'ipv6 address3': '',
         'port3': ''}
        '''
        log.debug('Entering get_srst_info function')
        return self._query_camelot(camelot.GET_SRST_INFO)

    def get_dn(self):
        '''get the display number

        :returns: returns dn of the endpoint

        >>> ep1.get_dn()
        '6001'
        '''
        result = self.get_lines()
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

    def get_lines(self):
        '''Retrieve current information about the lines associated with an
        endpoint. Displaying all lines, if line is skipped in between is not
        supported.

        :returns: A variable sized list of camelot.response.Line object.

        Note: For siptrunk connection to two CUCMs(US287164), line_num is same
        as index from get_conn_info() output. Please refer
        https://wiki.cisco.com/display/CAMELOT/Simulated+SIP+Trunk#SimulatedSIPTrunk-SipTrunkconnectionstotwoCUCM's

        >>> ep1.get_lines()
        {'full_address': '7003@10.20.1.21:5060', 'line_num': '1'}
        '''
        log.debug('Entering get_lines function')
        return self._query_camelot(camelot.GET_LINES)

    def get_calls(self, **kwargs):
        '''Retrieve current calls associated with an endpoint.

        :returns: A variable sized list. Each element in the list is a
                    camelot.response.Call object with following attributes:\n
            * call_ref: call reference of call
            * Line: line associated with call
            * state: current state of call
            * line_ref - line reference of line associated with call
            * state - current state of call
            * Id - call id of the call

        Note: For siptrunk connection to two CUCMs(US287164), line is same
        as index from get_conn_info() output. Please refer
        https://wiki.cisco.com/display/CAMELOT/Simulated+SIP+Trunk#SimulatedSIPTrunk-SipTrunkconnectionstotwoCUCM's

        >>> ep1.get_calls()
        Out[55]:
        [{
         'call_ref': '0xeff5c034',
         'CallState': 'connected',
         'state': 'connected',
         'line_ref': '1',
         'Line': '1',
         'Ref': '0xeff5c034',
         'Id': '0xeff5c034',
        }]
        '''
        log.debug('Entering get_calls function')
        key_list = ["callingname", "callingaddress", "calledaddress",
                    "calledname", "callref"]
        key = kwargs.get('type', None)
        value = kwargs.get('type_val', None)
        kargs = {}
        if key in key_list:
            kargs = {'key': key,
                     'value': value}
        return self._query_camelot(camelot.GET_CALLS, None, **kargs)

    def get_streams(self, mifc_type=None, additional_parms=True):
        '''Return the media streams associated with an endpoint.

        Retrieve current information about media streams associated with the
        endpoint. -mifctype is an optional argument to retrieve streams
        related to a specific media interface. When -mifctype is omitted,
        all streams present on endpoint are retrived.

        :parameter mifc_type: mifctype is an optional argument to retrieve
            streams related to a specific media interface.\n
            Following are valid values of mediainterfacetype those can go
            with:\n
            * line - Retrieves all streams (i.e., audio,
              video and data) related to line's
              media interface.
            * phoneconfcap - Retrieves all streams (i.e., audio) related to
              phone's conferencing capabilities. Use this option to retrieve
              streams related to barge, agent greeting or whisper coaching.
            * recordnearend - Retrieves all streams related to recording near
              end
            * recordfarend - Retrieves all streams related to recording far end

        :parameter additional_parms: additional_parms is an optional argument
            which by default will be true it returns current information about
            media streams associated with the endpoint. If the
            additional_param specified as false it return only the keys in the
            order returned by the Camelot server.

        :returns: Returns a variable sized list. Each element in the list is
            also a dictionay with follwoing params:\n
            * stream-ref - stream reference used to identify this
              stream in methods
            * call-ref - call reference of call this stream is/was
              associated with 0 if unknown
            * type - one of stream: audio, video, bfcp or data
            * direction - direction of stream: inbound or outbound
            * state - media stream state\n
              * opening - media stream opening
              * negotiating; media mux negotiation in progress
              * timedout - media mux negotiation timed out and no
                media traffic allowed
              * opened - media stream is open
              * controlled - media transmission is suppressed
              * closing - media stream is closing
              * closed - media stream is closed
              * mifctype - media interface type to which the stream belongs
                to. This would be one of line, phoneconfcap,
                recordnearend or recordfarend

        >>> ep1.get_streams()
        [{'CallId': '0xf1517838',
          'Direction': 'Rx',
          'RcvrCodec': 'g711u',
          'RemoteAddr': '10.20.1.3:51867',
          'StreamStatus': 'Active',
          'StrmID': '0x0b5b1288'},
         {'CallId': '0xf1517838',
          'Direction': 'Tx',
          'RemoteAddr': '10.20.1.3:40383',
          'SenderCodec': 'g711u',
          'StreamStatus': 'Active',
          'StrmID': '0x0b5e6c78'}]

        >>> ep1.get_streams(None, False)
         [{
             'stream_ref': '0x0a57c898',
             'call_ref': '0xf185a030',
             'type': 'audio',
             'direction': 'inbound',
             'state': 'open',
             'mifctype': 'line',
        }, {
             'stream_ref': '0x0a6e5328',
             'call_ref': '0xf185a030',
             'type': 'video',
             'direction': 'inbound',
             'state': 'open',
             'mifctype': 'line',
        }]
        '''
        log.debug('Entering get_streams function')
        stream_list = self._query_camelot(camelot.GET_STREAMS)
        ret_list = []
        if additional_parms:
            if stream_list:
                for stream in stream_list:
                    ret_stream = {}
                    ret_stream['StrmID'] = stream['stream_ref']
                    ret_stream['CallId'] = stream['call_ref']
                    ret_stream['Type'] = stream['type']
                    stream_info = self.get_stream_info(stream['stream_ref'])
                    ret_stream['RemoteAddr'] = stream_info['address']
                    if stream['state'] == 'open':
                        ret_stream['StreamStatus'] = 'Active'
                    else:
                        ret_stream['StreamStatus'] = 'Not Ready'
                    if stream['direction'] == 'inbound':
                        ret_stream['Direction'] = 'Rx'
                        ret_stream['RcvrCodec'] = stream_info.get('codec')
                    elif stream['direction'] == 'outbound':
                        ret_stream['Direction'] = 'Tx'
                        ret_stream['SenderCodec'] = stream_info.get('codec')

                    ret_list.append(ret_stream)
            return ret_list
        else:
            return stream_list

    def get_stream_info(self, stream_ref):
        '''Get information about a media stream.

        :parameter stream_ref: stream reference

        :returns: Upon success, A dictionary of field:value pairs.
                    Otherwise returns None
            * local_address - Shows Local ipaddress in ipaddress:port format
              for both inbound and outbound streams
            * remote_address - Shows Remote ipaddress in ipaddress:port format
              for both inbound and outbound streams
            * stream reference - stream reference of stream
            * call reference - call reference stream is/was associated with,
              0 if unknown
            * type - type of media stream, audio, video, data , bfcp or ix.
            * transport - media stream's transport,
              e.g. udp, tcp, rtp, srtp, t1, e1,udp/udt
            * direction -  direction of stream, inbound or outbound
            * state - state of media stream.
            * circuit -  TBD-circuit identifier for TDM, could be aggregate
              collection of circuits
            * date - date (mm/dd/yyyy) of when stream was opened
            * start - time stamp, hh:mm:ss:mmm, of when stream was opened
            * end -time stamp, hh:mm:ss:mmm, of when stream was closed
            * codec - coder/decoder, e.g. g711u, g711a, g729, g7221_32,
              g7221_24, h261, opus, mp4a-latm, h264, h265, ""* etc.
            * payloadtype -   payloadtype number for the codec
            * bit rate - bit rate in Kbps
            * packet size - size in milliseconds of packets
              (only for RTP audio streams)
            * frame rate  - video frame rate (only for video RTP streams)
            * frame format -video frame format (only for video RTP streams)
            * picture format customXMax - video frame format representing
              the number of pixels in x axis (only for video RTP streams)
            * picture format customYMax - video frame format representing
              the number of pixels in y axis (only for video RTP streams)
            * status - status or description of last asynchronous error
              occurring on the stream
            * recording - url of file containing recording if recording was
              initiated on stream (inbound streams only)
            * h264Profile - Profile used for H.264 video.
            * h264Level - Level used for H.264 video.
              Returns: 1, 1.1, 1.2 etc., as per below table.
              This is according to Annex A of ITU-T Rec. H.264
            * h264PacketizationMode - Packetization mode for used for
              H.264 video.
              Returns: Single NAL Unit(0), Non-interleaved(1), Interleaved(2).
            * h264ParameterSets - Encoding SPS(sequence),PPS(picture) parameter
              sets used for H.264 video.
            * mifctype - Media interface type to which the stream belongs to.
              This would be one of line, phoneconfcap, recordnearend
              or recordfarend
            * mux status - This field gives the mux negotiation status.
              This field is displayed only for outbound stream.
            * ixconnection - Negotiated conection value for IX media.
              Example new, existing.
            * ixsetup - ixmap attribute value for IX media.
              Example active, passive, holdconn or actpass.
            * ixImapVal - Negotiated setup value for IX media.
              Example ping, XCCP, MSCP, client sideor serverside.
            * content - Content of the video. Example slides, speaker,
              content , main or alt
            * floorctrl - It tells the role of the end point.
              It is related to bfcp. c-only, s-only, c-s  or empty string
            * setup - It is related to bfcp. Values are active, passive,
              actpass, holdconn or empty string
            * userid - It is related to bfcp. Identifier for the client.
              It is a string variable
            * confid - It is related to bfcp. Conference id.
            * floorid -It is related to bfcp.
              It is a list each element with floorid and associated stream
              label(s).Example:-  {floorid  {1  {10  11}}  {2  { 12  13}} }
            * label - Pointer to a media stream
            * v150fw payload - payload number for v150fw codec.
            * v150NoAudio payload - payload number for NoAudio codec
            * fingerprint data -  fingerprint attribute value
            * sprt payload -  payload number of sprt.
            * rfc2833payloadtype -  payload number of telephone-event
            * rfc2833fmtpparams -  list of event values in fmtp attribute
              for telephone-event payload
        >>> ep1.get_stream_info('0xe7c5d024')
        {'address': '10.12.10.113:45142',
         'bit rate': '64',
         'call reference': '0xf0424034',
         'circuit': '0',
         'codec': 'g711u',
         'confid': '0',
         'content': '',
         'date': '06/11/2019',
         'direction': 'inbound',
         'end': '00:00:00:000',
         'fingerprint data': '',
         'floorId': {'0': ['0']},
         'floorctrl': '',
         'fmtpinterleaving': '',
         'fmtpmodechangecapability': '',
         'fmtpmodechangeperiod': '',
         'fmtpmodeset': '',
         'fmtpoctetalign': '',
         'fmtprobustsorting': '',
         'frame format': '',
         'frame rate': '',
         'h264Level': '',
         'h264PacketizationMode': '',
         'h264ParameterSets': '',
         'h264Profile': '',
         'h265Level': '',
         'ixconnection': '',
         'ixmapval': '',
         'ixsetup': 'invalid',
         'label': '0',
         'local_address': '10.12.10.113:45142',
         'mifctype': 'line',
         'mst-mode': '',
         'mux status': 'disabled',
         'packet size': '20',
         'payloadtype': '0',
         'picture format customXMax': '0',
         'picture format customYMax': '0',
         'recording': '',
         'remote source': '10.12.10.213:52083',
         'remote_address': '10.12.10.213:52083',
         'rfc2833fmtpparams': '0-15',
         'rfc2833payloadtype': '101',
         'rtcp-fb-mst': '',
         'setup': '',
         'simulcast codecs': {},
         'sprop-source-id': '0',
         'sprt payload': '',
         'start': '20:03:27:142',
         'state': 'open',
         'status': '',
         'stream reference': '0xe7c5d024',
         'transport': 'srtp',
         'type': 'audio',
         'uc-mode': '0',
         'userid': '',
         'v150NoAudio payload': '',
         'v150fw payload': ''}

        '''
        log.debug('Entering method get_stream_info()')
        return self._query_camelot(camelot.GET_STREAM_INFO, stream_ref)

    def get_xulpfecuc_info(self, stream_ref):
        '''Get information about xulpfecuc codec info.

        :parameter stream_ref: stream reference

        :returns: Upon success, A dictionary of field:value pairs.
                    Otherwise returns None

        >>> ep1.get_xulpfecuc_info('0xf2c01bf0')
        {'payload ': '124 ',
         'multissrc': '1',
         'maxesel': '1400',
         'm': '8',
         'maxn': '32'}

        '''
        log.debug('Entering method get_stream_info()')
        return self._query_camelot(camelot.GET_XULPFECUC_INFO, stream_ref)

    def get_stream_info_ext(self, stream_ref):
        '''Get extended information about a media stream.
        Get extended information about the specified media stream.

        :parameter stream_ref:  stream reference

        :returns: Upon success, A dictionary of field:value pairs.
            Otherwise returns None.\n
            The current fields are support:\n
            * session key - SRTP session key generated for the given
              open (inbound / outbound) stream. Returns 'none' for closed /
              non-secure streams.
            * packets received - number of RTP packets received (
              inbound RTP streams only)
            * packets dropped - number of inbound RTP packets dropped (inbound
              RTP streams only)
            * packets outoforder - number of inbound RTP packets received
              out of order (inbound RTP streams only)
            * sequence number received - last received packet sequence number
            * average jitter - average jitter of inbound RTP packets (
              inbound RTP streams only)
            * maximum latency - maximum latency of inbound RTP packets (inbound
              RTP streams only)
            * packets sent - number of RTP packets sent (outbound RTP streams
              only)
            * sequence number sent - last sent packet sequence number
            * remote source - IP and port of source of last inbound packet
            * tag - negotiated SRTP crypto tag
            * suite - negotiated SRTP crypto suite
            * key salt - negotiated SRTP crypto key salt value
            * kdr - negotiated SRTP crypto session param kdr
            * wsh - negotiated SRTP crypto session param wsh
            * fec order - negotiated SRTP crypto session parm value
                            'FEC_SRTP' 'SRTP_FEC' ''
            * fec key - negotiated SRTP crypto session param fec key
            * unencrypted srtp - negotiated SRTP crypto session param value
                            '1' or ''
            * unencrypted srtcp - negotiated SRTP crypto session param value
                            '1' or ''
            * unautheticated srtp - negotiated SRTP crypto session param value
                            '1' or ''

        >>> ep1.dial(ep2)
        >>> ep1.get_streams()
        [{'CallId': '0xf1517838',
          'Direction': 'Rx',
          'RcvrCodec': 'g711u',
          'RemoteAddr': '10.20.1.3:51867',
          'StreamStatus': 'Active',
          'stream_ref': '0x0b5b1288'},
         {'CallId': '0xf1517838',
          'Direction': 'Tx',
          'RemoteAddr': '10.20.1.3:40383',
          'SenderCodec': 'g711u',
          'StreamStatus': 'Active',
          'stream_ref': '0x0b5e6c78'}]
        >>> ep1.get_stream_info_ext(ep1.get_streams()[0]['stream_ref'])
        {'average jitter': '0',
         'map': '0',
         'maximum latency': '0',
         'packets dropped': '0',
         'packets outoforder': '0',
         'packets received': '0',
         'sequence number received': '0',
         'remote source': '',
         'session key': 'none',
         'tag': '3',
         'suite': 'AEAD_AES_128_GCM',
         'key salt': '356429e7e3c83b7c7dc78b5e51c8cfe15c661cb1',
         'kdr': '',
         'wsh': '',
         'fec order': 'FEC_SRTP',
         'fec key': '',
         'unencrypted srtcp': '1',
         'unencrypted srtp': '',
         'unautheticated srtp': ''}
        '''
        if not stream_ref:
            log.error('get_stream_info_ext: invalid stream reference')
            return
        return self._query_camelot(camelot.GET_STREAM_INFO_EXT, stream_ref)

    def get_call_info(self, call_ref, **kwargs):
        '''Get information about a call

        :returns: Upon success, A dictionary of field:value pairs.
            Otherwise returns None.\n
            The current fields are support:\n
            * last_refresh_status - If UPDATE is sent or received as part of
              session refresh, it will display "update sent" or
              "update received". "update sent" is possible if the endpoint's
              role (refresher tag in sip message) is UAC and Originator of
              the call, or role is UAS as an call terminating end point.
            * midcall_pc_failures - number of attempts made for path
              confirmation during mid-call
            * sip_remote_session_id -it displays the value of remote session-id
              available in the SIP Session-ID header. The remote session id is
              nothing but the value available in remote parameter of the
              Session-ID header.
            * disconnect_reason -  keyword indicating reason for disconnect.
              possible values:\n
              * cleared - call cleared normally, i.e. disconnected from
                connected state by the endpoint
              * cleared by peer - call cleared normally, i.e. disconnected from
                connected state by the remote end or CCM
              * abandoned - call abandoned, i.e. disconnected during outbound
                or inbound call setup
              * abandoned by peer - call abandoned, i.e. disconnected during
                outbound or inbound call setup by remote end or CCM
              * glare - glare detected
              * busy - remote party busy
              * reorder - reorder tone detected
              * protocol - a protocol error occurred
              * no answer - remote end did not answer
              * no dial tone - dial tone was not detected
              * media - media streams could not get established
              * out of service - endpoint went out of service
              * path confirmation failure - auto path confirmation failed
              * supplementary service failure - an auto supplementary service
                failed.
              * ua preemption  - MLPP ua preemption
              * mra route failure - Call is disconnected, since endpoint got
                registration(SIP/STUN) failure and initiated fail-over on new
                route.
              Please refer wiki  for more details of disconnect_reason
           `<https://wiki.cisco.com/display/CAMELOT/Disconnect+Reason+%2C+Cause+Code+and+SIP+Reason+Header+in+Camelot>`_
            * stun_response_code - stun binding response code.
            * connect_time - time in milliseconds call has been or was
              connected
            * divert_destination - idivert destination number
            * direction - direction of call, inbound, outbound
            * cut-through_time - time in milliseconds from answer or resume a
              call to outbound audio channel opened
            * original_called_redirecting_reason - code for original called
              party redirecting   reason
            * session_refresher - Displays the negotiated Session refresher
              role.  Possible values are UAC or UAS.
            * video_midcall_pc_attempts - number of attempts made for video
              path confirmation during midcall
            * cause_code - disconnect cause code if supported by protocol
              (e.g. q931 cause code)
            * callsetup_pc_attempts - number of attempts made for path
              confirmation during callsetup
            * confidential_access_level_text - resolved CAL(Confidential
              Access Level) text.
            * precedence_domain - precedence domain of call (integer)
            * recording_type - information regarding what type of recording
              is in progress
            * sip_local_session_id - it displays the value of local session
              id available in the SIP Session-ID header. The local session-id
              is nothing but the value available in Session-ID header and it
              will not include the value of remote parameter.
            * end - timestamp, hh:mm:ss:mmm of when call was disconnected
              (i.e. entered disconnected state).
            * tx_subject - For the UAC the 'tx subject' will be the string
              set on the endpoint by set_call_subject. If the UAS has no
              subject set via set_call_subject, the 'tx_subject' will be equal
              to the 'rx_subject'.
            * start - timestamp, hh:mm:ss:mmm, of when call was initiated
            * called_mail_box - called party voice mail box
            * customdata -
            * last_redirecting_name - last redirecting party name
            * state - current state of call
            * original_called_name - original called party name
            * last_pathconf_trigger - the reason for the last path conf
              trigger. This could be either callsetup or midcall
            * called_address - called party address
                For outbound call it will be having RPID(with party=called)
                user info, if no RPID it will be taken from Dialed number.
                For inbound call will have local DN.
                For user=phone or tel URL, the host portion will be excluded.
            * video_callsetup_pc_failures - number of video path confirmation
              failures for callsetup video path confirmation attempts
            * disconnect_time - time in milliseconds from disconnect to
              disconnect acknowledgement
            * midcall_pc_successes - number of path confirmation successes for
              midcall path confirmation attempts
            * dialtone_time - time in milliseconds from state offhook to state
              dialtone
            * last_redirecting_reason - code for last redirecting reason
            * calling_mail_box - calling party voice mail box
            * last_media_error - information regarding a media error.
              Currently it is shown only when UPM is enabled.
            * active_media - active media in the call eg-'audio video'.
            * recording_status - information regarding status of the recording.
            * remote_call - This field will indicate the remote call
              information. It will display "private" for a private call and
              empty by default. The possible values are:
              * default
              * private
            * rx_subject - For UAC 'rx subject' will be the value of the
              Subject header received in the incoming sip messages. For the
              UAS the 'rx subject' will be the subject header that it received
              in the request.
            * video_pc_status - status of video call or description of last
              asynchronous error.
            * callid - The callid corresponding to this call.
            * video_midcall_pc_successes - number of video path confirmation
              successes for midcall video path confirmation attempts
            * call_security_status - call security possible values:\n
              * status
              * unknown
              * not authenticated
              * authenticated
              * encrypted
              * secured media
            * remote_xciscotenant - it displays the remote tenant value
              received in RPID.
            * midcall_pc_attempts - number of attempts made for path
              confirmation during midcall
            * original_called_address - original called party address
            * session_refresh_timer - Displays the negotiated Session Refresh
              timer
            * calling_address - calling party address
                For outbound call it will be having local phone DN.
                For inbound call will be having RPID(with party=calling)
                user info, if no RPID it will taken from the FROM header.
                For user=phone or tel URL, the host portion will be excluded.
            * isfocus - "true" is isfocus tag is present in contact header
              "false" is absent.
            * date - date (mm/dd/yyyy) of when call was initiated
            * video_callsetup_pc_attempts -
            * calling_name - number of attempts made for video path
              confirmation during callsetup
            * setup_time - time in milliseconds from addressing end to
              ring-back
            * movetomobile_mobileconnect - mobile connect is "on" or "off".
            * reinvite_status - after start_share/stop_share values is
              progressing after sending ACK status is completed.
            * script_start_time - sss script execution start time.
            * last_redirecting_address - last redirecting address
            * network_domain - network domain of the call
            * callsetup_pc_failures - number of path confirmation failures
              for callsetup path confirmation attempts
            * type - display type of call, in, out, or forward
            * last_redirecting_mail_box - last redirecting party voice mail box
            * callsetup_pc_successes - number of attempts made for path
              confirmation during callsetup
            * video_midcall_pc_failures - number of video path confirmation
              failures for midcall video path confirmation attempts
            * newdirection -
            * called_name - called party name
            * video_last_pathconf_trigger - the reason for the video last path
              conf trigger. This could be either callsetup or midcall
            * precedence_level - precedence level of call. Possible values
              are:\n
              * flash override
              * flash
              * immediate
              * priority
              * routine
            * status - status of call or description of last asynchronous error
            * failure_status - shows the first call failure status only for the
              auto operations and event based scripting.
            * termination_status_line - any non-2xx final response or CANCEL
              in there for INVITE.
            * remoteinuse_events - counter indicating the number of times the
              call has transitioned to the remoteinuse state
            * local_xciscotenant - it displays the local tenant value received
              in request uri.
            * call_reference - call reference.
            * line_reference - line reference of line associated with call
            * multipart_xml_body - it displays the xml body from received
              INVITE message if high level Content-Type is "multipart/mixed;
              boundary=uniqueBoundary" and low level Content-Type is
              "application/cisco-media-playback+xml"
            * movetomobile_status - shows the status of movetomobile operation.
            * original_called_mail_box - original called party voice mail box
            * stun_status - stun binding status.values: 'success' or 'failed'.
            * reason_header - reason header from SIP error response or BYE.
            * warning_header - warning header from SIP error response or BYE.
            * video_callsetup_pc_successes - number of video path confirmation
              successes for callsetup video path confirmation attempts
            * replaces - the call_ref of the call this call_ref replaced.
              The value can be used in get_call_info to retrieve information
              about the initial call. Valid value present for a get_call_info
              of a current active ('connected') call.
            * replaced_by - the call_ref of the call that replaced this
              call_ref. The value can be used in get_call_info to retrieve
              information of the current active call. Valid value present for
              a get_call_info of a previous inactive ('disconnected') call.
            * ice - This field will have ice vqmetrics information for
              audio stream in the format of ice=mmm:xxx:nnn:tttt e.g
              ice:host:0:0.If endpoint is not ice enabled value is none.
              where:\n
              * mmm: Mode. One of ice|lite|none|unk.Default value is unk
              * xxx: Type of candidate selected host/relay/srflx/prflx
              * nnn: max time(ms)for connectivity check on that path.Default
                value is 0
              * ttt: time(ms)for the full ICE negotiation to complete.Default
                value is 0
            * calling_privacy - Contains the privacy received in
              Remote-Party-ID header where party is calling.
            * called_privacy - Contains the privacy received in
              Remote-Party-ID header where party is called.

        >>> ep1.get_call_info(call_ref='0xf356f034')
        {'active_media': 'audio ',
         'call_reference': '0xf356f034',
         'call_security_status': 'not authenticated',
         'called_address': '710002',
         'called_mail_box': '',
         'called_name': '',
         'callid': '',
         'calling_address': '710001',
         'calling_mail_box': '',
         'calling_name': '710001',
         'callsetup_pc_attempts': '0',
         'callsetup_pc_failures': '0',
         'callsetup_pc_successes': '0',
         'cause_code': '0',
         'confidential_access_level_text': '',
         'connect_time': '0',
         'customdata': '',
         'cut-through_time': '0',
         'date': '04/06/2017',
         'dialtone_time': '0',
         'direction': 'outbound',
         'disconnect_reason': '',
         'reason_header': 'Q.850;cause=1',
         'warning_header': '',
         'disconnect_time': '0',
         'ice':'mmm:xxx:nnn:ttt'
         'divert_destination': '',
         'end': '00:00:00:000',
         'failure_status': '',
         'isfocus': 'false',
         'last_media_error': '',
         'last_pathconf_trigger': '',
         'last_redirecting_address': '',
         'last_redirecting_mail_box': '',
         'last_redirecting_name': '',
         'last_redirecting_reason': '',
         'last_refresh_status': '',
         'line_reference': '1',
         'local_xciscotenant': '',
         'midcall_pc_attempts': '0',
         'midcall_pc_failures': '0',
         'midcall_pc_successes': '0',
         'movetomobile_mobileconnect': '',
         'movetomobile_status': '',
         'multipart_xml_body': '',
         'network_domain': '',
         'newdirection': '',
         'original_called_address': '',
         'original_called_mail_box': '',
         'original_called_name': '',
         'original_called_redirecting_reason': '',
         'precedence_domain': '',
         'precedence_level': '',
         'recording_status': '',
         'recording_type': '',
         'reinvite_status': '',
         'remote_call': '',
         'remote_xciscotenant': '',
         'remoteinuse_events': '0',
         'rx_subject': '',
         'script_start_time': '',
         'session_refresh_timer': 'None',
         'session_refresher': 'none',
         'setup_time': '33',
         'sip_local_session_id': '1d08a99f004050008000aaaa99710001',
         'sip_remote_session_id': '1d08a99f004050008000aaaa99710002',
         'start': '15:47:26:810',
         'state': 'connected',
         'status': '',
         'stun_response_code': '0',
         'stun_status': '',
         'tx_subject': '',
         'type': '',
         'video_callsetup_pc_attempts': '0',
         'video_callsetup_pc_failures': '0',
         'video_callsetup_pc_successes': '0',
         'video_last_pathconf_trigger': '',
         'video_midcall_pc_attempts': '0',
         'video_midcall_pc_failures': '0',
         'video_midcall_pc_successes': '0',
         'video_pc_status': '',
         'replaces': '0xf01b0034',
         'replaced_by': '',
         'calling_privacy': 'full'.
         'called_privacy': 'name'}

        >>> Example for replaces/replaced_by:
        -Initial call is callref_1, INVITE dialog D1
        -Restich occurs
        -INVITE w/ Replace dialog D2 replaces D1; callref_2 created for D2.
        >>> ep1.get_calls()
        [{'Ref':'callref_2', 'CallState': 'connected'}
         {'Ref':'callref_1', 'CallState': 'disconnected'}]
        >>> ep1.get_call_info(call_ref='callref_1')
        get_call_info(callref_1)
        {'state': 'disconnected', 'replaces': '', 'replaced_by': 'callref_2'}
        >>> ep1.get_call_info(call_ref='callref_2')
        {'state': 'connected', 'replaces':'callref_1', 'replaced_by': ''}
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        key = kwargs.get('type', None)
        key_list = ["callingname", "callingaddress", "calledaddress",
                    "calledname", "callref"]
        kwargs = {}
        if key in key_list:
            kwargs = {'key': key}
        log.debug('Entering get_call_info function')
        ret = self._query_camelot(camelot.GET_CALL_INFO, call_ref, **kwargs)
        if ret.get('divert destination'):
            ret['divert destination'] = ret['divert destination'].split()

        return self._remove_undscr_tngpi(ret)

    def _remove_undscr_tngpi(self, mod_dict):
        new_dict = common_utils.CamelotOrderedDict()
        for key, value in mod_dict.items():
            if ' ' in key.strip():
                new_dict[key] = value
                new_dict[key.replace(' ', '_')] = value
            else:
                new_dict[key] = value
        return new_dict

    def get_call_info_ext(self, call_ref):
        '''Get extended, protocol-specific information about a call

        :returns: Upon success, A dictionary of field:value pairs.
            Otherwise returns None.\n
            The current fields are support:\n
            * h235_encryption_algorithm - DES, Triple DES, AES
            * prompt - last non call display prompt text
            * attribute - Attribute shows SIP protocol specific call-info
              headers up to 5.
            * holdreversionreq - Shows holdreversionreq REFER xml info.
            * x_farendrefci - CUCM call ID of the call leg opposite to the
              recording triggering side.
            * x_nearendguid - Cisco Guid (available only when nearend is the
              forking gateway).
            * participant - This field represent the type of recording emulator
              endpoint. Possible values are "nearend" or "farend".
            * cumccallmode - Indicates the DVO call mode ( lcr, forward or
              reverse)
            * selected - 1 indicating that call has been selected, 0 if not
              selected, see "select"
            * x_farenddevice - Device name of the far end party.
            * monitor_DN - If this is a monitoring call, this field provides
              the DN that is being monitored. Otherwise, an empty string will
              be displayed
            * x_farendclusterid - clusterid of far end party.
            * x_refci - CUCM call ID of the recording triggering side call leg
              in the triggering cluster.
            * history_info - History-info header content strings for
              NativeIMSClient call forward scenario
            * softkeys - list of currently available softkey labels
            * monitor_mode - If this is a monitoring call, the value will be
              either Monitoring or Coaching. Otherwise, an empty string will
              be displayed
            * x_nearendclusterid - clusterid of near end party.
            * x_farendaddr - Directory number of the far end party.
            * x_farendguid - Cisco Guid (available only when farend is the
              forking gateway).
            * did - Enterprise Feature Access Number/DID# provided by CUCM
              that is used in DialViaOffice forward call.
              See dial_via_office() api.
            * x_nearendaddr - Directory number of the near end party.
            * x_nearenddevice - Device name of the near end party.
            * protocol_disc_reason - Provides the protocol specific disconnect
              reason. Currently updated only for QBE protocol.
            * dtmf_digits - DTMF digits received for a connected call.
              Currently updated only for CTI/CSFD endpoints. This data reset
              happens after call transition to connected state from any other
              state. Invalid DTMF digit will be shown as space character.

        >>> ep1.get_call_info_ext(list_ep1[0].call_ref)
        {'attribute': '{{
                        {call-info}
                        {{1}{<urn:x-cisco-remotecc:callinfo>;
                             security= NotAuthenticated; orientation= to;
                        gci= 1-43776; call-instance= 1}}
                        {{2}{}}
                        {{3}{}}
                        {{4}{}}
                        {{5}{}}}}',
        'holdreversionreq': '{ 'dialogid': {
                        'callid': '30939b80-66e1dadc-317-2d050505@5.5.5.45',
                        'localtag': '59767ab7-7931-49bc-8b8e-166d4f2cee02',
                        'remotetag': '001795f9d7d300501fbe011f-2e95a245'
                        },
                        'revertinterval' : 30
                        }
         'cumccallmode': None,
         'did': None,
         'h235_encryption_algorithm': None,
         'history_info': None,
         'monitor_DN': None,
         'monitor_mode': None,
         'participant': None,
         'prompt': 'to 7004',
         'protocol_disc_reason': None,
         'selected': '0',
         'softkeys': 'Hold EndCall Trnsfer Park Confrn ConfList Select',
         'x_farendaddr': None,
         'x_farendclusterid': None,
         'x_farenddevice': None,
         'x_farendguid': None,
         'x_farendrefci': None,
         'x_nearendaddr': None,
         'x_nearendclusterid': None,
         'x_nearenddevice': None,
         'x_nearendguid': None,
         'x_refci': None}
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        log.debug('Entering get_call_info_ext function')
        return self._query_camelot(camelot.GET_CALL_INFO_EXT, call_ref)

    def place_call(self, dial_str='null', line_ref='0', calling='null',
                   call_type='0', **kwargs):
        '''Set up a call.

        :parameter dial_str: called party address (DN or URI)
        :parameter line_ref: line for outbound call
        :parameter calling: calling party address
        :parameter call_type: It would define the type of call

         * if call_type value is "all",camelot will send all
           configured m-lines on the endpoint and this is the default.
         * call_type value can be any combination of the following tokens:
            * audio
            * video
            * bfcp
            * slides
            * fecc
            * ix
           Tokens in the call_type value should be separated
           with the character '+'.

        :returns: Upon success, the call's call reference. Otherwise
                    camelot.CamelotError would be raised

        Note: For siptrunk connection to two CUCMs(US287164), line_ref is same
        as index from get_conn_info(), for any outbound call. Please refer
        https://wiki.cisco.com/display/CAMELOT/Simulated+SIP+Trunk#SimulatedSIPTrunk-SipTrunkconnectionstotwoCUCM's

        >>> ep1.place_call('7002')
        '0aef0000'
        >>> ep1.place_call(call_type='audio+video')
        '0aef0002'
        '''
        log.debug('Entering place_call function')
        if not line_ref:
            line_ref = '0'
        if not dial_str:
            dial_str = 'null'
        if not call_type:
            call_type = '0'
        if not calling:
            calling = 'null'
        dialstr = kwargs.get('dialstr', None)
        if dialstr and dialstr != 'null':
            dial_str = dialstr
        kargs = {'called': dial_str,
                 'lineref': line_ref,
                 'calling': calling,
                 'calltype': call_type}
        return self._query_camelot(
            camelot.PLACE_CALL, **kargs)

    def _device_dial(self, dialstr):
        '''Checks call info to determine whether to use 'dial' api
        or 'placecall' api

        :parameter  dialstr: Carries the string to dial
        :returns: True if successful else False
        '''
        calls = self.get_calls()
        if calls:
            for call in calls:
                if call['CallState'] == 'dialtone':
                    call_ref = call['Ref']
                    return self.dial(dialstr, call_ref)
        return self.place_call(dialstr)

    def dial(self, dial_str=None, call_ref=None, calling=None, **kwargs):
        '''Initiate call addressing for the specified call using the endpoint's
        default method of sending addresses and/or digits.  This method can
        be used to provide addressing information for a new outbound call
        or for sending digits to an IVR application during a connected call.

        For a new outbound call, this method will typically be called when the
        call progresses to the offhook and/or dialtone state.  Upon
        successful initiation of dialing and dial tone has been removed,
        the call progresses to the dialing state.  After addressing is
        complete and has been accepted by the remote end, the call
        progresses to the proceeding state.  Once the remote end is
        alerted of the new call and ring-back detected the call progresses
        to the alerting state.  After the remote end answers the call, the
        call progresses to the connected state.

        If the line upon which the call is placed does not have a fixed calling
        party address, one can be optionally specified via the calling
        argument.
        dialstr argument can take DN or URI.
        The complete called party address does not necessarily have to be sent
        in one method invocation. Rather, this method can be called several
        times in succession to send the complete called party address.
        Also, depending on the specific call control protocol, digits may
        be sent through the signaling or bearer channel.  Abbreviated
        dialing macros can not be used with the dial method.

        :parameter dial_str: can take DN or URI.
        :parameter call_ref: call reference of the call (:py:meth:`get_calls`)
        :parameter calling: calling party address

        :returns: Upon success returns call reference, and in case of
                    error/exception CamelotError exception is raised

        Making a new outgoing call

        >>> call_ref = ep1.offhook()
        >>> ep1.get_calls()
        [{'CallState': 'dialtone',
          'Id': '0xf0c76340',
          'Line': '1',
          'Ref': '0xf0c76340'}]
        >>> ep1.dial(ep2.get_number(), call_ref)
        True
        >>> ep1.get_calls()
        [{'CallState': 'alerting',
          'Id': '0xf0c76340',
          'Line': '1',
          'Ref': '0xf0c76340'}]
        >>> ep2.get_calls()
        [{'CallState': 'incoming',
          'Id': '0xa55fa60',
          'Line': '1',
          'Ref': '0xa55fa60'}]

        Sending DTMF digits on a connected call

        >>> ep1.dial(ep2)
        <Call <Device Camelot SEPBAACBAAC7001> <-> <Device Camelot SEPAAAABBBB
        6941>>
        >>> ep1.get_calls()
        [{'CallState': 'connected',
          'Id': '0xb34d948',
          'Line': '1',
          'Ref': '0xb34d948'}]
        >>> ep1.dial('123', '0xb34d948')
        True
        '''
        log.debug('Entering dial function')
        dialstr = kwargs.get('dialstr', None)
        if dialstr:
            dial_str = dialstr
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        kargs = {'called': dial_str,
                 'calling': calling}
        return self._query_camelot(
            camelot.DIAL, call_ref, **kargs)

    def answer(self, call_ref):
        '''Initiate answering of an inbound call by sending an answer protocol
        message.  When an inbound call is first detected, the call is in the
        seizure state.  If the protocol has to receive address digits, it then
        transitions to the recdigits state.  Once all addressing information is
        received, the call transitions to the incoming state.  At this point
        it can be answered.  Upon method invocation, the call transitions to
        the answering state and then to the connected state.

        :parameter call_ref: call reference

        :returns: Upon success, True is returned.  Otherwise False

        >>> ep1.answer('0xe8faf034')
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        log.debug('Entering answer function')
        return self._query_camelot(camelot.ANSWER_CALL, call_ref)

    def endcall(self, call_ref, timeout=0):
        '''Sends an endcall protocol message to disconnect a call.
        If successful, the call transitions to the disconnecting state and
        then to the disconnected state. endcall can also be used to
        disconnect a call in held state.

        :parameter call_ref: call reference
        :parameter timeout: delay in seconds to call endcall

        :returns: Upon success, True is returned.  Otherwise False
        >>> ep1.endcall('0xf01ae034')
        True
        '''
        log.debug('Entering endcall function')
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        return self._query_camelot(camelot.END_CALL, call_ref, timeout)

    def start_capf(self, auth_str=None):
        '''start_capf Initiate certificate update using CAPF.
         Initiate a certificate update process with the CAPF service.
         If an authentication string is provided it will be used to
         authenticate the endpoint to the CAPF service in case the
         endpoints authentication mode is set to 1 (string).
         The command will trigger a new SSL connection setup to the CAPF
         server and start the protocol.

        :parameter auth_str: endpoint to server authentication string.

        :returns: Upon success, True is returned.  Otherwise False.
        '''
        log.debug('Entering start_capf function')
        return self._query_camelot(camelot.START_CAPF, auth_str)

    def stop_capf(self):
        '''stopcapf  Terminate a running CAPF session.
         Terminates a running CAPF session. Invoking this command will
         cause closing the SSL connection to the CAPF server and release
         all related resources.

        :returns: Upon success, True is returned.  Otherwise False

        >>> ep1.stop_capf()
        True
        '''
        log.debug('Entering stop_capf function')
        return self._query_camelot(camelot.STOP_CAPF)

    def get_capf_info(self):
        '''Retrieve current information about a CAPF session.

        :returns: A dictionary of field:value pairs.
            The following fields are defined:

            :state: the current state of the CAPF session. \
                   below are possible values :-

                   :idle: CAPF session not started
                   :connecting: attempt to conntect to the CAPF service
                   :connected: connection established waiting for server    \
                               messages
                   :server busy: server busy, session timed out
                   :authenticating: endpoint attempts to authenticate itself \
                                   to the server
                   :generating key: endpoint is in the process of generating \
                                   a key or has sent the key to the server
                   :encrypting: endpoint is in the process of encrypting the \
                                responding to servers encrypt requests.
                   :storing certificate: endpoint is in process of storing   \
                                         the new certificate and responding to\
                                         the server
                   :deleting certificate: endpoint is in the process of      \
                                          deleting a certificate and         \
                                          responding to the server
                   :complete: the certficate update process has completed    \
                             successfully and a new certificate is stored
                   :aborted: the certificate update process has been aborted \
                            due to an abort message from the server
                   :stopped: user has requested to stop the session
                   :error state: an error has occurred during the certificate\
                                upgrade session.  The last error field should\
                                contain relevant information regarding the   \
                                error.
            :last error: contains an error description in case an error     \
                         occurs during the certificate upgrade process. In  \
                         case of no error the field value will be empty.
                         Below are the possible values :

                   :socket: a socket error has occurred                    \
                            (e.g. failed connecting)
                   :ssl: failed initializing SSL context
                   :authentication: failed authentication phase
                   :server busy: failed processing retry later message
                   :key generation: failed generating new key pair
                   :encrypting: failed processing encrypt request
                   :certificate store: failed processing certificate store \
                                       request.
                   :general: default error value
            :key_pair_gen: information related to key_gen request handling.
                           Following are the fields and the values

                   :key_type: key type received in key_gen request.        \
                             Values are RSA or ECDSA
                   :key_size: key size received in key_gen request for RSA \
                              Example: 2048
                   :ec_curve_id: curve name received in key_gen request for\
                                 ECDSA keys.Example: P-384
                   :reason: failure reason while generating key_gen response\
                            Example: mandatory_IE_missing
                   :status: status indicating if key_gen request was handled\
                           succesfully. Possible values: "Success","Failure"
            :sign_csr: contains information about capf details used in \
                       sign_csr request processing. It contains two fields \
                       digest algorithm & reason.

                :digest_algorithm: it specifies the type of digest algorithm\
                                   to be used in generating the signature \
                                   of certificate request.possible values :-

                    :sha1: if digest alorigthm used in CSR request is \
                           of type SHA1
                    :sha256: if digest alorigthm used in CSR request is of \
                             type SHA256
                    :sha384: if digest alorigthm used in CSR request is of \
                             type SHA384
                    :sha512: if digest alorigthm used in CSR request is of \
                             type SHA512
                    :Invalid algorithm, Type not supported: if digest \
                                                            alorigthm used\
                                                            in CSR request\
                                                            is of Reserved,\
                                                            Invalid, \
                                                            Unsupported type

                :reason: contains an appropriate reason description in case\
                         of any failure / error occurs during sign_csr\
                         request processing. possible values :-

                      :"": no problem in processing request
                      :success: process completed successfully
                      :unspecified: failed in initializing for CSR request
                      :resource_not_available: failed processing due to\
                                             internal resource unavailability\
                      :mandatory_IE_missing: failed to collect required IE\
                                           details for request processing
                      :internal_failure: for any failure within application on\
                                       processing request like not able to \
                                       send csr req, Digest msg create fail,\
                                       Digest Init fail etc.
                      :cert_update_fail: failed while updating the certificate\
                                       for request
                      :invalid_encrypt_operation: failed on encoding the \
                                                certificate with sign details\
                      :invalid_digest_algorithm: failed due to invalid digest\
                                               type received for csr request
                      :signature operation: failed on digest updation with\
                                            final sign data

        >>> ep1.get_capf_info()
        {'last error': '', 'state': 'complete',
         'key_pair_gen': {'key_type': 'RSA', 'status': 'success',
             'reason': '', 'key_size': '2048', 'ec_curve_name': ''},
         'sign_csr': {'digest_algorithm': 'sha384', 'reason': 'success'}}

        >>> ep1.get_capf_info()
        {'last error': '', 'state': 'complete',
         'key_pair_gen': {'key_type': 'ECDSA', 'status': 'success',
             'reason': '', 'key_size': '', 'ec_curve_name': 'P-384'},
         'sign_csr': {'digest_algorithm': 'sha384', 'reason': 'success'}}

        >>> ep1.get_capf_info()
        {'last error': 'sign_csr_error, 'state': 'error state',
         'key_pair_gen': {'key_type': 'ECDSA', 'status': 'success',
             'reason': '', 'key_size': '', 'ec_curve_name': 'P-384'},
         'sign_csr': {'digest_algorithm': 'sha384',
             'reason': 'invalid_encrypt_operation'}}

         >>> ep1.get_capf_info()
        {'last error': 'sign_csr_error, 'state': 'error state',
         'key_pair_gen': {'key_type': 'RSA', 'status': 'success',
             'reason': '', 'key_size': '', 'ec_curve_name': 'P-384'},
         'sign_csr': {'digest_algorithm': 'sha384',
             'reason': 'invalid_encrypt_operation'}}

        '''
        return self._query_camelot(camelot.GET_CAPF_INFO)

    def hedge_revoke_oauth(self, token_type=None):
        '''It will be used to delete access_token or refresh_token, based on
         the given input.

        :parameter token_type: type of the token.
         Below are the possible values: \n
         * refresh_token
         * access_token
         * none (default value)

        :returns: Upon success, True is returned.  Otherwise False
        '''
        log.debug('Entering hedge_revoke_oauth function')
        return self._query_camelot(camelot.HEDGE_REVOKE_OAUTH, token_type)

    def fax_switchto(self, call_ref, fax_type):
        '''Initiates switching to particular media for fax calls

        :parameter call_ref: call reference
        :parameter fax_type: type of fax mechanism used. Below
         is the possible value currently\n
         * T38_Relay(This is not case sensitive)

        :returns: Upon success, True is returned.  Otherwise False
                  For more reference on use of API please check
                  'https://wiki.cisco.com/display/CAMELOT/FAX+T
                  .38+Support'

        >>> ep1.fax_switchto()
        True
        '''
        log.debug('Entering fax_switchto function')
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        if not fax_type:
            log.error('fax type is not available')
            return
        return self._query_camelot(camelot.FAX_SWITCHTO, call_ref, fax_type)

    def hold(self, call_ref, timeout=0):
        '''Initiates placing a call on hold

        :parameter call_ref: call reference
        :parameter timeout: delay to call hold

        :returns: Upon success, True is returned.  Otherwise False

        >>> ep1.hold()
        'true'
        '''
        log.debug('Entering hold function')
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        return self._query_camelot(camelot.HOLD, call_ref, timeout)

    def resume(self, call_ref, timeout=0):
        '''Initiates call resume for a held call

        :parameter call_ref: call reference
        :parameter timeout: delay the resume operation in seconds

        :returns: Upon success, True is returned.  Otherwise False

        >>> ep1.resume()
        True
        '''
        log.debug('Entering hold function')
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        return self._query_camelot(camelot.RESUME, call_ref, timeout)

    def transfer(self, call_ref, transfer_mode=None, line_ref=None, **kwargs):
        '''Initiate/complete a call transfer.

        To complete the transfer of a call, this method needs to be invoked
        twice.  The first invocation puts the specified call on hold awaiting
        transfer.  A new outbound call is automatically generated, which will
        be destination of the transfer.  After setting up this new call,
        invoke transfer a second time to complete the transfer.  The previous
        call that was put on hold is automatically disconnected. If the mode
        is not specified the default mode of transfer is consultative. Specify
        the mode to be used for transfer when the feature is initiated. Mode
        should not be specified when transfer is invoked for the second time
        to complete it. In case mode is specified when completing the transfer,
        it is ignored. Refer Appendix D for more information on Connected
        transfer mode.

        The lineref parameter is used to perform Connected transfer across
        lines on RT endpoints. By default the lineref of the current call will
        be used if this parameter is not specified. The lineref parameter
        should be specified only when the mode is connected. In case lineref
        is specified when mode is not connected, it will be ignored. Also
        lineref should be specified only for the first invocation of transfer,
        if it is specified while completing the transfer it will be ignored.

        :parameter call_ref: call reference
        :parameter transfer_mode: mode for the transfer either consultative or
                                    connected
        :parameter line_ref: lineref for outbound new call for transfer

        :returns: Upon successful initiation/completion of the transfer True.
                    Otherwise camelot.CamelotError

        >>> ep1.transfer()
        True
        '''
        log.debug('Entering transfer function')
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        line_reference = kwargs.get('line_reference', None)
        if line_reference:
            line_ref = line_reference
        kwargs = {'mode': transfer_mode,
                  'lineref': line_ref}
        return self._query_camelot(camelot.TRANSFER, call_ref, **kwargs)

    def conference(self, call_ref, mode=None, line_ref=None, **kwargs):
        '''Add a call to a conference

        Initiate/add a call to a conference.  If the specified call is not a
        conference call, then invocation of this method changes the specified
        call to a conference call, puts it on hold, and automatically
        generates a new outbound call.  Client code can then setup this new
        call and execute conference a second time to add the new call to the
        existing conference. This will resume the conference call and
        disconnect the new call. If the mode is not specified the default mode
        of conference is consultative. Specify the mode to be used for
        conference when the feature is initiated. Mode should not be specified
        when conference is invoked for the second time to complete it. In case
        mode is specified when completing the conference, it is ignored.
        Refer Appendix D for more information on connected conference mode.

        The lineref parameter is used to perform Connected conference across
        lines on RT endpoints. By default the lineref of the current call will
        be used if this parameter is not specified. The lineref parameter
        should be specified only when the mode is connected. In case lineref
        is specified when mode is not connected, it will be ignored. Also
        lineref should be specified only for the first invocation of
        conference, if it is specified while completing the conference it will
        be ignored.

        :parameter call_ref: call reference
        :parameter mode: mode for the transfer either consultative or
                         connected.
        :parameter line_ref: lineref for outbound new call for transfer

        :returns: Upon successful initiation/completion of the transfer True.
                    Otherwise camelot.CamelotError

        >>> ep1.conference(call_ref='0xe805bb1c')
        True

        (!) Note conference() do not work for legacy SIP phones
        '''
        log.debug('Entering conference function')
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        transfer_mode = kwargs.get('transfer_mode', None)
        line_reference = kwargs.get('line_reference', None)
        if transfer_mode:
            mode = transfer_mode
        if line_reference:
            line_ref = line_reference
        kargs = {'mode': mode,
                 'lineref': line_ref}
        return self._query_camelot(camelot.CONFERENCE, call_ref, **kargs)

    def start_call_events(self):
        '''Enable call events

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.start_call_events()
        True
        '''
        log.debug('Entering start_call_events function')
        return self._query_camelot(camelot.START_CALL_EVENTS)

    def stop_call_events(self):
        '''diable call events

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.stop_call_events()
        True
        '''
        log.debug('Entering stop_call_events function')
        return self._query_camelot(camelot.STOP_CALL_EVENTS)

    def start_callback_events(self):
        '''Enable call events

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.start_callback_events()
        True
        '''
        log.debug('Entering start_callback_events function')
        return self._query_camelot(camelot.START_CALLBACK_EVENTS)

    def stop_callback_events(self):
        '''diable call events

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.stop_callback_events()
        True
        '''
        log.debug('Entering stop_callback_events function')
        return self._query_camelot(camelot.STOP_CALLBACK_EVENTS)

    def start_user_events(self):
        '''Enable user events

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.start_user_events()
        True
        '''
        log.debug('Entering start_user_events function')
        return self._query_camelot(camelot.START_USER_EVENTS)

    def stop_user_events(self):
        '''Disable user events

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.stop_user_events()
        True
        '''
        log.debug('Entering stop_user_events function')
        return self._query_camelot(camelot.STOP_USER_EVENTS)

    def start_stream_events(self):
        '''Enable stream_events

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.start_stream_events()
        True
        '''
        log.debug('Entering start_stream_events function')
        return self._query_camelot(camelot.START_STREAM_EVENTS)

    def stop_stream_events(self):
        '''Disable stream_events

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.stop_stream_events()
        True
        '''
        log.debug('Entering stop_stream_events function')
        return self._query_camelot(camelot.STOP_STREAM_EVENTS)

    def start_station_events(self):
        '''Enable collection of station events

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.start_station_events()
        True
        '''
        log.debug('Entering start_station_events function')
        return self._query_camelot(camelot.START_STATION_EVENTS)

    def stop_station_events(self):
        '''Disables collection of station events

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.stop_station_events()
        True
        '''
        log.debug('Entering start_station_events function')
        return self._query_camelot(camelot.STOP_STATION_EVENTS)

    def start_info_events(self, event_type='state'):
        '''Enable collection of info events of specifide type

        :parameter event_type: event type can be one of the following:\n
                                * state\n
                                * calls\n
                                * streams\n
                                * primarycm\n
                                * backupcm\n
                                * bcgready\n
                                * lostconn\n
                                * transports\n

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.start_info_events()
        True
        '''
        log.debug('Entering start_info_events function')
        return self._query_camelot(camelot.START_INFO_EVENTS, event_type)

    def stop_info_events(self, event_type='state'):
        '''Disables collection of info events of specifide type

        :returns: Upon success, True is returned.Otherwise camelot.CamelotError

        >>> ep1.stop_info_events()
        True
        '''
        log.debug('Entering stop_info_events function')
        return self._query_camelot(camelot.STOP_INFO_EVENTS, event_type)

    def start_call_info_events(self, call_ref):
        '''Enables collection of the call info events for a call

        :parameter call_ref: reference of the call for which event collection
            to be enabled

        >>> ep1.start_call_info_events()
        True
        '''
        log.debug('Registering for Callinfoevent on')
        if not call_ref:
            log.error('Can not register to callinfo events,'
                      ' No call_ref provided')
            return
        kwargs = {'type': 'callstate',
                  'state': 'on'}
        return self._query_camelot(camelot.CALL_INFO_EVENT, call_ref,
                                   **kwargs)

    def stop_call_info_events(self, call_ref):
        '''
        Disables collection of the call info events for a call

        :parameter call_ref: reference of the call for which event collection
            to be disabled

        >>> ep1.stop_call_info_events()
        True
        '''
        if not call_ref:
            log.error('Cant un-register callinfo events, No call_ref provided')
            return
        kwargs = {'type': 'callstate',
                  'state': 'off'}
        return self._query_camelot(camelot.CALL_INFO_EVENT, call_ref,
                                   **kwargs)

    def start_stream_info_events(self, stream_ref):
        '''
        Enables the collection of streaminfo events whenever media stream
         changes state

        :parameter stream_ref: stream reference
        :returns: True on success, Error message on failure

        >>> ep1.start_stream_info_events()
        True
        '''
        log.debug('Registering for streaminfoevent on')
        if not self._is_valid_call_ref(stream_ref):
            log.error('Can not register to streaminfo events,'
                      ' No stream_ref provided')
            return
        kwargs = {'type': 'streamstate',
                  'state': 'on'}
        return self._query_camelot(camelot.STREAM_INFO_EVENT, stream_ref,
                                   **kwargs)

    def stop_stream_info_events(self, stream_ref):
        '''
        Deactivates new streaminfo event generation.

        :parameter stream_ref: stream reference
        :returns: True on success, Error message on failure

        >>> ep1.stop_stream_info_events()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('Can not un-register streaminfo events,'
                      ' No stream_ref provided')
            return
        kwargs = {'type': 'streamstate',
                  'state': 'off'}
        return self._query_camelot(camelot.STREAM_INFO_EVENT, stream_ref,
                                   **kwargs)

    def start_transport_info_events(self, transport_ref):
        '''enables the collectoin of transportinfo events.

         A transport event occurs as long as the transport has 1 or more
         protocol messages to pass to the client.

        :parameter transport_ref: transport reference of the transport

        :returns: True on success, Error message on failure

        >>> ep1.start_transport_info_events()
        True
        '''
        if not self._is_valid_call_ref(transport_ref):
            log.error('Cant register to transport info events, No '
                      'transport_ref provided')
            return
        decimal_val = int(transport_ref, 16)
        kwargs = {'type': 'transportstate',
                  'state': 'on'}
        return self._query_camelot(camelot.TRANSPORT_INFO_EVENT, decimal_val,
                                   **kwargs)

    def stop_transport_info_events(self, transport_ref):
        '''
        Disables the collectoin of transportinfo events.
        :parameter transport_ref: transport reference of the transport

        :returns: True on success, Error message on failure
        >>> ep1.stop_transport_info_events()
        True
        '''
        if not self._is_valid_call_ref(transport_ref):
            log.error('Cant unregister transport info events, No transport_ref'
                      ' provided')
            return
        decimal_val = int(transport_ref, 16)
        kwargs = {'type': 'transportstate',
                  'state': 'off'}
        return self._query_camelot(camelot.TRANSPORT_INFO_EVENT, decimal_val,
                                   **kwargs)

    def start_trace_events(self, mask=None):
        '''Activate trace collection with an optional filter mask.

        :parameter mask:  bit mask, Enables trace collection based on the
            specified bit mask.  If the bit mask argument is omitted, this
            command simply returns the current bitmask value.  Bit mask values
            are tool-specific.\n
            For Camelot the values are:\n
            * 0x0 - Disable all trace logging
            * 0x1 - Enable collection of error traces
            * 0x2 - Enable collection of  second level error traces
            * 0x4 - Enable collection of informational traces
            * 0x8 - Enable collection of level 1 debug traces
            * 0x10 - Enable collection of level 2 debug traces
            * 0x20 - Enable collection of level 3 debug traces
            * 0x40 - Enable collection of level 4 debug traces
            * 0x80 - Enable collection of IP-STE debug traces

        :returns: The current trace filter bit mask

        >>> ep1.start_trace_events('0X1')
        '0X1'
        '''
        log.debug('Entering start_trace_events function')
        mask = str(mask)
        trace_masks = ['0x0', '0x1', '0x2', '0x4',
                       '0x8', '0x10', '0x20', '0x40', '0x80']
        if not mask or mask not in trace_masks:
            log.error('Cant register to Trace events, Not a valid Mask')
            return
        return self._query_camelot(camelot.START_TRACE_EVENTS, mask)

    def stop_trace_events(self):
        '''
        Deactivates trace collection

        :returns: Trace event status

        '''
        log.debug('Entering stop_trace_events function')
        return self._query_camelot(camelot.STOP_TRACE_EVENTS)

    def start_transport_events(self, transport_ref):
        '''enables the collectoin of transport events.

         A transport event occurs as long as the transport has 1 or more
         protocol messages to pass to the client.

        :parameter transport_ref: transport reference of the transport

        :returns: True on success, Error message on failure

        >>> ep1.start_transport_events()
        True
        '''
        log.debug('Entering start_transport_events function')
        if not self._is_valid_call_ref(transport_ref):
            log.error('Cant register to transport events, No transport_ref '
                      'provided')
            return
        return self._query_camelot(
            camelot.START_TRANSPORT_EVENTS, transport_ref)

    def stop_transport_events(self, transport_ref=None):
        '''
        Disables the collectoin of transport events.
        :parameter transport_ref: transport reference of the transport

        :returns: True on success, Error message on failure

        >>> ep1.stop_transport_events()
        True
        '''
        log.debug('Entering stop_transport_events function')
        if not transport_ref or not self._is_valid_call_ref(transport_ref):
            log.error('Cant stop transport events, No transport_ref '
                      'provided')
            return
        return self._query_camelot(
            camelot.STOP_TRANSPORT_EVENTS, transport_ref)

    def is_endpoint_bcg_ready(self):
        '''
        Returns if the end point bcg is ready
        :returns: 1 if bcg is ready
        '''
        log.debug('Entering is_endpoint_bcg_ready function')
        return self._query_camelot(camelot.ISENDPOINTBCGREADY)

    def place_script(self, shandle='null', sargs='', scripttype='tcl'):
        '''
        Place script

        :parameter shandle: handled returned by loadsss
        :paramter sargs: arguments to the sss script
         else respective error will be returned.
        '''
        log.debug('Entering place_script function')
        sArgs = ''
        if shandle != 'null':
            hex_val = shandle[2:]
            if not (c in string.hexdigits for c in hex_val):
                return 'Invalid string handle'
        if scripttype is "tcl" and not isinstance(sargs, str):
            return "Invalid argument format - argument must be space separated"
        if scripttype is "python" and not isinstance(sargs, list):
            return "Invalid argument format - argument must be in list"
        if scripttype is "tcl":
            sArgs = sargs
        else:
            if sargs:
                for key in range(0, len(sargs)):
                    if (type(sargs[key]) is CamelotEndpoint):
                        sargs[key] = "%s:%s" % ("endpoint",
                                                sargs[key].get_ref())
                    else:
                        sargs[key] = "%s:%s" % ("string",
                                                sargs[key])

                sArgs = ' '.join(sargs)
            else:
                sArgs = ''

        return self._query_camelot(camelot.PLACE_SCRIPT, shandle, sArgs)

    def get_script_info(self, shandle):
        '''get sss script info

        :parameter ip: ip address of Camelot server
        :parameter port: listening port of Camelot server
        :parameter shandle: script handled returned by loadsss

        :returns: dictionary of sss script information
        '''
        log.debug('Entering into get_script_info function')
        return self._query_camelot(camelot.GET_SCRIPT_INFO, shandle)

    def get_ref(self):
        '''
        Returns the camelot specific reference of an endpoint

        :returns: returns and endpoint referance in the format
        ::camelot::camelot_Server_ip:camelot_server_port:index

        >>> serv = camelot.create_camelot_server('10.12.10.180', '5001')
        >>> ep = serv.create_new_endpoint()
        >>> ep.get_camelot_endpoint_ref()
        '::camelot::10.12.10.180:5001:00000006'
        '''
        return '::camelot::{}:{}:{}'.format(
            self._get_server_conn().server_ip,
            self._get_server_conn().server_port,
            self.ep_id)

    def get_call_stats(self, clear=None):
        '''get call stat

        :parameter clear: return and clear the buffer

        :returns: the call statistic in dict

        >>> ep.get_call_stats()
        {
        'outbound': '0',
        'inbound': '1',
        'connects': '1',
        'disconnects': '1',
        'failures': '0',
        'cleared': '0',
        'cleared by peer': '1',
        'glare': '0',
        'no dial tone': '0',
        'busy': '0',
        'reorder': '0',
        'setup timeout': '0',
        'protocol error': '0',
        'no answer': '0',
        'abandoned': '0',
        'abandoned by peer': '0',
        'out of service': '0',
        'media error': '0',
        'supp. service error': '0',
        'mra route failure': '1',
        'callsetup path conf. error': [u'{Audio} 0', u'{Video} 0'],
        'midcall path conf. error': [u'{Audio} 0', u'{Video} 0'],
        'script error': '0',
        'current calls': [u'outbound 0', u'offhook 0', u'dialtone 0',
        u'dialing 0', u'proceeding 0', u'alerting 0', u'seizure 0',
        u'recdigits 0', u'incoming 0', u'answering 0', u'rejecting 0',
        u'connected 0', u'held 0', u'remoteinuse 0',
        u'disconnecting 0', u'disconnected 1'],
        'missedcallinfo': [u'missedcalls 0'],
        'placedcallinfo': [u'placedcalls 0']
        }

        case 1) If normal call disconnected due to STUN KA failure then,

        >>> ep1.get_call_info(cref)['disconnect reason']
            'mra route failure'

        >>> ep1.get_call_info(cref)['failure status']
            'VCSC node failure detected;stun keep alive failure'

        >>> ep1.get_call_stats()
        {
         'outbound': '1',
         'inbound': '0',
         'connects': '1',
         'disconnects': '2',
         'failures': '1',
          ...
         'supp. service error': '0',
         'mra route failure': '1',
          ...
        }

        case 2) auto supplementary service ex., auto_hold() enabled and
                new INVITE failed due to MRA route failure
        >>> ep1.get_call_info(cref)['disconnect reason']
            'supplementary service failure'

        >>> ep1.get_call_info(cref)['failure status']
            'received response:503 Service Unavailable for INVITE Transaction;
             VCSC node failure detected;Warning: 382 10.12.10.156 System in
             Maintenance Mode;mra route failure'

        >>>  ep1.get_call_stats()
        {
         'outbound': '1',
         'inbound': '0',
         'connects': '0',
         'disconnects': '1',
         'failures': '1',
          ...
         'supp. service error': '1',
         'mra route failure': '0',
          ...
        }
        '''
        log.debug('Entering into get_call_stats function')
        return self._query_camelot(camelot.GET_CALL_STATS, clear)

    def set_client_data(self, data):
        '''Associates an arbitrary string to an endpoint

        :parameter data: arbitrary string to associate with endpoint

        :returns: The newly assigned string

        >>> ep.set_client_data('phone1')
        phone1
        '''
        log.debug('Entering into set_client_data function')
        return self._query_camelot(camelot.SET_CLIENT_DATA, data)

    def get_client_data(self):
        '''Returns endpoint's assigned client string

        :returns: The endpoint's assigned arbitrary client string

        >>> ep.get_client_data()
        phone1
        '''
        log.debug('Entering into get_client_data function')
        return self._query_camelot(camelot.GET_CLIENT_DATA)

    def set_client_desc(self, desc=None):
        '''This command saves an arbitrary string description on the endpoint.
        This description cannot be used to retrieve or lookup the endpoint.
        To remove the saved string from the endpoint, omit the desc argument.
        Saved description can be retrieved using the command get_client_desc

        :parameter desc: arbitrary string to associate with endpoint

        :returns: The newly saved string

        >>> ep.set_client_desc('phone1')
        phone1
        '''
        log.debug('Entering into set_client_desc function')
        if not desc:
            raise Exception('empty description is passed')
        return self._query_camelot(camelot.SET_CLIENT_DESC, desc)

    def get_client_desc(self):
        '''Retrieve the arbitrary string description saved using setclientdesc

        :returns: The saved arbitrary client string

        >>> ep.get_client_desc()
        phone1
        '''
        log.debug('Entering into get_client_desc function')
        return self._query_camelot(camelot.GET_CLIENT_DESC)

    def set_call_subject(self, subject='null'):
        '''Sets the SIP Subject header value for the next call
         initiated on the endpoint.

        :parameter subject: value string. Default value empty string

        :returns: same set value string

        >>> ep.set_call_subject('Message from PhoneA')
        Message from PhoneA
        '''
        if not subject:
            subject = 'null'
        return self._query_camelot(camelot.SET_CALL_SUBJECT, subject)

    def get_call_subject(self):
        '''Get the SIP Subject header value set by set_call_subject api
         for the endpoint.

        :returns: subject string set by set_call_subject() or empty string

        >>> ep.get_call_subject()
        Message from PhoneA
        '''
        return self._query_camelot(camelot.GET_CALL_SUBJECT)

    def get_methods(self):
        ''' Returns all supported methods

        :returns: Returns list of all methods supported/implemented
                  by this endpoint.

        '''
        mlist = []
        for l_indx in inspect.getmembers(camelot.endpoint.CamelotEndpoint,
                                         predicate=inspect.ismethod):
            if l_indx[0] not in ('__init__',
                                 '_binary_to_boolean', '_convert_hex_to_int',
                                 '_is_valid_call_ref', '_is_valid_decimal',
                                 '_is_valid_integer', '_query_camelot'):
                mlist.append(l_indx[0])
        return mlist

    def get_uris(self, line=-1, uri=-1, primary=0):
        ''' Returns list of directory uri(s) associated with the line(s)

        :parameter line: Specifying the line argument with the value between
         1 to 200 returs the directory uri(s) associated with the specified
         lineIndex
        :parameter primary: returns only the primary directory uri of all the
         line or specific line if the line argument is also specified.
        :parameter uri: If specified with the lineIndex returns only the uri
         name of the particular uri index of that line.

        Note: uri option cannot be given with primary argument.
        And uri must be used along with line.
        '''
        if line > 200:
            raise camelot.CamelotError('Invalid line index passed')
        if line < 0 and uri > 0:
            raise camelot.CamelotError('Uri cannot be specified without line')
        if primary > 0 and uri > 0:
            raise camelot.CamelotError('Uri cannot be specified with primary')

        if primary:
            primary = 'primary'
        else:
            primary = 'all'

        kwargs = {'uri': uri,
                  'primary': primary}

        return self._query_camelot(camelot.GET_URIS, line, **kwargs)

    def get_rtp_rx_stats(self, stream_type='audio'):
        ''' Returns the RTP Rx statistics information

        :parameter stream_type:  stream_type of stream. Possible values \n
            * audio - statistics with respect to audio stream (default)
            * video - statistics with rspect to video stream

        :returns: dictionary of informations mentioned below \n
            Audio Statistics field: \n
            * duration - Total number of seconds since beginning of reception
            * pktrcvd - Total number of RTP packets received
            * octrcvd - Total number of RTP payload octets received
                        (not including RTP header).
            * latepkt - Total number of late RTP packets received.
            * lostpkt - Total number of lost RTP packets received
                        (not including late RTP packets).
            * avgjitter - An estimate of the statistical variance of the
                        RTP packet inter-arrival time measured in timestamp
                        units and calculated according to RFC 1889.
            * vqmetrics - The VQ metrics are a free form text field.
                            In order to support extensions to this without
                            modifying the SIP header, the value of the VQ
                            metrics will be copied into the CMR exactly as it
                            appears in the SIP message. Since the VQ metrics
                            need to be copied directly into the CMR, the
                            following format will be used in the
                            SIP message: VqMetrics='<metrics>'\n
            Video Statistics field: \n
            * duration - Total number of seconds since beginning of reception\n
            * numpktrcvd - Total number of RTP packets received\n
            * numoctrcvd - Total number of RTP payload octets received
                           (not including RTP header).\n
            * numlostpkt - Total number of lost RTP packets received
                           (not including late RTP packets).\n
            * avgjitter - Average jitter.  An estimate of the statistical
                         variance of the RTP packet inter-arrival time measured
                         in timestamp units.\n
            * content - Identifies the type of received video stream.
                        The possible values can be \n
                        * main
                        * speaker
                        * slides
            * roundtriptime - Round Trip Time. Useful for figuring out how fast
                             recovery can happen and to ensure within
                             expected bound.\n
            * onewaydelay - One Way Delay.  Only available if endpoints are
                            time synchronized (same NTP source).
                            otherwise 'NA'\n
            * CiscoRxVM - This field is a combination of certain other
                          parameters which user can configure them sperately,
                          but when displaying this field all the related fields
                          wil be combined and displayed as a complete string.
                          For example, CS, SCS, DSCP, etc., can be configured
                          separately.  Refer sip.rtpstats configuration
                          parameter. For example \n
                          CiscoRxVM='CS=xxx;SCS=xxx;DSCP=xxx;DSCPunad=xxx;
                          RxFramesLost=xxx;RxCodec=xxx;RxBw=xxx;RxBwMax=xxx;
                          RxReso=xxx;RxFrameRate=xxx; PRPL=xxx;PostFEC=xxx'\n
            * ice      - if Ice enabled Ice info in format mmm:xxx:nnn:tttt\n
                        * mmm: Mode.One of ice|lite|none|unk.Default value unk
                        * xxx:Type of candidate selected host/relay/srflx/prflx
                        * nnn: Max time(ms)for connectivity check on that path
                          Default value is 0
                        * ttt: time(ms)for the full ICE negotiation to complete
                          Default value is 0\n
        >>> ep1.get_rtp_rx_stats()
        {'avgjitter': '0',
         'duration': '0',
         'latepkt': '0',
         'lostpkt': '0',
         'octrcvd': '0',
         'pktrcvd': '0'}
        '''
        return self._query_camelot(camelot.GET_RTP_RX_STAT, stream_type)

    def get_rtp_tx_stats(self, stream_type='audio'):
        ''' Returns the   Gets the RTP Tx statistics.

        :parameter stream_type:  stream_type of stream. Possible values \n
            * audio - statistics with respect to audio stream (default)
            * video - statistics with rspect to video stream

        :returns: dictionary of informations mentioned below \n
            Audio Statistics field: \n
            * duration - Total number of seconds since beginning of reception
            * pktsent - Total number of RTP packets transmitted
            * octsent -Total number of RTP payload octets transmitted
                        (not including RTP header).
            Video Statistics field: \n
            * duration - Total number of seconds since beginning of reception
            * numpktsent - Total number of RTP packets transmitted
            * numoctsent - Total number of RTP payload octets transmitted
                           (not including RTP header).
            * content - Identifies the type of transmitted video stream.
                        The possible values can be \n
                        * main
                        * speaker
                        * slides
            * roundtriptime - Round Trip Time. Useful for figuring out how fast
                             recovery can happen and to ensure within
                             expected bound.
            * onewaydelay - One Way Delay.  Only available if endpoints are
                            time synchronized (same NTP source).
                            otherwise 'NA'
            * CiscoRxVM - This field is a combination of certain other
                          parameters which user can configure them sperately,
                          but when displaying this field all the related fields
                          wil be combined and displayed as a complete string.
                          For example, TxCode,TxNW, etc., can be configured
                          separately.  Refer sip.rtpstats configuration
                          parameter. For example \n
                          CiscoTxVM='TxCodec=xxx;TxBw=xxx;TxBwMax=xxx;
                          TxReso=xxx;TxFrameRate=xxx'\n

        >>> ep1.get_rtp_tx_stats()
        {'duration': '0',
         'octsent': '0',
         'pktsent': '0'}
        '''
        return self._query_camelot(camelot.GET_RTP_TX_STAT, stream_type)

    def get_user_info(self, jid=None, username=None,
                      emailid=None, phonenumber=None):
        '''Shows the entire contact list for a jabber end point. Any one of the
        parameters should be provided to return the contact list otherwise
        returns error string.

        :parameter jid: Jid of the buddy
        :parameter username: username of the buddy
        :parameter emailid: emailid of the buddy
        :parameter phonenumber:  phone number of the buddy

        :returns: information of the buddy in key-value pair
                  format as a dictionary.

        >>> ep1.get_user_info('regep3200003@camelot.test')
        {
        'department': 'sales',
        'directoryuri': '',
        'displayname': '',
        'email': 'regep3200003@camelot.test',
        'firstname': 'reg',
        'homenumber': '',
        'id': '7457aa7c-0a39-c88c-14ac-fedbd031368c',
        'lastname': 'ep3200003',
        'manager': '',
        'middlename': '',
        'mobilenumber': '',
        'msuri': '',
        'nickname': '',
        'pager': '',
        'phonenumber': '',
        'title': 'regep3200003',
        'username': 'regep3200003'
        }
        '''
        kwargs = {'username': username,
                  'emailid': emailid,
                  'phonenumber': phonenumber}

        return self._query_camelot(camelot.GET_USER_INFO, jid, **kwargs)

    def gen_cert_key(self):
        '''
        Initiate certificate/key generation for secured connection

        Creates certificate and key files within the current endpoint's context
        During registration, secured endpoints require certificate and key
        files. Certificates are generated in the server's /lib/certificates
        directory. Keys are generated in the server's /lib/clientkeys directory
        In order for CCM to recognize these files, the user must copy the file
        with the .0 extension to the server's /lib/certsigner directory and to
        the CCM's certificate directory, \Program Files\Cisco\Certificates.
        Once the certificate and key are generated for an endpoint, they may
        be reused in subsequent registrations.

        returns: True on successful execution of the command, else
        will print error statement.

        >>> ep1.gen_cert_key()
        True
        '''
        log.debug('Entering method gen_cert_key().')
        result = self._query_camelot(camelot.GEN_CERT_KEY)
        if not result:
            return True
        else:
            return result

    def get_cert_info(self, file_name=None):
        '''It displays various fields of an X509 certificate file.

        :parameter file_name: Its a optional parameter which
         indicates the file name (with absolute path) of the
         certificate file. If not provided , the command will
         pickup default endpoint certificate.This certifcate file
         should be of X509 format.

        :returns: On success a json string with following fields :\n
               * sign_algorithm - name of the signature algorithm.
                 For example, ecdsa-with-SHA1
               * key_algorithm - name of the public key algorithm.
                 For example, id-ecPublicKey
               * key_curve - name of the EC curvename of the certificate
                 For example, P-384
                 This info is relevant only when key is ECDSA
               * key_length - bit size of the public key
                 For example, 4096 (for RSA)
               * file_name - name (absolute path) of the certificate file
               * parse_error - error message in case of any failure
                 For example:\n
                 * failed to open certificate file
                 * parsing X509 certificate failed


        >>> ep.get_cert_info()
        {"certificate_data":
          {"sign_algorithm": "sha1WithRSAEncryption",
              "key_algorithm": "id-ecPublicKey",
              "key_curve": "P-384", "key_length": "256"
             },
         "file_name":
         "/usr/local/camelot/lib/certificates/SEPDAAADAAA6002.cer",
         "parse_error":""
         }
        '''
        return self._query_camelot(camelot.GET_CERT_INFO, file_name)

    def get_vmws_info(self):
        '''returns the current voice mail web service information

        :returns: A variable sized list of dictionaries with {field value}
        pairs containing extended information about the vmws.
        * state - login/logout state with unity server.
        Below are the possible values:\n
         * "" - initial value
         * login pending - login is invoked, waiting for the response.
         * login completed - login is completed successfully.
         * login failed - login is failed successfully.
         * logout pending - logout function is invoked,
         waiting for the response.
         * logout completed - logout is completed successfully.
         * logout failed - logout is failed successfully.
         * get message count pending - /GetMessageCounts request is
         invoked, waiting for the response
         * get message count completed - successful response is received
         for /GetMessageCounts
         * get message count failed - failed response is received
         for /GetMessageCounts
         * get messages pending - /GetMessages request is invoked,
         waiting for the response
         * get messages completed - successful response is received
         for /GetMessages
         * get messages failed - failed response is received for
         GetMessages
         * get callid pending - /GetCallId request is invoked,
         waiting for the response
         * get callid completed - successful response is received
         for /GetCallId
         * get callid failed - failed response is invoked
         for /GetCallId.
        * error code - received 3xx/4xx/5xx/6xx response code
        * failure reason - received 3xx/4xx/5xx/6xx reason phrase
        from status line.
        * session id - returned session id, upon login successful.
        * session timeout min - returned SessionTimeoutMin property value,
        upon login successful.
        * refresh state - renew login state with unity server.
        Below are the possible values:\n
            * "" - initial value
            * refresh pending - renew login is invoked,
            waiting for the response.
            * refresh completed - renew login is completed successfully.
            * refresh failed - renew login is failed successfully.
        * renew login response status - received RenewLoginResponse status
        value, upon RenewLogin successful.
        * refresh attempts - attempted number of renew logins.
        * successful refresh attempts - successful renew login attempts.
        * current unity ip - present unity server ip address
        * current unity port - present unity server port.
        * mail box status - received mail box status in
        GetMessageCounts response body
        * voiceandreceipts count - received VoiceAndReceipts filter message
        count in /GetMessages response body
        * voice count - received Voice filter message count in
        GetMessages response body
        * newvoice count - received NewVoice filter message count in
        GetMessages response body
        * newreceipt count - received NewReceipt filter message count in
        GetMessages response body
        * callid response value - received callid response value in
        GetCallId response body.

        >>> ep.get_vmws_info()
        {'state' : 'login completed',
         'error code' : '',
         'failure reason' : '',
         'session id' : '013545f0-6f6a-4756-b18f-f8a352313579',
         'session timeout min' : '1',
         'refresh state' : 'refresh completed',
         'renew login response status' :'S_VMWS_GEN_SERVER_RUNNING',
         'refresh attempts' : '1',
         'successful refresh attempts' : '1',
         'current unity ip' : '10.12.10.130',
          'current unity port' : '80',
          'mail box status' : '',
          'voiceandreceipts count' : '4',
          'voice count' : '4',
          'newvoice count' : '',
          'newreceipt count' : '',
          'callid response value' : 'Okay'}
        '''
        return self._query_camelot(camelot.GET_VMWS_INFO)

    def get_supported_conversations_info(self):
        '''returns the supported conversation information

        :returns: list of conversations, received in vmws /Login response

        >>> ep.get_supported_conversations_info()
        {'conversations' : ["SetupOptions", "TUIRedirect"]}
        '''
        return self._query_camelot(camelot.GET_SUPPORTED_CONVERSATION_INFO)

    def get_edge_info(self):
        '''returns the current edge config download status information
         like home edge download status, status, tftpserveraddress,
         sipedgeserveraddress, sipedgeserverport, siproute,
         httpedgeserveraddress and httpedgeserverport.

        :returns: A variable sized list of dictionaries with {field value}
            pairs containing extended information about the edge config
            information.\n
            * auth cookie refresh - status of VCS-E authentication cache
              refresh.Below are the possible values:\n
              * "" - initial value
              * pending - refresh is started
              * success - refresh is completed successfully
              * failed - refresh is failed
            * config refresh - status of edge configuration download
              refresh. Below are the possible values:\n
              * "" - initial value
              * pending - refresh is started
              * success - refresh is successfully completed
              * failed - refresh is failed
            * tftpserveraddress -
            * sipedgeserveraddress - VCS-Edge server address used for active
              registration.
            * siproute - VCS-Connect server address used for active
              registration.
            * httpedgeserveraddress - VCS-Edge http server address used for
              active registration.
            * httpedgeserverport - VCS-Edge http server port used for
              active registration.
            * sip_routes - List of dictonary depicting the routes with their
              roles and states used for sip registration. Each dictonary has
              the following keys:\n
              * priority - priority of the route. For MRA deployments the
                priority number will be based on the cucm's received in device
                config file. The value starts from 0.
              * reg_type - role of the path used. Below are the possible
                values:\n
                * active - Path on which SIP Registration is sent.
                * standby - Path on which cisco-keepalive SIP Registration is
                  sent.
                * primary_fallback_monitoring - Path on which SIP Registration
                  primary fallback probe is sent.
                * secondary_fallback_monitoring - Path on which SIP
                  Registration secondary fallback probe is sent.
              * edge - VCS-Edge server address.
              * edgc - VCS-connect server address path.
              * cucm - CUCM address SIP Register is sent to.
              * camelot_reason - error if registration fails.
                examples:\n
                * 408 received: 'received response:404 Not found; CUCM node
                  failure detected;Warning: 399 10.12.10.152:5061 Policy
                  Response '
                * TCP connection failure: 'error:TCP connection error:(11):
                  Resource temporarily unavailable;VCS Edge node failure
                  detected'.
              * time - time stamp, if 200ok was received or if an error
                occured on the path.
              * sessionId - Is the sessionid of the regisration happening
                on the given route.
              * state - is the state of the route.  Below are the possible
                values:\n
                * init - one of the available route selected.
                * inservicepending - sent TCP/TLS connect request, then
                  sent register to the network and waiting for the response.
                * outofservice -  TCP/TLS negotiation failure, or Registration
                  failures.
                * inservice - Successful registration response.
              * callid -  It is callid of the regisration happening on
                the given route.
              * stun_keepalive - SK stats are captured here:\n
                * sent_time -shows the time stamp of stun binding request
                  (stun keepalive) sent most recently.
                * recv_time - stun binding response(stun keepalive) recv
                  timestamp for the request sent most recently.
                * status - possible values are:\n
                  * active - Camelot received successful response
                  * failed - Camelot received error response/timedout
                  * "" - if stunKeepAlive is not enabled/till we receive
                    first STUN successful/failure response.
                * negotiation_status - possible values are:\n
                  * true -  stun keepalive is supported by VCSE
                  * false - stun keepalive is supported by VCSE
                  * "" - user has not configured 'edge.ha.token_value' with
                    'SK' or 'AR_SK'
              * adaptive_routing - Adaptive Routing stats are captured here:\n
                * negotiation_status - possible values are: \n
                  * success - AR is supported by Expressway
                  * not_supported_by_vcse - AR is not supported by Expressway
                  * "" - AR is not configured on client / AR is configured
                    but response to which is not received yet from Expressway.
                * replaced_edgec - Carries the failed edgec node
                  when Expressway-E has adaptively routed the registration\n
                  '' - If AR is not being applied on Expressway-E side
                * timestamp - Shows the timestamp at which edgec node failed\n
                  '' - If AR is not being applied on Expressway-E side
              * edge_remote_port - VCS-Edge server remote port
              * edgec_remote_port - VCS-connect server remote port
              * cucm_remote_port - CUCM remote port
            * edge_config - Dictionary contains List of dictonaries depicting
              DNS SRV records found and the current state of the Edge topology
              and routes in priority order. Each list of dictonary has
              the following keys:\n
              * edge_srv - List of dictonary depicting resolved VCS-E servers
                ipaddress and port in the priority order from DNS SRV lookup\n
                * host - DNS SRV resolved address
                * port - DNS SRV resolved port
              * edge_sip - List of dictonary depicting resolved VCS-E servers
                and port in the priority order discovered from get_edge_config
                response.Values\n
                * host - VCS-Edge  address
                * port - VCS-E port
              * edgc - List of dictonary depicting resolved VCS-C servers
                ipaddress and port in the priority order discovered from
                get_edge_config response.Values\n
                * host - VCS-C address
                * port - VCS-C port
              * edge_http - List of dictonary depicting resolved http edge
                server ipaddress and port in the priority order discovered from
                get_edge_config response.Values\n
                * host - edge http server address
                * port - edge http server port
              * edge_xmpp - List of dictonary depicting resolved xmpp edge
                server ipaddress and port in the priority order discovered from
                get_edge_config response.Values\n
                * host - edge xmpp server address
                * port - edge xmpp server port
              please refer to following wiki.\n
              https://wiki.cisco.com/display/CAMELOT/14.0+Edge%28MRA%29+SIP+failover+and+fallback#id-14.0Edge(MRA)SIPfailoverandfallback-get_edge_infoAPItoshowAdaptiverouting(AR)infoifARischosen


        >>> ep.get_edge_info()
        {
            'status': 'edgecomplete',
            'error': '',
            'auth cookie refresh': '',
            'config refresh': '',
            'tftpserveraddress': '',
            'sipedgeserveraddress': 'cam-vcse-154.camelot.test',
            'sipedgeserverport': '5061',
            'siproute': '<sip:10.12.10.155:5061;transport=tls;zone-id=1;direc
            ted;lr>',
            'httpedgeserveraddress': 'cam-vcse-154.camelot.test',
            'httpedgeserverport': '8443',
            'sip_routes': [{
            'priority': 0,
            'reg_type': 'active',
            'edge': 'cam-vcse-152.camelot.test',
            'edgc': '<sip:10.12.10.157:5061;transport=tls;zone-id=1;directed
            ;lr>',
            'cucm': 'cam-ccm-99.camelot.test',
            'state': 'outofservice',
            'camelot_reason': 'received response:408 Request Timeout;CUCM no
            de failure detected;Warning: 383 10.12.10.157:5061  next hop no
            t reachable ',
            'sessionId': '6d6c9275004050008000be5e61100001;remote=0000000000
            0000000000000000000000',
            'callid': '920680807051458@10.12.10.227',
            'time': '2021-05-04T15:45:51.501',
            'edge_remote_port': '5061',
            'edgec_remote_port': '5061',
            'cucm_remote_port': '5091',
            'stun_keepalive': {
            'sent_time': '',
            'recv_time': '',
            'status': '',
            'negotiation_status': '',
            },
            'adaptive_routing': {
            'negotiation_status': '',
            'replaced_edgec': '',
            'timestamp': '',
            },
            }, {
            'priority': 1,
            'reg_type': 'active',
            'edge': 'cam-vcse-153.camelot.test',
            'edgc': '<sip:10.12.10.156:5061;transport=tls;zone-id=1;directed
            ;lr>',
            'cucm': 'cam-ccm-116.camelot.test',
            'state': 'outofservice',
            'camelot_reason': 'VCSC node failure detected;stun keep alive fai
            lure',
            'sessionId': '6d6c9275004050008000be5e61100001;remote=00000000000
            000000000000000000000',
            'callid': '920680996035089@10.12.10.227',
            'time': '2021-05-04T15:46:52.060',
            'edge_remote_port': '5061',
            'edgec_remote_port': '5061',
            'cucm_remote_port': '5091',
            'stun_keepalive': {
            'sent_time': '2021-05-04T15:46:52.57-05:30',
            'recv_time': '2021-05-04T15:46:52.60-05:30',
            'status': 'failed',
            'negotiation_status': 'true',
            },
            'adaptive_routing': {
            'negotiation_status': 'success',
            'replaced_edgec': '',
            'timestamp': '',
            },
            }, {
            'priority': 2,
            'reg_type': 'active',
            'edge': 'cam-vcse-154.camelot.test',
            'edgc': '<sip:10.12.10.155:5061;transport=tls;zone-id=1;directed
            ;lr>',
            'cucm': 'cam-ccm-117.camelot.test',
            'state': 'inservice',
            'camelot_reason': '',
            'sessionId': '6d6c9275004050008000be5e61100001;remote=0000000000
            0000000000000000000000',
            'callid': '920741475044911@10.12.10.227',
            'time': '2021-05-04T15:46:52.228',
            'edge_remote_port': '5061',
            'edgec_remote_port': '5061',
            'cucm_remote_port': '5091',
            'stun_keepalive': {
            'sent_time': '2021-05-04T15:46:52.223-05:30',
            'recv_time': '2021-05-04T15:46:52.227-05:30',
            'status': 'active',
            'negotiation_status': 'true',
            },
            'adaptive_routing': {
            'negotiation_status': 'success',
            'replaced_edgec': '<sip:10.12.10.156:5061;transport=tls;zone-id=1
            ;directed;lr>',
            'timestamp': '2021-05-04T15:46:52.61-05:30',
            },
            }],
            'edge_config': {
            'edgc': [{
            'host': '10.12.10.157',
            'port': 5061,
            }, {
            'host': '10.12.10.156',
            'port': 5061,
            }, {
            'host': '10.12.10.155',
            'port': 5061,
            }],
            'edge_http': [{
            'host': 'cam-vcse-152.camelot.test',
            'port': 8443,
            }, {
            'host': 'cam-vcse-153.camelot.test',
            'port': 8443,
            }, {
            'host': 'cam-vcse-154.camelot.test',
            'port': 8443,
            }],
            'edge_sip': [{
            'host': 'cam-vcse-152.camelot.test',
            'port': 5061,
            }, {
            'host': 'cam-vcse-153.camelot.test',
            'port': 5061,
            }, {
            'host': 'cam-vcse-154.camelot.test',
            'port': 5061,
            }],
            'edge_srv': [{
            'host': 'cam-vcse-152.camelot.test',
            'port': 8443,
            }, {
            'host': 'cam-vcse-154.camelot.test',
            'port': 8443,
            }, {
            'host': 'cam-vcse-153.camelot.test',
            'port': 8443,
            }],
            'edge_xmpp': [{
            'host': 'cam-vcse-152.camelot.test',
            'port': 5222,
            }, {
            'host': 'cam-vcse-153.camelot.test',
            'port': 5222,
            }, {
            'host': 'cam-vcse-154.camelot.test',
            'port': 5222,
            }],
            },
        }
        '''
        return self._query_camelot(camelot.GET_EDGE_INFO)

    def get_hedge_info(self):
        '''Along with state of Hedge IR4 call flow, it displays retrieved otp,
        access token and url information. This command also displays the
        failure status happened at any point during the OTP, userReference
        and /register

        :returns: A variable sized list of dictionaries with {field value}.
         The following fields are supported:\n
         * state : Below are the possible values:
               * ""
               * otp pending
               * otp complete
               * otp failed
               * lookup user id pending
               * lookup user id complete
               * lookup user id failed
               * register user ref pending
               * register user ref complete
               * register user ref failed
               * hedge tftp resource pending
               * hedge tftp resource complete
               * hedge tftp resource failed
               * self provision pending
               * self provision complete
               * self provision failed
               * device download pending
               * device download complete
               * device download failed
               * complete
         * failure reason : error information
         * activation code: activation code returned by /cmi/identity/users/otp
                http query
         * refresh token : refresh token returned by
           /v1/actions/register http query
         * access token : access token returned by
           /v1/actions/register http query
         * token type : token type returned by
           /v1/actions/register http query
         * expires in : expires in field returned by
           /v1/actions/register http query, life time in seconds of the
           access token
         * refresh token expires in : refresh token expires in field returned
           by /v1/actions/register http query, life time in seconds of
           the refresh token
         * url : Device registration URL url field returned by
           /v1/actions/register http query,
         * cis domain : cis domain returned by
           /v1/actions/register http query
         * uds domain : uds domain returned by
           /v1/actions/register http query
         * callcontrol hedge ip : resolved ip for the host name
           callcontrol.serviceDomain. Here serviceDomain is received in
           /userReference 200 OK response.
         * response: Captures status code, phrase and response body of last
           HTTP/SIP REGISTER request, even if the response is
           positive (200 OK).\n
               * code: Status code
               * phrase: reponse phrase
               * body: response body if present along with response
                     * Note: Camelot is removing special characters "<CR><LF>
                             from the body of last received response unless
                             otherwise loading into the json format will fail.

        >>> ep.get_hedge_info()
        {
           "refresh success":"1",
           "access token":"YmIyNzY3NWYtOTEwOC00YjYtMTll",
           "refresh token":"NDMzNjQxZTItOTkwOS00YT32M22",
           "revokestate":"ath revoke complete",
           "refresh token expires in":"5174523",
           "drs ip":"",
           "gds ip":"",
           "state":"complete",
           "refresh attempts":"1",
           "expires in":"43199",
           "clientcfg hedge ip":"52.14.62.90",
           "failure reason":"hedge access token refresh pending:
            Server certificate validation failed",
           "callcontrol hedge ip":"52.14.62.90",
           "token type":"Bearer",
           "response":{
              "body":"<x-cisco-remotecc-response>
              <code>200</code></x-cisco-remotecc-response>",
              "phrase":"OK",
              "code":"200"
           },
           "uds ip":"",
           "activation code":"refresh",
           "request":"REGISTER sip:cms-vip-a-01-internal.na-int2.hron-
           int.com SIP/2.0",
           "refresh failed":"0",
           "url":"",
           "uds domain":"hron-int.com",
           "cis domain":""
        }
        '''
        return self._query_camelot(camelot.GET_HEDGE_INFO)

    def http_response(self, url_name):
        '''Displays various information on http response received for the last
        headset request sent by Camelot for a particular headset URL.

        :parameter url_name: headset url value. It can be fetched from\n
         get_headset() API.
         For example config url:\n
         '/headset/config/user/JABBEREP1200001'

        :returns: A dictionary with the following fields:\n

         * response:received  response for the headset URL with below info:\n
               * status_code: response code received . For example 200 ,404 etc
               * status_text: response pharse/text received.
               * body: body of the response
               * headers: the header names and values in dictioanry format\n
                 present in the response. For example\n
                     * Content-length: 2264
                     * Content-type:''
                     * Cache-Control: 'no-store'
         * url: headset url/path for which request was sent without any spaces
         * start_time: time at which request was sent
         * end_time: time at which response was received
         * camelot_reason: reason text notifying different error cases such\n
           as TCP conect error,timeout ,SSL Error etc. For more details\n
           please refer to following wiki.\n
           `<https://wiki.cisco.com/display/CAMELOT/Headset+feature+support+in+Camelot>`_
         * remote_port: remote port of the sent request same as get_headset()
         * remote_ip: remote ip of the sent request same as get_headset()

        >>> ep.http_response('/headset/config/user/JABBEREP1200001')
        {u'end_time': u'2019-01-23T11:52:09',
        u'camelot_reason': u'',
        u'remote_host': u'10.12.10.2',
        u'remote_port': u'6971',
        u'response': {u'body': u'',
        u'headers': {u'Cache-Control': u'no-store',
        u'Content-length': u'2236',
        u'Content-type': u'*/*'},
        u'status_code': u'200',
        u'status_text': u'OK'},
        u'start_time': u'2019-01-23T11:52:09',
        u'url': u'/headset/config/user/JABBEREP1200001'
        u'body': {"headsetConfig":{ "templateConfiguration":
         {"configTemplateVersion":"1",
         "updatedTime":1537399899,"reportId":3,"usageId":35}}
        }
        Note: Above body example is a dummy one

        >>> ep.http_response('/headset/config/user/JABBEREP1200001')
        {u'end_time': u'2019-02-28T11:52:09',
        u'camelot_reason': u'TCP connection error:(11)Resource temporarily
        unavailable',
        u'remote_host': u'10.12.10.2',
        u'remote_port': u'6971',
        u'response': {u'body': u'',
         u'headers': {}
         u'Content-length': u'',
         u'Content-type': u''},
        u'status_code': u'',
        u'status_text': u''},
        u'start_time': u'2019-02-28T11:52:09',
        u'url': u'/headset/config/user/JABBEREP1200001'
        u'body':
        }

        >>> ep.http_response('/headset/config/user/JABBEREP1200001')
        {u'end_time': u'2019-02-29T11:52:09',
        u'camelot_reason': u'error:14094410:SSL Routines:ssl3_read_bytes:
        sslv3 alert handshake failure',
        u'remote_host': u'10.12.10.2',
        u'remote_port': u'6971',
        u'response': {u'body': u'',
         u'headers': {}
         u'Content-length': u'',
         u'Content-type': u''},
        u'status_code': u'',
        u'status_text': u''},
        u'start_time': u'2019-02-29T11:52:09',
        u'url': u'/headset/config/user/JABBEREP1200001'
        u'body':
        }
        '''

        return self._query_camelot(camelot.HTTP_RESPONSE, url_name)

    def get_device_config(self, mode='1'):
        '''It displays device configurations of the endpoint.Takes mode
        as a parameter.Mode=2 is the recommended value of mode for the API
        Default mode=1 is for backward compatibility of test scripts for
        Camelot version 12.5.21 and earlier.
        :returns: A multi layered json string with field values

        >>> ep.get_device_config()
        {
        {"devicePool":
          {"name": "Default",
             "callManagerGroup":
             {"name": "Default",
             "members":
             [
             {"priority": "0", "name": "cam-feature15-pub.camelot.test",
              "ipv6Addr": "2002:db8:c18:1:20c:29ff:fe08:ffef", "
              description": "cam-feature15-pub", "sipPort": "5060",
              "securedSipPort": "5061","sipoauthport": "5064",
              "processNodeName": "cam-feature15-pub.camelot.test"
             },
             {"priority": "1", "name": "cam-feature16-pub.camelot.test",
             "ipv6addr": "2002:db8:c18:1:20c:29ff:fe08:feef", "
             description": "cam-feature16-pub", "sip_port": "5060",
             "securedSipPort": "5061","sip_oauth_port": "5064",
             "processNodeName": "cam-feature15-pub.camelot.test"
             }
             ]
         }
         },
         "sipoauthmode": "0"
        }
        }
        >>> ep.get_device_config('2')
        {'device': {'@ctiid': 14,
          '@id': '{c7129337-8d3f-6760-9285-3aaa33fdc9b5}',
          '@xsi:type': 'axl:XIPPhone',
          'SSOSPServers': {'SSOSPServer': 'ciscart192'},
          'TLSResmptionTimer': 3600,
          'TVS': {'members': {'member': {'@priority': 0,
         'address': 'ciscart192',
         'port': 2445}}},
          'advertiseG722Codec': 1,
          'allowAtoConfig': Tre,
        'vendorConfig': {'AlternatePhonebookServerAddress': None,
       'AlternatePhonebookServerType': 'CCM',
       'DefaltVolme': 50,
       'FarEndCameraControlGrop': {'FarEndCameraControlMode': 'Off'},
       'LDAPserManagement': {'LDAPAdminFilter': None,
        'LDAPAdminGrop': None,
        'LDAPAttribte': None,
        'LDAPBaseDN': None,
        'LDAPEncryption': 'LDAPS',
        'LDAPMinimmTLSVersion': 'TLSv1.0',
        'LDAPMode': 'Off',
        'LDAPServerAddress': None,
        'LDAPServerPort': 0,
        'LDAPVerifyServerCertificate': 'Off'},
       'MaxTotalDownstreamRate': 3072,
       'MaxTotalpstreamRate': 3072,
       'Proximity': {'ProximityCallControl': 'Disabled',
        'ProximityContentShareFromClients': 'Disabled',
        'ProximityContentShareToClients': 'Disabled',
        'ProximityMode': 'Off'},
       'SerialPortGrop': {'SerialPortLoginReqired': 'Off',
        'SerialPortMode': 'Off'},
       'StandbyGrop': {'StandbyDelay': 10, 'StandbyMode': 'Off'},
       'SystemName': None,
       'TelnetMode': 'Off',
       'WakepOnMotionDetection': 'Off',
       'sshAccess': 1,
       'webAccess': 0,
       'xConfigration': {'xConfigration Adio DefaltVolme': '50',
        'xConfigration Adio Inpt MicrophoneMode': 'Focsed',
        'xConfigration Adio Microphones Mte Enabled': 'InCallOnly',
        'xConfigration Adio SondsAndAlerts RingTone': 'Snrise',
        'xConfigration Adio SondsAndAlerts RingVolme': '50',
        'xConfigration Adio ltrasond MaxVolme': '70',
        'xConfigration Cameras Camera 1 Backlight DefaltMode': 'Off',
        'xConfigration Conference AtoAnswer Delay': '0',
        'xConfigration Conference AtoAnswer Mode': 'Off',
        'xConfigration Conference AtoAnswer Mte': 'Off',
        'xConfigration Conference DefaltCall Protocol': 'Ato',
        'xConfigration Network 1 QoS Diffserv ICMPv6': '0',
        'xConfigration Network 1 QoS Diffserv NTP': '0',
        'xConfigration Network 1 QoS Diffserv Signalling': '0',
        'xConfigration Network 1 QoS Diffserv Video': '0',
        'xConfigration Network 1 QoS Mode': 'Diffserv',
        'xConfigration Network 1 RemoteAccess Allow': '',
        'xConfigration Network 1 Speed': '1000fll',
        'xConfigration Network 1 VLAN Voice Mode': 'Ato',
        'xConfigration Video Inpt Connector 2 Visibility': 'Always',
        'xConfigration Video Monitors': 'Single',
        'xConfigration Video Otpt Connector 1 Resoltion': '1920_1080_60',
        'xConfigration Video Presentation DefaltSorce': '2',
        'xConfigration Video Selfview Defalt FllscreenMode': 'Crrent',
        'xConfigration Video Selfview Defalt Mode': 'Crrent',
        'xConfigration Video Selfview Defalt OnMonitorRole': 'First',
        'xConfigration Video Selfview Defalt PIPPosition': 'CenterLeft',
        'xConfigration Video Selfview Mirrored': 'Off',
        'xConfigration Video Selfview OnCall Dration': '10',
        'xConfigration Video Selfview OnCall Mode': 'Off'}},
          'versionStamp': '1532339890-92e02811-5ddf-4a81-95be-b6d5cb9a5748'}}
        '''
        if mode == '2':
            dev_conf = self._query_camelot(camelot.GET_DEVICE_CONFIG, mode)
            if dev_conf is None:
                return None
            if 'device' in dev_conf.keys():
                if 'vendorConfig' in dev_conf['device'].keys():
                    vconfig = dev_conf['device']['vendorConfig']
                    if vconfig is not None:
                        if 'xConfiguration' in vconfig.keys():
                            xconfigval = vconfig['xConfiguration']
                            if xconfigval is not None:
                                mylist = xconfigval.splitlines()
                                xconfig_dict = {}
                                for i in mylist:
                                    if i is not None:
                                        j = i.split(':')
                                        if len(j) is not 1:
                                            xconfig_dict[j[0]] = j[1][1:-1]
                                if xconfig_dict:
                                    vconfig['xConfiguration'] = xconfig_dict
            return dev_conf
        else:
            return self._query_camelot(camelot.GET_DEVICE_CONFIG, mode)

    def get_hlog_status(self):
        '''Get information about an Huntgroup logged-in status

        :returns: "Logged On" if endpoint logged On to Hunt group
                  "Logged Off" if endpoint logged Off from Hunt group

        >>> ep.get_hlog_status()
            Logged Off
        '''
        return self._query_camelot(camelot.GET_HLOG_STATUS)

    def send_location_info(self):
        '''Explicitly sends the location info to CUCM

        :returns: sent if success or not supported if error

        >>> ep.send_location_info()
            {sent}
        '''
        return self._query_camelot(camelot.SEND_LOCATION_INFO)

    def register_event_callback(
            self, callback, event_type='all',
            event_sub_type='all', evtargsdict={}):
        '''Register an event callback that can be notified when a event
        is received for this endpoint from camelot server.

        event will be a dictionary with following falues:
            :camelot_ip: Camelot server ip
            :camelot_port: Camelot server port
            :endpoint_id: Camelot endpoint id
            :event_type: type of the event
            :event_sub_type: sub type of the event
            :message: following message from the even

        event_type: currently supported for type callevent
        event_sub_type: connected,end,sendreinvitecompleted,hold
        evtargsdict: Given by user to track user given arguements

        Note: If register_event_callback is been called without event_type
        and event_sub_type callback will be registered for all incoming
        events. We can't override it.

        :parameter callback: callback method which can be invoked by SDK

        >>> def event_callback(event):
        ...     print 'Received Event: %s' % event
        ...
        >>> server = camelot.create_camelot_server('10.106.248.199', 5004)
        >>> ep1 = server.create_new_endpoint('sipx', 'SEPBAACBAAC7001')
        >>> ep1.register_event_callback(event_callback)
        <camelot.endpoint.CamelotEndpoint object at 0x29ed490>
        >>> ep1.start_info_events()
        True
        >>> ep1.start_station_events()
        True
        >>> ep1.init()
        'outofservice'
        >>> ep1.inservice()
        'inservicepending'
        >>> Received Evenet: {'event_sub_type': 'ccmreg', 'event_type':
                 'station',
                'camelot_ip': '10.106.248.199', 'endpoint_id': '00000003',
                'camelot_port': 5004, 'message':
                '17:27:33:314 ccmreg {registration ok} 10.20.1.21'}
            Received Evenet: {'event_sub_type': None, 'event_type': 'state',
                'camelot_ip': '10.106.248.199', 'endpoint_id': '00000003',
                'camelot_port': 5004, 'message': ''}
        '''
        if event_type == 'all' and event_sub_type == 'all':
            self._callback = callback
        else:
            if self._callback:
                log.warning('Already callback is set for all'
                            'events cannot add new callback')
                return
            if not self._callback:
                key = event_type + ":" + event_sub_type
                self._callbackdict[key] = callback
                self._callbackarg = evtargsdict

    def _get_message_length_hex(self, message):
        if not message:
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

    def _send_query(self, sendMsg, functionStr):
        hex_len = self._get_message_length_hex(sendMsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, sendMsg)
        return self._camelot_query(rawmessage)

    def _camelot_query(self, encoded_msg):
        with self._get_server_conn().command_lock:
            ret = self._get_server_conn()._send_and_receive(encoded_msg)
            if ret.message:
                return ret.message

    def get_rpid(self, call_ref):
        '''Get Latest Remote-Party-ID information of a call.

        :returns: A list of dictionary with remote-party-ID attributes.
         The attribute which by default is display_name, uri, privacy,
         screen, party and tokens list, even if the value is not there it
         will shown as empty string (' ') and if there is no tokens in
         RPID header the token list will shown as empty list [].

        :Note: The attributes which all not permanent(x-cisco-number,
         x-cisco-tenant,x-cisco-callback-number etc) will raise exception
         (key error)if trying to access the attributes which is not present
         in Remote-Party-ID.

        >>> ep1.get_rpid('0xabcdabcd')
        [{'display_name': ' ', 'privacy': 'off', 'screen': 'yes',
        'uri': 'sip:+17206343685@192.168.90.190',
        'x-cisco-tenant': '5171fdae-f5a3-4a7b-8901-7f69872d31f4',
        'party': 'calling', 'x-cisco-number': '3685',
        'x-cisco-callback-number': '17206343685', 'key1': '',
        'token': ['token1', 'token2']},
        {'display_name': ' ', 'privacy': 'off', 'screen': 'yes',
        'uri': 'sip:+17206343685@192.168.90.90',
        'x-cisco-tenant': '571fdae-f5a3-4a7b-8901-7f69872d31f4',
        'party': 'calling', 'x-cisco-number': '368',
        'x-cisco-callback-number': '1720633685', 'token': []}]
        '''

        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        log.debug('Entering get_rpid function')
        return self._query_camelot(camelot.GET_RPID, call_ref)

    def get_call_history(self):
        '''Get call history for the endpoint.

        :returns: A list of call history, using Remote-party-ID header.
         This will show maximum of 30 recent call records. It will show
         empty list if there are no call records.
         The attributes are type, number, name, datetime. If the attribute
         value is not there it will shown as empty string (' ').

         * type :
           Below are the possible values:
           * R=Received
           * P=Placed
         * number : number value from RPID header as follows

           If URIDialingDisplayPreference is set as DN then :

                If x-cisco-callback present is used to populate
                the received call history

                If x-cisco-callback is not present then use the uri part
           if URIDialingDisplayPreference is set as URI then :

                x-cisco-calback is ignored and URI part is used for display.
         * name : display name from, RPID header
         * datetime : datetime in ISO8601 format
        >>> ep1.get_call_history()
        [ {'type': 'R', 'number': 'share@adgj.mpt',
        'name': ' ', 'datetime': '2015-04-05T22:24:35.123+00:00'},
        {'type': 'P', 'number': 'cr1@c.c',
        'name': 'Display 51031', 'datetime': '2015-04-05T22:26:35.123+00:00'},
        {'type': 'P', 'number': '51007',
        'name': 'AN 51007', 'datetime': '2015-04-05T22:29:35.123+00:00'},
        {'type': 'R', 'number': '+19193922000',
        'name': 'Cisco Systems', 'datetime': '2015-04-05T22:34:35.123+00:00'} ]
        '''

        log.debug('Entering get_call_history function')
        return self._query_camelot(camelot.GET_CALL_HISTORY)

    def get_conn_info(self):
        '''Get siptrunk cucm connection information.

        :returns: A list of cucm connection(s) information for siptrunk.
         Shows all the cucm ip, port configured and their connection state
         for this siptrunk.
        :Note: For API usage please refer:
               https://wiki.cisco.com/display/CAMELOT/Simulated+SIP+Trunk#SimulatedSIPTrunk-SipTrunkconnectionstotwoCUCM's

               https://wiki.cisco.com/display/CAMELOT/Simulated+SIP+Trunk#SimulatedSIPTrunk-OPTIONSpingInserviceintervalforCUCMconnections

         * index : cucmip index configured
         * ipaddr : cucm ipaddress
         * port : cucm port
         * local_addr : local ipaddress
         * local_port : local port
         * state : siptrunk connection state for this cucm ip.
           Possible values:\n
             * siptrunk_connect - Internal resources are allocated for the
               siptrunk and a TCP connection (and TLS if applicable) is
               attempted. After initiating a new socket connection, camelot
               waits for it to complete.

               'local_port' will not have a value until connection has
               reached a final connected or failure state. Local port
               number will not be shown while connection attempt is
               in progress.

             * connected - If options_keepalive is not enabled, this will be
               the state after new connection success (after inservice())
             * options_keepalive_ins - This state is used for sending OPTIONS
               keepalive requests if options_keepalive is enabled while the
               siptrunk is inservice. OPTIONS requests are sent at
               ins_interval time slots.

               The options_keepalive key holds the result of the most recent
               OPTIONS request.
             * options_keepalive_oos - This state is used for sending OPTIONS
               keepalive requests if options_keepalive is enabled while the
               siptrunk is inservicepending. OPTIONS requests are sent at
               oos_interval time slots.

               Note that the keys of the options_keepalive dictionary will be
               cleared just prior to initiating a new OPTIONS request. Thus
               the options_keepalive will show the results of the current or
               most recent request.

               Note: In this state, Camelot will not be able to initiate any
               new calls. Calls in progress will attempt to remain active
               until the user end_call().
             * wait_reconnect - state of the connection while it is waiting for
               the backoff timer to expire after a TCP or TLS connection
               failure. Once expired, the trunk will re-attempt the
               connection.
             * disconnected - On manual outofservice().  no further attempts
               will be made to initiate a connection until inservice().
         * options_keepalive : Holds the result of the most recent OPTIONS
           request.
             * sent_time - time the OPTIONS request was sent
             * result: the result of the request one of:
                 * success: response received was a 200 OK or a code not in
                   the oos_codes list.  The trunk is considered inservice.
                 * failure: response received was one of the codes in
                   the oos_codes list.
                 * timeout: no response was was received.
                 * connection failure: if a connection failure occurred at
                   any time.  The actual error, if available, will be shown
                   in 'error' key.
                 * internal error: any internal error, such as unable to
                   allocate or free memory.
                 * sip error: an error occurred in the sip stack during sending
                   the request or receiving the response
             * response - OPTIONS response message information. Ex.,
                {'code': '200','phrase': 'OK','reason': '','warning': ''}
             * receive_time - last response/timeout time stamp.
             * interval - current active timer interval in secs.
             * callid - OPTIONS call-id header value
             * cseq - OPTIONS cseq header value
             * sessionid - OPTIONS sessionid header value.
         * error : brief error response description. Refer
             https://wiki.cisco.com/display/CAMELOT/Simulated+SIP+Trunk#SimulatedSIPTrunk-ErrorMessages

        >>> trunk1.get_conn_info()
        [{ 'index': '1',
           'ipaddr': '10.12.10.87',
           'port': '5071',
           'local_addr': '10.12.10.92',
           'local_port': '42034',
           'state': 'options_keepalive_ins',
           'options_keepalive': {
           'sent_time': '2018-01-09T19:24:04.614-05:30',
           'result': 'success',
           'response': {
              'code': '200',
              'phrase': 'OK',
              'reason': '',
              'warning': '',},
           'received_time': '2018-01-09T19:24:04.622-05:30',
           'interval': '60',
           'callid': 'ef9b5e7c-db330ec7-0-bec7bb4@10.12.10.92',
           'cseq': '101 OPTIONS',
           'sessionid': '',},
           'error': '',
         },
         {
           'index': '2',
           'ipaddr': '10.12.10.87',
           'port': '5072',
           'local_addr': '10.12.10.92',
           'local_port': '59036',
           'state': 'options_keepalive_oos',
           'options_keepalive': {
           'sent_time': '2018-01-09T19:22:04.49-05:30',
           'result': 'timeout',
           'response': {
              'code': '',
              'phrase': '',
              'reason': '',
              'warning': '',},
           'received_time': '2018-01-09T19:22:23.571-05:30',
           'interval': '11',
           'callid': 'ef9b5e7c-db3137d3-0-4fe51e5b@10.12.10.92',
           'cseq': '',
           'sessionid': '',},
           'error': 'options keepalive timeout',
        }]

        >>> trunk1.get_info()
        For get_info error description changes please refer
        https://wiki.cisco.com/display/CAMELOT/Simulated+SIP+Trunk#SimulatedSIPTrunk-ErrorMessages
        '''

        log.debug('Entering get_conn_info function')
        return self._query_camelot(camelot.GET_CONN_INFO)

    def get_web_service_info(self):
        '''returns the HTTP Web Service Info for device remote monitor

        :returns: A variable sized list of dictionaries with {field value}
         pairs containing service status, ip, port, last query url etc.,

             * status :  Web service status
                    * uninit - Uninitialised, pl check last error
                    * active - Active, ready for query
                    * request process - Request in-process
             * ipaddr : Service IPAddr
             * port : Service port
             * last error : Last Error
             * last query url : Last query url
             * last response timestamp : Time stamp
             * last session cipher : last session cipher negotiated

        >>> ep.get_web_service_info()
        { "status": "active", "ipaddr": "10.12.10.32", "port": "443"
          "last error": "no error", "last query url": "\/DeviceInformationX",
          "last response timestamp": "2016-03-02::12:17:14:835",
          "last session cipher": "RAES128-SHA"
        }
        '''
        return self._query_camelot(camelot.
                                   GET_WEB_SERVICE_INFO)

    def set_custom_data(self, data):
        '''Associates an arbitrary custom data to an endpoint

        :parameter data: arbitrary string to associate with endpoint

        :returns: The newly assigned string

        >>> ep.set_custom_data('customdata')
        customdata
        '''
        log.debug('Entering into set_custom_data function')
        return self._query_camelot(camelot.SET_CUSTOM_DATA, data)

    def get_custom_data(self):
        '''Returns endpoint's assigned custom data string

        :returns: The endpoint's assigned arbitrary client string

        >>> ep.get_custom_data()
        phone1
        '''
        log.debug('Entering into get_custom_data function')
        return self._query_camelot(camelot.GET_CUSTOM_DATA)

    def setup_line(self, local_number, local_sub_address, voice_options=0):
        '''Setup the voice line profile for Analog endpoint. Invoking this
        API will call the DivaSetLineDeviceParamsVoice.

        :parameter local_number: Local Number of the Line.
        :parameter local_sub_address: Lcoal Sub Address of the Line.
        :parameter voice_options: DivaVoiceOptions in terms of \n
                                 0 - DivaVoiceOptionDefault (Default)\n
                                 1 - DivaVocieOptionEarlyDataChannel\n
                                 2 - DivaVoiceOptionEchoCanceller\n

        :returns: True or False

        >>> ep1.setup_line('1002','10',0)
        >>> True

        >>> ep2.setup_line('1003','11')
        >>> True
        '''
        log.debug('Entering into setup_line function')
        return self._query_camelot(camelot.SETUP_LINE, local_number,
                                   local_sub_address, voice_options)

    def get_cas_call_info(self, call_ref):
        ''' This API applicable only for CAS endpoint.  This will display the
        Call Info values returned from DivaGetCallInfo API. Valid cal
        information is available only if call is in incoming or connected state

        :parameter call_ref: valid call reference

        :returns: dictionary of call information or error string.\n
                    Possible error values are:\n
                    * bad call reference
                    * endpoint does not support this feature.
                    * no data available

        >>> ep1.vapi.get_cas_call_info('0xf5722cac')
        >>> {"line device": "1",
        "call state": "DivaCallStateDisconnected",
        "listen type": "DivaListenNone",
        "call type": "DivaCallTypeVoice",
        "data transfer possible": "0",
        "RxSpeed": "0",
        "TxSpeed": "0",
        "disconnect reason": "DivaDRActiveDisconnect",
        "isdn cause": "13456",
        "remote fax id": "",
        "local fax id": "",
        "fax pages": "",
        "polling active": "",
        "page resolution": "",
        "MR active": "",
        "MMR active": "",
        "ECM active": "",
        "echo canceller active": "0",
        "redirect reason": "0",
        "redirected number": "",
        "redirecting number": "",
        "signelled call type": "DivaSignalledCallTypeUnknown",
        "assigned B channel": "2",
        "compression": "0",
        "cpc detected": "false",
        "calling name": "",
        "connected name": "",
        "calling sub": "",
        "called sub": "",
        "connected number": "",
        "called name": "",
        "start": "",
        "end": "",
        "silence detected":{"time": "2017-08-10T15:23:45.644-5:30"
        "duration": "1"},
         "
         }
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        log.debug('Entering get_cas_call_info function')
        return self._query_camelot(camelot.GET_CAS_CALL_INFO, call_ref)

    def get_cas_llsa_info(self, call_ref):
        ''' This API applicable only for CAS endpoint.  This will display the
        low level signalling access call property returned from
        DivaGetCallProperties API.

        :parameter call_ref: valid call reference

        :returns: dictionary of call information or error string.\n
                    Possible error values are:\n
                    * bad call reference
                    * endpoint does not support this feature.
                    * no data available

        >>> ep1.vapi.get_cas_llsa_info('0xf5722cac')
        >>> {
             'display info': 'Call form Diva Board',
            }
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        log.debug('Entering get_cas_llsa_info function')
        return self._query_camelot(camelot.GET_CAS_LLSA_INFO, call_ref)

    def setup_fax_line(self, fax_profile):
        '''Setup the voice line profile for Analog endpoint. Invoking this
        API will call the DivaSetLineDeviceParamsFax.

        :parameter fax_profile: object of camelot.FaxProfile class\n
                                The FaxProfile class is given below:\n
                                class DivaFaxOptions(Enum):\n
                                    DivaFaxOptionsDefault = 0x00000000\n
                                    DivaFaxOptionDisableHighResolution
                                    = 0x00000001\n
                                    DivaFaxOptionDisableMR = 0x00000002\n
                                    DivaFaxOptionDisableMMR = 0x00000004\n
                                    DivaFaxOptionDisableECM = 0x00000008\n
                                    DivaFaxOptionEnablePolling = 0x00000100\n
                                    DivaFaxOptionRequestPolling = 0x00000200\n
                                    DivaFaxOptionReverseSession = 0x00000400\n
                                    DivaFaxOptionMultipleDocument
                                    = 0x00000800\n
                                    DivaFaxOptionEnableColor = 0x00001000\n
                                    DivaFaxOptionEnableInterrupt = 0x00010000\n
                                    DivaFaxOptionRequestInterrupt
                                    = 0x00020000\n

                                class FaxProfile:\n
                                    local_number = '-1'\n
                                    local_sub_address = '-1'\n
                                    local_fax_id = '-1'\n
                                    fax_headline = 'camelot'\n
                                    default_fax_speed =\n
                                    DivaFaxMaxSpeedAutomatic\n
                                    diva_fax_options =
                                    [DivaFaxOptions.DivaFaxOptionsDefault]\n
                                As shown in FaxProfile class, the default
                                values are applicable as it is.\n
                                * if -1 (by default), then the value will be
                                  empty when sent to respective Diva SDK
        :returns: True or CamelotException\n
                  Possible CamelotExceptions is:\n
                  1. Interface error
                      This occurs if invoking Diva SDK API fails
                  2. Invalid argument
                      This occurs when faxProfile is not instantiated with
                      FaxProfile()
                  3. Invalid FaxOptions
                      This occurs when FaxProfile.dvia_fax_options is not list
                      or its content is not type of DivaFaxOptions enum
                  4. Invalid fax speed
                      This occurs if FaxProfile.dvia_fax_speed is not type of
                      DivaFaxMaxSpeed enum

        >>> profile = camelot.FaxProfile()
        >>> profile.local_number = '1002'
        >>> profile.local_sub_address = '200'
        >>> profile.local_fax_id = '100'
        >>> profile.fax_headline = 'myfax'
        >>> profile.default_fax_speed
        = DivaFaxMaxSpeed.DivaFaxMaxSpeed2400
        >>> profile.diva_fax_options
        = [DivaFaxOptions.DivaFaxOptionEnableColor]
        >>> ep1.vapi.setup_fax_line(profile)
        >>> True
        '''

        if fax_profile and isinstance(fax_profile, FaxProfile):
            if fax_profile.diva_fax_options and \
                (type(fax_profile.diva_fax_options) is not
                 list or all(isinstance(fo, DivaFaxOptions)
                             for fo in fax_profile.diva_fax_options) is False):
                raise camelot.CamelotError('Invalid FaxOptions')
            if not isinstance(fax_profile.default_fax_speed,
                              DivaFaxMaxSpeed):
                raise camelot.CamelotError('Invalid fax speed')

        return self._query_camelot(camelot.SETUP_FAX_LINE, fax_profile)

    def get_ice_config(self):
        '''Get the information about ICE configuration

        :returns: A dictionary field:value pairs.\n
            current fields are supported:\n
            * "ice_enable" denotes either ICE is enabled or disabled.
              possible values 1 for enabled and 0 for disabled.
            * "ice_default_candidate" denotes the path which clients
              use to communicate to to each other.It can have 3
              possible values:\n
              * "host": Host candidate
              * "relay": Turn relay candidate
              * "srvRflx": server reflexive candididate.
            * "ice_server_reflex": shows whether server reflex address
              is enabled or not possible values 1 or 0.

        >>> ep1.vapi.get_ice_config()
        [{u'ice_enable': u'1'
        u'ice_default_candidate': u'host'
        u'ice_server_reflex': u'1'}]

        For more information on how users can overwrite the above values
        and how camelot determines those explained in camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/ICE+and+TURN+support

        '''
        ret = self._query_camelot(camelot.GET_ICE_CONFIG)

        return ret

    def get_jabber_profile(self):
        '''Get the information about jabberProfile configuration

        :returns: A dictionary field:value pairs.\n

        >>> ep1.get_jabber_profile()
        {
            u'Config': {u'Common': {u'ChatTelephonyEscalationLimit': 25,
            u'ContactCardonHover': True,
            u'Disable_IM_History': False,
            u'EnableAutosave': True,
            u'EnableAutosaveUserPref': False},
            u'Desktop': None,
        u'Mobile': None}}
        '''
        return self._query_camelot(camelot.GET_JABBER_PROFILE)

    def get_turn_config(self):
        '''Get the information about turn configuration

        :returns: A dictionary field:value pairs.\n
            current fields are supported:\n
            * "turn_enable" denotes either turn is enabled or not.
              possible values are 1 and 0.
            * "turn_transport" denotes the protocol client uses to
              send request to turn server.It can have 4 possible
              values mentioned below:\n
              * "auto" It will allow client to decide transport type.
              * "UDP"
              * "TCP"
              * "TLS"
              * Camelot currently uses UDP transport to communicate to
                TURN server to gather the candidated, other
                values are not supported yet.
            * "turn_username" denotes the user name to authenticate
              turn client to turn server.

        >>> ep1.vapi.get_turn_config()
        [{u'turn_enable': u'0',
        u'turn_transport': u'auto'
        u'turn_username': u'admin'}]

        For more information please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/ICE+and+TURN+support

        '''
        ret = self._query_camelot(camelot.GET_TURN_CONFIG)

        return ret

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
        hex_len = self._get_message_length_hex(outmsg)
        rawmessage = 'm:{0}:{1}:{2}'.format(self.ep_id, hex_len, outmsg)

        if actionset.event_type != '':
            self.register_to_event(actionset.event_type,
                                   actionset.event_sub_type,
                                   actionset.call_back)

        try:
            with_new_line = self._camelot_query(rawmessage)
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
        hex_len = self._get_message_length_hex(outmsg)

        rawmessage = 'm:{0}:{1}:{2}'.format(self.ep_id, hex_len,
                                            outmsg)

        try:
            with_new_line = self._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
            else:
                log.error('remove_action_set failed nul returned')
        except Exception as e:
            log.error('remove_action_set request failed reason:%s' % e)
            return

    def sip_custom_headers(self,
                           headers,
                           methods=['INVITE'],
                           action='add',
                           mode='request'):
        '''
        This is used for addition (or 'removal',which is yet to be implemented)
        of SIP headers to outgoing SIP messages.

        :parameter headers: dictionary which takes a set of SIP header Name
                            and value pairs.This is a mandatory field.
        :parameter methods: list of SIP method names.Default is ['INVITE']
        :parameter action: action to be performed. Possible values are:
                           add, remove and modify.Default is 'add'.
        :parameter mode: To indicate if its request or response.Default is
                         'request'. Other value is 'response'
                         (response is yet to be implemented).

        :returns: an instance of CustomHeadersObject on success.\n
                  Camelot Exceptions in case of error.
                  For the list of possible exceptions please refer
                  to the wiki link mentioned below.

        >>> Obj = ep1.sip_custom_headers(headers={'Subject':'SIP Call'},
        methods=['INVITE','BYE'],action='add', mode='request')

        >>> ep1.place_call(ep2line)
        ...  Verify custom changes in SIP messages ...

        >>> Obj.clear()
        True

        For more information please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/Simplified+SIP+Message+handling#SimplifiedSIPMessagehandling-SipCustomHeadersAPIimplementation
        '''
        log.debug("in sip_custom_headers method")

        out_message = camelot.SIP_CUSTOM_HEADERS

        if not headers:
            raise camelot.CamelotError('headers parm not specified')

        if not isinstance(headers, dict):
            msgtext = 'not a valid {header: value} dictionary for headers'
            raise camelot.CamelotError(msgtext)

        if not methods:
            raise camelot.CamelotError('methods parm not specified')

        if not isinstance(methods, list):
            raise camelot.CamelotError('not a valid list for methods')

        if not action:
            raise camelot.CamelotError('action is not specified')

        if not mode:
            raise camelot.CamelotError('mode is not specified')

        methodlist = ",".join(methods)

        out_message = '{} {}^{}^{}^{}'.format(
            out_message, headers, methodlist, action, mode)

        reply_buff = self._query_camelot(
            camelot.SIP_CUSTOM_HEADERS, out_message)

        if reply_buff:
            customHeadersObj = CustomHeadersObject(self,
                                                   reply_buff)
            if customHeadersObj:
                return customHeadersObj

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
        res = self._query_camelot(camelot.CREATE_TEMPLATE_MSG)
        try:
            if res:
                actionObj = InActionObject(self, res)
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
            self.unregister_event(event_type, inaction_obj.sub_type)
        return self._query_camelot(
            camelot.REMOVE_INACTION_OBJ, inaction_obj.msgid)

    def sip_message_detailed(self, call_ref=None, methods=['INVITE']):
        '''
        This is used for displaying received and sent SIP messages for a call.
        One can choose to display messages only for the methods of their
        choice.

        :parameter call_ref: call reference of the call.
                             If call_ref=None is set, then
                             displays OOD message of REFER, NOTIFY.
        :parameter methods: list of SIP method names.Default is ['INVITE'].
                            This list will restrict the output to only those
                            messages received with the matching methods.
                            If methods=None is set, then the messages related
                            to all methods will be displayed.

        :returns: A list of SIP Messages belonging the call and as chosen by
                  the methods list.Individual fields of the list of the
                  dictionaries are explained below:\n
                  * start_line: request or response line for the SIP Message
                  * headers: It is a dictionary of all the headers with their
                    name and value pairs
                  * body: Content body of the SIP message
                  * direction: Direction of the message. Possible values are
                    'send' and 'recv'

        :Note: configure sip.phone.outofdialogcapture as 1 for capturing
               outofdialogue NOTIFY or REFER (response/request).

        >>> ep1.sip_message_detailed(call_ref='0xf356f034',
        methods=['INVITE','BYE'])
        Content is not shown here because of space constraint
        >>> ep1.sip_message_detailed(call_ref='0xf356f034',methods=None)
        [0]['start_line']
        u'INVITE sip:430002@10.12.10.87:5060 SIP/2.0'

        For all OOD messages of supported
        >>> ep1.sip_message_detailed(methods=None)
        [0]['start_line']
        u'REFER sip:430002@10.12.10.87:5060 SIP/2.0'

        For only NOTIFY OOD messages
        >>> ep1.sip_message_detailed(methods=['NOTIFY'])
        u'NOTIFY sip:430002@10.12.10.87:5060 SIP/2.0'
        Other content is not shown here because of space constraint

        For more information and examples please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/Simplified+SIP+Message+handling#SimplifiedSIPMessagehandling-SipMessageDetailedAPI
        '''
        if call_ref:
            if not self._is_valid_call_ref(call_ref):
                log.error('call reference not valid')
                return
        else:
            call_ref = 'null'

        if not methods:
            methods = ['NONE']

        if not isinstance(methods, list):
            log.error('not a valid list for methods')

        out_message = camelot.SIP_MESSAGE_DETAILED

        methodlist = ",".join(methods)

        out_message = '{} {}^{}'.format(
            out_message, call_ref, methodlist)

        return self._query_camelot(
            camelot.SIP_MESSAGE_DETAILED, out_message)

    def get_tvs_info(self):
        '''Displays the information related to TVS Client

        :returns: If the -field argument is omitted, a variable sized list of
            field  value pairs is returned with all the details of TVSClient
            If the -field option is specified,only the value for the specified
            field is returned\n
            If a failure occurs returns the appropriate error string\n
            * "tvsmode" TVS Client mode set by the user for the config parm
            * "tvscache" Displays if the TVS Client local cache is
               enable/disable
            * "currentserver" Displays the IP address of TVS Server to be used
              for a TVS query
            * "tvsservers" Displays IP addresses of all the TVS Servers
               available in the cluster in the order of their priority
               When TVSClient is not active, the field 'tvsclientstatus'will
               display status as 'inactive'

        >>> get_tvs_info()
        {'currentserver': '10.12.10.5',
        'tvscache': 'enabled',
        'tvsclientstatus': 'ready',
        'tvsmode': 'trustlist',
        'tvsservers': {'server 1':'10.12.10.5','server 2':'','server 3':''}}

        For more information please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/gettvsinfo

        '''
        log.debug('Entering get_tvs_info function')
        return self._query_camelot(camelot.GET_TVS_INFO)

    def get_tvs_client_stats(self):
        '''Displays TVS Client statistics for the certificate verify
           requests received
           :returns: A variable size list of(field,value)pairs with all
                     statistics of TVS Client Certificate verify requests
                     If the -field option is specified, only the value
                     for the specified field is returned\n
            If a failure occurs, it returns the appropriate error string
            * "success" Total number of certificate verify requests succeeded\n
            * "failed" Total number of certificate requests failed\n
            * "found in trustlist" Number of verify requests for which
              certificate is found in trustlist\n
            * "found in cache" Number of verify requests for which certificate
              is found in local cache
            * "tvs server" Number of  verify requests for which TVS Server was
               contacted to verify certificate
            * "found" Certificates found on TVS Server
            * "notfound" Certificates not found on TVS Server

        >>> ep1.get_tvs_client_stats()
        {'found in cache': '0',
         'found in trustlist': '3',
         'success 3': 'failed 0',
         'tvs server': 'notfound 0'}

        For more information please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/gettvsclientstats

        '''
        log.debug('Entering get_tvs_clientstats function')
        return self._query_camelot(camelot.GET_TVS_CLIENTSTATS)

    def get_tvs_server_stats(self):
        '''Displays TVS Server statistics for the no of times the TVS Client
            interacted with primary,failover to secondary and failover to
            teritiary TVS Servers
           :returns: A variable size list of(field,value)pairs with all
                     statistics of TVS server
            If the -field option is specified, only the value for the specified
            field is returned
            If a failure occurs, it returns the appropriate error string
            * "successful connections primary" No of  times TVS Client setup
              the successful connections with Primary TVS Server
            * "failover to secondary" Number of times failover happened to
               secondary TVS Server
            * "failover to tertiary" Number of times failover happened to
              tertiary TVS Server

        >>> ep1.get_tvs_server_stats()
        {'failover to secondary': '0',
         'failover to tertiary': '0',
          'successful connections primary': '0'}

        For more information please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/gettvsserverstats

        '''
        log.debug('Entering get_tvs_serverstats function')
        return self._query_camelot(camelot.GET_TVS_SERVERSTATS)

    def display_tvs_cache(self):
        '''Displays the details of all the certificates present in TVS Client
           local cache
           :returns: A variable sized list of {field  value} pairs is returned
                     with each entry of the certificate in the local cache
           If a failure occurs returns the appropriate error string
           * "certlen" length of the certificate
           * "timetolive" time to live value for the given certificate in the
             cache

        >>> ep1.disp_tvs_cache()
        {'tvs local cache': ''}

        For more information please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/disptvscache

        '''
        log.debug('Entering disp_tvs_cache function')
        return self._query_camelot(camelot.DISP_TVS_CACHE)

    def reset_tvs_cache(self):
        '''Displays the details of all the certificates present in the
           endpoint local trust list
           :returns: A variable sized list of {field  value} pairs is returned
                     with each entry of the certificate in the trust list
            In case of failure returns appropriate error string
            * "subjectipaddress" Subject IP address for the certificate
            * "subjectfunction"  Subject function
            * "issuername"  Issuer details of the certificate
            * "certlen" Length of the Certificate

        For more information please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/resettvscache

        >>> ep1.reset_tvs_cache()
        {enabled}

        '''
        log.debug('Entering disp_tvs_trustlist function')
        return self._query_camelot(camelot.RESET_TVS_CACHE)

    def display_tvs_trust_list(self):
        '''Displays the details of all the certificates present in the
           endpoint local trust list
           :returns: A variable sized list of {field  value} pairs is returned
            with each entry of the certificate in the trust list
            In case of failure returns appropriate error string
            * "subjectipaddress" Subject IP address for the certificate
            * "subjectfunction"  Subject function
            * "issuername"  Issuer details of the certificate
            * "certlen" Length of the Certificate

        >>> ep1.display_tvs_trust_list()
        '{{trust list} {{cert:0 {subjectipaddress 10.12.10.5}
        {subjectfunction 0} {issuername CN=seeapl-ROOTDC1-CA}{certlen 1237} }',
        '{cert:1 {subjectipaddress 10.12.10.5} {subjectfunction 2}
        {issuername CN=seeapl-ROOTDC1-CA} {certlen 1237} }',

        For more information please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/disptvstrustlist

        '''
        log.debug('Entering disp_tvs_trustlist function')
        return self._query_camelot(camelot.DISP_TVS_TRUSTLIST)

    def get_info_transactions(self):
        '''
        Get information about transactions done during inservice.\n
        Note: Currently it supports only below mentioned fields.

        :returns: dictionary of dictionaries with the fields mentioned below:\n
                  * tftp_config - it is a dictionary containing tftp
                    transaction info:\n
                    currently it supports below mentioned fields only:\n
                    * device_config_file - it is a dictionary containing two
                      fileds:\n
                      * url - It contains the endpoint specific devie
                        configuration file name.
                      * status - It contains the status of received response.
                    * xmldefault - it is a dictionary containing 3 fileds:\n
                      * url - it contains the defautl device configuration file
                        name.
                      * status - it contains the status of received response.
                      * mode - it can be any of the two values either
                        onboarding or autoregistration.It will be empty if
                        parsing of the file failed or validation of
                        <activationDomainURL> fails.

        For more info please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/Activation+Code+Onboarding#ActivationCodeOnboarding-On-boarddiscovery


        >>> ep1.get_info_transactions()
            {u'tftp_config': {
            u'device_config_file': {u'status': u'404 Not Found',
            u'url': u'EP886588650003.cnf.xml'},
            u'xmldefault': {u'mode': u'onboarding',
            u'status': u'200 OK',
            u'url': u'XMLDefault.cnf.xml'}}}
        '''
        return self._query_camelot(camelot.GET_INFO_TRANSACTION)

    def get_onboarding(self):
        '''
        Displays various information on on-boarding process.

        :returns: dictionary of dictionaries with the fields mentioned below:\n
                  * activation_url - absolute URI of activation URL
                  * atls- information about GDS operation over ATLS\n
                    with following fields:\n
                    * abs_path - URI of last sent message over ATLS
                    * state -shows the current state of ATLS operations
                      with GDS
                    * response - response details of ATLS GDS redirection
                      request with following fields:\n
                      * body - if ATLS redirect request gets successful
                        response and camelot has successfully parsed body
                        it will contain three fields:\n
                        * serviceDomain - DNS server records for MRA cluster
                        * callControl - It identifies the deployment if value
                          is CUCM means it is a CUCM/MRA registration and
                          proceeds for MRA onboarding.
                        * state - This represents the clusterUUID.
                      * code - http response code for GDS redirection request
                      * phrase - reason_phrase of the response
                      * warning - warning header if any
                      * reason - reason header if any
                  * camelot_reason - application error, connection down\n
                    events tcp Connection error/TLS negotiation failure etc.
                  * gds - information about gds servers with following\n
                    fields:\n
                    * host -host name of gds server
                    * error -
                    * servers - list of dictionaries for each gds server\n
                      with following fields:\n
                      * address - IP address of gds server
                      * state  - state information
                      * error  - error info
                  * service_data -
                  * srp_invoke - information about srp_invoke operation\n
                    with following fields:\n
                    * abs_path - absolute path of srp invoke URL
                    * response - response details of srp invoke request with
                      following fields:\n
                      * code - http response code for srp invoke request
                      * phrase - reason_phrase of the response
                      * reason - reason header if any
                      * warning - warning header if any
                  * srp_register - information about srp_register operation\n
                    with following fields:\n
                    * abs_path - absolute path of srp register URL
                    * response - response details of srp register request with
                      following fields:\n
                      * code - http response code for srp register request
                      * phrase - reason_phrase of the response
                      * reason - reason header if any
                      * warning - warning header if any
                  * state - operation state of srp_invoke and srp_register.\n
                  * tokens - string values of true or false for valid or
                    invalid\n
                  * valid_hmac - string value of true or false to indicate\n
                    if its valid or invalid\n
                  * autoreg_status - it indicates the current mode or status\n
                    with respect to auto registration. For possible values\n
                    and their meaning , please refer to following wiki link:\n
                    https://wiki.cisco.com/display/CAMELOT/Activation+Code+Onboarding#ActivationCodeOnboarding-autoreg_statusfield


        For more info please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/Activation+Code+Onboarding#ActivationCodeOnboarding-get_onboardingAPI

        >>> Sample Example for On-prem
        >>>
           ep1.get_onboarding()
            {u'activation_url': u'https://cam-ccm-9.camelot.test:8443/ccmact',
             u'camelot_reason': u'',
             u'gds': {u'host': u'',
              u'servers': [{u'address': u'', u'error': u'', u'state': u''}]},
             u'service_data': u'',
             u'atls': u'',
             u'srp_invoke': {u'abs_path': u'/ccmact/v1/actions/srp/invoke',
              u'response': {u'code': u'401',
               u'phrase': u'Unauthorized',
               u'reason': u'',
               u'warning': u''}},
             u'srp_register': {u'abs_path': u'/ccmact/v1/actions/srp/register',
              u'response': {u'code': u'200',
               u'phrase': u'OK',
               u'reason': u'',
               u'warning': u''}},
             u'state': u'ONBOARDED',
             u'tokens': u'true',
             u'autoreg_status': u'onboarding',
             u'valid_hmac': u'true'}

        >>> Sample Example for MRA
        >>> ep1.get_onboarding()
            {u'activation_url': u'',
             u'atls':{
              u'abs_path': u'/api/v2/atls/redirect',
              u'state': u'SUCCESS_RESPONSE_OVER_ATLS_RECEIVED',
              u'response': {u'body': {u'callControl': u'CUCM',
                  u'serviceDomain': u'camelot.test',
                  u'state': u'7b644b72-0d92-4f0e-b010-ffdbcdb52d4d'},
               u'code': u'200',
               u'phrase': u'OK',
               u'reason': u'',
               u'warning': u''}},
             u'camelot_reason': u'',
             u'gds': {u'error': u'',
             u'host': u'activation.webex.com',
             u'servers': [{u'address': u'35.172.26.181', u'error': u'',
             u'state': u''},
             {u'address': u'34.237.14.82', u'error': u'',
             u'state': u''}]},
             u'service_data': u'',
             u'srp_invoke': {u'abs_path': u'',
              u'response': {u'code': u'',
               u'phrase': u'',
               u'reason': u'',
               u'warning': u''}},
             u'srp_register': {u'abs_path': u'',
              u'response': {u'code': u'',
               u'phrase': u'',
               u'reason': u'',
               u'warning': u''}},
             u'state': u'ATLS_REDIRECT_SUCCESS',
             u'tokens': u'false',
             u'autoreg_status': u'',
             u'valid_hmac': u'false'}

        '''
        return self._query_camelot(camelot.GET_ONBOARDING)

    def cm(self, cm_ref, operation):
        '''
        The down operation is used to break the socket between the endpoint
        and specified CM and thereby kick off failover. It also changes the
        virtual state of the CM in endpoint to down and prohibits it from
        further consideration for failback operation.  The up operation changes
        the virtual state of CM in endpoint to up and it is considered for
        failback.

        :parameter cm_ref: specifies the cm on which the operation will be
         performed. Valid range is 0 ..(number of CMs configured - 1)
        :parameter operation: specifies which operation to perform.
         Valid values are 'up' and 'down'.

        :returns: returns boolean when action is accepted, else
         :py:meth:`camelot.CamelotError`

        >>> ep1.cm(2, 'down')
        >>> True

        >>> ep1.cm(2, 'up')
        -----------------------------------------------------------------------
        CamelotError                          Traceback (most recent call last)
        CamelotError: can't initiate operation on cm: invalid argument
        '''

        if not isinstance(cm_ref, int):
            raise camelot.CamelotError(
                'invalid cm reference - invalid integer')

        if cm_ref < 0:
            raise camelot.CamelotError('invalid cm reference - less than zero')

        operation = operation.lower()
        if operation not in ['up', 'down']:
            raise camelot.CamelotError(
                'invalid operation not in "up" and "down"')

        if operation == 'up':
            op = '1'
        else:
            op = '2'

        return self._query_camelot(camelot.CM, cm_ref, op)

    def cmstats(self):
        '''
        Returns CM failover and failback statistics for the specified endpoint.

        :returns: A dictionary of {field  value} pairs and list of significant
         registration event timestamps are returned\n
         * failover primary: number of failovers from primary to backup
         * failover backup: number of failovers from backup to next available
           CM
         * failback primary: number of failbacks from primary to next CCM
           of higher precedence
         * failback backup: number of failbacks from backup to next CCM
           of higher precedence
         * timestamps: a list of dictionaries covering following params:

           * registration_event: The registration event recorded. Can have
             one of the following values:

             * registration ok
             * registration error
             * failover
             * fallback
             * keepalive error
           * ip_addr: The CM IP address.
           * date: Recorded event date - MM/DD/YYYY
           * time: Recorded event time - HH:MM:SS:MMM


        >>> ep1.cmstats()
        >>>
        {'failback backup': '0',
         'failback primary': '0',
         'failover backup': '0',
         'failover primary': '0',
         'timestamps': [{'date': '05/18/2020',
            'ip_addr': '10.12.10.87',
            'registration_event': 'registration ok',
            'time': '15:43:40:938'}]}

        >>> ep2.cmstats()
        >>>
        {'failback backup': '0',
         'failback primary': '0',
         'failover backup': '0',
         'failover primary': '0',
         'timestamps': []}

        >>> ep1.cmstats()
        >>>
        {'failback backup': '0',
         'failback primary': '0',
         'failover backup': '0',
         'failover primary': '0',
         'timestamps': [{'date': '05/18/2020',
             'ip_addr': '10.12.10.87',
            'registration_event': 'registration ok',
            'time': '15:50:19:655'},
           {'date': '05/18/2020',
            'ip_addr': '10.12.10.87',
            'registration_event': 'registration ok',
            'time': '15:50:09:441'},
           {'date': '05/18/2020',
            'ip_addr': '10.12.10.87',
            'registration_event': 'registration ok',
            'time': '15:49:59:249'}]}
        '''

        return self._query_camelot(camelot.CMSTATS)

    def get_oauth_info(self):
        '''
        Get detailed informations about the access token information.

        :returns: dictionary of informations.\n
                  * request - request info\n
                    * url - url of the request
                    * host - node to which request is sent
                    * remote_port - port of host at which request is received
                    * sent_time - time,  in UTC format, when request is sent
                  * response - response info\n
                    * code - http response code
                    * phrase - http response "reason phrase"
                    * warning - http warning header if any
                    * received_time - time,  in UTC format, when request is
                      received
                  * last_successful_refresh_timestamp - time of the
                    successfully received access token in UTC format
                  * time_to_refresh_access_token - time when next refresh
                    request will be sent in UTC format
                  * camelot_reason - Error information in case of connection
                    error or some other Camelot internal errors
                  * oauth_mode - Camelot has 3 modes for oauth\n
                    * sso - If access token is generated because SSO is\n
                      enabled "success"\n
                    * zero_touch_onboarding - If access token is generated\n
                      because oauth for TFTP is enabled\n
                    * activation_based_onboarding - If access token is\n
                      generated because activation code based onboarding is\n
                      enabled\n


        For more info please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/Activation+Code+Onboarding\n
        https://wiki.cisco.com/display/CAMELOT/OAuth+for+TFTP\n
        https://wiki.cisco.com/display/CAMELOT/SSO+-+Single+Sign+On\n

        >>> ep1.get_oauth_info()
        {
        'request': {
        'url': '/Y2FtZWxvdC50ZXN0/access_token',
        'host': '10.12.10.153',
        'remote_port': '8443',
        'sent_time': '2021-02-04T18:41:50.166',
        },
        'response': {
        'code': '',
        'phrase': '',
        'warning': '',
        'received_time': '',
        },
        'last_successful_refresh_timestamp': '2021-02-04T18:41:30.160',
        'time_to_refresh_access_token': '',
        'camelot_reason': 'TCP Connect Timeout:(11)',
        'oauth_mode': 'sso',
        }

        >>> ep1.get_oauth_info()
        {
        'request': {
        'url': '/Y2FtZWxvdC50ZXN0/access_token',
        'host': '10.12.10.152',
        'remote_port': '8443',
        'sent_time': '2021-02-04T18:47:30.889',
        },
        'response': {
        'code': '200',
        'phrase': 'OK',
        'warning': '',
        'received_time': '2021-02-04T18:47:31.275',
        },
        'last_successful_refresh_timestamp': '2021-02-04T18:47:31.276',
        'time_to_refresh_access_token': '2021-02-04T18:47:41.276',
        'camelot_reason': '',
        'oauth_mode': 'sso',
        }
        '''

        return self._query_camelot(camelot.GET_OAUTH_INFO)

    def get_conference_info(self):
        '''
        Displays the detailed information about the conference participants
        and complete information of the conference user capabilities.
        This API displays the body retrieved from the INFO sip message received
        after conference INFO package negotiation successfuly completed 
        between the camelot endpoints and cucm.
        If called before conference INFO package negotiation it will 
        return empty List.

        :returns: Dictionary contains List of dictonaries depicting
                  information like participants involved,security
                  information, user capabilities of the conference.
        Please refer to following wiki:\n
        https://wiki.cisco.com/display/CAMELOT/Remove+Conference+Participant#RemoveConferenceParticipant-ConferenceINFOpackagesupport

        >>> ep2.get_conference_info()
        Out[92]: 
        {
          'conference-info': {
          'xmlns': 'urn:ietf:params:xml:ns:conference-info',
          'xmlns:ce': 'urn:cisco:params:xml:ns:conference-info',
          'entity': 'Voice-Conference',
          'state': 'full',
          'version': 1,
          'conference-description': {
          'display-text': ' Cisco CallManager hosted Conference ',
          'maximum-user-count': 4,
        },
        'conference-state': {
        'user-count': 3,
        'locked': False,
        },
        'users': {
        'user': [{
        'entity': 'sip:2400012@10.12.10.99;ci=24476360',
        'state': 'full',
        'display-text': None,
        'endpoint': {
        'entity': 'sip:2400012@10.12.10.99;ci=24476360',
        'state': 'full',
        'display-text': None,
        'status': 'connected',
        'joining-info': {
        'by': None,
        },
        'call-info': {
        'sip': {
        'call-id': 24476360,
        },
        'ce:security': 'NotAuthenticated',
        },
        'ce:self': {
        'ce:user-capabilities': {
        'ce:remove-participant': None,
        },
        },
        'ce:host': None,
        },
        }, {
        'entity': 'sip:2400014@10.12.10.99;ci=24476364',
        'state': 'full',
        'display-text': None,
        'endpoint': {
        'entity': 'sip:2400014@10.12.10.99;ci=24476364',
        'state': 'full',
        'display-text': None,
        'status': 'connected',
        'call-info': {
        'sip': {
        'call-id': 24476364,
        },
        'ce:security': 'NotAuthenticated',
        },
        },
        }, {
        'entity': 'sip:2400013@10.12.10.99;ci=24476361',
        'state': 'full',
        'display-text': None,
        'endpoint': {
        'entity': 'sip:2400013@10.12.10.99;ci=24476361',
        'state': 'full',
        'display-text': None,
        'status': 'connected',
        'call-info': {
        'sip': {
        'call-id': 24476361,
        },
        'ce:security': 'NotAuthenticated',
        },
        },
        }],
        },
        },
        }

        '''
        return self._query_camelot(camelot.GET_CONFERENCE_INFO)

    def remove_conference_participant(self, callref, user_info={}):
        '''
        Removes the given participant from the conference\n
        :parameter call_ref: The call reference
        :parameter user_info:  
         This user_info dictionary will have 'type' and 'value' keys in it.
         Below are the possible values of 'type' key are: \n
         * 'dn'   - for directory number as a value.
         * 'uri' - for sip uri as a value.
        :returns: True: Camelot could successfully triggered the
         operation. For a successful removal of participant from
         conference user can check by calling API get_conference_info()
         after receiving station event which have updated participant
         list in the conference.\n
         Exception:\n
         when 'remove-participant' capability not present for the
         for the endpoint \n
         when 'x-cisco-conferance' package is not supported
         for conference \n
         when invalid DN or Sip Uri is given as input to the API
        For any missing/invalid arguments, exception will be thrown and can
        be referred camelot logs for more information.\n
        Please refer to following wiki:\n
        https://wiki.cisco.com/display/CAMELOT/Remove+Conference+Participant#RemoveConferenceParticipant-RemoveconferenceparticipantAPI

        >>> input to API
        mydict = {'type':'dn', 'value':'1100002'}
        OR
        mydict = {'type':'uri', 'value':'sip:1100002@cam-ccm-99.camelot.test'}
        >>> ep1.remove_conference_participant(callref,user_info=mydict)
        'True'
        >>> when conference/x-cisco-conference package is not negotiated
        >>> ep1.remove_conference_participant(callref,user_info=mydict)
        Exception:'conference/x-cisco-conference package is not 
                   negotiated for conference'
        >>> when remove-participant capability not present for endpoint
        >>> ep1.remove_conference_participant(callref,user_info=mydict)
        Exception:'remove-participant capability not present for this user'
        >>> Inavalid dn or sip uri given as input
        >>> ep1.remove_conference_participant(callref,user_info=mydict)
        Exception:'Invalid Conference particiapant'
        '''
        if not callref:
            raise camelot.CamelotError(
                'callreference not present')
        if not user_info or not isinstance(user_info, dict):
            raise camelot.CamelotError(
                'Pass {parameter: value} dictionary for configuring endpoint')
        if (len(user_info)):
            user_type = user_info.get('type', None)
            user_value = user_info.get('value', None)
            key_list = ['dn', 'uri']
            if not user_type:
                raise Exception('not valid key given as input')
            if not user_value:
                raise Exception('not valid value given as input')
            if user_type not in key_list:
                raise Exception('invalid type for cucm info dict')
            return self._query_camelot(camelot.REMOVE_CONF_PARTICIPANT,
                                       callref, **user_info)
        return self._query_camelot(camelot.REMOVE_CONF_PARTICIPANT)

