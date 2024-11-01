import camelot
import sys
import string
import enum
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger
from camelot import AgentStatusEnum

log = camlogger.getLogger(__name__)


class CamelotHeadsetOperation(v.CamelotVapiUtils):

    '''Camelot Headset operations'''

    def __init__(self):
        pass

    def get_headset(self):
        '''Display all headset URL attributes, detailed download status
        info from each URL along with headset connectivity status.

        :returns: A json formatted string with following fields:\n

         * backoff: remaining realtime value of backofftimer in seconds
         * state: download state. Possible values are idle,timer_wait,
               initiated, request_sent, retry_timer_wait ,retry_initiated,\n
               retry_request_sent  and complete.
         * response: following fields about the response received while
               sending download request\n
               * code: response code received . For example 200 ,404 etc
               * phrase: response phrase , for example OK (for 200)
               * reason: reason phrase if available (not available yet)
               * warning: warning text if available (not available yet)
         * Firmware Info of Headset:
               * version: firmware version
               * camelot_reason: reasons/error while parsing for Firmware info
                 like modelseries not found.
         * Info of Headset URL listed as a set of below:
               * protocol: URL type(http/https/tftp)
               * host: host IP where the request to be sent
               * port: host port
               * url: path
         * status : headset connectivity status
               * "": Not implemnted yet

        >>> ep.get_headset()
        {u'configURL': {u'backoff': u'0',
        u'camelot_reason': u'',
        u'host': u'10.12.10.9',
        u'port': u'6970',
        u'protocol': u'http',
        u'response': {
        u'code': u'200',
        u'phrase': u'OK',
        u'reason': u'',
        u'warning': u''},
        u'state': u'complete',
        u'url': u'/headset/config/user/',
        u'version': u''},
        u'firmware': {u'backoff': u'0',
        u'camelot_reason': u'',
        u'host': u'10.12.10.9',
        u'port': u'6970',
        u'protocol': u'http',
        u'response': {u'code': u'404',
        u'phrase': u'Not Found',
        u'reason': u'',
        u'warning': u''},
        u'state': u'complete',
        u'url': u'/1-0-2PA-84.bin',
        u'version': u'1-0-200-84'},
        u'inventoryPostURL': {u'backoff': u'0',
        u'camelot_reason': u'',
        u'host': u'10.12.10.9',
        u'port': u'9444',
        u'protocol': u'https',
        u'response': {u'code': u'',
        u'phrase': u'',
        u'reason': u'',u'warning': u''},
        u'state': u'idle',
        u'url': u'/headset/inventory',
        u'version': u''},
        u'discoveryURL': {u'backoff': u'0',
        u'camelot_reason': u'',
        u'host': u'10.12.10.9',
        u'port': u'9444',
        u'protocol': u'https',
        u'response': {u'code': u'',
        u'phrase': u'',
        u'reason': u'',u'warning': u''},
        u'state': u'idle',
        u'url': u'/headset?device=SEP886588650001',
        u'version': u''},
        u'serviceInfoURL': {u'backoff': u'0',
        u'camelot_reason': u'',
        u'host': u'10.12.10.9',
        u'port': u'9444',
        u'protocol': u'https',
        u'response': {u'code': u'',
        u'phrase': u'',
        u'reason': u'',
        u'warning': u''},
        u'state': u'idle',
        u'url': u'/metrics/serviceinfo',
        u'version': u''},u'status': u''}
        '''
        return self._query_camelot(camelot.GET_HEADSET)

    def get_headset_services(self):
        '''Display details of all headset services (currently onboarding
        and cc services only) with different fields as explained below.

        :returns: A json formatted string with list of servies:\n

         * service_name: Name of the headset service.('onboarding' or 'cc')
         * status: whether the service is disabled or enabled.
         * state: State of the service.Please note, for CC service this
           field's name will be "agent_state". For knowing more details\n
           on the state values and their significance please refer to
           wiki page as mentioned below.
         * http_messages: A list of dictionaries detailing about the http
           messages exchanged the headset service. Each dictionary\n
           item has info on a single http message via following fields:\n
           * backoff: Value of remaining backoff time if applicable.
           * camelot_reason: Error information if any.
           * host: Destination Host IP for the http message.
           * protocol: Protocol used to send http message
           * port: Port number of the destination host
           * state: Headset state(For cc) or onboarding state (For
             onboarding) for the message. Possible values for
             headset onboarding are\n
             * headsetstatus connected
             * headsetstatus disconnected
             * headsetonboarding success
             * headsetonboarding failure
             * headsetdisconnect success
             * headsetdisconnect failure
           * url: URL of the http message
           * version: Version value of http message if any
           * response: It is a dictionary having fields detailing
             the response of the message with following fields:\n
             * code: Status code of the http response
             * phrase: Status phrase of the http response
             * reason: Value of the reason header if any
             * warning: Value of the warning header if any
           * extension_mobility: It is a dictionary having fields detailing
             the extension mobility (EM) service which is invoked after a\n
             successful onboarding operation.These fields and values are also
             present in an other API called 'get_service_info'.\n
             Note: This field is visible only for onboarding service
             It has the following fields:\n
             * state: State of EM service
             * error: Error message if any
             * start: Start time of EM action
             * end: End time of EM action
             * action: Action performed on EM
             For more info please refer to camelot wiki page:\n
             https://wiki.cisco.com/display/CAMELOT/Headset+feature+support+in+Camelot#HeadsetfeaturesupportinCamelot-get_headset_services()API.

        >>> ep.get_headset_services)
        [{
        'service_name': 'onboarding',
        'status': 'enabled',
        'state': 'onboarded',
        'extension_mobility': {
        'state': 'completed',
        'error': '',
        'start': '2020-02-19T21:41:10.645-05:30',
        'end': '2020-02-19T21:41:10.645-05:30',
        'action': 'sign-in',
        },
        'http_messages': [{
        'backoff': '0',
        'camelot_reason': '',
        'host': 'cam-ccm-32.camelot.test',
        'port': '9444',
        'protocol': 'https',
        'state': 'complete',
        'url': '/headset/onboarding/v1/onboard/GTK221612CDB/'
        'SEP886188610002/headsetconnect',
        'version': '',
        'response': {
        'code': '200',
        'phrase': 'OK',
        'reason': '',
        'warning': '',
        },
        }, {
        'backoff': '0',
        'camelot_reason': '',
        'host': 'cam-ccm-32.camelot.test',
        'port': '9444',
        'protocol': 'https',
        'state': 'complete',
        'url': 'https://cam-ccm-32.camelot.test:9444/headset/onboarding/'
        'v1/onboard/GTK221612CDB/SEP886188610002/headsetconnectreq',
        'version': '',
        'response': {
        'code': '200',
        'phrase': 'OK',
        'reason': '',
        'warning': '',
        },
        }],
        },
        {
        'service_name': 'cc',
        'status': 'enabled',
        'agent_state': 'login',
        'http_messages': [{
        'backoff': '0',
        'camelot_reason': '',
        'host': 'cam-ccm-32.camelot.test',
        'port': '6970',
        'protocol': 'https',
        'state': 'complete',
        'version': '',
        'response': {
        'url': '/headset/cc/v1/event'
        'code': '200',
        'phrase': 'OK',
        'reason': '',
        'warning': '',
        }]
        }]
        '''
        return self._query_camelot(camelot.GET_HEADSET_SERVICES)

    def change_headset_status(self, status='disconnected'):
        '''Changes headset status to connected or disconnected.
        On successful status change causes headset inventory POST request
        to be sent.\n Use http_response() to see the
        detailed results of the request itself.\n Use get_headset()['status']
        for current status of the headset.\n
        For more info Camelot Wiki:
            https://wiki.cisco.com/display/CAMELOT/Headset+integration+with+contact+centre#Headsetintegrationwithcontactcentre-change_headset_status()APIforconnectinganddisconnectingheadset

        :parameter status: value should be 'connected' or 'disconnected'

        :returns:
         * True if camelot has changed the status of headset.
            does not depend on the success or failure of the POST request.
         * False if the status change requested is the same as the current
            status. Nothing is done

        >>> ep.change_headset_status(status='connected')
        True

        >>> ep.get_headset()['status']
        'connected'
        '''
        if status not in ['connected', 'disconnected']:
            raise Exception('invalid status value')

        log.debug('Entering into setup_headset_Status function')
        return self._query_camelot(camelot.CHANGE_HEADSET_STATUS, status)

    def change_headset_cc_agent_state(self, agent_status, event=None):
        '''
        The Camelot headset users can use newly introduced API
        change_headset_cc_agent_state() to change the CC agent state
        from current state to provided new state.
        This API will only work provided the headset is connected and
        cc service is enabled.

        :parameter:
         * agent_status Mandatory parameter.\n
           agent_status is of type string.
           Any one of the supported values should be provided as input
           else it will return "Attribute Error"
           Supported Values for the agent_Status will be in below link:
           http://10.106.248.246:8080/job/CAMELOT_PI_SDK_DEV/API_Doc/api/camelot.html?highlight=enum#camelot.AgentStatusEnum
         * event Optional parameter.
           event is of type dictionary with key and value pairs.
           If provided will be sent in agentstate
           request URL body
        :returns:
         * True   if camelot has sent the headset cc Agent state Request URL.
         * False  Agent state is same so Camelot has not sent the cc Agent
           State Request URL (Non Fatal Errors)\n
         * Error   Exception with appropriate error string and headset cc agent
           state URL not sent(Fatal Errors)
           For any Errors occured before sending Agent State URL
        >>> ep.change_headset_status('connected')
        True
        >>> from camelot import AgentStatusEnum
        >>> state = AgentStatusEnum.READY
        >>> event = {'state':'Karnataka',"encoding" : "Integer"}
        >>> ep1.change_headset_cc_agent_state(state, event)
        True

        * Unsupported Agent Status Attribute
        >>> ep.change_headset_status('connected')
        True
        >>> state = AgentStatusEnum.BUSY
        >>> ep1.change_headset_cc_agent_state(state)
        AttributeError: BUSY

        * Trying to change agent state to ready, when headset is not connected
        >>> ep.change_headset_status('disconnected')
        False
        >>> state = AgentStatusEnum.READY
        >>> event = {'state':'Karnataka',"encoding" : "Integer"}
        >>> ep1.change_headset_cc_agent_state(state,event)
        Exception: headset device status disconnected

        * Trying to change agent state to READY, when state is already\n
        in ready state

        >>> ep.change_headset_status('connected')
        True
        >>> state = AgentStatusEnum.READY
        >>> event = {'state':'Karnataka',"encoding" : "Integer"}
        >>> ep1.change_headset_cc_agent_state(state,event)
        False
        '''
        log.debug('Entering change_headset_cc_agent_state function')
        request = ''

        if not isinstance(agent_status, AgentStatusEnum):
            raise Exception('invalid agentstatus value')

        request = '{} {}'.format(request, agent_status.value)
        if event is None:
            request = '{} ^{}'.format(request, 'NULL')
        else:
            request = '{} ^{}'.format(request, event)

        log.debug("change_headset_cc_agent_state arguments{}".format(request))
        return self._query_camelot(
            camelot.HEADSET_CC_AGENTSTATE, request)

    def get_headset_cc_agent_state(self):
        '''Shows the current state of headset agent received from
        CUCM as part of <agentstatusupdate> of SIP REFER message.
        Usally phone receives this REFER on any change in agent status
        at headset by sending HTTP POST /event towards Contact Center.
        However in Camelot the change agent state will be informed using
        an api change_headset_cc_state()
        For more info Camelot Wiki:
            https://wiki.cisco.com/display/CAMELOT/Headset+integration+with+contact+centre

        :returns: A json formatted string with following fields:\n

         * status: agent status received in <agentstatusupdate>
                   Camelot demoulated state like  NOT_READY/ACTIVE etc.,
         * reasoncode: reasoncode received in <agentstatusupdate>
         * request_time: HTTP message sent time stamp.
         * request_status: HTTP response received status
               * status_change_pending: Response not received yet
               * success: 200 OK response received
               * fail: response failed, check http_response() for the given URL
         * refer_time: REFER received time stamp.
         * camelot_reason: any reason from Camelot while parsing REFER

        >>> ep.get_headset_cc_agent_state()
        {'status': 'LOGIN',
        'reasoncode': '0',
        'request_time': 'YYYY-MM-DDTHH:MM:SS',
        'request_status': 'success',
        'refer_time': 'YYYY-MM-DDTHH:MM:SS',
        'camelot_reason': ''
        }
        '''
        return self._query_camelot(camelot.GET_HEADSET_CC_AGENTSTATE)
