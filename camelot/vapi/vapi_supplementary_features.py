import camelot
import json
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger

log = camlogger.getLogger(__name__)


class CamelotSFeatureControl(v.CamelotVapiUtils):

    '''Camelot supplementary feature representation
    '''

    def __init__(self):
        pass

    def blind_transfer(self, call_ref, called):
        ''' Blind Transfer a call

        Do blind call transfer on Legacy SIP endpoints registered with CME.

        The invocation of this command puts the specified call on hold
        awaiting transfer.  A new outbound call is automatically generated from
        the Transferee to the, which will be destination of the transfer.
        After generating the new calldialing the destination number, the
        previous call that was put on hold is automatically disconnected.
        called argument can take DN or URI.

        :parameter call_ref: call reference
        :parameter called: called party address (DN or URI)

        :returns: True on Success

        >>> ep.blind_transfer('0xf2c3a4a0','880002')
        True
        '''

        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.BLIND_TRANSFER, call_ref,
                                    called))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def cme_hw_conference(self, call_ref):
        ''' Add a call to a CME based hardware conference

        initiate/add a call to a hardware conference for the CME interfacing
        SIP endpoints. The CME interfacing can be configured using
        sip.registrar.isCM is set to 2. If the specified call is not a
        hardware conference call, then invocation of this method changes
        the specified call to a hardware conference call, puts it on hold,
        and automatically generates a new outbound call. Client code can
        then setup this new call (using dial command on this new outbound call)
        and execute cmehwconference for a second time to add the new call to
        the existing hardware conference. This will resume the hardware
        conference call and new call will get disconnected by CME.

        :parameter call_ref: call reference.

        :returns: True on Success.

        >>> ep.cme_hw_conference('0xf2c3a4a0')
        True
        '''

        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.CME_HW_CONFERENCE, call_ref))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def park(self, call_ref, park_type='default'):
        '''Park a call

        Parks an active call to a number designated via the CCM configuration.
        The parked call is automatically disconnected.
        It is supported for both sipx and jabbermobile endpoints for both
        deployments On-Premise and Collab-Edge.
        Also please refer following Wiki \n
        https://wiki.cisco.com/display/CAMELOT/Call+Park

        :parameter call_ref: call reference is mandatory
        :parameter park_type: Type of park to initiate. Passible
         values \n
            * softkey - for as softkey based park (default)
            * parkmonitor   - for park monitor

        :returns: True on Success

        Note: if park_type is omitted and sip.phone.park_type is configured
        then configured value will take effect.

        >>> ep.park('0xf2c3a4a0')
        True
        >>> retrieving the parked call.
        >>> ep.placecall('parked_number')
        Oxfe12434

        >>> ep.park('0xf2c3a4a0', park_type='parkmonitor')
        True
        '''
        if park_type not in ['default', 'softkey', 'parkmonitor']:
            raise Exception('Invalid park_type')
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.PARK, call_ref, park_type))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def pickup(self, call_ref=None):
        '''pickup a call
        Picks up a call inbound on another phone in the same CCM
        configured group.  To answer a call bound to another endpoint
        within your call pickup group, first initiate a new call, then
        invoke pickup.  The inbound call will be directed to this endpoint,
        and a new inbound call will be present.  The current call is
        automatically disconnected.

        Some CCMs may enable calls to be picked up without first initiating
        a new outbound call.  In this case, the call reference argument is
        optional.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.pickup('0xf2c3a4a0')
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.PICKUP, call_ref))

    def gpickup(self, call_ref=None):
        '''pickup a call

        Same as the pickup command, except it allows one to pick up calls
        targeted to an associated group. To answer a call bound to an endpoint
        in a different call pickup group, first initiate a new call then invoke
        gpickup.  Dial the desired call pickup group number.  The inbound call
        will be directed to this endpoint, and a new inbound call will be
        present.  The current call is automatically disconnected.

        Some CCMs may enable calls to be picked up without first initiating
        a new outbound call.  In this case, the call reference argument is
        optional.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.gpickup('0xf2c3a4a0')
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.GPICKUP, call_ref))

    def cell_pickup(self, call_ref=None):
        '''pickup a call

        Cellpickup is used to send the currently connected call to the
        remote destination of that phone. If the call reference is not
        mentioned then the current mobility status of the phone will be
        fetched from the CCM and could be retrieved through getstationevent.


        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.cell_pickup('0xf2c3a4a0')
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.CELL_PICKUP, call_ref))

    def opickup(self, call_ref=None):
        '''pickup a call
        Same as the pickup command, except it allows one to pick up calls
        targeted to other pickup groups. To answer a call bound to an endpoint
        in a different call pickup group, first initiate a new call then invoke
        opickup.  Dial the desired call pickup group number.  The inbound call
        will be directed to this endpoint, and a new inbound call will be
        present.  The current call is automatically disconnected.

        Some CCMs may enable calls to be picked up without first initiating
        a new outbound call.  In this case, the call reference argument
        is optional.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.opickup('0xf2c3a4a0')
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.OPICKUP, call_ref))

    def send_user_answer(self, call_ref=None):
        '''
         This command is used to send the explicit user answer notification
         and is supported for (cumc/dmc) endpoints. On issuing this command
         Camelot dmc endpoint would send an in-dialogue REFER message with the
         required xml body which indicates UCM that the call is answered by the
         user and not by voice mail.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.cell_pickup('0xf2c3a4a0')
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.SEND_USER_ANSWER, call_ref))

    def set_pref_mode(self, mode):
        '''Updates the preferred mode of a dual mode single registration
          endpoint (dmc). The updated value will reflect in the REGISTER
          message sent to CUCM.

        :parameter mode: 0 - Cellular mode, 1- VOIP mode

        :returns: 0 - Cellular mode, 1- VOIP mode

        >>> ep.set_pref_mode(1)
        1
        '''
        if str(mode) not in ['1', '0']:
            raise camelot.CamelotError('mode not specified/wrong mode')
        return self._query_camelot(camelot.SET_PREF_MODE, mode)

    def set_call_type(self, mode):
        '''Sets the call type parm and same thing is used when the next call
         is initiated on the DMC endpoint. This command is used to change the
         type of the next call to be initiated on the given DMC endpoint.

        :parameter mode: 0 - Cellular mode, 1- VOIP mode

        :returns: 0 - Cellular mode, 1- VOIP mode

        >>> ep.set_call_type(1)
        1
        '''
        if str(mode) not in ['1', '0']:
            raise camelot.CamelotError('mode not specified/wrong mode')
        return self._query_camelot(camelot.SET_CALL_TYPE, mode)

    def get_mobile_identity(self):
        '''Display the mobile identity of the endpoint and is applicable
         for (cumc) and (dmc) endpoints.

        :returns: returns mobile identity of the endpoint.

        >>> ep.get_mobile_identity()
        '''
        return self._query_camelot(camelot.GET_MOBILE_IDENTITY)

    def rmlstc(self, call_ref):
        '''Remove last conference participant

        Removes the conference participant last added to the
        specified conference call.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.rmlstc('0xf2c3a4a0')
        True
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.RMLSTC, call_ref))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def meetme(self, call_ref):
        '''Initiate a meetme conference

        Initiates a meet-me conference on an outbound call.  To initiate a
        meetme conference, initiate a new call by invoking newcall or offhook.
        Then invoke meetme and then dial the meetme conference number.
        Removes the conference participant last added to the
        specified conference call. meetme uri is picked up from
        sip.phone.sip_call_features.meetme_service_uri config parm.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.meetme('0xf2c3c4a0')
        True
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.MEETME, call_ref))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def redial(self, call_ref=None):
        '''Initiate a call to last called party

        Initiate a call to the last called address dialed.


        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.redial('0xf2c3c4a0')
        True
        '''

        if call_ref and not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')

        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.REDIAL, call_ref))

    def get_token(self):
        ''' returns the Hedge token associated with endpoint

        :returns: On success returns the Hedge token associated with
         the endpoint, else returns enpty string

        >>> ep.get_token()
        testuser_ep2@gmail.com_DEADBEEF1235
        '''

        return self._query_camelot(camelot.GET_TOKEN)

    def call_fwd_all(self, call_ref=None):
        '''Forward all inbound calls

        Inform CCM of called address to forward all inbound calls.
        Upon executing this command a new outbound call is created.
        Then use the dial method to send the called address
        (called address can be DN or URI) to CCM.  Once complete, the call is
        automatically disconnected.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.call_fwd_all('0xf2c3c4a0')
        True
        '''
        if call_ref and not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')

        return self._binary_to_boolean(
            self._query_camelot(camelot.CFWDALL, call_ref))

    def idivert(self, call_ref, eidivert_dest=None):
        '''Divert an inbound call.

        This api returns True on successful initiation of process.
        It doesn't mean that idivert process is complete.

        On success of completing idirect process from CUCM, CUCM disconnects
        the command initiator call.
        On any failures from CUCM, CUCM sends REFER with statuslineupdatereq,
        which user can validate from get_info() or from stationevent.

        :parameter call_ref: call reference
        :parameter eidivert_dest: enhanced destination number or 'Cancel'

        :returns: True on Success


        >>> ep.idivert('0xf16cc830') # passing call reference
        True
        >>> ep2.idivert('0xf16cc830', '36001') # passing
        call reference and enhanced idivert destination to be diverted
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')

        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.IDIVERT, call_ref, eidivert_dest))

    def barge(self, call_ref):
        '''Barge into a call on a shared line

        Join an active call on a shared line using conferencing resources on
        the target endpoint.  The call specified must be in the remoteinuse
        state.

        :parameter call_ref: call reference

        :returns: True on Success and exception on failure

        >>> ep.barge('0xf2c3c4a0')
        True
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.BARGE, call_ref))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def cbarge(self, call_ref):
        '''Barge into a call on a shared line converting the call to a
        conference call

        Join an active call on a shared line using shared conferencing
        resources.  The barge call becomes a standard conference call.
        The call specified must be in the remoteinuse state.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.cbarge('0xf2c3c4a0')
        True
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.CBARGE, call_ref))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def select(self, call_ref):
        '''Select calls for subsequent invocation of a supplementary service

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.meetme('0xf2c3c4a0')
        True
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.SELECT, call_ref))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def privacy(self):
        '''Toggle privacy on/off for an endpoint sharing a line

        Toggle privacy on/off for the specified endpoint.
        This can be invoked only on a shared line.

        :returns: True on Success

        >>> ep.privacy()
        True
        '''
        return self._binary_to_boolean(
            self._query_camelot(camelot.PRIVACY))

    def join(self, call_ref):
        '''Join selected calls into an ad hoc conference

        Join the specified call and other selected calls into an
        ad hoc conference.
        See also ep.select.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.join('0xf2c3c4a0')
        True
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.JOIN, call_ref))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def direct_transfer(self, call_ref):
        '''Transfer two selected calls to each other

        Directly transfer two selected calls to each other.
        The call reference specified should be one of the selected calls.


        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.direct_transfer('0xf2c3c4a0')
        True
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.DIRECT_TRANSFER, call_ref))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def callback(self, call_ref):
        '''Get notified when a called party is available

        Inform CCM to alert endpoint when remote party becomes available.


        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.callback('0xf2c3c4a0')
        True
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.CALL_BACK, call_ref))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def conflist(self, call_ref):
        '''Get a list of conference participants

        Get CCM to send a list of conference participants.
        This information is returned via userdata station event.

        Note: When conflist() API is used, Camelot sends a REFER with XML body
        having <softkeyevent>ConfList</softkeyevent>.
        If we get an non-success/error response for this
        then the userdata station event will not be sent.

        The conflist() API is supported for both On-Prem and MRA deployments.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.conflist('0xf2c3c4a0')
        True

        >>> Sample userdata station event:
        Received Event: <camelot.events.Event object at 0x7f29d9c009d0>
        Event sub type : userdata
        Event message: 20:24:26:270 userdata (nil) 0x00000000 0x0100000a
        <?xml version="1.0" encoding="UTF-8" ?><CiscoIPPhoneIconFileMenu>
        <Title IconIndex="1">Conferee List</Title>
        <Prompt>Make Your Selection</Prompt><MenuItem><IconIndex>1</IconIndex>
        <Name>1200003</Name><URL>UserCallData:0:0:30592909:16777226:30592913</URL>
        </MenuItem><MenuItem><IconIndex>1</IconIndex>
        <Name>1200002</Name><URL>UserCallData:0:0:30592909:16777226:30592910</URL>
        </MenuItem><MenuItem><IconIndex>1</IconIndex>
        <Name>1100001 *</Name>
        <URL>UserCallData:0:0:30592909:16777226:30592909</URL>
        </MenuItem><SoftKeyItem><Name>Update</Name><Position>1</Position>
        <URL>UserCallData:0:0:30592909:16777226:Update</URL>
        </SoftKeyItem><SoftKeyItem>
        <Name>Exit</Name><Position>3</Position><URL>SoftKey:Exit</URL>
        </SoftKeyItem><SoftKeyItem>
        <Name>Remove</Name><Position>4</Position><URL>SoftKey:Select</URL>
        </SoftKeyItem><IconItem><Index>1</Index><URL>Resource:Icon.Connected</URL>
        </IconItem><IconItem><Index>2</Index><URL>Resource:Icon.AuthenticatedCall</URL>
        </IconItem><IconItem><Index>3</Index><URL>Resource:Icon.SecureCall</URL>
        </IconItem><IconItem><Index>4</Index><URL>Resource:AnimatedIcon.RingIn</URL>
        </IconItem><IconItem><Index>5</Index><URL>Resource:AnimatedIcon.Hold</URL>
        </IconItem></CiscoIPPhoneIconFileMenu>
        '''
        if call_ref and self._is_valid_call_ref(call_ref):
            return self._binary_to_boolean(
                self._query_camelot(camelot.CONFLIST, call_ref))
        else:
            raise camelot.CamelotError('Invalid call reference')

    def flash(self, call_ref, flash_length=500, time_out=2000):
        '''
        For Skinny endpoints,
        It sends flash softkey event to CCM.
        It actually sends StationSoftKeyEventMessage to CCM
        to simulate hookflash

        For CAS endpoints,
        It invokes DivaSendFlash.

        :parameter call_ref: reference for the call. Its mandatory param.

        :parameter flash_length: flash length, Only needed for CAS endpoints.
         default value '500' will be set on absence of this value.

        :parameter time_out: time out , Only needed for CAS endpoints
         default value is '2000' (in millisecond) will be set on
         absence of this value.

        :returns: True On success.

        For skinny endpoints this API returns
        immediately on success or failure. But for CAS endpoints, after
        successful processing of Diva API it does not return immediately.
        For CAS, this API will return only when 'DivaEventFlashCompleted'
        is received by Camelot from Diva Board. In case this event is
        not received, this API will wait for "time_out" duration and
        will throw Camelot Error.

        Please refer the following wiki link to know different possible
        return texts on failure (only for CAS endpoints).
        `<https://wiki.cisco.com/display/CAMELOT/Analog+ATA-190+Voice+Support#
        AnalogATA-190VoiceSupport-SupportofHookFlashfunctionalityinCamelot>`_

        >>> ep.flash('0xf2c3c4a0')
        True
        >>> ep.flash('0xf2c3c4a0',flash_length=300, time_out=2500)
        True

        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')

        if flash_length:
            if not self._is_valid_integer(flash_length):
                log.error('invalid flash_length')
                return

        if time_out:
            if not self._is_valid_integer(time_out):
                log.error('invalid time_out')
                return

        kwargs = {'flash_length': flash_length,
                  'time_out': time_out
                  }

        return self._binary_to_boolean(
            self._query_camelot(camelot.FLASH, call_ref, **kwargs))

    def hlog(self, call_ref=None):
        '''Send hlog softkey event to CCM

        Sends StationSoftKeyEventMessage to CCM to activate or deactivate
        'Logged into Hunt Group'. If the line is logged out of Hunt Group,
        no incoming call is allowed when a call comes to the line group.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.hlog('0xf2c3c4a0')
        True
        '''

        if call_ref and not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.HLOG, call_ref))

    def record(self, call_ref=None):
        '''Send record softkey event only for Chaperone Call to CUCM

        Sends StationSoftKeyEventMessage to CUCM for SCCP Phones with
        appropriate index. Sends 'StartRecording' softkey REFER message
        with XML content to the CUCM for SIPX and RT Phones.
        For example, Chaperone connected Calls.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.record('0xf2c3c4a0')
        True
        '''

        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return

        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.RECORD, call_ref))

    def live_record(self, call_ref=None):
        '''Send liverecord softkey event to CCM


        Sends StationSoftKeyEventMessage to CCM to start the live
        recording of the connected call.


        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.live_record()
        True
        '''

        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')

        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.LIVE_RECORD, call_ref))

    def stop_record(self, call_ref=None):
        '''Send stoprecord softkey event only for SIPX and RT phones to CUCM

        Send 'StopRecording' softkey REFER message with XML content to the CUCM
        for SIPX and RT Phones when recording is already in progress.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.stop_record(call_ref)
        True
        '''

        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')

        return self._binary_to_boolean(
            self._query_camelot(camelot.STOP_RECORD, call_ref))

    def transfer_vm(self, call_ref=None):
        '''Send transfervm softkey event to CCM

        Sends StationSoftKeyEventMessage to CCM to transfer to Voice mail.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.transfer_vm()
        True
        '''

        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.TRANSFER_VM, call_ref))

    def login(self):
        '''Send login softkey event

        Sends login StationSoftKeyEventMessage. A callref is created after
        getting response from the gateway. Use get_calls to get the call_ref.
        Then use the dial command with the call_ref for sending the
        pin in the called filed.

        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep1.login
        True
        >>> after 500
        >>> ep1.get_calls
        [{'0x010a5650': '1': 'dialtone'}]
        >>> ep1.dial(4321, '0x010a5650')
        True

        '''
        # FIXME: This might fail
        # if call_ref and not self._is_valid_call_ref(call_ref):
        #    raise camelot.CamelotError('Invalid call reference')

        # else:
        return self._binary_to_boolean(self._query_camelot(camelot.LOGIN))

    def start_fax_send(self, call_ref, filename):
        '''Initiate T.30 fax send operation

        :parameter callref:    call reference
        :parameter url:  URL of TIFF file to send

        :returns: True on Success

        >>> ep1.start_fax_send('0x1232af2', "/home/camelot/diva/sendfax.tiff')
        True
        '''

        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        if not filename:
            raise camelot.CamelotError('filename not specified')
        return self._binary_to_boolean(
            self._query_camelot(camelot.START_FAX_SEND, call_ref, filename))

    def start_fax_receive(self, call_ref, prefix=None, filename=None):
        '''Initiate T.30 fax send operation

        :parameter callref: call reference
        :parameter prefix:  string to prepend to the received TIFF file.
                            This is mandatory if filename not given.
        :parameter filename: Name of the file with absolute path,
                             provided the file will be saved here.
                             If  not provided, by default received file
                             will be stored in
                             /usr/local/camelot/lib/recordings/
                             with the prefix added to the source file name.
        :returns: True on Success

        >>> ep2.vapi.start_fax_receive('0x12ef231', "ep2",
        "/root/tmp/myfax.tiff')
        True
        '''

        # FIXME: This method also might fail verify and fix

        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        if not filename and not prefix:
            raise camelot.CamelotError('prefix not specified')
        return self._binary_to_boolean(
            self._query_camelot(camelot.START_FAX_RECEIVE, call_ref, prefix,
                                filename))

    def intercom(self, line_ref=0, called='null', calling='null'):
        '''Make an intercom call on intercom line

        Make a intercom call from caller's intercom line to callee's
        intercomline. Both caller and callee's DNs has to be in the same
        Intercom Partition and Intercom CSS. Currently, camelot server support
        the intercom speeddial feaure only on SCCP endpoints,but not on SIP
        endpoints. Hence the 'called' commandline option is optional for the
        former but not the later. We will implement the same feature for SIP
        in next release.

        So for SCCP endpoints, there are ways of using this command:

            (1) endp.intercom(line_ref=caller-intercom-line-number,
            called=callee-intercom-DN) or
            (2) endp.intercom(lineref=caller-intercom-line-number)
            Where in case (2), caller's intercom line must have a speed dial
            configured with callee's intercom DN. Or else, camelot server will
            reject the call.

        For SIP endpoints, only case (1) applies. This will change once we
        implement the speed dial feature for SIP endpoints.

        For SCCP endpoints, there is another way to invoke intercom feature:
            endp.select_line(lineref='caller-intercom-line-number')
            and then use the call_ref returned by this in the next dial
            command,
            endp.dial(call_ref=call_ref1, called= callee-intercom-DN)

        However, it is unsupported for SIPX endpoints.

        :parameter line_ref: line number of the configured intercom line
        :parameter called: DN of calle's intercom line.
                Optional for SCCP endpoint but required for SIP endpoints.

        :returns: call reference for caller's endpoint

        '''
        kwargs = {'called': called,
                  'calling': calling}
        return self._query_camelot(camelot.INTERCOM, line_ref, **kwargs)

    def talk_back(self, call_ref):
        '''Establish a two way communication between caller and callee
        who were engaged in an open way intercom call.

        The callee of an established one-way intercom call uses this method to
        change the existing call into a two way call. Note, only the callee can
        initiate this method, not the caller.


        :parameter call_ref: call reference

        :returns: True on Success

        >>> ep.callback('0xf2c3c4a0')
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.TALK_BACK, call_ref))

    def move(self, call_ref, mute=0):
        '''Move a connected call on a CUMC endpoint to the shared line

        The CUMC endpoint uses this method to move an established call
        to the shared line.


        :parameter call_ref: call reference
        :parameter mute: disable or enable the mute
            * 0 - disable mute (default value)
            * 1 - enable mute

        :returns: True on Success

        >>> ep.move('0xf2c3c4a0')
        True
        '''
        if mute and str(mute) == '1':
            mute = '1'
        else:
            mute = '0'
        kwargs = {'mute': mute}
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        else:
            return self._binary_to_boolean(
                self._query_camelot(camelot.MOVE, call_ref, **kwargs))

    def send_reinvite(self, call_ref, w_last_sdp=1, timeout=0, contents=[]):
        '''
        Initiates sip Re-Invite with SDP and optionally with a list of
        contents provided for a given call.

        :parameter call_ref: The call reference
        :parameter w_last_sdp:
         * 1- send Re-Invite with last sent SDP(default)
         * 0 - send with new configured SDP codecs
        :parameter timeout: The time out in seconds after which this API
         will be invoked by Camelot . Default value is 0 seconds.
        :parameter contents: Using this parameter tester can provide
         one or multiple contents which will be added to outgoing reinvite.
         Type of this parameter is a list of json dictionaries, each
         dictionary containing information for each content.
         Syntax of this parameter is as below (with key name and values).

        >>> [{'content':<Value for the body in string>,
              'headers':{'Content-Type':<Value of content type>,
                         'Content-Transfer-Encoding':<Value>,'Content-ID':<Val
                         ue>}},..,]

        :description: key fields-
                      * content: Its the key name for a body to be attached.
                        Note: Camelot will treat the body as opaque. Hence
                        please pass it as a string. Camelot will not try to
                        check the validity or format the content of the body.
                        This field is mandatory if contents parameter is
                        populated.
                      * headers: Its a dictionary of set of headers name and
                        its values. Camelot supports only the following
                        headers:\n
                        * Content-Type (Mandatory),
                        * Content-Disposition
                        * Content-Transfer-Encoding and
                        * Content-ID.

          For more detail, please refer to following wiki link
          https://wiki.cisco.com/display/CAMELOT/Simulated+SIP+Trunk#SimulatedSIPTrunk-send_reinvitewithcustombody

        :returns: True on success.In case of errors different CamelotError
                  exceptions are raised.To know the entire list of possible
                  errors please refer above wiki link.

        >>> ep1.send_reinvite('0x010a5650', 1 )
        True
        >>> ep1.send_reinvite(call_ref='0x010a5650', w_last_sdp=1, timeout=5 )
        True
        >>> ep1.send_reinvite('0x010a5650', 1, contents=[{'content': 'abcd' ,
         'headers':{'Content-Type':'Sample'}}]
        True
        >>> ep1.send_reinvite('0x010a5650', 1, contents=[{'content': myBody ,
         'headers':{'Content-Type':'application/x-cisco-fork-request+json'}}]
          here myBody is a variable which contains following value
            "{
            "Record": {
            "Message": "Start/Stop",
            "CALLGUID": "3FBF760000010000001FF2691D0816AC",
            "Connection": {
            "Destination": "IP/Host",
            "Port": "8080",
            "Auth-Token": "Speech Server Auth Token Fetched from Cloud Connect
            ",
            "Secure": "True/False"
            },
            "Encoding": "G711-ALaw / G711-ULaw",
            "SampleRate": "8000",
            "Services": {
            "Language": "en-US",
            "Answers": {
            "profile-id": "My Profile with KB",
            "project-id": "My GCP Project Id"
            },
            "Transcription": "",
            "Record": ""
            }
            }
            }"



        True
        '''
        log.debug('Entering method send_reinvite().')
        if not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')

        if w_last_sdp and w_last_sdp == 1:
            w_last_sdp = '1'
        else:
            w_last_sdp = '0'

        if not contents:
            contents = []

        if type(contents) != list:
            raise camelot.CamelotError('Invalid JSON-List format for contents')

        kwargs = {'last_sdp': w_last_sdp, 'timeout': str(timeout),
                  'contents': json.dumps(contents)}

        return self._query_camelot(camelot.SEND_REINVITE, call_ref, **kwargs)

    def start_share(self, call_ref, secvidtype="slides"):
        '''
        once the call is established with BFCP m=line negotiated,
        start_share() will initiate start share procedures, which includes
        BFCP floorctrl messages and SIP Re-Invite for secondary presentation
        video.
        The type of presentation is specified in secvidtype parameter.

        :parameter call_ref: reference of the call
        :parameter secvidtype: optional string type parameter\n
         * if secvidtype parameter omitted, default will be "slides"
         * secvidtype parameter value can be:
             * slides
             * speakar
             * alt
             * content

        :returns: True on success  otherwise False is returned.
                 For error the CamelotError exception is raised

        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        kwargs = {'secvidtype': secvidtype}
        return self._query_camelot(camelot.START_SHARE, call_ref, **kwargs)

    def stop_share(self, call_ref, secvidtype="slides"):
        '''
        once the call is established with BFCP m=line and seconday video
        m=line, stop_share() will initiate stop share procedures, which
        includes BFCP floorctrl messages and SIP Re-Invite for secondary
        presentation video.
        The type of presentation is specified in secvidtype parameter.

        :parameter call_ref: reference of the call
        :parameter secvidtype: optional string type parameter\n
         * if secvidtype parameter omitted, default will be "slides"
         * secvidtype parameter value can be:
             * slides
             * speakar
             * alt
             * content

        :returns: True on success  otherwise False is returned.
                 For error the CamelotError exception is raised

        >>> ep1.stop_share()
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        kwargs = {'secvidtype': secvidtype
                  }
        return self._query_camelot(camelot.STOP_SHARE, call_ref, **kwargs)

    def dtmf_hold(self, call_ref=None):
        '''
        After call connect user need to execute command dtmf_hold.

        :parameter call_ref: call reference

        >>> ep.dtmf_hold( call_ref='call_ref-value')
        '''
        if not call_ref:
            log.error('call reference not specified')
            return
        call_ref = self._convert_hex_to_int(call_ref)
        return self._query_camelot(camelot.DTMF_HOLD, call_ref)

    def dtmf_resume(self, call_ref=None):
        '''
        Hold calls (using DTMF) can be resumed by dtmf_resume command.

        :parameter call_ref: call reference

        >>> ep.dtmf_resume(call_ref='call_ref-value')
        '''
        if not call_ref:
            log.error('call reference not specified')
            return
        call_ref = int(call_ref, 16)
        return self._query_camelot(camelot.DTMF_RESUME, call_ref)

    def dtmf_exclusive_hold(self, call_ref=None):
        '''Exclusive hold is required , when end points needs to dial
        for a new call. This is required to to realize call
        transfer / conference scenarios, where user needs to dial
        to a new call.

        :parameter call_ref: call reference

        >>> ep.dtmf_exclusive_hold(call_ref='call_ref-value')
        '''
        if not call_ref:
            log.error('call reference not specified')
            return
        call_ref = int(call_ref, 16)
        return self._query_camelot(camelot.DTMF_EXCLUSIVE_HOLD, call_ref)

    def dtmf_dust(self, call_ref=None):
        '''The complete dusting feature can move single call,
        conference, and session collaboration among mobile phone,
        PC, and desk phone. To get more understanding on dusting please
        refer EDCS-804326.

        :parameter call_ref: call reference

        >>> ep.dtmf_dust(call_ref='call_ref-value')
        '''
        if not call_ref:
            log.error('call reference not specified')
            return
        call_ref = int(call_ref, 16)
        return self._query_camelot(camelot.DTMF_DUST, call_ref)

    def dtmf_transfer(self, call_ref=None):
        '''Call transfer (in DTMF smart mode) can be achieved similar way as
        that of legacy call transfer. Lets take an example to explain the
        steps to get dtmf transfer working. Assume there are three phones,
        A, B and C. A calls B, A and B are connected. Now A invokes
        dtmf_transfer, A-B call goes to held state. A gets dial tone.
        A dials to new phone C and now A and C are connected. Again A
        invokes dtmf_transfer using connected call reference to complete
        the transfer. After this two calls at A get disconnected,
        B-C call gets connected.

        :parameter call_ref: call reference

        >>> ep.dtmf_transfer(call_ref='call_ref-value')
        '''
        if not call_ref:
            log.error('call reference not specified')
            return
        call_ref = int(call_ref, 16)
        return self._query_camelot(camelot.DTMF_TRANSFER, call_ref)

    def dtmf_conference(self, call_ref=None):
        '''Call conference (in DTMF smart mode) works similar to legacy
        conference way. Lets take an example to explain the steps to get
        dtmf_conference working. Assume there are three phones, A, B and C.
        A calls B, A and B are connected. Now A invokes dtmf_conference,
        A-B call goes to held state. A gets dial tone. A dials to new phone C
        and now A and C are connected. Again A invokes dtmf_conference using
        connected call reference to complete the conference. After this, A, B
        and C are in conference each having a single call.

        :parameter call_ref: call reference

        :returns: 1 on success 0 on failure.

        >>> ep.dtmf_conference(call_ref='call_ref-value')
        '''
        if not call_ref:
            log.error('call reference not specified')
            return
        call_ref = int(call_ref, 16)
        return self._query_camelot(camelot.DTMF_CONFERENCE, call_ref)

    def get_timing_stats(self, method):
        '''Enable the timing to check how much time spent for particular
           method to get it complete

        :parameter method: method name for which timing need to calculate
            (e.g inservice, uxnssologin, ucmssologin, uxnssoredirect,
            ucmssoredirect, uxnssopostcredrential, ucmssopostcredrential).

        :returns: Upon success returns the timing stats or else error msg
        >>> ep1.get_timing_stats(inservice or uxnssologin or ucmssologin
             or uxnssoredirect or ucmssoredirect or uxnssopostcredrential
             or ucmssopostcredrential)
        '''
        method_id = 0
        if method == 'inservice':
            method_id = '1'
        elif method == 'uxnssologin':
            method_id = '2'
        elif method == 'ucmssologin':
            method_id = '3'
        elif method == 'uxnssoredirect':
            method_id = '4'
        elif method == 'ucmssoredirect':
            method_id = '5'
        elif method == 'uxnssopostcredential':
            method_id = '6'
        elif method == 'ucmssopostcredential':
            method_id = '7'
        else:
            log.error('Unknown method type')
            return
        return self._query_camelot(camelot.GET_TIMING_STATS, method_id)

    def escalate(self, call_ref, option):
        '''
        This command will be used after the call is connected, to promote the
        new media on top of the existing media by using option parameter.

        :parameter call_ref: reference of the call
        :parameter option: it is string type parameter.
                           It tells, what type of media is being
                           escalated/deescalated.
                           if the initial call is
                           "audio+video+fecc+bfcp+slides"
                           and option = "audio+video+fecc+ix",
                           SDP in the reinvite shall have audio, video, fecc,
                           ix m-lines with non zero port and
                           bfcp, slides m-lines with zero port


        :returns: True on success  otherwise False is returned.
                 For error the CamelotError exception is raised

        >>> ep1.escalate('0xe8faf034',option="audio")
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        return self._query_camelot(camelot.ESCALATE, call_ref, option)

    def deescalate(self, call_ref, option):
        '''
        This command will be used after the call is connected,
        to deescalate the media using option parameter.

        :parameter call_ref: reference of the call
        :parameter option: tells, what type of media is being deescalated.
                           if the initial call is
                           "audio+video+fecc+bfcp+slides"
                           and option = "audio+video",
                           SDP in the reinvite shall have audio, video
                           m-lines with non zero port and
                           fecc, bfcp, slides m-lines with zero port

        :returns: True on success  otherwise False is returned.
            For error the CamelotError exception is raised

        >>> ep1.deescalate('0xf1f6d034',option="audio+video")
        True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        return self._query_camelot(camelot.DEESCALATE, call_ref, option)

    def config_header(self, param, value):
        '''Sets or gets the specified configuration parameter.

        :parameter header: name of the header
        :parameter value: value to be set

        :returns: '1' in case of success and '0' in case of failure

        >>> ep1.config_header('Allow','ACK,BYE,CANCEL,INVITE')
        1
        '''
        kwargs = {'param': param,
                  'value': value
                  }
        return self._query_camelot(camelot.CONFIG_HEADER, None, **kwargs)

    def refresh_template_message(self, method='all'):
        '''refresh the template message stored in camelot.

        :parameter method: The name of the method which user wants
            to refresh. If no parameter is given, it will refresh all
            the methods stored in camelot.

        :returns: 1 on success 0 on failure.

        >>> ep.refresh_template_message(method)
        1
        '''
        return self._query_camelot(camelot.REFRESH_TEMPLATE_MESSAGE, method)

    def move_to_mobile(self, call_ref):
        '''Move a call from VoIP to Cellular side.

        Move a connected call in a DMC (or jabber mobile) endpoint
        (attended in VoIP mode), from IP to GSM.
        Its supported for both deployments On-Premise and Collab Edge.

        :parameter call_ref: call reference

        :returns: 1 on success

        >>> ep.move_to_mobile('0xf1706408')
        >>> 1
        '''
        log.debug('Entering method move_to_mobile().')
        if not call_ref:
            log.error('call reference not specified')
            return

        return self._query_camelot(camelot.MOVE_TO_MOBILE, call_ref)

    def exec_mediator_cmd(self, cmd, output=0, delay=10):
        '''
        accepts the command from the user and passes the same
        on to the mediator. Depending upon the output
        configuaration the camelot either to wait for the
        response from mediator or returns immediately without
        wiating.returns error string if the mediator is not running.

        :parameter cmd: mandatory parameter. command to be passed to
         mediator application.
         if the command takes multiple arguements then provide them
         in the this parameter. one example can be "startrectpat video
         1920 1000 30". The set of supported mediator commands can be
         found here https://pypi.lal.cisco.com/doc/phone-e/mediator.html.
        :parameter output: accepts 0 or 1. 0 can be given when the user
         just want to pass the command to mediator but not expecting the
         response from mediator. 1 can be given when the user expecting
         to get the response returned by the mediator.
        :parameter delay: It accepts the delay time in seconds and defaults
         to 10 decs.This parameter has the significance only when the
         user set the output parameter to 1 otherwise this value will
         be ignored. it says how long the Camelot need to wait for
         the response to receive from mediator before returning to
         the user. if set with -1 then the camelot will wait infinitely
         to receive the response.

        :returns: If output parameter was set to 0 then the return will be
         either 0 or 1, on success 1 will be returned otherwise 0.
         if the output is set to 1 then the camelot returns the response
         in the format returned by the mediator.

        >>> ep1.exec_mediator_cmd("enable audio")
        1
        >>> ep1.exec_mediator_cmd("audiosample,1,10)
        audiosampleresult 8000 [-1564,-1980,-2108,-1980,-1564,-1052,-396,
        308,988,1500,1884,2108,1980,1628,1116,460,-244,-924,-1500,-1884,-2108,
        -1980,-1692,-1180,-524,180,876,1436,1820,1980,1980,1692,1244,588,-120,
        -812,-1372,-1820,-1980,-1980,-1756,-1244,-652,48,748,1372,1820,1980,
        1980,1756,1308,716,16,-684,-1308,-1756,-1980,-1980,-1820,-1372,-780,
        -80,620,1244,1756,1980,1980,1820,1436,812,148,-556,-1180,-1692,-1980,
        -2108,-1884,-1436,-876,-212,]
        >>> ep1.exec_mediator_cmd("enable video")
        mediator not running
        '''
        kwargs = {'cmd': cmd,
                  'output': output,
                  'delay': delay
                  }

        return self._query_camelot(camelot.EXEC_MEDIATOR_CMD, None, **kwargs)

    def start_raw_events(self, callid_filter, method_filter, cseq_filter,
                         assist):
        kwargs = {'callid_filter': callid_filter,
                  'method_filter': method_filter,
                  'cseq_filter': cseq_filter,
                  'assist': assist
                  }
        return self._query_camelot(camelot.START_RAW_EVENTS, None, **kwargs)

    def stop_raw_events(self, callid_filter, method_filter, cseq_filter,
                        assist):
        kwargs = {'callid_filter': callid_filter,
                  'method_filter': method_filter,
                  'cseq_filter': cseq_filter,
                  'assist': assist
                  }
        return self._query_camelot(camelot.STOP_RAW_EVENTS, None, **kwargs)

    def send_non_invite_msg(self, call_ref, method, timeout=0, contents=[],
                            headers={}):
        '''
        Initiates in dialog Sip INFO message and optionally with a list of
        contents and headers parameters provided for a given call.

        :parameter call_ref: The call reference
        :parameter method:
         * INFO - currently this method supports INFO message only.
         If given other than value 'INFO',returns invalid method name.
        :parameter timeout: The time out in seconds after which this API
         will be invoked by Camelot . Default value is 0 seconds.
        :parameter contents: Using this parameter tester can provide
         one or multiple contents which will be added to outgoing reinvite.
         Type of this parameter is a list of json dictionaries, each
         dictionary containing information for each content.

         * content: Its the key name for a body to be attached.
           Note: Camelot will treat the body as opaque. Hence
           please pass it as a string. Camelot will not try to
           check the validity or format the content of the body.
           This field is mandatory if contents parameter is
           populated.
         * headers: Its a dictionary of set of headers name and
           its values. Camelot supports only the following
           headers:\n
           * Content-Type (Mandatory),
           * Content-Disposition
           * Content-Transfer-Encoding and
           * Content-ID.
         Syntax of this parameter is as below (with key name and values).

        >>> [{'content':<Value for the body in string>,
              'headers':{'Content-Type':<Value of content type>,
                         'Content-Transfer-Encoding':<Value>,'Content-ID':<Val
                         ue>}},..,]

        :parameter headers: Using this parameter tester can provide
         single/multiple sipheaders to add/modify to the INFO message.
        >>> {'Header-Key':<Value of header>,
               'Header-Key':<Value of header>}
        >>> headers = {'Subject':'Cisco-CUCM'}
            headers = {'Content-Type': 'mime'}

        For more detail, please refer to following wiki link
        https://wiki.cisco.com/display/CAMELOT/Generate+Customized+Sip+Message

        :returns: True on success.In case of errors different CamelotError
                  exceptions are raised.To know the entire list of possible
                  errors please refer above wiki link.

        >>> ep1.send_non_invite_msg(call_ref='0x010a5650','INFO',timeout=5,
         contents=[{'content': 'abcd','headers':{'Content-Type':'Sample'}}])
        True
        >>> ep1.send_non_invite_msg('0x010a5650', 'INFO',
         contents=[{'content': 'abcd','headers':{'Content-Type':'Sample'}}])
        True
        >>> ep1.send_non_invite_msg('0x010a5650', 'INFO',contents=[{'content':
         myBody,
         'headers':{'Content-Type':'application/x-cisco-fork-request+json'}}],
         headers = {'Subject':'Cisco-CUCM'})
        True
          here myBody is a variable which contains following value
            "{
            "Record": {
            "Message": "Start/Stop",
            "CALLGUID": "3FBF760000010000001FF2691D0816AC",
            "Connection": {
            "Destination": "IP/Host",
            "Port": "8080",
            "Auth-Token": "Speech Server Auth Token Fetched from Cloud Connect
            ",
            "Secure": "True/False"
            },
            "Encoding": "G711-ALaw / G711-ULaw",
            "SampleRate": "8000",
            "Services": {
            "Language": "en-US",
            "Answers": {
            "profile-id": "My Profile with KB",
            "project-id": "My GCP Project Id"
            },
            "Transcription": "",
            "Record": ""
            }
        '''
        log.debug('Entering method send_non_invite_msg().')
        if not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        if not contents:
            contents = []
        if not headers:
            headers = []

        try:
            api_contents = json.dumps(contents)
        except Exception as e:
            raise camelot.CamelotError('contents json parsing failed; err={}'
                                       .format(e))

        try:
            api_hdrs = json.dumps(headers)
        except Exception as e:
            raise camelot.CamelotError('headers json parsing failed; err={}'
                                       .format(e))

        if type(contents) != list:
            raise camelot.CamelotError('Invalid List format for contents')

        kwargs = {'method_type': method, 'timeout': timeout,
                  'contents': api_contents,
                  'headers': api_hdrs}

        return self._query_camelot(camelot.SEND_NON_INVITE, call_ref, **kwargs)
