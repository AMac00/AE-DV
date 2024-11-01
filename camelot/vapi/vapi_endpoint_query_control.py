import camelot
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger
import socket

log = camlogger.getLogger(__name__)


class CamelotEndpointControl(v.CamelotVapiUtils):

    '''CamelotVapiUtils representation
    '''

    def __init__(self):
        pass

    def DnD(self, call_ref=None):
        '''Sends StationSoftKeyEventMessage to CCM to activate or deactivate
        DnD softkey when pressed in idle state.

        When pressed during incoming state, sends a StationSoftKeyEventMessage
        to CCM to STOP RINGING.

        :parameter call_ref: call reference of incoming call, fetch call
                         reference :py:meth:`CamelotTCPFront.get_calls`

        :returns: True upon success

        >>> ep1.dial(ep2)
        <Call <Device RT 10.20.1.72> <-> <Device TNP 10.20.1.81>>
        >>> ep2.DnD(ep2.get_calls()[0]['Ref'])
        True
        '''

        log.debug('Entering function DnD')

        if call_ref and not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return

        return self._binary_to_boolean(
            self._query_camelot(camelot.DND, call_ref))

    def get_sip_call_features(self):
        '''returns all the current values of the sipCallFeatures
        block (or its defaults) as a dictionary.
        sip.phone.sip_call_features parms can be modified using
        config command. (config command has higher priority than
        parsing from the configuration file)

        :returns: following fields-\n
            * cnf_join_enabled - the value extracted from
              sip.phone.sip_call_features.cnf_join_enabled. This is
              of type integer. Possible values 1 or 0. Default value
              is 1.
            * call_forward_uri - value extracted from
              sip.phone.sip_call_features.call_forward_uri.
              This is of type string. Default value is None.
            * call_pickup_uri - value extracted from
              sip.phone.sip_call_features.call_pickup_uri.
              This is of type string. Default value is None.
            * call_pickup_list_uri - value extracted from
              sip.phone.sip_call_features.call_pickup_list_uri.
              This is of type string. Default value is None.
            * call_pickup_group_uri - value extracted from
              sip.phone.sip_call_features.call_pickup_group_uri.
              This is of type string. Default value is None.
            * meetme_service_uri - value extracted from
              sip.phone.sip_call_features.meetme_service_uri.
              This is of type string. Default value is None.
            * abbreviated_dial_uri - value extracted from
              sip.phone.sip_call_features.abbreviated_dial_uri.
              This is of type string. Default value is None.
            * rfc2543hold - value extracted from
              sip.phone.sip_call_features.rfc2543hold. This is
              of type integer. Possible values 1 or 0. Default
              value is 0.
            * call_hold_ringback - value extracted from
              sip.phone.sip_call_features.call_hold_ringback.
              This is of type integer. Default value is 255.
            * uri_dialing_display_preference - value extracted from
              sip.phone.sip_call_features.uri_dialing_display
              preference. valid values are 0(URI) and 1(DN).
              This is of type integer. Default value is 255.
            * local_cfwd_enable - value extracted from
              sip.phone.sip_call_features.local_cfwd_enable.
              valid values are 0 and 1. This is of type integer.
              Default value is 1.
            * semi_attended_transfer - value extracted from
              sip.phone.sip_call_features.semi_attended_transfer.
              valid values are 0 and 1. This is of type integer.
              Default value is 1.
            * anonymous_call_block - value extracted from
              sip.phone.sip_call_features.anonymous_call_block.
              This is of type integer. Default value is 255.
            * callerid_blocking - value extracted from
              sip.phone.sip_call_features.callerid_blocking.
              This is of type integer. Default value is 255.
            * dnd_control - value extracted from
              sip.phone.sip_call_features.dnd_control.
              This is of type integer. Default value is 255.
            * remotecc_enable - value extracted from
              sip.phone.sip_call_features.remotecc_enable.
              valid values are 0 and 1. This is of type integer.
              Default value is 1.
            * retain_forward_information - value extracted from
              sip.phone.sip_call_features.retain_forward_information.
              valid values are 0 and 1. This is of type integer.
              Default value is 1.

        >>> ep1.vapi.get_sip_call_features()
        {
         'cnf_join_enabled': 1,
         'call_forward_uri': 'x-cisco-serviceuri-cfwdall',
         'call_pickup_uri': 'x-cisco-serviceuri-pickup',
         'call_pickup_list_uri': 'x-cisco-serviceuri-opickup',
         'call_pickup_group_uri': 'x-cisco-serviceuri-gpickup',
         'meetme_service_uri': 'x-cisco-serviceuri-meetme',
         'abbreviated_dial_uri': 'x-cisco-serviceuri-abbrdial',
         'rfc2543hold': 0,
         'call_hold_ringback': 2,
         'uri_dialing_display_preference': 1,
         'local_cfwd_enable': 1,
         'semi_attended_transfer': 1,
         'anonymous_call_block': 2,
         'callerid_blocking': 2,
         'dnd_control': 0,
         'remotecc_enable': 1,
         'retain_forward_information': 0,
        }
        >>> ep1.vapi.get_sip_call_features()
        {
         'cnf_join_enabled': 1,
         'call_forward_uri': None,
         'call_pickup_uri': None,
         'call_pickup_list_uri': None,
         'call_pickup_group_uri': None,
         'meetme_service_uri': None,
         'abbreviated_dial_uri': None,
         'rfc2543hold': 0,
         'call_hold_ringback': 255,
         'uri_dialing_display_preference': 255,
         'local_cfwd_enable': 1,
         'semi_attended_transfer': 1,
         'anonymous_call_block': 255,
         'callerid_blocking': 255,
         'dnd_control': 255,
         'remotecc_enable': 1,
         'retain_forward_information': 1,
        }
        '''
        log.debug('Entering method get_sip_call_features().')
        ret_val = self._query_camelot(camelot.GET_SIP_CALL_FEATURES)
        return self._binary_to_boolean(ret_val)

    def blf_call_park(self, call_ref=None):
        '''Allows directed call parking using blf
        BLF directed call park allows user to park a call on a preconfigured
        park number which can exist on a set of phone.To retrieve a parked call
        user need to dial confiured retrieval prefix followed by the park
        number The call_reference parameter is used to perform call parking.
        If none is given as callrefrence it will allow retreiving existing
        parked call if any otherwise if no call is parked it will throw error

        :parameter call_ref: call reference

        :returns: True if successful else False

        >>> ep1.blfcallpark(ep2.get_number(ep1 callref))
        True
        >>> ep1.blfcallpark(ep2.get_number())
        True
        '''
        log.debug('Entering method blf_call_park().')
        ret_val = self._query_camelot(camelot.BLFCALLPARK, call_ref)
        return self._binary_to_boolean(ret_val)

    def get_rtcp_stream_info(self, stream_ref):
        '''Get RTCP information on a media stream.

        :parameter stream_ref: stream reference

        :returns: A variable sized list of dictionary with {field  value}
         pairs containing extended information about the stream.

         The current fields supported:\n
         * rtcpaddress - ip:port of receive end if inbound RTCP stream, or
           address to send to if outbound RTCP stream.
         * cname - Canonical endpoint identifier. CNAME will be same for a set
           of related RTP sessions i.e audio & video streams of the same call(
           outbound streams only).
         * last report time - time stamp, hh:mm:ss:mmm of last RTCP report(for
           inbound stream shows timestamp of last report received, for
           outbound stream shows timestamp of last report sent)
         * compound reports sent - Number of  RTCP messages sent since call
           connected (outbound streams only). A single RTCP message can carry
           multiple RTCP reports like RR, SR, SDES, APP, BYE etc.
         * receiver reports sent - Number of receiver reports sent since call
           connected (outbound streams only). Refer RFC 3550 for details on
           RTCP receiver report (RR).
         * sender reports sent - Number of sender reports sent since call
           connected (outbound streams only). Refer RFC 3550 for details on
           RTCP sender report (SR).
         * sdes reports sent - Number of source description reports sent since
           call connected (outbound streams only). Refer RFC 3550 for details
           on RTCP source description report (SDES).
         * app reports sent - Number of application-defined reports sent since
           call connected (outbound streams only). Refer RFC 3550 for details
           on Application-defined RTCP report (APP). Applicable only for
           Telepresence endpoints.
         * compound reports received - Number of  RTCP messages received since
           call connected (inbound streams only). A single RTCP message can
           carry multiple RTCP reports like RR, SR, SDES, APP, BYE etc.
         * error reports received - Number of  malformed RTCP messages received
           and dropped since call connected (inbound streams only).
         * receiver reports received - Number of receiver reports received
           since call connected (inbound streams only). Refer RFC 3550 for
           details on RTCP receiver report (RR).
         * sender reports received - Number of sender reports received since
           call connected (inbound streams only). Refer RFC 3550 for details
           on RTCP sender report (SR).
         * sdes reports received - Number of source description reports
           received since call connected (inbound streams only). Refer RFC
           3550 for details on RTCP source description report (SDES).
         * app reports received - Number of application-defined reports
           received since call connected (inbound streams only). Refer
           RFC 3550 for details on Application-defined RTCP report (APP).
           Applicable only for Telepresence endpoints.
         * bye reports received - Number of bye reports received since call
           connected (inbound streams only). Refer RFC 3550 for details on BYE
           RTCP report.
         * x-cisco-cts sent - Number of x-cisco-cts sent since call connected
           (outbound video streams only).
         * x-cisco-cts received - Number of x-cisco-cts received since call
           connected (inbound video streams only).
         * pli received - Number of PLI (Picture Loss Indication) request
           received since call connected (inbound video streams only).
           Refer RFC 4585 for details on PLI.
         * fir received - Number of FIR (Full Intra Request) requests received
           since call connected (inbound video streams only). Refer RFC 5104
           for details on FIR.
         * tmmbr received - Number of TMMBR received since call connected
           (inbound video streams only). Refer RFC 5104 for details on TMMBR.
         * tmmbn sent - Number of TMMBN sent since call connected (outbound
           video streams only). Refer RFC 5104 for details on TMMBN.
         * mux-ctrl received - Number of MUX Control packet received during MUX
           Negotiation. (inbound video streams only).
         * mux-ctrl sent - Number of MUX Control packet sent during MUX
           Negotiation. (outbound video streams only).
         * mux-mediaopt received - Number of MUX Media Option packet received
           during and after MUX Negotiation. (inbound video streams only).
         * mux-mediaopt sent - Number of MUX Media Option packet sent during
           MUX Negotiation. (outbound video streams only).
         * mux-echo received - Number of MUX echo packet received.
           (inbound video streams only).
         * mux-echo sent - Number of MUX echo packet sent.
           (outbound video streams only).
         * mux-refresh received - Number of MUX video refresh packet received.
           (inbound video streams only).
         * mux-txflowctrl received - Number of MUX Tx Flow Control packet
           received. (inbound video streams only).
         * last report - A list of lists that displays protocol fields of last
           RTCP message sent/ received. Each list is an RTCP report of type
           sender, receiver or     SDES report. A one sentence summary of
           fields is provided here. Refer RFC 3550 for detailed decription.\n
           * sender report - Incoming/ outgoing sender report.\n
             * ssrc - Synchronization source is a 32-bit integer that
               uniquely identifies an audio/ video stream. Corresponds to the
               sender of the report.
             * rtp timestamp - Timestamp of report in the same unit as
               used by RTP in its timestamps.
             * sent packets - The total number of RTP data packets
               transmitted by the sender since starting transmission
               up until the time this SR packet was generated
             * sent octets - The total number of RTP payload octets
               transmitted by the sender since starting transmission
               up until the time this SR packet was generated.
           * receiver report - Incoming/ outgoing receiver report.\n
             * ssrc - The SSRC identifier of the source about which
               the information in this reception report block pertains.
             * fraction lost - The fraction of RTP data packets from
               the source lost since the previous SR or RR packet was
               sent.Not implemented.
             * cum lost packets - The total number of RTP data packets
               from source that have been lost since the beginning of
               reception.
             * high seq num - The low 16 bits contain the highest
               sequence number received in an RTP data packet from
               source and the most significant 16 bits extend that
               sequence number with the corresponding count of
               sequence number cycles. Not implemented.
             * jitter - Average jitter of RTP packets.
             * last sr timestamp - The middle 32 bits out of 64 in
               the NTP timestamp received as part of the most recent
               RTCP sender report (SR) packet from source.
             * sr rr delay - Delay in milliseconds between receiving
               the last SR packet from source and sending this receiver
               report.
           * sdes report - Incoming/ outgoing source description report.\n
             * cname - Canonical endpoint identifier for the RTP session
         * rtcp-fb negotiated - A list of negotiated RTCP-feedback attributes
           (inbound/outbound video streams only). Please refer sip.phone
           configuration section for supported RTCP-feedback types(
           rtcpfb.X.typeY).

        >>> ep1.dial(ep2)
        >>> ep1.get_streams()
        [{'CallId': '0xf1541c18',
          'Direction': 'Rx',
          'RcvrCodec': 'g711u',
          'RemoteAddr': '10.20.1.3:50943',
          'StreamStatus': 'Active',
          'StrmID': '0x0b515908'},
         {'CallId': '0xf1541c18',
          'Direction': 'Tx',
          'RemoteAddr': '10.20.1.3:60324',
          'SenderCodec': 'g711u',
          'StreamStatus': 'Active',
          'StrmID': '0x0b944568'}]
        >>> ep1.get_rtcp_stream_info(ep1.get_streams()[1]['StrmID'])
        {'rtcpaddress': '10.12.10.121:38501',
         'cname': 'e93af034@10.12.10.227',
         'last report time': '18:10:56:520',
         'compound reports sent': '3',
         'receiver reports sent': '2',
         'sender reports sent': '0',
         'sdes reports sent': '2',
         'app reports sent': '0',
         'x-cisco-cts sent': '0',
         'tmmbn sent': '0',
         'mux-ctrl sent': '0',
         'mux-mediaopt sent': '0',
         'mux-echo sent': '0',
         'rtcp-fb negotiated': '',
         'last report': {
             'sender ssrc': '4056167420',
             'sender report': {
                 'rtp timestamp': '0',
                 'sent packets': '0',
                 'sent octets': '0'},
             'receiver report': {
                 'ssrc': '0',
                 'fraction lost': '0',
                 'cum lost packets': '0',
                 'high seq num': '0',
                 'jitter': '0',
                 'last sr timestamp': '0',
                 'sr rr delay': '0'},
             'sdes report': {
                 'cname': 'e93af034@10.12.10.227'}
             }
         }
        '''
        if not stream_ref or not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        return self._query_camelot(camelot.GET_RTCP_STREAM_INFO,
                                   stream_ref)

    def get_stream_ice(self, stream_ref):
        '''provides detailed information for each stream for just the selected
        (nominated) candidates as well as current state of the ICE checklist
        for the stream.

        :parameter stream_ref: stream reference can be retrieved
         from get_streams()

        :returns: A variable sized list of dictionary with {field  value}
         pairs containing ice information about the stream.

         The current fields supported:\n
         * role - specifies the role of the ICE agent, either
           controlling or controlled
         * ice_vqmetrics- ice vqmetrics information for audio stream
           in the format of mmm:xxx:nnn:tttt e.g ice:host:0:0
           if endpoint is not ice enabled value is none.
           where:\n
            * mmm: Mode. One of ice|lite|none|unk.Default value is unk
            * xxx: Type of candidate selected host/relay/srflx/prflx
            * nnn: max time(ms)for connectivity check on that path.Default
              value is 0
            * ttt: time(ms)for the full ICE negotiation to complete.Default
              value is 0
         * index - index of the mline inside the SDP, with the first mline = 1
         * media - media type of the mline
         * rtp - this defines a dictionary that contains ICE information for
           the RTP portion of the media stream
         * rtcp - a dictionary that contains ICE information for the RTCP
           portion of the media stream.If RTCP is not enable for the
           endpoint, the dictionary will be empty.  Attempting to access
           a key will result in exception KeyError.
         * state - the state of the ice checklist state for the session created
           for each media stream (defined in ice_session.h,
           pj_ice_sess_checklist_state).It can have one of the following
           values:
             * idle: The checklist is not yet running.
             * running: In this state, ICE checks are still in progress for
               this media stream.
             * completed: In this state, ICE checks have completed for this
               media stream, either successfully or with failure.
         * result - final result of the ice checklist after reaching the
           completed state.  Values will be either success or failed. If
           failure, the error that caused the failure will be in
           the 'error' key.
         * selected_pair - a dictionary that contains the candidate pair
           selected by ICE for sending and receiving media.  Each of its
           candidates is called the selected candidate
         * local - a dictionary containing information about the selected
           candidate that an agent has obtained and included in an offer
           or answer it sent.
         * remote - a dictionary containing information about the selected
           candidate that an agent has obtained and included in an offer or
           answer it sent.
         * address - ip address of selected candidate
         * port - port of selected candidate.
         * type - type of the selected candidate:
             * host: Host Candidate
             * srflx: Server Reflexive Candidate
             * prflx: Peer Reflexive Candidate
             * relay: Relayed Candidate
         * error - if the ICE session or checklist failed,
           this will contain the error.

        >>> ep1.get_streams()
        [{'CallId': '0xf1541c18',
          'Direction': 'Rx',
          'RcvrCodec': 'g711u',
          'RemoteAddr': '10.20.1.3:50943',
          'StreamStatus': 'Active',
          'StrmID': '0x0b515908'},
         {'CallId': '0xf1541c18',
          'Direction': 'Tx',
          'RemoteAddr': '10.20.1.3:60324',
          'SenderCodec': 'g711u',
          'StreamStatus': 'Active',
          'StrmID': '0x0b944568'}]
        >>> ep1.get_stream_ice(ep1.get_streams()[1]['StrmID'])
        {'role': 'controlling',
         'index': 1,
         'media': 'audio',
         ice_vqmetrics': u'ice:none:0:0
         'rtp': {
          'state': 'completed',
          'result': 'success',
          'selected_pair': {
            'local': {'address':'10.104.45.107', 'port': 8002, 'type': 'host'},
            'remote': {'address':'72.163.212.37', 'port': 2328, 'type': 'host'}
            },
          'error': ''
          },
         'rtcp': {
          'state': 'completed',
          'result': 'success',
          'selected_pair': {
            'local': {'address':'10.104.45.107', 'port': 8003, 'type': 'host'},
            'remote': {'address':'72.163.212.37', 'port': 2329, 'type': 'host'}
            },
          'error': ''
          }
         }
        '''
        if not stream_ref or not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        return self._query_camelot(camelot.GET_STREAM_ICE,
                                   stream_ref)

    def update_media(self, call_ref, option):
        '''
        once the call is established update_media() helps, to
        escalate/deescalate the media by using option parameter.

        :parameter call_ref: reference of the call
        :parameter option: it is string type parameter\n
            * if option parameter value is "all", camelot will send reinvite
              with all configured m-lines with non zero port.
            * if option parameter value is "none",  camelot will send reinvite
              with all configured m-lines with zero port.
            * option parameter value can be any combination of the
              following tokens:\n
                * audio
                * video
                * bfcp
                * slides
                * fecc
                * ix
        Tokens in the option value should be separated with
        the character '+'.

         * if "the number of tokens in the opiton value is matching with
           the number of active media" and "the tokens in the option value
           are matching with the active media"
           then camelot will throw an error with "can't update media".

         * For example if the initial call is
             "audio+video+fecc+bfcp+slides"
             and option = "audio+video+fecc+ix" then
             SDP in the reinvite shall have audio, video, fecc,
             ix m-lines with non zero port and
             bfcp, slides m-lines with zero port


        :returns: True on success  otherwise False is returned.
                 For error the CamelotError exception is raised

        '''

        if not call_ref:
            raise camelot.CamelotError('call reference is not available')

        if not option:
            raise camelot.CamelotError('option is not available')

        if not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')

        return self._binary_to_boolean(
            self._query_camelot(camelot.ESCALATE, call_ref, option))

    def get_service_info(self):
        '''
        :returns: Returns a dictionary reflecting the status of the last
         user initiated service.

        The following field/values are defined:\n
        * type - the type of service attempted.
        * state - the state of the service. Upon termination the service
          can be in either the completed or error states ; otherwise a
          service specific interim state is returned.
        * error - the last error message associated with the service
        * transport - the transport type used by the service. secured
          in case secured URL used or nonsecured.
        * start - em_service or em_logout initiation date and time
          stamp in GMT format
        * end - em_service or em_logout completion date and time
          stamp in GMT format
        * total attempts - total number of service invocations on
          that endpoint
        * total completes - total number of services completed on that
          endpoint
        * total errors - total number of service attempts which had
          terminated with an error
        * action - the URI of the profile used during sign-in
        * pin - the PIN used to access the service
        * profile uri - the URI of the profile used during sign-in
        * requested action - in case emlogout was invoked sign-out
          will be set otherwise "none" is set
        * service name - the name of the service accessed
        * user - the user id used to access the service
        * response: It is a dictionary having fields detailing
          the response of the message with following fields:\n
          * code: Status code of the http response
          * phrase: Status phrase of the http response
          * reason: Value of the reason header if any
          * warning: Value of the warning header if any

        >>> ep1.get_service_info()
        {
         'type': 'headset onboarding',
         'state': 'completed',
         'error': '',
         'transport': 'nonsecured',
         'start': '2020-02-19T21:41:10.506-05:30',
         'end': '2020-02-19T21:41:10.645-05:30',
         'total attempts': '1',
         'total completes': '1',
         'total errors': '0',
         'user': 'user88610001',
         'pin': '12345',
         'service name': 'Extension Mobility',
         'profile uri': '',
         'action': 'sign-in',
         'requested action': 'sign-in',
         'http_messages': [{
         'backoff': '0',
         'camelot_reason': '',
         'host': 'cam-ccm-32.camelot.test',
         'port': '8080',
         'protocol': '',
         'state': 'idle',
         'url': '/emapp/EMAppServlet?device=SEP886188610002'
         '&userid=user88610001&headsetbasedem=true&seq=12345',
         'version': '',
         'response': {
         'code': '200',
         'phrase': 'OK',
         'reason': '',
         'warning': ''
        }
        '''
        return self._query_camelot(camelot.GET_SERVICE_INFO)

    def get_service_info_ext(self):
        '''Returns a dictionary reflecting the status of the last user
        initiated service.

        The following field/values are defined:\n
            * action - the URI of the profile used during sign-in
            * pin - the PIN used to access the service
            * profile uri - the URI of the profile used during sign-in
            * requested action - in case emlogout was invoked sign-out
              will be set otherwise "none" is set
            * service name - the name of the service accessed
            * user - the user id used to access the service

        :returns: Returns a dictionary reflecting the status of the last
                 user initiated service.

        >>> ep1.get_service_info_ext()
        {'action': 'sign-in',
         'pin': '12345',
         'profile uri': '',
         'requested action': 'none',
         'service name': 'Extension Mobility',
         'user': 'EMCC_24_997124011'
        }
        '''
        return self._query_camelot(camelot.GET_SERVICE_INFO_EXT)

    def get_services_urls(self):
        '''Returns the list of services extracted by the Camelot endpoints.
           Only a subset of the services as configured on the Unified
           Call Manager are returned.
           As of the current release Extension Mobility related services
           are returned.

        :returns: A Tcl list of lists of the following format:
            {{name {service name}}{url url-string} {secured-url url-string}}...
            {{name {service name}} {url url-string} {secured-url url-string}}.
        '''
        return self._query_camelot(camelot.GET_SERVICES_URLS)

    def get_sso_info(self, sso_service='cucm'):
        '''It returns the current ssologin information, like home
        node cluster, auththoken, jsessionid, etc., as shown in the
        Returns section. For code grant flow, since there is no
        separate login for unity, for sso_service of unity it will return
        same info of cucm.

        :parameter sso_service: The services supported for
             sso login currently are: cucm and unity_connection.
            this parameter can take two values: 'cucm' and 'unity'.
            Defaults to 'cucm'.

        :returns: A variable sized list of dictionaries with {field value}
            pairs containing extended information about the sso login.\n
            The following fields are supported:\n
            * state -  SSO Login state. Possible values are loggedin,
              loggedout and loggingin.
            * homenode url - UDS home node url
            * remote sso enabled - True of False. Indicates the sso status
              at CUCM
            * central-uds server - Central Uds server discovered
            * jsessionid - jsession id of the sso login successful session
            * jsessionidsso - jsessionidsso of the successful sso login
              session.
            * authtoken - auth token of the successful sso login session
              or code grant flow login session.
            * refresh token- refresh token of the successful sso login session
              or code grant flow login session.
            * login response time : The time taken for sso login in milli
              seconds.
            * last successful login time: last successful sso login time.
            * error code - http error code incase of sso login fails.
            * failure reason - describes the failure reason for ssologin
            * auth token refresh - status of auth token refresh for cucm or
              unity. Below are the possible values:\n
                * "" - initial value
                * pending - refresh is started
                * success - refresh is successfully completed
                * failed - refresh is failed
            * refresh token expiry: refresh token expiry time recevied in
              code grant.
            * authtoken expiry: auth token expiry time recevied in code grant.

        >>> ep.get_sso_info()
        {'authtoken': 'eyJhblU3OC1DR1',
         'central-uds server': 'cam-ccm-11',
         'self contained token': 'true',
         'authtoken expiry': '900',
         'homenode url': 'cam-ccm-11',
         'remote sso enabled': 'false',
         'idp ciphers': 'AES256-SHA',
         'jsessionid': '88132D85B87B284F54696FBD374AC1DD',
         'state': 'loggedin',
         'refresh token': 'eyJhbGc',
         'auth token refresh': '',
         'jsessionidsso': '086D519BE0ABB7F9F0A14CB61E639B76',
         'failure reason': '',
         'error code': '0',
         'login response time': '411.1820',
         'token reuse': 'true',
         'last successful login time': '2017-02-23::15:19:45:241',
         'refresh token expiry': '86400'}

         >>> ep.get_sso_info()
         {'authtoken': 'eyJhbGciOiJ',
          'central-uds server': 'cam-ccm-11',
          'self contained token': 'true',
          'authtoken expiry': '536',
          'homenode url': 'cam-ccm-11',
          'remote sso enabled': 'false',
          'idp ciphers': 'AES256-SHA',
          'jsessionid': '7D44332BA93F04ADB6B8CE6D296108FC',
          'state': 'loggedin',
          'refresh token': 'eyJhbGc',
          'auth token refresh': '',
          'jsessionidsso': '4C3A91742A19B3AD46B21F669A5FF236',
          'failure reason': '',
          'error code': '0',
          'login response time': '0.000000',
          'token reuse': 'true',
          'last successful login time': '2017-02-23::15:19:45:241',
          'refresh token expiry': '51836'}
        '''
        if sso_service not in ("cucm", "unity"):
            raise camelot.CamelotError('Invalid sso_service')

        if sso_service == 'unity':
            sso_service = 'ucxn'
        else:
            sso_service = 'cucm-uds'

        return self._query_camelot(
            camelot.GET_SSO_INFO, sso_service)

    def get_sso_stats(self, clear=None, sso_service='cucm'):
        '''returns the sso login statistics on an endpoint

        :parameter clear: Possible values None and 1. Defaults to None.
         When 1 is passed the sso stats will be cleared on
         returning to the client.
        :parameter sso_service: Possible values cucm and unity.
         Defaults to cucm.sso stats will be returned for the service
         passed for this parameter.

        :returns: contains the list of dictionaries with {field, value} pars.\n
             The following fields are supported:\n
             * login attempts: number of sso login attempted
             * login successes: number of sso login successess
             * login failures: number of sso login failures
             * ssomode queries attempted:  number of ssomode discovery
               attempted.
             * ssomode queries succeeded: number of ssomode queries
               succeeded.
             * ssomode queries failed: no.of ssomode queries failed
             * homenode queries attempted: no.of homenode queries attempted
             * homenode queries succeeded: no.of homenode queries succeeded
             * homenode queries failed: no.of homenode queries failed
             * device discovery queries attempted: no.of devicediscovery
               queries attempted
             * device discovery queries failed: no.of devicediscovery queries
               failed.
             * device discovery queries succeeded: no.of devicediscovery
               queries succeeded.
             * self-provision queries attempted: no.of self-provision queries
               attempted.
             * self-provision queries succeeded: no.of self-provision queries
               succeeded.
             * self-provision queries failed: no.of self-provision queries
               failed
             * 5xx errors: no.of 5xx errors
             * 4xx errors: no.of 4xx errors
             * 3xx errors: no.of 3xx errors
             * oauthrefresh failed: no.of oauth/access token refresh
               attempt failed.
             * oauthrefresh succeeded: no.of oauth/access refresh
               attempt succeeded.
             * oauthrefresh attempted: no.of oauth/access refresh
               attempt attempted.

        >>> ep.get_sso_stats()
        {'device discovery queries failed': '0',
        'login successes': '1',
        'ssomode queries succeeded': '1',
        '4xx errors': '0',
        'oauthrefresh failed': '0',
        'oauthrefresh succeeded': '0',
        'oauthrefresh attempted': '0',
        'login attempts': '1',
        'self-provision queries failed': '0',
        'homenode queries attempted': '1',
        'ssomode queries attempted': '1',
        'ssomode queries failed': '0',
        'homenode queries succeeded': '1',
        'devicediscovery queries succedded': '0',
        'login failures': '0',
        '3xx errors': '0',
        'devicediscovery queries attempted': '0',
        '5xx errors': '0',
        'homenode queries failed': '0',
        'self-provision queries attempted': '0',
        'self-provision queries succeeded': '0'}
        '''
        if sso_service not in ("cucm", "unity"):
            raise camelot.CamelotError('Invalid sso_service')

        if sso_service == 'unity':
            sso_service = 'ucxn'
        else:
            sso_service = 'cucm-uds'

        if clear:
            clear = 'clear'
        else:
            clear = 'noclear'
        kwargs = {'clear': clear
                  }

        return self._query_camelot(
            camelot.GET_SSO_STATS, sso_service, **kwargs)

    def get_fax_stats(self, clear=None):
        '''Get an endpoint's fax statistics.

        Retrieve accumulated fax statistics on a specific endpoint.

        :parameter clear: Clear all fax statistics upon return

        :returns: a variable sized list of dictionaries with {field  value}
         pairs.

         The following fields are defined:

            * send attempts - number fax send attempts
            * send successes - number of successful fax send tranmissions
            * receive attempts - number of fax receive attempts
            * receive successes - number of successful fax receive
              transmissions
            * sent pages - number of pages sent
            * received pages - number of pages received
            * retries - number of transmission retries
            * bad lines - number of calls bad lines received

        >>> ep1.get_fax_stats()
        {'bad lines': '0',
         'receive attempts': '0',
         'receive successes': '0',
         'received pages': '0',
         'retries': '0',
         'send attempts': '0',
         'send successes': '0',
         'sent pages': '0'}
        '''

        log.debug('Entering into get_fax_stats')
        return self._query_camelot(camelot.GET_FAX_STATS, clear)

    def refresh_register(self, ip='null', ipv6='null', tcpconndropfirst='0'):
        '''Refresh register - Establish new connection
                            with CUCM and bring endpoint in service

        :parameter ip: ipv4 address
        :parameter ipv6: ipv6 address
        :parameter tcpconndropfirst: options for existing tcp connection\n
         * 0 - Refresh register will be sent on new connection first and
               old connection will be closed
         * 1 - Current active connection is closed first and refresh register
               will be sent on new connection
         * 2 - Current active connection is closed first and refresh register
               wil be sent after 30secs on a new connection

        :returns: endpoint state

        >>> ep.refresh_register()
        'inservicepending'
        >>> ep.refresh_register(ip='10.22.22.22',ipv6='2001:db8::1428:57ab')
        'inservicepending'
        >>> ep.refresh_register(tcpconndropfirst=2)
        'inservicepending'
        >>> ep.refresh_register(ip='15.12.11.22',ipv6='2001:db8:1428:57ab',
            tcpconndropfirst=1)
        'inservicepending'
        '''
        log.debug('Entering into refresh_register function')
        kwargs = {'ip': ip,
                  'ipv6': ipv6,
                  'tcpdrop': tcpconndropfirst}

        if ip != 'null':
            try:
                socket.inet_aton(ip)
            except socket.error as e:
                raise camelot.CamelotError(e)

        if ipv6 != 'null':
            try:
                socket.inet_pton(socket.AF_INET6, ipv6)
            except socket.error as e:
                raise camelot.CamelotError(e)

        return self._query_camelot(camelot.REFRESH_REGISTER, **kwargs)

    def initial_register(self):
        '''initial_register - After endpoint comes into the inservice,
             establishes new connection  with CMS and then sends
             full register message.After invoking this endpoint state would be
             moved to insfailover. once camelot receives the 200 ok for the
             full register message endpoint state would be moved to inservice.
             Here endpont acts like to simulate hedge behaviour towards cms.

        :returns: 1 on success,on failure returns the error string:
                  "initialregister can't be invoked"

        >>> ep.initial_register()
        '1'
        '''
        log.debug('Entering into initial_register function')
        return self._query_camelot(camelot.INITIAL_REGISTER)

    def refresh_subscribe(self, event=0, eventstr='null',
                          unsubscribe=0, clear=0):
        ''' refreshsubscribe   -  will initiates the subscribe.

        For the DMC endpoint case, it will use a new IP after refreshregister.

        :parameter event: DMC Refresh events.  The possible values are \n
            * 1 - Send subscribe only for DIALOG event
            * 2 - Send subscribe only for PRESENCE event
            * 3 - Send subscribe for DIALOG and PRESENCE event
        :parameter eventstr: User defined event string for NanoCUBE interface.
                             Possible values are \n
            * dialog
            * line-seize
            * call-info
            * message-summary
            * x-broadworks-hoteling
            * as-feature-event
            * x-broadworks-call-center-status
            * Any new event string defined by user
        :parameter unsubscribe: Unsubscribe specified event string. If event is
         not given unsubscribe all events.  Its applicable only for NanoCUBE
         interface.
        :parameter clear: clear the get_info_ext for terminated subscription
         data. It is applicable only for NanoCUBE interface.

        :returns: True or False.

        >>> ep.refresh_subscribe()
        True
        >>> ep.refresh_subscribe(eventstr='dialog')
        True
        >>> ep.refresh_subscribe(eventstr='dialog', unsubscribe=1)
        True
        '''
        if event not in (0, 1, 2, 3):
            raise camelot.CamelotError('Invalid event.  It should be 1/2/3')

        if event > 0 and (clear > 0 or unsubscribe > 0 or eventstr != 'null'):
            raise camelot.CamelotError(
                'event cannot be given with eventstr/clear/unsubscribe')

        kwargs = {'eventstr': eventstr,
                  'unsubscribe': unsubscribe,
                  'clear': clear}

        return self._binary_to_boolean(
            self._query_camelot(camelot.REFRESH_SUBSCRIBE, event, **kwargs))

    def start_blf_status(self, called):
        ''' Enable monitoring of a called address's busy lamp field

        Enable monitoring of a called address busy lamp field (BLF).
        Once enabled, the endpoint will receive periodic BLF status updates for
        the monitored called address.Use the get_blf_info method to
        retrieve the current BLF status of all monitored called addresses.
        Monitored called addresses also generate station events corresponding
        to the actual updates received from CCM.

        :parameter called: called address to be monitored

        :returns: True or False

        >>> ep.start_blf_status('880011')
        True
        '''

        return self._binary_to_boolean(
            self._query_camelot(camelot.START_BLF_STATUS, called))

    def stop_blf_status(self, called):
        ''' Disable monitoring of a called address's busy lamp field

        Disable monitoring of a called address busy lamp field (BLF).
        Once disabled, the endpoint will no longer receive periodic BLF status
        updates for the monitored called address.

        :parameter called: called address to disable blf monitoring

        :returns: True or False

        >>> ep.stop_blf_stats('880011')
        True
        '''

        return self._binary_to_boolean(
            self._query_camelot(camelot.STOP_BLF_STATUS, called))

    def get_transport_info(self, transport_ref, field=None):
        '''Get detailed information about a transport

        Get information about the specified transport connection. For UDP
        transport connections, destaddr field will return the destination
        address for the most recently transmitted packet.

        :parameter transport_ref: The transport reference

        :returns: If the field argument is omitted, a variable sized list of
         disctionaries with {field  value} containing generic information
         about the transport.  If the field option is specified, only the
         value for the specified field is returned.\n
         The following filed names are spported:\n
         * transport - connection type of the transport, tcp or udp
         * protocol - protocol associated with the transport, sip
         * type -  socket type of the transport, client, server,
           accept or none (for UDP transport connections)
         * state - state of the transport:\n
           * open: socket associated with the transport is open
           * closed : socket associated with the transport is
             closed.
         * srcaddr - source ip and port
         * destaddr - destination ip and port
        >>> get_transport_info()
        {'destination address': '10.12.10.122:36596',
         'protocol': 'sip',
         'source address': '10.12.10.224:43889',
         'state': 'open',
         'transport': 'tcp',
         'transportref': '0x94fbd7b',
         'type': 'server'}
        '''
        if not transport_ref:
            log.error('Invalid transport reference, returning..')
            return
        kwargs = {'field': field}
        return self._query_camelot(
            camelot.GET_TRANSPORT_INFO, transport_ref, **kwargs)

    def get_transports(self):
        '''
        Return information about transports associated with an endpoint

        Retrieve current transports associated with an endpoint.

        :returns: The list of dictionatires with the followinf form:\n
         [{transport-ref  transport protocol  type  state }]\n
             * transport-ref - transport reference of the transport
             * transport -  connection type of the transport, tcp or udp
             * protocol - protocol associated with the transport, sip
             * type -  socket type of the transport, client, server,
               accept or none (for UDP transport connections)
             * state - state of the transport\n
               * open - socket associated with the transport is open
               * closed - socket associated with the transport is closed

         If no transports exist, nothing is returned. When a transport is
         released via the releasetransports method, it no longer appears
         in this list.
        >>> get_transports()
        '[{"transport-ref":"0x94fbbc1","transport":"tcp",
        "protocol":"h225-ras", "type":"server", "state":"connecting"}]'
        '''
        return self._query_camelot(camelot.GET_TRANSPORTS)

    def log_mask(self, level=None, moduleid=None, device=None, reset=False):
        '''Set or get the configured endpoint logging level.
        For parameters description please refer to the server console log
        commands documentation.

        :returns: When trying to apply new settings a status string is
         returned. On success Log Level Set is returned; otherwise an
         informative exception raised.
        For exmaple when log level set as:
        log_mask(moduleid='*',level='debug_5',device='file')

        >>> ep1.log_mask()
        {'*': {'console': '', 'file': ''},
        'auto': {'console': '', 'file': 'debug_5'},
        'button': {'console': '', 'file': ''},
        'config': {'console': '', 'file': 'debug_5'},
        'csfd': {'console': '', 'file': ''},
        'cupc': {'console': '', 'file': ''},
        'cupcd': {'console': '', 'file': ''},
        'http': {'console': '', 'file': ''},
        'jguest': {'console': '', 'file': ''},
        'media': {'console': '', 'file': ''},
        'mediatransp': {'console': '', 'file': ''},
        'method': {'console': '', 'file': 'debug_5'},
        'qbe': {'console': '', 'file': ''},
        'qbetransp': {'console': '', 'file': ''},
        'sccp': {'console': '', 'file': ''},
        'sccptransp': {'console': '', 'file': ''},
        'sip': {'console': '', 'file': ''},
        'siptransp': {'console': '', 'file': ''},
        'srtp': {'console': '', 'file': ''},
        'sss': {'console': '', 'file': ''},
        'tdm': {'console': '', 'file': ''},
        'tftp': {'console': '', 'file': ''},
        'tvs': {'console': '', 'file': ''},
        'vapi': {'console': '', 'file': ''},
        'xmpp': {'console': '', 'file': ''},
        '~': {'console': '', 'file': ''}}
        '''
        # EXECUTE AND MODIFY
        kwargs = {
            'moduleid': moduleid or '',
            'level': level or '',
            'device': device or '',
            'reset': reset
        }
        return self._query_camelot(camelot.LOG_MASK, None, **kwargs)
    ep_log_mask = log_mask

    def log_dir(self):
        '''Returns the endpoint's execution logs directory path on
        Camelot server.

        :returns: The execution log folder's path.

        >>> ep1.log_dir()
        '/var/camelot/logs/02006_20131018_113644/sipx8'

        '''
        kwargs = {
        }
        return self._query_camelot(camelot.LOG_DIR, None, **kwargs)
    ep_log_dir = log_dir

    def log_filesz(self, size=None):
        '''
        The command enables setting the endpoint's log file size.

        :parameter size: size in kbytes

        :returns: The current set log file size or 0 on error.

        Fetching the current file size

        >>> ep1.log_filesz()
        '1024'

        Changing the current file size

        >>> ep1.log_filesz('2048')
        '2048'

        '''
        kwargs = {
            'size': size
        }
        return self._query_camelot(camelot.LOG_FILESZ, None, **kwargs)
    ep_log_filesz = log_filesz

    def max_log_files(self, numfiles=None):
        '''The command sets a limit on the number of log files in the
        endpoint's log folder. The arguments and mechanism are identical
        to those of camelot max_log_files.

        :parameter numfiles: number of files

        :returns: The current log files limit

        >>> ep1_max_log_files()
        '1024'
        '''
        kwargs = {
            'numfiles': numfiles
        }
        return self._query_camelot(camelot.LOG_MAX_FILES, None, **kwargs)
    ep_max_log_files = max_log_files

    def log_file_prefix(self, prefix=None):
        '''Changes the current endpoint's log file name prefix.

        The command sets or returns the endpoints log file prefix.
        The arguments and mechanism are identical to those of camelot
        log_file_prefix.

        :parameter prefix: filename prefix.

        :returns: The current log file name prefix.

        Fetching the current file prefix

        >>> ep1.log_file_prefix()
        'sipx8'

        Changing the current file prefix

        >>> ep1.log_file_prefix('sipx8_new')
        'sipx8_new'

        '''
        kwargs = {
            'prefix': prefix
        }
        return self._query_camelot(camelot.LOG_FILE_PREFIX, None, **kwargs)
    ep_log_file_prefix = log_file_prefix

    def clear_mwi_stats(self):
        '''
        Clears Message Waiting Indicator(MWI) stats on the Endpoint

        :returns: True on success

        >>> ep1.get_info_ext()['mwi stats']
        {'icon off': '1', 'icon on': '2', 'lamp off': '0', 'lamp on': '0'}
        >>> ep1.clear_mwi_stats()
        True
        >>> ep1.get_info_ext()['mwi stats']
        {'icon off': '0', 'icon on': '0', 'lamp off': '0', 'lamp on': '0'}
        '''
        return self._query_camelot(camelot.GET_INFO_EXT_CLEAR_MWI)

    def set_traffic(self, mode):
        ''' sets Tranistion between non-secure and secure modes on
        IP-STE endpoints

        Invokes either secure or nonsecure mode on an IP-STE endpoint.

        :parameter mode: mode of transition.  Possible values are\n
            * secure - Secure mode
            * nonsecure - Non secure mode
        :returns: True or False

        >>> ep.set_traffic('secure')
        True
        '''

        return self._binary_to_boolean(
            self._query_camelot(camelot.SET_TRAFFIC, mode))

    def set_eptiming(self,
                     eptimer=camelot.EpTimer.EpTimerType.all,
                     tmin=5000,
                     trange=55000,
                     increment=1000,
                     honor_header=True):
        ''' Allows a tester to set the retry timing behavior on
        receiving an error responses. sets Timer for specified timer type.

        :parameter eptimer: Provided arguments are applicable to
            specified endpoint timer type.
            Possible values are as below\n
            * camelot.EpTimer.EpTimerType.retryafter = 1\n
            * camelot.EpTimer.EpTimerType.all =2 (Default)
        :parameter tmin: Mimimal retry value.
        :parameter trange: Camelot will choose a random number
            between tmin and tmin+trange.
            specified endpoint timer.
        :parameter increment: The random number between tmin and
            tmin+trange will be rounded off to nearest increment.
        :parameter honor_header: honor_header==True means that if
            a specified header is present in the response then
            the Retry-After header value will be used instead
            of the timing settings.
            If honor_header==False then timing setting will be used.

        :Note: tmin, trange and increment are in ms.
            Retry timing applies to all SIP and HTTP response
            codes, regardless of request:

        :returns: True or False
            Possible error responses:
            Invalid timer type, please refer API guide.
            increment should be positive number
            tmin and trange can not be less than zero

        >>> set_eptiming(eptimer='Retry-After',
                        tmin=5000, trange=55000,
                        increment=1000, honor_header=True)
        >>> True
        >>> The above example will set retry after "backoff timer"
        to a random number between 5 and 60 seconds in 1 second increments.
        If the response contains a Retry-After header, it will
        be used instead, if valid.
        '''
        if 0 > eptimer > camelot.EpTimer.EpTimerType.all:
            log.error('Invalid timer type, please refer API guide')
        if increment <= 0:
            log.error('increment should be positive number')
        if tmin < 0 or trange < 0:
            log.error('tmin and trange can not be less than zero')
        kwargs = {'timer_type': eptimer,
                  'tmin': tmin,
                  'trange': trange,
                  'increment': increment,
                  'honor_header': honor_header}
        return self._query_camelot(camelot.SET_EPTIMING, **kwargs)

    def em_service(self, user, pin, profile=None,
                   transport='nonsecured',
                   servicename='Extension Mobility', title=None):
        '''Initiate an Extension Mobility service procedure.
        Initiates an Extension Mobility service with the specified
        user credentials.
        The endpoint will attempt to access the Extension Mobility
        service menu page and will attempt login/logout based on
        menu options.

        :parameter user: The user-id used for Extension Mobility service
         log on.
        :parameter pin: The PIN used for Extension Mobility log on.
        :parameter profile: Profile name to select. If not specified
         the first profile returned will be automatically selected.
        :parameter servicename: The service name to match. If not specified
         'Extension Mobility' will be attempted.
        :parameter transport: Sets the transport type to be used. If secured
         is specified then the service will be attempted via the secured URL
         if available. If nonsecured is specified then the non-secured URL will
         be used if available. If not specified the secured URL will be used if
         available otherwise the non-secured.
        :parameter title: Sets the title to be "Please Login"  for CUCM version
         >=9.0 and "Please Sign On" for CUCM version <=8.6.
         If not specified "Please Sign On" will be attempted

        :returns: 1 on success 0 otherwise.Note, success means that the
         endpoint had successfully initiated the procedure. For final
         status the getserviceinfo should be called. Camelot Exception
         is thrown if secured transport is used for nonsecured endpoint
         or viceversa.

        >>> ep1.em_service(user = 'EM_USER_510001',pin = '12345',
         profile = 'EM_SIP_510001',transport = 'nonsecured',
         servicename = 'Extenstion Mobility',title = 'Please Login')
         '1'

        >>> ep1.em_service(user = 'EM_USER_510001',pin = '12345',
         profile = 'EM_SIP_510001',transport = 'secured',
         servicename = 'Extenstion Mobility',title = 'Please Login')
         CamelotError: invalid transport type
        '''

        if not user:
            log.error('user not specified')
            return
        if not pin:
            log.error('pin not specified')
            return

        if not title:
            title = "Please Sign On"

        kwargs = {'user': user,
                  'pin': pin,
                  'profile': profile,
                  'transport': transport,
                  'servicename': servicename,
                  'title': title
                  }
        return self._query_camelot(camelot.EMSERVICE, None, **kwargs)

    def em_logout(self):
        '''Attempts to initiate an explicit Extension Mobility logout
        operation.

        :returns: 1 on success 0 otherwise.
         Note, success means that the endpoint had successfully
         initiated the procedure.
         For final status the getserviceinfo should be called.
        '''
        return self._query_camelot(camelot.EMLOGOUT)

    def get_call_time_stats(self, clear=False):
        '''Get an endpoint's call timing statistics

        :parameter clear: Clear the call time stats on return.
                          Possible values are \n
            * True - Clear on return
            * False - Don't clear on return

        :returns: A dictionary of statistics information as shown below \n

            * average dialtone - average delay in milliseconds from call off
                                 hook to dial tone
            * maximum dialtone - maximum delay in milliseconds from call off
                                 hook to dial tone
            * average setup - average delay in milliseconds from dialing
                              complete to ring back
            * maximum setup - maximum delay in milliseconds from dialing
                              complete to ring back
            * average connect - average time in milliseconds calls are
                                connected. Note, a call on hold is still
                                considered connected.
            * maximum connect - maximum time in milliseconds call was connected
            * average disconnect - average time in milliseconds from call
                                disconnect to disconnect acknowledgement
                                from the network
            * maximum disconnect - maximum time in milliseconds from call
                                   disconnect to disconnect acknowledgement
                                   from the network
            * average cut-through - average time in milliseconds from call
                                    answer or resume to outbound audio
                                    stream open
            * maximum cut-through - maximum time in milliseconds from call
                                    answer or resume to outbound audio stream
                                    open
            '''

        return self._query_camelot(camelot.GET_CALL_TIME_STATS, clear)

    def get_cas_voice_stats(self):
        '''Get an cas endpoint's voice data related statistics

        :returns: A dictionary of statistics information as shown below \n

            *total received bytes - total voice bytes received
            *total read bytes - total voice bytes read by calling
            DivaReceiveAudio
            *last received bytes - last received bytes
            *last read bytes - last read bytes by calling DivaReceiveAudio
            *voice file path --file used for playing voice
            *sent sampling rate --sampling rate used for playing voice
            *received audio format - audio format used for receiving voice
            For more info: please refer to following wiki:
           'https://wiki.cisco.com/display/CAMELOT/Analog+ATA-190+Voice+Support'

        >>> ep.get_cas_voice_stats()
        {'total received bytes': '34816',
        'last received bytes': '2048',
        'total read bytes': '34816',
        'last read bytes': '2048',
        'voice file path': '',
        'sent sampling rate': '0',
        'received audio format': '100'}
            '''

        return self._query_camelot(camelot.GET_CAS_VOICE_STATS)

    def get_blf_info(self):
        ''' Get busy lamp field status of monitored called addresses

        :returns: dictionary of blf information in a key value of pair of
                  monitored called address and blf status respectively.

        >>> ep.get_blf_info()
        [{"called_dn":"88658593","blfState":"alerting"}]

        >>> ep.get_blf_info()
        [{"called_dn":"88658593","Line":"8593","blfState":"alerting"},
                {"called_dn":"88658592","Line":"8592","blfState":"idle"}]
        '''

        return self._query_camelot(camelot.GET_BLF_INFO)

    def delete_sip_messages(self, call_ref=None):
        '''delete_sip_messages deletes the list of SipMsgObjects

        :parameter call_ref: Optional Parameter. If provided the command uses
         this call_ref to delete list of inbound and outbound SipMsgObjects
         for a call, otherwise it will delete the out of dialog SipMsgObjects

        :returns: True on success and throws exception on failure

        >>> ep2.delete_sip_messages('0xaf62ec8')
            True
        >>> ep2.delete_sip_messages('0x11111111')
            CamelotError: Invalid Callref
        '''
        if call_ref:
            if not self._is_valid_call_ref(call_ref):
                log.error('deletesipmessages: Invalid Call-ref passed,'
                          ' returning')
                return
        else:
            call_ref = 'null'

        ret = self._query_camelot(camelot.DELETE_SIP_MESSAGES, call_ref)
        return ret

    def get_sip_messages(self, call_ref=None, mode='inbound'):
        '''get_sip_messages gets the list of SipMsgObjects

        :parameter call_ref: Optional Parameter. If provided the command uses
                             this call_ref to retrieve list of SipMsgObjects
                             for a call, otherwise it list all the
                             SipMsgObjects of out of dialog NOTIFY or REFER
                             (response/request).

        :parameter mode: this parameter can be either inbound/outbound

        :returns: list of SipMsgObject associated with the callrefrence or
                  out of dialog NOTIFY or REFER (response/request).

        :Note: configure sip.phone.outofdialogcapture as 1 for capturing
               outofdialogue NOTIFY or REFER (response/request).

        `refer wiki documentation page for example <https://wiki.cisco.com
        /display/CAMELOT/Simulated+endpoint+
        features+to+overcome+raw+endpoint+challenges#Simulatedendpointfeatu
        restoovercomerawendpointchallenges-Scripts&DemoLinks>`_

        >>> ep2.get_sip_messages('0xaf62ec8')
        [<tng.plugins.camelot.camelot_vapi_plugin.SipMsgObject
         at 0x7f381012e0d0>,
         <tng.plugins.camelot.camelot_vapi_plugin.SipMsgObject
         at 0x7f381012e610>]
        '''
        ret_result = []
        if call_ref:
            if not self._is_valid_call_ref(call_ref):
                log.error('getsipmessages: Invalid Call-ref passed, returning')
                return
        else:
            call_ref = 'null'

        ret = self._query_camelot(camelot.GET_SIP_MESSAGES, call_ref, mode)

        for ref_id in ret:
            if not ref_id:
                continue
            temp_list = ref_id.split(':')
            message_type = temp_list[0]
            method_name = temp_list[1]
            resp_code = temp_list[2]
            msg_id = temp_list[3]
            ret_result.append(SipMsgObject(self, call_ref, message_type,
                                           method_name, resp_code, msg_id))

        return ret_result


