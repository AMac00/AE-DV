import camelot
import sys
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger, FaxProfile, DivaFaxOptions

log = camlogger.getLogger(__name__)


class CamelotCallControl(v.CamelotVapiUtils):

    '''Camelot call control representation
    '''

    def __init__(self):
        pass

    def release_calls(self, call_ref=None):
        ''' Release call resources

        Releases all resources consumed by the specified call.
        The call must be in the disconnected state. Upon successful completion,
        the specified call reference can no longer be used in future method
        invocations.  If -callref is omitted, all disconnected calls
        on the end point are released.

       :parameter call_ref: call reference

        '''
        if call_ref and not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')

        return self._query_camelot(camelot.RELEASE_CALLS, call_ref)

    def release_call_ref(self, call_ref=None):
        '''Release/decrement the reference count associated with a call.

        Decrements the Camelot server's reference count associated with a call.
        A call can not be released or deleted on the server unless its
        reference count is 0 or below. Currently a call's reference count is
        incremented when a call event of type start is sent to a client
        application. It is incremented once for each client receiving the
        event. It is the responsibility of each client to decrement the
        reference count via releasecallref when the client is done processing
        the call. This ensures the call is not deleted inadvertently via
        releasecalls or autorelease before the client can process the call.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.release_call_ref(0x010a5650)
        True
        '''

        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')

        return self._binary_to_boolean(
            self._query_camelot(camelot.RELEASE_CALLREF, call_ref))

    def release_streams(self, stream_ref=None):
        ''' Release resources associated with the stream

        Releases all resources associated with the specified stream.
        The stream must be in the closed state.  Upon successful completion,
        the specified stream reference can no longer be used in future
        method invocations.  If -streamref is omitted, all closed streams
        on the endpoint are released.

        :parameter stream_ref: stream reference.  can be get from get_streams()

        '''
        if stream_ref and not self._is_valid_call_ref(stream_ref):
            raise camelot.CamelotError('Invalid call reference')

        return self._query_camelot(camelot.RELEASE_STREAMS, stream_ref)

    def onhook(self, callref=None, **kwargs):
        '''Clicks on phones hookswitch

        Sends an onhook protocol message to disconnect a call. If successful,
        the call transitions to the disconnecting state and then to the
        disconnected state.

        :parameter call_ref: call reference

        :returns: 1 if onhook is successful else False

        >>> ep1.onhook('0xf2c3a4a0')
        True

        Unknown call reference

        >>> ep1.onhook('0xf2c3a4a')
        'invalid call reference'
        '''
        call_ref = kwargs.get('call_ref', None)
        if call_ref:
            callref = call_ref
        if not callref or not self._is_valid_call_ref(callref):
            log.error('Invalid call reference')
            return
        ret_val = self._query_camelot(camelot.ONHOOK, callref)
        return self._binary_to_boolean(ret_val)

    def offhook(self, callref=None, **kwargs):
        '''Initiate or answer a call

        Sends an off-hook protocol message to originate or answer a call

        If no arguments are specified, then an outbound call is attempted.
        Upon return, the outbound call will be in the outbound state.
        Once the off hook protocol message as been acknowledged
        (if necessary), the call will transition to the offhook state.
        Once the line has been seized, glare resolved, and dial tone
        detected, the call will progress to the dialtone state.

        To answer an inbound call, a call reference must be specified, and
        the specified call must be in the incoming state.  Upon success,
        the call transitions from the incoming state to the answering
        state and then to the connected state.

        For those call control protocols that do not support the notion of
        going off hook, call setup may not actually commence until
        the dial method is invoked.

        :parameter call_ref: call reference

        :returns: Upon success, the call reference of the new outbound or
         answered call is returned.  Otherwise False is returned.

        Offhook the endpoint

        >>> ep1.offhook()
        '0xf22076a8'

        Offhook in failure

        >>> ep1.offhook()
        False

        Calls on endpoint after offhook

        >>> ep1.get_calls()
        [{'CallState': 'dialtone',
        'Id': '0xf22076a8',
        'Line': '1',
        'Ref': '0xf22076a8'}]
        '''
        call_ref = kwargs.get('call_ref', None)
        if call_ref:
            callref = call_ref
        if callref and not self._is_valid_call_ref(callref):
            raise camelot.CamelotError('call reference not valid')

        ret_val = self._query_camelot(camelot.OFFHOOK, callref)
        return self._binary_to_boolean(ret_val)

    def newcall(self, lineref=None, **kwargs):
        ''' Initiates a call

        Sends a newcall  protocol message to originate a new call
        Upon return, the outbound call will be in the outbound state.
        Once the newcall protocol message as been acknowledged (if necessary),
        the call will transition to the offhook state. Once the line has been
        seized, glare resolved, and dial tone detected, the call will progress
        to the dialtone state.  The new outbound call will be attempted on the
        specified line if a line reference is specified. Otherwise, the
        endpoint will choose which line to use.

        If the call control protocol has no newcall protocol message, this
        method is identical to offhook for outbound calls with the additional
        ability to specify the line for the outbound call.

        :returns: Upon success, the call reference of the new outbound call
         is returned.  Otherwise False is returned, and error information
         CamelotError exception is raised.
        '''
        log.debug('Entering method newcall()')
        line_ref = kwargs.get('line_ref', None)
        if line_ref:
            lineref = line_ref
        if lineref:
            if sys.version_info < (3, 5):
                if not isinstance(lineref, (int, long)) or lineref < 0:
                    raise camelot.CamelotError('invalid line reference')
            else:
                if not isinstance(lineref, int) or lineref < 0:
                    raise camelot.CamelotError('invalid line reference')
        ret_val = self._query_camelot(camelot.NEWCALL, lineref)
        return self._binary_to_boolean(ret_val)

    def select_line(self, lineref):
        '''Send a line/feature button selection protocol message

        Sends a line selection  protocol message (for SCCP this is a station
        stimulus message).  Depending on the state of the line, this may
        generate a new outbound call if no call already exists on the specified
        line, disconnect an outbound call during setup, answer an inbound call
        if an incoming call exists on the specified line, or resume a call
        if a held call exists on the specified line. If the button is
        associated with any CCM feature, this sends a station stimulus message
        with the appropriate device stimulus.

        :parameter line_ref: line reference

        :returns: True or False

        >>> ep.select_line(1)
        True

        '''
        log.debug('Entering method select_line()')
        if lineref:
            if sys.version_info < (3, 5):
                if not isinstance(lineref, (int, long)) or lineref < 0:
                    raise camelot.CamelotError('invalid line reference')
            else:
                if not isinstance(lineref, int) or lineref < 0:
                    raise camelot.CamelotError('invalid line reference')
        ret_val = self._query_camelot(camelot.SELECT_LINE, lineref)
        return self._binary_to_boolean(ret_val)

    def select_plk(self, buttonref):
        '''New command to initiate the CME HLog PLK Login/Logout
           Note:This command is applicable for only SCCP endpoints

        This command is only for SCCP endpoints,which are interfacing with CME.
        Sends a Station Stimulus SCCP protocol message. If the button is
        associated with any CME feature, this command sends a station stimulus
        message with the appropriate device stimulus data.

        :parameter button_ref: button index.  It can be get from get_info_ext()

        :returns: True or False

        >>> ep.select_plk(1)
        True

        '''
        log.debug('Entering method select_plk()')
        if buttonref:
            if sys.version_info < (3, 5):
                if not isinstance(buttonref, (int, long)) or buttonref < 0:
                    raise camelot.CamelotError('invalid button reference')
            else:
                if not isinstance(buttonref, int) or buttonref < 0:
                    raise camelot.CamelotError('invalid button reference')
        ret_val = self._query_camelot(camelot.SELECT_PLK, buttonref)
        return self._binary_to_boolean(ret_val)

    def reject(self, call_ref,
               response_code='403', reason='Q.850;cause=21', retry_after=None):
        '''Reject an inbound call

        Reject an inbound call by allowing it to go unanswered.  Upon method
        invocation, the call transitions to the rejecting state and then
        to the disconnected state when the remote peer abandons the call.

        Some call control protocols may also support an active or forced
        reject mechanism where by the call is immediately disconnected
        rather than allowed to go unanswered.

        :parameter call_ref: - call reference
        :parameter response_code: - inbound call response code
        :parameter reason: - reason to reject the inbound call.
         If reason value is None then Camelot will not send Reason header.
        :parameter retry_after: - indicates how long(in seconds) the
         service/user is expected to be unavailable.
        :returns: True if successfully clicked, False in case of failure

        >>> ep1.place_call('880002')
        '0xb79fdd8'
        >>> ep1.get_calls()
        [{'CallState': 'alerting',
          'Id': '0xb79fdd8',
          'Line': '1',
          'Ref': '0xb79fdd8'}]
        >>> ep2.get_calls()
        [{'CallState': 'incoming',
          'Id': '0xb79fdd8',
          'Line': '1',
          'Ref': '0xb79fdd8'}]
        >>> ep2.reject('0xb79fdd8')
        True
        >>> ep2.get_calls()
        [{'CallState': 'rejecting',
          'Id': '0xb79fdd8',
          'Line': '1',
          'Ref': '0xb79fdd8'}]
        >>> time.sleep(5)
        >>> ep2.get_calls()
        [{'CallState': 'disconnected',
          'Id': '0xb79fdd8',
          'Line': '1',
          'Ref': '0xb79fdd8'}]
        >>> ep1.place_call('880002')
        '0xb79fdd8'
        >>> ep1.get_calls()
        [{'CallState': 'alerting',
          'Id': '0xb79fdd8',
          'Line': '1',
          'Ref': '0xb79fdd8'}]
        >>> ep2.get_calls()
        [{'CallState': 'incoming',
          'Id': '0xb79fdd8',
          'Line': '1',
          'Ref': '0xb79fdd8'}]
        >>> ep2.reject(call_ref='0xb79fdd8',response_code='603',reason='None')
        True
        >>> ep2.get_calls()
        [{'CallState': 'rejecting',
          'Id': '0xb79fdd8',
          'Line': '1',
          'Ref': '0xb79fdd8'}]
        >>> time.sleep(5)
        >>> ep2.get_calls()
        [{'CallState': 'disconnected',
          'Id': '0xb79fdd8',
          'Line': '1',
          'Ref': '0xb79fdd8'}]
        '''
        log.debug('Entering method reject().')
        if not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('call reference not valid')
        if not reason:
            raise camelot.CamelotError('reason is empty')
        if not response_code:
            raise camelot.CamelotError('response_code is empty')
        kwargs = {'response_code': response_code,
                  'reason': reason,
                  'retry_after': retry_after}
        ret_val = self._query_camelot(camelot.REJECT, call_ref, **kwargs)
        return self._binary_to_boolean(ret_val)

    def dial_via_office(self, callref, mode, callbacknumber=None,
                        called=None):
        '''Initiate a dial-via-office call placing on Camelot mobile clients.

        Initiate a dial-via-office specific call placing according to
        the specified mode.  For a new outbound call, this method will
        typically be called when the call progresses to the offhook and/or
        dialtone state.  Upon successful initiation of dialing and dial tone
        has been removed, the call progresses to the dialing state.  After
        addressing is complete and has been accepted by the remote end, the
        call progresses to the proceeding state.  Once the remote end is
        alerted of the new call and ring-back detected the call progresses to
        the alerting state.  After the remote end answers the call, the call
        progresses to the connected state.

        If the call mode is set to forward then the DID/Enterprise Feature
        Access number should be available via the getcallinfoext command.
        If the call mode is not set, by default, it executes reverse
        dialviaoffice. If the call mode is set to lcr , CUCM would apply the
        LCR rules configured on it and decides whether the call mode to be
        forward or reverse. Once the mode is decided the behavior of the
        call is same as the respective mode.   If callbackno is provided, then
        this line will receive the dialviaoffice reverse call instead of
        mobile client.

        mode with  lcrhandout will be applicable for DMC endpoints.Dmc calltype
        value shall be set to 0, before calling dialviaoffice with mode
        lcrhandout. The intension of lcrhandout is to switch the call from VoIP
        line to Cellular line on DMC endpoints.  Called parameter is
        optional for lcrhandout mode.

        :parameter callref: call reference of call
        :parameter called: called party address
        :parameter mode: call mode.  The possible values are \n
            * forward
            * reverse
            * lcr
            * lcrhandout
        :parameter callbackno: directory number of a non remote destination
                               to receive the call(applicable for dialviaoffice
                               reverse and lcr/reverse modes)

        :returns: True or False

        >>> ep.dial_via_office('0xb79fdd8', 'forward', '88001', '88002')
        True
        '''

        if not callref or not self._is_valid_call_ref(callref):
            raise camelot.CamelotError('Invalid call reference')
        if not mode or mode not in ('forward', 'reverse', 'lcr', 'lcrhandout'):
            raise camelot.CamelotError('Invalid mode')
        if not called and 'lcrhandout' not in mode:
            raise camelot.CamelotError('called number is not specified')

        kwargs = {'called': called,
                  'mode': mode,
                  'callbackno': callbacknumber}

        return self._binary_to_boolean(
            self._query_camelot(camelot.DIAL_VIA_OFFICE, callref, **kwargs))

    def dmchandin(self, called='null', calling='null', calltype=0, lineref=0,):
        ''' Switches call from cellular mode to Voip mode on DMC end points

        This command is used to switch the mode from cellular line to Voip line
        on a DMC end point. The call should  be made from the DMC end point
        to the mobile handoff number configured in the call manager. The
        calltype on the dual mode camelot client should be set to Voip i.e. 1,
        before invoking this command.On successful initiation the cellular call
        on the dual mode client will be disconnected and a Voip call
        will be established.

        :parameter called: mobile handoff numbr configured in UCm
        :parameter calling: calling number
        :parameter calltype: call type.  Possible values \n
            * 0 - Cellular
            * 1 - Mobile
        :parameter lineref: line index of the call to be switched.

        :returns: Callreference or False (if failed)

        >>> ep.dmchandin(called='88002',lineref=1)
        '0xb79fdd8'
        '''
        log.debug('Entering method dmchandin()')
        if lineref:
            if sys.version_info < (3, 5):
                if not isinstance(lineref, (int, long)) or lineref < 0:
                    raise camelot.CamelotError('invalid line reference')
            else:
                if not isinstance(lineref, int) or lineref < 0:
                    raise camelot.CamelotError('invalid line reference')
        kwargs = {'calling': calling,
                  'calltype': calltype,
                  'lineref': lineref}
        return self._binary_to_boolean(
            self._query_camelot(camelot.DMC_HANDIN, called, kwargs))

    def enable_mobile_connect(self):
        ''' enables mobile connect.
        Specific usage is for CUMC endpoints

        :returns: True or False

        >>> ep.enable_mobile_connect()
        '''

        return self._binary_to_boolean(
            self._query_camelot(camelot.ENABLE_MOBILE_CONNECT, '1'))

    def disable_mobile_connect(self):
        ''' disables mobile connect.
        Specific usage is for CUMC endpoints

        :returns: True or False

        >>> ep.enable_mobile_connect()
        '''

        return self._binary_to_boolean(
            self._query_camelot(camelot.ENABLE_MOBILE_CONNECT, '0'))

    def get_fax_info(self, call_ref):
        '''Get fax-related information on a call
        Retrieve current information about a fax session on a call.
        If a call has more than one fax transmission, this method
        retrieves information about the last session.

        :parameter callref: call reference

        :returns: dictionary of fax call info with following field values.
            * state - state of the session.  Possible values \n
                * idle - fax session has not started.\n
                * connecting - fax terminals connecting.\n
                * negotiating - fax terminals negotiating a modem and speed.\n
                * sending - fax terminal sending a fax.\n
                * receiving - fax terminal receiving a fax.\n
                * done - fax session complete.\n
                * error - fax session did not complete but had an error.\n
            * page - page number currently being transferred.\n
            * modem - modem selected for transfer, v27, v29, v33, or v17.\n
            * rate -  rate selected for transfer, 2400, 4800, 7200, 9600,
                      12000, or 14400.\n
            * url - tiff file currently being transferred.
            * error - error information if state is error.
        '''

        if call_ref and self._is_valid_call_ref(call_ref):
            return self._query_camelot(camelot.GET_FAX_INFO, call_ref)
        else:
            raise camelot.CamelotError('Invalid call refernce')

    def get_ice_info(self, call_ref, ptype=None, subtype=None, fixup=0):
        '''
        Get an endpoint ICE specific statistics.
        Can extract ICE specific parameters received from far end.

        :parameter callref: call reference.
        :parameter ptype: type of media like audio, video etc. if not used
                          session params will be displayed.
        :parameter subtype: in case of multiple video this field can be used to
                          specify type of video like slides, presentation etc.
                          default value is None.
        :parameter fixup: when this flag is given ICE Parameters received in
                          fixup SDP will be shown and if this is not set only
                          parameters received in main SDP will be shown.

        :returns: dictionary of fax call info with following field values.\n
            * candidates - shows all candidates received from far end in list
                           format.
            * ufrag - ufrag received from far end.
            * pwd - pwd received from far end.
            * options - options received from far end.
            * rem-cand - remote candidates recevied from far end.
            * ice-mismatch - 'true' if ice-mismatch is received else 'false'.

        >>> ep1.get_ice_info('0xf13244')
            {'candidates': '',
             'ice-mismatch': 'false',
             'options': 'rtp+ecn',
             'pwd': 'SypB+3lO0wbhmnRz4pJedeGS',
             'rem-cand': '',
             'ufrag': 'ShfOWS'}
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            kwargs = {'type': ptype,
                      'subtype': subtype,
                      'fixup': fixup}
            return self._query_camelot(camelot.GET_ICE_INFO, call_ref, kwargs)
        else:
            raise camelot.CamelotError('Invalid call refernce')

    def get_ice_details(self, call_ref):
        '''Get an endpoint ICE specific statistics.
        Can extract ICE specific parameters generated locally and
        received from far end.


        :parameter callref: call reference

        :returns: JSON of Hedge call info with following field values.\n
            * local-candidate and remote-candidate - shows all local and
              candidates received from far end in list format.
            * local-parm and remote-parm  - shows ufrag and password of
              local and remote

        >>> ep1.get_ice_details('0xf13244')
        {'AUDIO':
        {'remote_parms': {
          'passwd': '',
          'ufrag': '4fa'},
         'local_candidates':[
         ''Ha6925ba 1 UDP 2130706431 10.105.37.186 21634 typ host',
          'Sa6925ba 1 UDP 1694498815 10.105.37.186 21634 typ srflx raddr
           10.105.37.186 rport 21634',
          'Ra6925ba 1 UDP 16777215 128.107.0.231 24000 typ relay raddr
           10.105.37.186 rport 21634'],
        'local_parms': {
                       'passwd': '52d1de0',
                       'ufrag': '077d4b9'},
        'remote_candidates': [
        'Ha6925ba 1 UDP 2130706431 10.105.37.186 21899 typ host',
        'Sa6925ba 1 UDP 1694498815 10.105.37.186 21899 typ srflx raddr
         10.105.37.186 rport 21899',
        'Ra6925ba 1 UDP 16777215 128.107.0.231 24001 typ relay raddr
         10.105.37.186 rport 21899',
        'vcs 1 UDP 16777470 128.107.0.231 42256 typ host']
              }
        }
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._query_camelot(camelot.GET_ICE_DETAILS, call_ref)
        else:
            raise camelot.CamelotError('Invalid call refernce')

    def config_ice_candidate_order(self, candidate=None):
        '''Get/Set the ICE candidate order list

        :parameter candidate: Is an order list which need to be set
              for next call.
              If list is None then it will return the current used list.
              If list has only empty string or empty list then the current
              order will be reset to Camelot default.
              If list has only member other than
              "host","srflx","relay" then api will raise ValueError exception.
        :returns: If input is None then, returns the current candiate order
            list used.

        >>> ep1.vapi.config_ice_candidate_order()
        [u'host', u'srflx', u'relay'] #Current/Camelot default

        >>> ep1.vapi.config_ice_candidate_order(
        candidate=['srflx','host','relay'])
        [u'srflx', u'host', u'relay']
        >>> ep1.vapi.config_ice_candidate_order()
        [u'srflx', u'host', u'relay'] # Currently set

        >>> ep1.vapi.config_ice_candidate_order([''])
        [] # reset to Camelot default
        >>> ep1.vapi.config_ice_candidate_order()
        [u'host', u'srflx', u'relay'] #back to Camelot default

        For more information on how users can overwrite the above values
        and how camelot determines those explained in camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/ICE+and+TURN+support
        '''
        operation = 1
        cand_present = 0
        if candidate is None:
            operation = 0
        elif len(candidate) == 1:
            for x in candidate:
                if x == '' or x == ' ':
                    cand_present = 0
                elif x not in ("relay", "host", "srflx"):
                    cand_present = 0
                    raise camelot.CamelotError('invalid candidates')
        elif len(candidate) > 1:
            cand_present = 1
            for x in candidate:
                if x not in ("relay", "host", "srflx"):
                    cand_present = 0
                    raise camelot.CamelotError('invalid candidates')
        else:
            cand_present = 0

        if cand_present == 0:
            candidate = []
        ret = self._query_camelot(camelot.CONF_ICE_CAND, operation, candidate)
        return ret

    def update_call(self, call_ref, sdp_option):
        '''
        once the call is established update_call() helps, to
        send the mid call update message to the other end.

        :parameter call_ref: reference of the call
        :parameter sdp_option: it is string type parameter and it is optional\n
         * user can pass the parameter list to update the sdp portion of
           UPDATE message. Parameter list is Below:

             * audioport - it takes the following values:
                    * nonzero - audio port will be refreshed.
             * videoport - it takes the following values:
                    * nonzero - video port will be refreshed.
             * ipv4address - ipv4 address will be refreshed at the
                             session level.
             * vidpayloadtype - dynamic video payload type.

         *  Below are the examples:
              ipv4Address:10.105.37.185
              ipv4Address:10.105.37.185;audioport:nonzero;videoport:nonzero
              ipv4Address:10.105.37.185;vidpayloadtype:122

        :returns: True on success  otherwise False is returned.
                 For error the CamelotError exception is raised

        >>> ep1.update_call('0x010a5650', 'ipv4Address:10.105.37.185')
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call refernce')
        if not sdp_option:
            sdp_option = 'null'

        return self._query_camelot(camelot.UPDATE_CALL, call_ref, sdp_option)

    def set_reinvite_response(self, call_ref='null', value='408',
                              reason_phrase='Request Timeout', repeat='1',
                              initial_invite=False):
        '''
        Set reinvite response - set the response code for mid call reinvite
        or initial invite.
        The sip error response with the set response code and
        reason_phrase will be sent immediately after receiving invite (for re-
        invite also), meaning neither 100 Trying nor 180 ringing will be sent
        before responding with error response.

        `Refer the following wiki link for sample scripts and demo recording-
        <https://wiki.cisco.com/display/CAMELOT/Simulated+endpoint+features+to
        +overcome+raw+endpoint+challenges#Simulatedendpointfeaturestoovercomeraw
        endpointchallenges-4xx/5XX/6XXforinitialinviteormid-callre-invite>`_

        RE-INVITE

        When a mid call reinvite is received by endpoint, user can set what
        needs to be responded for it. It sets the response code to be
        considered only for a particular call or all calls of an endpoint.
        Also user can decide for how many times to repeat to send the
        response with the given value for the reinvites. \n
        If the call_ref is given, re-invite is responded with the configured
        response code value only for that call/dialog. if no call_ref is given,
        re-invite is responsed with the configured response code value for all
        the calls/dialogs and for each call the repeat value is set with the
        original value. i.e for example, if repeat is configured as 2 and no
        call_ref is given, for first call, the first two revinvite will be
        responded with the value. And again for second call, the first two
        reinvite will be responded with the value.

        :parameter call_ref:    call reference of a call.

        :parameter value:       value of SIP Response code.possible values:\n
                                * 0 - no resposne will be sent for re-invite
                                * any 4xx/5xx/6xx response code

        :parameter reason_phrase:  reason phrase with respect to the value.
                                   if value is given but no reason phrase, then
                                   camelot will send the standard reason phrase
                                   of the value.

        :parameter repeat:   It decides, for how many reinvites the configured
                             value should be considered.
                             Possible options are given below:\n
                             * 0 - configured value wont be considered and
                                   normal flow for reinvite will happen
                             * -1 - configured values will be considered for
                                  all mid call reinvites
                             * any valid integer.
                                If 4, for example,configured value will be sent
                                for 4 reinvites only.

        :parameter initial_invite: set response code, reason phrase and repeat
                values for initial invite or reinvite.default is for reinvite.

        :returns: On error, CamelotError Exception will be thrown.

        >>> ep1.place_call('76553')
        '0xf1706408'
        >>> ep1.set_reinvite_response(call_ref='0xf1706408',value='487',
        ...                           repeat=1)
        >>> ep2.get_calls()
        [{'CallState': 'connected',
          'Id': '0xaa2beb8',
          'Line': '1',
          'Ref': '0xaa2beb8'}]
        >>> ep2.hold('0xaa2beb8')
        True

        In the above case, ep1 will receive reinvite and respond with
        487 Request Terminated

        >>> ep1.place_call('76558')
        '0xf0f7d2b0'
        >>> ep3.enable_auto_answer(delay=0)
        'enabled'
        >>> ep3.get_calls()
        [{'CallState': 'connected',
          'Id': '0xaa2aea8',
          'Line': '1',
          'Ref': '0xaa2aea8'}]
        >>> ep3.hold('0xaa2aea8')
        True

        In the above case, ep1 will receive reinvite and respond with
        normal response (200 OK, if no internal errors).  Becasuse
        set_reinvite_response is not invoked and earlier we have set it
        only for that call.

        If the user wants to make the set_reinvite_response to
        work for all calls:

        >>> ep1.set_reinvite_response(value='408', repeat='-1')

        This will make the endpoint to respond 408 Request Timeout for
        all the reinvites it receives.

        INITIAL INVITE

        When a initial invite is received by endpoint, user can set what
        needs to be responded for it. It sets the response code to be
        considered for all calls of an endpoint.
        Also user can decide for how many times to repeat to send the
        response with the given value for the initial invite. \n
        The call_ref should not be given in case of initial invite,
        initial invite is responsed with the configured response code value
        for all the calls and for each call the repeat value is
        set with the original value. i.e for example, if repeat is configured
        as 2 the first two initial invite will be
        responded with the value.

        >>> ep2.set_reinvite_response(call_ref='0xf1706408',value='487',
        ...                           repeat=1, initial_invite=True)
        >>> ep1.place_call('76553')
        '0xf1706408'

        >>> ep1.get_calls()
        [{'CallState': 'disconnected',
          'Id': '0xaa2beb8',
          'Line': '1',
          'Ref': '0xaa2beb8'}]
        >>> ep1.get_calls()
        []

        In the above case, ep2 will receive invite and respond with
        487 Request Terminated

        '''

        log.debug('Entering method set_reinvite_response().')

        if call_ref != 'null' and not self._is_valid_call_ref(call_ref):
            raise Exception("Invalid Call Reference")

        if str(value) != '408' and str(reason_phrase) == 'Request Timeout':
            reason_phrase = 'null'

        if initial_invite:
            initial_invite = '1'
        else:
            initial_invite = '0'

        kwargs = {'value': value,
                  'reason_phrase': reason_phrase,
                  'repeat': repeat,
                  'initial_invite': initial_invite
                  }
        return self._query_camelot(
            camelot.SET_REINVITE_RESPONSE, call_ref, **kwargs)

    def get_confid_list(self):
        '''
        Get the list of all AdHoc Conference ids and their active status.
        This command is supported for SIP TRUNK only.

        :returns: On error, CamelotError Exception will be thrown.

        >>> ep1.get_confid_list()
        [{'status': 'active', 'confid': '111111'},
         {'status': 'inactive', 'confid': '222222'}]

        '''

        log.debug('Entering method get_confid_list().')

        return self._query_camelot(
            camelot.GET_CONFID_LIST)

    def clear_inactive_conference(self):
        '''
        Clear all inactive conference ids from the list.
        This command is supported for SIP TRUNK only.

        :returns: On error, CamelotError Exception will be thrown.

        >>> ep1.get_confid_list()
        [{'status': 'active', 'confid': '111111'},
         {'status': 'inactive', 'confid': '222222'}]

        >>> ep1.clear_inactive_conference()

        >>> ep1.get_confid_list()
        [{'status': 'active', 'confid': '111111'}]

        '''

        log.debug('Entering method clear_inactive_conference().')

        return self._query_camelot(
            camelot.CLEAR_INACTIVE_CONFERENCE)

    def get_conf_calls(self, confid=None):
        '''
        Retrieve current calls associated with a confid.

        The required confid can be picked from get_confid_list()
        This command is supported for SIP TRUNK only.

        :parameter confid:    confid of a AdHoc Conference

        :returns: A variable sized list. Each element in the list is a
                    camelot.response.Call object with following attributes:\n
                        :call_ref: call reference of call
                        :line: line associated with call
                        :state: current state of call


        >>> ep1.get_confid_list()
        [{'status': 'active', 'confid': '111111'},
         {'status': 'inactive', 'confid': '222222'}]
        >>> ep1.get_conf_calls(confid='111111')
        [{'CallState': 'connected',
          'Id': '0xaa2beb8',
          'Line': '1',
          'Ref': '0xaa2beb8'}
        {'CallState': 'connected',
          'Id': '0xbb2beb8',
          'Line': '1',
          'Ref': '0xbb2beb8'}
        {'CallState': 'connected',
          'Id': '0xcc2beb8',
          'Line': '1',
          'Ref': '0xcc2beb8'}
        {'CallState': 'connected',
          'Id': '0xdd2beb8',
          'Line': '1',
          'Ref': '0xdd2beb8'}]

        '''

        log.debug('Entering method get_conf_calls().')

        if confid != 'null' and not self._is_valid_call_ref(confid):
            raise Exception("Invalid confid")

        return self._query_camelot(
            camelot.GET_CONF_CALLS, confid)

    def get_conf_streams(self, confid=None):
        '''
        Return the media streams associated with a confid.

        The required confid can be picked from get_confid_list().
        This command is supported for SIP TRUNK only.

        :parameter confid:    confid of a AdHoc Conference

        :returns: A variable sized list. Each element in the list is a
                    camelot.response.Stream object


        '''

        log.debug('Entering get_conf_streams function')

        # if confid and self._is_valid_call_ref(confid):
        #    raise Exception("Invalid confid")

        stream_list = self._query_camelot(camelot.GET_CONF_STREAMS, confid)
        ret_list = []
        if self._get_server_conn().output_format != 'json':
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

    def send_dtmf(self, call_ref, dtmf_digits=''):
        '''
        This funciton is applicable only fo CAS endpoint to send DTMF
        digits from a given call reference.

        :parameter call_ref: valid callreference
        :parameter dtmf_digits: DTMF digits to send. Valid ditits are:\n
                                * 0 - 9, A - D, * and #
        :return: True or False
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call refernce')
        if not dtmf_digits:
            raise camelot.CamelotError('DTMF digits should not be empty')

        return self._query_camelot(camelot.SEND_DTMF, call_ref, dtmf_digits)

    def setup_fax_call_options(self, call_ref, fax_profile):
        '''
        This function is applicable only for CAS endpoint to set fax
        options for a particular call.  Fax options are like enable interrupt,
        enable color, etc.,

        :parameter call_ref: valid call reference
        :parameter fax_profile: Object of FaxProfile class\n
                               The FaxProfile here takes LocalFaxId,
                               FaxHeadLine and MaxSpeed as
                               camelot.DivaFaxMaxSpeed\n
                               class DivaFaxMaxSpeed(Enum):\n
                                    DivaFaxMaxSpeedAutomatic = 0\n
                                    DivaFaxMaxSpeed2400 = 2400\n
                                    DivaFaxMaxSpeed4800 = 4800\n
                                    DivaFaxMaxSpeed7200 = 6200\n
                                    DivaFaxMaxSpeed9600 = 9600\n
                                    DivaFaxMaxSpeed14400 = 14400\n
                                    DivaFaxMaxSpeed33600 = 33600\n
        :return: True or Camelot exception\n
                 Possible exceptions are:\n
                 1. Interface error
                       * This will happen if something wrong with Diva SDK API
                 2. Invalid callrerence
                       * This will happen if call reference is not valid

        >>> profile = FaxProfile()
        >>> profile.diva_fax_options =
        [DivaFaxOptions.DivaFaxOptionEnableColor,
        DivaFaxOptions.DivaFaxOptionDisableECM]
        >>> ep2.vapi.enable_auto_answer(delay=0)
        >>> ep1.vapi.place_call('1002')
        >>> '0xfe211abef'
        >>> ep1.vapi.setup_fax_call_options('0xfe211abef', profile)
        >>> True
        '''

        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call refernce')
        if fax_profile and isinstance(fax_profile, FaxProfile):
            if fax_profile.diva_fax_options and \
                (type(fax_profile.diva_fax_options) is not
                 list or all(isinstance(fo, DivaFaxOptions)
                             for fo in fax_profile.diva_fax_options) is False):
                raise camelot.CamelotError('Invalid FaxOptions')
            if not isinstance(fax_profile.default_fax_speed,
                              camelot.DivaFaxMaxSpeed):
                fax_profile.default_fax_speed = \
                    camelot.DivaFaxMaxSpeed.DivaFaxMaxAutomatic
        return self._query_camelot(camelot.SETUP_FAX_CALL_OPTIONS,
                                   call_ref, fax_profile)