class ContentBodyObject(object):

    '''ContentBodyObject object contains content body associated with
    SipMessage object.

    User can extract the full content body from this object along
    with the content type associated with it using different API's.
    '''

    def __init__(self, conn, callref, contenttype,
                 subcontenttype, msgid, method_name):
        self.vapi = conn
        self.call_ref = callref
        self.content_type = contenttype
        self.sub_content_type = subcontenttype
        self.msg_id = msgid
        self.method_name = method_name

    def get_content_body(self):
        '''get_content_body gets the content body

        :returns: the full content body in string format

        >>> msgobj = ep2.get_sip_messages('0xf24bb5c0')

        >>> print msgobj
            [<tng.plugins.camelot.camelot_vapi_plugin.SipMsgObject object
             at 0x7ffb0438ddd0>,
            <tng.plugins.camelot.camelot_vapi_plugin.SipMsgObject object
             at 0x7ffb0438dfd0>]

        >>> msgobj[1].get_content_body_list()
            [<tng.plugins.camelot.camelot_vapi_plugin.ContentBodyObject
            at 0x7ffb0438df50>]

        >>> msgobj[1].get_content_body_list()[0].get_content_body()
            'v=0[CRLF]o=CiscoSystemsCCM-SIP 23210 1 IN IP4 10.12.10.86[CRLF]
             s=SIP Call[CRLF]c=IN IP4 10.12.10.194b=TIAS:64000[CRLF]
             b=AS:64[CRLF]t=0 0[CRLF]m=audio 43840 RTP/AVP 0 101[CRLF]
             a=label:403[CRLF]a=ptime:20[CRLF]a=rtpmap:0 PCMU/8000[CRLF]
             a=rtpmap:101 telephone-event/8000[CRLF]a=fmtp:101 0-15[CRLF]'
        '''
        if self.call_ref != 'null':
            if not self.vapi._is_valid_call_ref(self.call_ref):
                log.error('getcontentbody: Invalid Call-ref passed')
                return
        kwargs = {'msg_id': self.msg_id,
                  'method_name': self.method_name
                  }
        return self.vapi._query_camelot(
            camelot.GET_CONTENT_BODY, self.call_ref, **kwargs)

    def is_part_of_mime(self):
        '''
        :returns: True if content body is part of multipart/mixed

        >>> msgobj[1].get_content_body_list()[0].is_part_of_mime()
            True
        '''
        return self.content_type == 'mime'

    def get_content_type(self):
        '''
        :returns: the content type of the body

        >>> msgobj[1].get_content_body_list()[0].get_content_type()
            'application/sdp'

        '''
        return self.sub_content_type


class SipMsgObject(object):

    '''
    SipMsgObject object contains single SIP message and it's headers.

    With the SipMsgObject user can retrieve the content bodies associated
    with the SIP message. User can get full sip message headers or selective
    headers using this object.

    '''

    def __init__(self, conn, callref, msgtype, methodname,
                 respcode, msgid):
        self.vapi = conn
        self.msg_type = msgtype
        self.method_name = methodname
        self.resp_code = respcode
        self.call_ref = callref
        self.msg_id = msgid
        self.content_body_list = []

    def get_sip_headers(self):
        '''
        :returns: All the sip headers in message in string format

        >>> msgobj[0].get_sip_headers()
             'INVITE sip:900002@10.12.10.194:27237;transport=tcp SIP/2.0[CRLF]
             Via: SIP/2.0/TCP 10.12.10.86:5060;
             branch=z9hG4bK7d27976c2de[CRLF]
             Remote-Party-ID: <sip:900001@10.12.10.86;
             x-cisco-callback-number=900001>;party=calling;
             screen=yes;privacy=off[CRLF]
             From: <sip:900001@10.12.10.86>;
             tag=23210~752e3d62-2290-435d-b5ce-7887afcb1d9d-23391191[CRLF]
             To: <sip:900002@10.12.10.86>[CRLF]
             Date: Wed, 08 Oct 2014 08:38:01 GMT[CRLF]
             Call-ID: 685fc000-4341f7e9-187-560a0c0a@10.12.10.86[CRLF]
             Supported: timer,resource-priority,replaces[CRLF]
             Min-SE: 1800[CRLF]User-Agent: Cisco-CUCM10.5[CRLF]
             Allow: INVITE, OPTIONS, INFO, BYE, CANCEL, ACK, PRACK,
             UPDATE, REFER, SUBSCRIBE, NOTIFY[CRLF]CSeq: 101 INVITE[CRLF]
             Max-Forwards: 5[CRLF]
             Contact: <sip:900001@10.12.10.86:5060;transport=tcp>;
             +sip.instance="<urn:uuid:00000000-0000-0000-0000-DADDAD900001>";
             +u.sip!model.ccm.cisco.com="493"[CRLF]Expires: 180[CRLF]
             Allow-Events: presence[CRLF]Content-Length: 0[CRLF]
             Alert-Info:<file://Bellcore-dr1/>[CRLF]
             Call-Info:<urn:x-cisco-remotecc:callinfo>; security= Unknown;
             orientation= from; gci= 1-38158; isVoip; call-instance= 1[CRLF]
             Send-Info:conference, x-cisco-conference[CRLF]'

        '''
        if self.call_ref and self.call_ref != 'null':
            if not self.vapi._is_valid_call_ref(self.call_ref):
                log.error('getsipheaders: Invalid Call-ref passed, returning')
                return
        kwargs = {'msg_id': self.msg_id
                  }
        return self.vapi._query_camelot(
            camelot.GET_SIP_HEADERS, self.call_ref, **kwargs)

    def get_sip_header(self, header_value):
        '''
        :parameter: header-name to be retrieved

        :returns: list of header values in particular message which has
         same header name

        >>> msgobj[0].get_sip_header('From')
            ['<sip:900001@10.12.10.86>;
            tag=23210~752e3d62-2290-435d-b5ce-7887afcb1d9d-23391191']

        '''
        if self.call_ref and self.call_ref != 'null':
            if not self.vapi._is_valid_call_ref(self.call_ref):
                log.error('getsipheader: Invalid Call-ref passed, returning')
                return
        kwargs = {'msg_id': self.msg_id,
                  'header_val': header_value
                  }
        return self.vapi._query_camelot(
            camelot.GET_SIP_HEADER, self.call_ref, **kwargs)

    def get_content_body_list(self):
        '''
        :returns: the list of ContentBodyObjects associated with SipMsgObject

        >>> ep2.get_sip_messages('0xf24bb5c0')
           [<tng.plugins.camelot.camelot_vapi_plugin.SipMsgObject
             at 0x7ffb0438dc50>,
            <tng.plugins.camelot.camelot_vapi_plugin.SipMsgObject
             at 0x7ffb0438de90>]

        >>> ep2.get_sip_messages('0xf24bb5c0')[0].get_content_body_list()
           []

        >>> ep2.get_sip_messages('0xf24bb5c0')[1].get_content_body_list()
            [<tng.plugins.camelot.camelot_vapi_plugin.ContentBodyObject
              at 0x7ffb0438df10>]

        '''
        ret_result = []
        if self.content_body_list:
            return self.content_body_list
        out_msg = camelot.GET_CONTENT_BODY_LIST
        if self.call_ref != 'null':
            if not self.vapi._is_valid_call_ref(self.call_ref):
                log.error('getcontentbodylist: Invalid Call-ref, returning')
                return
        out_msg = "{} {} {} {}".format(
            out_msg, self.call_ref, self.msg_id, self.method_name)
        ret = self.vapi._query_camelot(
            camelot.GET_CONTENT_BODY_LIST, out_msg)
        if self.call_ref == 'null' or self.method_name == 'notify':
            content_type = ret[0]
            ret_result.append(ContentBodyObject(self.vapi, self.call_ref,
                                                'null',
                                                content_type, self.msg_id,
                                                self.method_name))
            self.content_body_list = ret_result
            return ret_result
        for ref_id in ret:
            if ref_id == '':
                continue
            temp_list = ref_id.split(':')
            content_type = temp_list[0]
            sub_content_type = temp_list[1]
            msg_id = temp_list[2]
            ret_result.append(ContentBodyObject(self.vapi, self.call_ref,
                                                content_type,
                                                sub_content_type,
                                                msg_id, self.method_name))
        self.content_body_list = ret_result
        return ret_result

    def is_request(self):
        '''
        :returns: True if the Sip message is request else return False

        >>> ep2.get_sip_messages('0xf24bb5c0')[1].is_request()
            True
        '''
        return self.msg_type == 'request'

    def get_method_name(self):
        '''
        :returns: the name of the method based on CSeq header

        >>> ep2.get_sip_messages('0xf24bb5c0')[1].get_method_name()
            'INVITE'
        '''
        return self.method_name.upper()

    def get_response_code(self):
        '''
        :returns: the response code if the message is SIP response

        >>> ep2.get_sip_messages('0xf24bb5c0')[1].get_response_code()
            '200'
        '''
        if self.resp_code != 'null':
            return self.resp_code

    def get_content_body_obj(self, input_content_type):
        '''
        :parameter: content-type of body

        :returns: It will return the particular ContentBodyObject from all the
                 ContentBodyObjects associated with the SipMsgObject

        >>> msgobj[1].get_content_body_list()
           [<tng.plugins.camelot.camelot_vapi_plugin.ContentBodyObject
             at 0x7ffb0438df50>]

        >>> msgobj[1].get_content_body_obj('application/sdp')
            <tng.plugins.camelot.camelot_vapi_plugin.ContentBodyObject
             at 0x7ffb0438df50>

        '''
        ret_result = []
        if not self.content_body_list:
            if self.call_ref and self.call_ref != 'null':
                if not self.vapi._is_valid_call_ref(self.call_ref):
                    log.error('get_content_body_obj: Invalid Call-ref passed')
                    return
            kwargs = {'msg_id': self.msg_id
                      }
            ret = self.get_content_body_list()

        for content_body_elem in self.content_body_list:
            check_body_type = content_body_elem.get_content_type()
            if check_body_type == input_content_type:
                return content_body_elem
