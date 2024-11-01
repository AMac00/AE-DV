import camelot
import sys
import string
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger

log = camlogger.getLogger(__name__)


class CamelotAutoOperation(v.CamelotVapiUtils):

    '''Camelot Auto operations'''

    def __init__(self):
        pass

    def enable_auto_dial(self, dial_list=None, event=None, **kwargs):
        '''Configures an endpoint to auto dial

        Configures an endpoint to automatically dial on placing a call.

        :parameter dial_list: dial_list is a list of dictionaries
            with following dictionary keys


            called address : destination number or URI to be dialed.
                             It's a mandatory parameter

            calling address : number or URI from which call has to be dialed.
                              It's an optional parameter
                              if not provided, first line will be used by
                              default

            calling line : line reference number from which call has to be
                           dialed
                           index starts from 1. It's an optional parameter;
                           if not provided, first line will be used by default.

            Queue of called party address with no lineref or
            calling party information

            URL:
            [{'called address':'h15001-154468328@10.12.10.43:1720'},
             {'called address':'h25001-154468328@10.12.10.43:1720'}]

            DN:
            [{'called address':'6003' },
             {'called address':'6004'}]

            If we want to use different line on each call,
            for example line 1 will be used to call 6003, line 2 will be used
            to call 6004


            DN:
            [{'called address':'6003', 'calling address':'6001' },
             {'called address':'6004', 'calling line':'2'}]


            URL:
            [{'called address':'h45001-155123688@10.12.10.43:1720',
              'calling address':'h35001-155123688@10.12.10.43:1720'},
             {'called address':'h55001-155123688@10.12.10.43:1720',
              'calling line':'2'}]

        :parameter event: configure a trigger event for the auto dial
            An example:
            "envelope icon on" - trigger dial when Voice Mail icon is received

        :returns:  If the command enables autodial configuration
                   it returns enabled.

        >>> ep1.enable_auto_dial([{'called address':
            'h45001-155123688@10.12.10.43:1720',
            'calling address':
            'h35001-155123688@10.12.10.43:1720' },
            {'called
            address':'h55001-155123688@10.12.10.43:1720',
            'calling line':'2'}])
            'enabled'

        >>> ep1.enable_auto_dial([{'called address':
            'h45001-155123688@10.12.10.43:1720'},
            {'called address':
            'h45001-155123688@10.12.10.43:1720'}])
            'enabled'

        >>> ep1.enable_auto_dial([{'called address':'99719099',
            'calling address':'99718088' },
            {'called address':'99717077', 'calling line':'2'}])
            'enabled'

        >>> ep1.enable_auto_dial([{'called address':'99719099' }
            {'called address':'99717077'}])
           'enabled'
        '''

        log.debug('Entering enable_auto_dial function')
        auto_dial_called_list = kwargs.get('auto_dial_called_list', None)
        auto_dial_event = kwargs.get('auto_dial_event', None)
        if auto_dial_called_list:  # used for TNGpi backward compatibility
            dial_list = auto_dial_called_list
        if auto_dial_event:  # used for TNGpi backward compatibility
            event = auto_dial_event
        if not kwargs:
            kwargs = {
                'dial_list': dial_list,
                'event': event,
            }
        return self._query_camelot(camelot.ENABLE_AUTO_DIAL, None, **kwargs)

    def disable_auto_dial(self):
        '''
        disables autodial for an endpoint.

        :returns: If the command disables autodial configuration
                  it returns disabled. Incase of error, returns the
                  specific error.

        >>> ep1.disable_auto_dial()
        'disabled'
        '''
        log.debug('Entering disable_auto_dial function')
        return self._query_camelot(camelot.DISABLE_AUTO_DIAL)

    def get_auto_dial_event(self):
        '''
        Return the registered event string.

        :returns: registered event string will be returned.
        '''
        return self._query_camelot(camelot.GET_AUTO_DIAL_EVENT)

    def get_auto_dial_called_list(self):
        '''
        To get the current configuration of the address queue

        :returns: the currently configured address queue is returned.

        Before invoking get_auto_dial_called_list() call enable_auto_dial()

        For more information refer to enable_auto_dial() API documentation.
        For example if DN's and line configured for auto dialling

        >>> ep1.enable_auto_dial
        ([{'called address':'99719099','calling address':'99718088' },
        {'called address':'99717077', 'calling line':'2'}])

        >>> ep1.get_auto_dial_called_list()
        [{"called":"99719099","line":"0","calling":"99718088"},
        {"called":"99717077","line":"2"}]
        '''
        return self._query_camelot(camelot.GET_AUTO_DIAL_CALLED_LIST)

    def get_auto_dial_status(self):
        '''
        The current autodial state, either enabled or disabled

        :returns: The current autodial state, either enabled or disabled

        >>> ep1.get_auto_dial_status()
        'enabled'
        '''
        return self._query_camelot(camelot.GET_AUTO_DIAL_STATUS)

    def enable_auto_transfer(self, mode=None, talk_time=None, target=None,
                             line_ref=None):
        '''
        Configures an endpoint to auto transfer
        Configures an endpoint to automatically dial on placing a call.

        :parameter talk_time: delay in milliseconds from call
                             connection until transfer is invoked

        :parameter mode: transfer mode, supervised, blind,
                            connected, supervisedonhook or blindonhook

        :parameter target: called party address (DN or URI)
                            of the transfer target

        :parameter line_ref: line for outbound new call for transfer

        :returns:  If the command enables autotransfer
                   configuration it returns enabled.

        >>> ep.enable_auto_transfer(20,'supervised',12000,1)
        'enabled'
        '''

        log.debug('Entering enable_auto_transfer function')

        if mode not in ['supervised', 'blind', 'connected',
                        'supervisedonhook', 'blindonhook']:
            return 'Invalid mode'

        if not talk_time and (target and mode):
            return 'talk time not specified'
        elif not target and (talk_time and mode):
            return 'target not specifed'
        elif not mode and (talk_time and target):
            return 'mode not specified'

        kwargs = {'talktime': str(talk_time),
                  'mode': str(mode),
                  'target': str(target),
                  'lineref': str(line_ref)}

        return self._query_camelot(camelot.ENABLE_AUTO_TRANSFER, **kwargs)

    def get_auto_transfer_status(self):
        '''
        returns the status of auto transfer on endpoint

        :returns: Returns 'enabled' if auto transfer is enabled otherwise
         'disabled'.

        >>> ep1.get_auto_transfer_status()
        'enabled'
        '''
        return self._query_camelot(camelot.GET_AUTO_TRANSFER_STATUS)

    def get_auto_transfer_mode(self):
        '''returns the mode of the auto transfer on endpoint

        :returns: Returns the transfer mode like supervised, blind,
         connected, supervisedonhook or blindonhook if auto_transfer is enabled
         otherwise False.

        >>> ep1.get_auto_transfer_mode()
        'enabled'
        '''
        return self._query_camelot(camelot.GET_AUTO_TRANSFER_MODE)

    def get_auto_transfer_talk_time(self):
        '''
        returns the talk_time in milli seconds configured for an
        auto_transfer for an endpoint

        :returns: returns delay in milliseconds configured to invoke the
         transfer once from call is connected.

        >>> ep1.get_auto_transfer_talk_time()
        'enabled'
        '''
        return self._query_camelot(camelot.GET_AUTO_TRANSFER_TALK_TIME)

    def get_auto_transfer_target(self):
        '''returns the called paety address of the transfer target

        :returns: called party address (DN or URI) of the transfer target

        >>> ep1.enable_auto_transfer('supervised', 20, 12000,1)
        'enabled'
        >>> ep1.get_auto_transfer_target()
        '12000'
        '''
        return self._query_camelot(camelot.GET_AUTO_TRANSFER_TARGET)

    def disable_auto_transfer(self):
        '''
        disables autodial for an endpoint.

        :returns: If the command disables autodial configuration it returns
         disabled. Incase of error, returns the specific error

        >>> ep1.disable_auto_transfer()
        'disabled'
        '''
        log.debug('Entering disable_auto_transfer function')
        return self._query_camelot(camelot.DISABLE_AUTO_TRANSFER)

    def get_auto_conference_status(self):
        '''
        returns the status of the auto_conference on an endpoint

        :returns: returns Enabled if auto conference is enabled otherwise
         disabled.

        >>> ep1.get_auto_conference_status()
        'enabled'
        '''
        return self._query_camelot(camelot.GET_AUTO_CONFERENCE_STATUS)

    def get_auto_conference_mode(self):
        '''
        returns the conference mode configured for auto conference

        :returns: returns mode like conference mode, consultative or connected.

        >>> ep1.get_auto_conference_mode()
        'connected'
        '''
        return self._query_camelot(camelot.GET_AUTO_CONFERENCE_MODE)

    def get_auto_conference_talk_time(self):
        '''
        Returns the talk time configured for an auto conference

        :returns: returns the delay in milliseconds from call connection
         until conference is invoked.

        >>> ep1.get_auto_conference_talk_time()
        '200'
        '''
        return self._query_camelot(camelot.GET_AUTO_CONFERENCE_TALK_TIME)

    def get_auto_conference_target(self):
        '''
        returns the target configured for auto conference on endpoint

        :returns: returns the called party address (DN or URI) of the target
         endpoint to conference

        >>> ep1.get_auto_conference_target()
        '6001'
        '''
        return self._query_camelot(camelot.GET_AUTO_CONFERENCE_TARGET)

    def enable_auto_resume(self, hold_time=None):
        '''
        Configures an endpoint to auto resume

        :parameter hold_time:  delay in milliseconds call is on
                    hold before resume is invoked

        :returns: If the command enables autoresume configuration
         it returns enabled.

        >>> ep.enable_auto_resume(20)
        'enabled'
        '''
        log.debug('Entering enable_auto_resume function')
        if(hold_time < 0):
            return 'Invalid hold time'
        return self._query_camelot(camelot.ENABLE_AUTO_RESUME, hold_time)

    def disable_auto_resume(self):
        '''
        disables autodial for an endpoint

        :returns: If the command disables autodial configuration it returns
         disabled. Incase of error, returns the specific error

        >>> ep1.disable_auto_dial()
        'disabled'
        '''
        log.debug('Entering disable_auto_resume function')
        return self._query_camelot(camelot.DISABLE_AUTO_RESUME)

    def get_auto_resume_status(self):
        '''
        returns the status of auto resume on an endpoint

        returns: Returns 'enabled' if auto resume is enabled otherwise
                'disabled'.

        >>> ep1.get_auto_resume_status()
        'enabled'
        '''
        log.debug('Entering get_auto_resume_status function')
        return self._query_camelot(camelot.GET_AUTO_RESUME_STATUS)

    def get_auto_resume_hold_time(self):
        '''
        returns the hold_time configured for the
        endpoint to remain in hold state before invoking
        resume.

        :returns: Returns hold time in milli seconds if auto_resume_hold
         is enabled and hold_time is configured otherwise 0.

        >>> ep1.get_auto_resume_hold_time()
           '200'
        '''
        log.debug('Entering get_auto_resume_hold_time function')
        return self._query_camelot(camelot.GET_AUTO_RESUME_HOLD_TIME)

    def enable_auto_conference(self, talk_time=None, mode=None, target=None,
                               line_ref=None):
        '''
        Configures an endpoint to auto conference
        Configures an endpoint to automatically dial on placing a call.

        :parameter talk_time: delay in milliseconds from call
                             connection until conference is invoked
        :parameter mode: conference mode, consultative or connected
        :parameter target: called party address (DN or URI) of the
                            target endpoint to conference in
        :parameter line_ref: line for outbound new call for conference

        :returns: If the command enables autoconference
                  configuration it returns enabled.

        >>> ep.enable_auto_conference(20,'connected',12000,1)
            'enabled'
        '''

        log.debug('Entering enable_auto_conference function')
        mode_types = ['consultative', 'connected']
        if talk_time:
            if talk_time in mode_types:
                temp = talk_time
                talk_time = mode
                mode = temp
            if sys.version_info < (3, 5):
                if (not isinstance(talk_time, (int, long, float)) or
                        talk_time < 0):
                    raise Exception('invalid talk time specified')
            else:
                if not isinstance(talk_time, (int, float)) or talk_time < 0:
                    raise Exception('invalid talk time specified')
        if mode and mode not in mode_types:
            raise Exception('invalid mode specified')

        if line_ref:
            if sys.version_info < (3, 5):
                if not isinstance(line_ref, (int, long)) or line_ref < 0:
                    raise Exception('invalid lineref specified')
            else:
                if not isinstance(line_ref, int) or line_ref < 0:
                    raise Exception('invalid lineref specified')

        kwargs = {'talktime': talk_time,
                  'mode': mode,
                  'target': target,
                  'lineref': line_ref}

        return self._query_camelot(camelot.ENABLE_AUTO_CONFERENCE, **kwargs)

    def disable_auto_conference(self):
        '''
        disables autoconference for an endpoint

        :returns: If the command disables autoconference configuration it
                  returns disabled. Incase of error, returns the specific
                  error.

        >>> ep1.disable_auto_conference()
        'disabled'
        '''
        log.debug('Entering enable_auto_conference function')
        return self._query_camelot(camelot.DISABLE_AUTO_CONFERENCE)

    def enable_auto_answer(self, line_ref=None, calling_list=None, delay=None):
        '''Configures an endpoint to answer a call after a specified delay.

        Configures an endpoint to automatically answer an incoming call
        after the specified delay has expired.  This command also
        allows the user to have the autoanswer configuration for line.
        Multiple lines of the endpoint can also be configured. When
        autoanswer is configured for a line it overrides the endpoint
        level configuration for that line. Either for line configuration
        or for the endpoint configuration a list of calling DN patterns
        can be given as input such that only the call that has a calling
        DN matching with any of the value in the input list will be auto.
        answered.

        :parameter line_ref: configure autoanswer for a line
        :parameter calling_list: configure a list of calling DN patterns so
            that autoanswer is triggered only if an incoming call's calling
            number is matched with any regular expression value in the list.
        :parameter delay:  delay in milliseconds.  If this option is specified
            along with lineref then specified delay value is applicable only
            to calls incoming on the line.

        :returns: If the command enables autoanswer configuration it returns
         enabled. Incase of error, returns the specific error.

        >>> ep1.enable_auto_answer()
        'enabled'

        '''
        log.debug('Entering enable_auto_answer function')
        kwargs = {'lineref': line_ref,
                  'calling': calling_list,
                  'delay': delay}
        return self._query_camelot(camelot.ENABLE_AUTO_ANSWER, **kwargs)

    def disable_auto_answer(self, line_ref=None):
        '''
        disable autoanswer. If this option is specified along with lineref then
        autoanswer configuration for that line will be removed.

        :parameter line_ref: disable autoanswer for a line

        :returns: If the command disables autoanswer configuration it returns
         disabled. Incase of error, returns the specific error

        >>> ep1.disable_auto_answer()
        'disabled'
        '''
        log.debug('Entering disable_auto_answer function')
        kwargs = {'lineref': line_ref}
        return self._query_camelot(camelot.DISABLE_AUTO_ANSWER, **kwargs)

    def get_auto_answer_info(self, line_ref=None):
        '''
        Returns autoanswer configuration. If this option is specified along
        with lineref then the configuration of the specified line will be
        returned. Otherwise, all lines configuration and the endpoint level
        configuration will be returned.

        :parameter line_ref: configuration of the specified line will be
         returned

        :returns: returns the formatted list of endpoint and lines
         configuration as shown below.

        >>> ep1.ep1.enable_auto_answer(0,['1200001','1200002'])
        'enabled'
        >>> ep1.get_auto_answer_info()
        [{u'calling': u'{1200002 1200001}',
        u'delay': u'0',
        u'line_config': [{u'calling': u'{1200002 1200001}',
        u'delay': u'0',
        u'lineref': u'1',
        u'status': u'enabled'}],
        u'status': u'enabled'}]
        '''
        log.debug('Entering get_auto_answer_info  function')
        kwargs = {'lineref': line_ref}
        return self._query_camelot(camelot.AUTO_ANSWER_INFO, **kwargs)

    def enable_auto_cell_pickup(self, delay=0):
        '''
        Configures an endpoint to automatically perform cell pickup
         after a specified delay

        :parameter delay: delay in milliseconds before autocellpickup
         operation is invoked

        :returns: 'enabled'

        >>> ep1.enable_auto_cell_pickup()
        'enabled'
        '''
        log.debug('Entering enable_auto_cell_pickup function')
        if delay < 0:
            raise camelot.CamelotError('delay cannot be negative')
        kwargs = {'delay': delay}
        return self._query_camelot(camelot.ENABLE_AUTO_CELL_PICKUP, **kwargs)

    def disable_auto_cell_pickup(self):
        '''
        disable autocellpickup

        :returns: 'disabled'

        >>> ep1.disable_auto_cell_pickup()
        'diabled'
        '''
        log.debug('Entering disable_auto_cell_pickup function')
        return self._query_camelot(camelot.DISABLE_AUTO_CELL_PICKUP)

    def get_auto_cell_pickup_status(self):
        '''
        get autocellpickup status whether enabled or disabled

        :returns: enabled /disabled

        >>> ep1.get_auto_cell_pickup_status()
        'diabled'
        '''
        log.debug('Entering get_auto_cell_pickup_status function')
        return self._query_camelot(camelot.GET_AUTO_CELL_PICKUP_STATUS)

    def get_auto_cell_pickup_delay(self):
        '''
        get autocellpickup delay

        :returns: delay in milliseconds that was set in enable_auto_cell_pickup

        >>> ep1.get_auto_cell_pickup_delay()
        '10'
        '''
        log.debug('Entering get_auto_cell_pickup_delay function')
        return self._query_camelot(camelot.GET_AUTO_CELL_PICKUP_DELAY)

    def enable_auto_disconnect(self, hold_time=None):
        '''
        Configures an endpoint to disconnect a call after a specified hold time

        Configures an endpoint to automatically disconnect its call after the
         specified call hold time has expired.  Specify a hold time of zero to
         disconnect the call immediately.

        :parameter hold_time: hold time in milliseconds (Int parameter)

        :returns: The current autodisconnect state, enabled or disabled

        >>> ep4.enable_auto_disconnect(hold_time = 3000)
        'enabled'
        '''

        log.debug('Entering enable_auto_disconnect function')
        kwargs = {'holdtime': hold_time}
        return self._query_camelot(camelot.ENABLE_AUTO_DISCONNECT, **kwargs)

    def disable_auto_disconnect(self):
        '''
        Disables autodisconnect.

        :returns: The current autodial state, either enabled or disabled

        >>> ep4.disable_auto_disconnect()
        'disabled'
        '''
        log.debug('Entering disable_auto_disconnect function')
        return self._query_camelot(camelot.DISABLE_AUTO_DISCONNECT)

    def get_auto_disconnect_status(self):
        '''
        The current autodisconnect state, either enabled or disabled is
        returned

        :returns: The current autodisconnect state, either enabled or disabled

        >>> ep1.get_auto_disconnect_status()
        'enabled'
        '''
        log.debug('Entering get_auto_disconnect_status function')
        return self._query_camelot(camelot.AUTO_DISCONNECT_STATUS)

    def get_auto_disconnect_delay(self):
        '''
        Returns currently configured hold time

        :returns: The currently configured hold time in milliseconds
                  is returned.

        >>> ep1.get_auto_disconnect_delay()
        '200'
        '''
        log.debug('Entering get_auto_disconnect_delay function')
        return self._query_camelot(camelot.AUTO_DISCONNECT_DELAY)

    def enable_auto_sss(self, shandle, sargs='', scripttype='tcl'):
        '''
        enable the auto sss.

        :parameter shandle: shandle returned by loadsss
        :paramter args: arguments to the sss script
                        else respective error will be returned.
        >>> ssh_handle=serv.load_sss(script='/home/camelot/from_ubuntu14
            /raseel/load_scripts/sss/placecall_sss.tcl',scripttype='tcl'
        >>> ep1.enable_auto_sss(shandle=ssh_handle)
        '1'
        '''
        sArgs = ''
        log.debug('Entering enable_auto_sss function')
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
                    if (type(sargs[key]) is camelot.endpoint.CamelotEndpoint):
                        sargs[key] = "%s:%s" % ("endpoint",
                                                sargs[key].get_ref())
                    else:
                        sargs[key] = "%s:%s" % ("string",
                                                sargs[key])

                sArgs = ' '.join(sargs)
            else:
                sArgs = sargs
        return self._query_camelot(camelot.ENABLE_AUTO_SSS, shandle, sArgs)

    def get_auto_call_guard_delay(self):
        ''' get the current autocallguard delay.

        :returns: auto call gaurd delay time in milli seconds.

        >>> ep1.get_auto_call_guard_delay()
        '200'
        '''
        return self._query_camelot(camelot.GET_AUTO_CALL_GUARD_DELAY, None)

    def enable_auto_call_guard(self, delay=None):
        '''
        Enable auto call guard

        Configures minimum delay from call disconnect to call initiation
        on an endpoint

        :parameter delay: delay in milliseconds
        :returns: enabled or disabled

        >>> ep.enable_auto_call_guard(delay=0)
        enabled
        '''
        return self._query_camelot(camelot.ENABLE_AUTO_CALL_GUARD, delay)

    def disable_auto_call_guard(self):
        '''
        disable auto call guard

        :returns: 'disabled'.

        >>> ep1.disable_auto_call_guard()
        'disabled'
        '''
        return self._query_camelot(camelot.DISABLE_AUTO_CALL_GUARD, None)

    def get_auto_call_guard_status(self):
        '''
        disable auto call guard

        :returns: enabled or disabled.

        >>> ep1.get_auto_call_guard_status()
        'disabled'
        '''
        return self._query_camelot(camelot.GET_AUTO_CALL_GUARD_STATUS, None)

    def enable_auto_path_conf(self, mode=None, start_delay=None,
                              trigger='callsetup', media_type=None):
        '''
        Configures an endpoint to perform path confirmation when a call
        connects, i.e., during callsetup or whenever RTP path is renegotiated

        Configures an endpoint to perform path confirmation when a call
        connects.  The mode option indicates which end will initiate path
        confirmation.  The start_delay option indicates the delay from call
        connect until path confirmation begins.  If path confirmation fails,
        the call will disconnect immediately and a failure indication will be
        logged with the call via the failure status field returned by
        getcallinfo.

        Mid-call path confirmation is not supported on conference call flows.

        :parameter mode: One of the following:\n
                         * initiator - initiate path confirmation to remote end
                         * responder - respond to path confirmation initiated
                             from remote end
        :parameter start_delay: delay in milliseconds after the call connects
         and before initiating path confirmation (initiator) or listening for
         path confirmation (responder)
        :parameter trigger: This configuration parameter mentions when to
         trigger path confirmation. This parameter takes two values.
         i.e., callsetup and midcall.\n
         * callsetup - As the call being setup for the first time. i.e., the
           path confirmation is triggered for the first time the call goes to
           connected state. This is the default argument for trigger. i.e. if
           user omits trigger option then it is considered that autopathconf
           shall be executed only once during the call setup.
         * midcall - Path confirmation will be triggered whenever RTP path
           is renegotiated. Note that path confirmation will be kicked off
           when both inbound and outbound streams are open and the call is
           in connected state.

         Both trigger options can be configured on an endpoint and mode of
         endpoint can possibly be different in both cases. When path
         confirmation fails call will be disconnected in both trigger case

        :parameter media_type: This configuration parameter mentions the type
         of media i.e, audio or video

        :returns: Returns current auto_path_conf state,
         enabled or disabled

        >>> ep1.enable_auto_path_conf(mode='responder',start_delay='12000',
                trigger='callsetup',media_type='audio')
        'enabled'
        '''

        if not mode or mode not in ['initiator', 'responder']:
            raise camelot.CamelotError('invalid mode specified')

        if trigger not in ['callsetup', 'midcall']:
            raise camelot.CamelotError('invalid trigger specified')

        if media_type not in ['audio', 'video']:
            raise camelot.CamelotError('invalid mediatype specified')

        kwargs = {'trigger': trigger,
                  'mode': mode,
                  'media': media_type}

        return self._query_camelot(
            camelot.ENABLE_AUTO_PATH_CONF, start_delay, **kwargs)

    def disable_auto_path_conf(self, trigger=None, media_type=None):
        '''
        Disables autopathconf

        Autopathconf can be disabled either for callsetup trigger or midcall
         trigger or both.
         :parameter media_type:This configuration parameter mentions the type
         of media i.e, audio or video

        :returns: The current autopathconf state, enabled or disabled

        >>> ep4.disable_auto_path_conf(trigger = 'callsetup',
        media_type = 'audio')
        'disabled'

        >>> ep4.disable_auto_path_conf(trigger = 'midcall',
        media_type = 'video')
        'disabled'

        >>> ep4.disable_auto_path_conf()
        'disabled'
        '''

        if not trigger or trigger not in ['callsetup', 'midcall']:
            raise camelot.CamelotError('invalid trigger specified')
        if media_type not in ['audio', 'video']:
            raise camelot.CamelotError('invalid mediatype specified')

        kwargs = {'trigger': trigger,
                  'mode': None,
                  'media': media_type}

        return self._query_camelot(
            camelot.DISABLE_AUTO_PATH_CONF, None, **kwargs)

    def enable_auto_path_conf_video(self, mode=None,
                                    start_delay=None, trigger=None):
        '''Configures an endpoint to perform video path confirmation
        when a call connects, i.e., during callsetup or whenever
        RTP path is renegotiated

        Configures an endpoint to perform video path confirmation when a call
        connects.  The mode option indicates which end will initiate path
        confirmation.  The start_delay option indicates the delay from call
        connect until video path confirmation begins.  If video path
        confirmation fails, the call will disconnect immediately and
        a failure indication will be logged with the call via the
        failure status field returned by getcallinfo.

        Mid-call video path confirmation is not supported on
        conference call flows.

        :parameter mode: One of the following:\n
            * initiator - initiate video path confirmation to remote end
            * responder - respond to video path confirmation initiated
                             from remote end
        :parameter start_delay: delay in milliseconds after the call connects
         and before initiating video path confirmation (initiator) or
         listening for video path confirmation (responder)
        :parameter trigger: This configuration parameter mentions when to
         trigger video path confirmation. This parameter takes two values.
         i.e., callsetup and midcall.\n
         * callsetup - As the call being setup for the first time. i.e., the
           video path confirmation is triggered for the first time the call
           goes to connected state. This is the default argument for
           trigger. i.e. if user omits trigger option then it is considered
           that autopathconfvideo shall be executed only once during the
           call setup.
         * midcall - Video Path confirmation will be triggered whenever
           RTP path is renegotiated. Note that video path confirmation
           will be kicked off when both inbound and outbound streams
           are open and the call is in connected state.

         Both trigger options can be configured on an endpoint and mode of
         endpoint can possibly be different in both cases. When video path
         confirmation fails call will be disconnected in both trigger cases.

        :returns: Returns current autocallguard state,
         enabled or disable

        >>> ep1.enable_auto_path_conf_video(mode='responder',
                start_delay='12000', trigger='callsetup')
        'enabled'
        '''
        mode_types = ['initiator', 'responder']
        trigger_types = ['callsetup', 'midcall']
        if not trigger or trigger not in trigger_types:
            log.error('Invalid Trigger Mode,'
                      'Please check the request')
            return
        if not mode or mode not in mode_types:
            log.error('Invalid Path Mode specified,'
                      'Please check the request')
            return
        if not start_delay:
            log.error('Invalid delay specified')
        kwargs = {'mode': mode,
                  'trigger': trigger,
                  'start_delay': start_delay,
                  'media': 'video'}
        return self._query_camelot(
            camelot.ENABLE_AUTO_PATH_CONF_VIDEO, None, **kwargs)

    def get_auto_path_conf_status(self, trigger=None, media_type='audio'):
        '''
        auto path configuration status

        :parameter trigger: This configuration parameter mentions when to
            trigger path confirmation. Possible values \n
            * callsetup (default)
            * midcall\n

        :returns: disabled/enabled

        >>> ep.get_auto_path_conf_status('callsetup')
        120
        '''
        trigger_types = ['callsetup', 'midcall']
        if not trigger or trigger not in trigger_types:
            log.error('Invalid Trigger Mode specified.')
            return

        kwargs = {'trigger': trigger,
                  'mode': None,
                  'media': media_type}

        return self._query_camelot(
            camelot.GET_AUTO_PATH_CONF_STATUS, None, **kwargs)

    def get_auto_path_conf_delay(self, trigger=None):
        '''
        Returns the delay from call connect until path confirmation begins

        :parameter trigger: This configuration parameter mentions when to
                            trigger path confirmation. Possible values \n
                            * callsetup (default)
                            * midcall
                            Note: If trigger not specified, it disables all

        :returns: the currently start delay is returned in millisec.

        >>> ep1.get_auto_path_conf_delay()
        '200'
        '''
        trigger_types = ['callsetup', 'midcall']
        if not trigger or trigger not in trigger_types:
            log.error('Invalid Trigger Mode specified.')
            return
        kwargs = {'trigger': trigger,
                  'mode': None}

        return self._query_camelot(
            camelot.GET_AUTO_PATH_CONF_DELAY, None, **kwargs)

    def get_auto_path_conf_mode(self, trigger=None):
        '''
       The currently configured mode is returned.

        :returns: The currently configured mode is returned.
        '''
        trigger_types = ['callsetup', 'midcall']
        if not trigger or trigger not in trigger_types:
            log.error('Invalid Trigger Mode specified.')
            return
        kwargs = {'trigger': trigger,
                  'mode': None}

        return self._query_camelot(
            camelot.GET_AUTO_PATH_CONF_MODE, None, **kwargs)

    def enable_auto_record(self, stream_type=None, prefix=None, **kwargs):
        '''Configures an endpoint to record inbound stream traffic to a file

        :parameter stream_type: type of traffic should be recorded. Possible
         values \n
            * audio
            * video
        :parameter prefix: String prefix to te beginning of all recorded files.

        :returns: enabled or disabled

        >>> ep.enable_auto_record('audio','camelot')
        enabled
        '''
        media_type = kwargs.get('media_type', None)
        if media_type:
            stream_type = media_type
        stream_types = ['audio', 'video']
        if not stream_type or stream_type not in stream_types:
            log.error('enable_auto_record: invalid media/stream'
                      'type specified')
            return
        kargs = {'type': stream_type,
                 'prefix': prefix}

        return self._query_camelot(camelot.ENABLE_AUTO_RECORD, **kargs)

    def disable_auto_record(self, stream_type=None, **kwargs):
        '''Disable auto record

        :parameter stream_type: type of traffic should be recorded. Possible
         values \n
            * audio
            * video

        :returns: disabled

        >>> ep.disable_auto_record('audio')
        disabled
        '''
        media_type = kwargs.get('media_type', None)
        if media_type:
            stream_type = media_type
        stream_types = ['audio', 'video']
        if not stream_type or stream_type not in stream_types:
            log.error('disable_auto_record: invalid media/stream'
                      'type specified')
            return
        kargs = {'type': stream_type,
                 'prefix': None}

        return self._query_camelot(camelot.DISABLE_AUTO_RECORD, **kargs)

    def get_auto_record_status(self, stream_type=None, **kwargs):
        '''get auto record status

        :parameter stream_type: type of traffic should be recorded. Possible
         values \n
            * audio
            * video

        :returns: enabled or disabled

        >>> ep.get_auto_record_status('audio)
        disabled
        '''
        media_type = kwargs.get('media_type', None)
        if media_type:
            stream_type = media_type
        stream_types = ['audio', 'video']
        if not stream_type or stream_type not in stream_types:
            log.error('disable_auto_record: invalid media/stream'
                      'type specified')
            return
        kargs = {'type': stream_type,
                 'prefix': None}

        return self._query_camelot(camelot.GET_AUTO_RECORD_STATUS, **kargs)

    def get_auto_record_prefix(self, stream_type=None, **kwargs):
        '''
        The currently configured prefix is returned.

        :parameter stream_type: type of traffic should be recorded. Possible
         values \n
            * audio
            * video

        :returns: the currently configured prefix is returned.
        '''
        media_type = kwargs.get('media_type', None)
        if media_type:
            stream_type = media_type
        stream_types = ['audio', 'video']
        if not stream_type or stream_type not in stream_types:
            log.error('disable_auto_record: invalid media/stream'
                      'type specified')
            return
        kargs = {'type': stream_type,
                 'prefix': None}

        return self._query_camelot(camelot.GET_AUTO_RECORD_PREFIX, **kargs)

    def enable_auto_hold(self, talk_time, hold_time):
        '''autohold Configures an endpoint to place a connected call on
        hold and then resume it.

        :parameter talk_time: delay in milliseconds from call connection
                              until hold is invoked
        :parameter hold_time: time in milliseconds call is on hold before
                              resume is invoked

        :returns: enabled or disabled

        >>> ep.enable_auto_hold(10,10)
        enabled
        '''
        kwargs = {'talk_time': talk_time,
                  'hold_time': hold_time}

        return self._query_camelot(camelot.ENABLE_AUTO_HOLD, **kwargs)

    def disable_auto_hold(self):
        '''disable auto hold


        :returns: disabled

        >>> ep.disable_auto_hold()
        disabled
        '''
        kwargs = {'talk_time': None,
                  'hold_time': None}

        return self._query_camelot(camelot.DISABLE_AUTO_HOLD, **kwargs)

    def get_auto_hold_hold_time(self):
        '''returns the hold time configured on an endpoint
        using auto_hold command

        :returns: hold time in milli secconds if auto_hold is enabled and
         hold_time is configured on endpoint therewise 0.

        >>> ep1.get_auto_hold_hold_time()
        '200'
        '''
        kwargs = {'talk_time': None,
                  'hold_time': None}

        return self._query_camelot(camelot.GET_AUTO_HOLD_HOLD_TIME, **kwargs)

    def get_auto_hold_talk_time(self):
        '''returns the auto talk time configured on an endpoint
        using auto_hold command

        :returns: talk time in milli secconds if auto_hold is enabled and
         talk_time is configured on endpoint therewise 0.
         '''
        kwargs = {'talk_time': None,
                  'hold_time': None}

        return self._query_camelot(camelot.GET_AUTO_HOLD_TALK_TIME, **kwargs)

    def get_auto_hold_status(self):
        '''get auto hold timer information


        :returns: disabled

        >>> ep.disable_auto_hold()
        disabled
        '''
        kwargs = {'talk_time': None,
                  'hold_time': None}

        return self._query_camelot(camelot.GET_AUTO_HOLD_STATUS, **kwargs)

    def disable_auto_select_join(self):
        '''disable auto select join


        :returns: disabled

        >>> ep.disable_auto_select_join()
        disabled
        '''
        kwargs = {}

        return self._query_camelot(camelot.DISABLE_AUTO_SELECT_JOIN, **kwargs)

    def enable_auto_select_join(self, mode=None, delay=None, called_list=None,
                                no_of_calls=None, timeout=None,
                                timer_action=None):
        '''Configures an endpoint to select multiple calls on it and join
        all of them to create an ad hoc conference.The trigger used for this
        is based on the mode specified

        For outbound mode, the list of targets specified are taken. Multiple
        outbound calls to these targets from respective lines specified are
        made on the calling device, keeping them connected for the specified
        talk_time. Once the talk_time for a call expires, the call would be
        put on hold and the next call to next target will be placed. Once the
        final talk_time of the final called party expires, all the calls on
        the endpoint will be selected and then finally joined into an ad hoc
        conference.

        For mode specified as inbound, the no of calls (connected+held) are
        taken as the trigger point. When the endpoints have the mentioned no
        of calls, the calls are selected and finally joined into an ad hoc
        conference. If timeout is specified, then if noofcalls are not made
        on the endpoint within the specified timeout value, autoselectjoin
        would either proceed and join available calls, or disconnect all
        calls, as specified in the timer_action parameter.

        :parameter mode:
                        * inbound - when the other calls included in the
                          select-join operation are expected to be inbound
                          and the trigger used is the no of calls on the
                          endpoint.
                        * outbound - where a called queue is provided and after
                          a delay the target list is called one after the other
                          and then all calls are selected and joined into a
                          single ad hoc conference.
        :parameter delay: For outbound mode, the time delay after the first
         call connects for the autoselectjoin operation to commence. For
         inbound mode, the time delay after the last call connects for
         auto select join to commence.
        :parameter called_list: required parameter if the mode is specified as
         'outbound'. It is a list of disctionaries with called address,
         calling line_ref and talk_time. list of dictionary format:
         [{'CalledDN': '123', 'LineRef': '1', 'Talktime': '1000'}, ...] where

            * CalledDN: Called Address for the outbound call
            * LineRef : The calling line reference on which the new call
              should be placed (to be able to support Join across
              lines)
            * Talktime: after connect how much longer should the endpoint wait
              before it puts the call on hold and dials out another
              call. For the final target, the completion of the
              talktime would trigger the auto select followed by
              join operation.
        :parameter no_of_calls: required parameter if the mode is specified as
         'inbound'. It is the number of connected and held calls on an
         endpoint for the autoselectjoin operation to trigger.
        :parameter timeout: In mode 'inbound', if the criteria for
         joining the selected calls (noofcalls) is not met within
         timeout ms, then autoselectjoin will proceed as mentioned
         in timer_action. If not specified, inbound autoselectjoin
         will not timeout.
        :parameter timer_action: required parameter if timeout is
         specified. proceed auto select join, on timeout after timeout
         ms, joins the selected calls.

        :returns: The current autoselectjoin state, enabled or disabled,
         unless the delay or called or no_of_calls or mode or timeout or
         timer_action option is specified with no argument.
         In which case the currently configured value for the parameter is
         returned.

        >>> ep.enable_auto_select_join(mode='inbound', delay='12000',
                no_of_calls='1', timeout='18000', timer_action='proceed')
        enabled
        '''
        mode_types = ['inbound', 'outbound']
        if sys.version_info < (3, 5):
            if not delay or not isinstance(delay, (int, long)) or delay < 0:
                delay = None
        else:
            if not delay or not isinstance(delay, int) or delay < 0:
                delay = None
        if sys.version_info < (3, 5):
            if (not no_of_calls or not isinstance(no_of_calls, (int, long)) or
                    no_of_calls < 0):
                no_of_calls = None
        else:
            if (not no_of_calls or not isinstance(no_of_calls, int) or
                    no_of_calls < 0):
                no_of_calls = None
        if sys.version_info < (3, 5):
            if (not timeout or not isinstance(timeout, (int, long)) or
                    timeout < 0):
                timeout = None
        else:
            if (not timeout or not isinstance(timeout, int) or
                    timeout < 0):
                timeout = None

        if not mode or mode not in mode_types:
            raise camelot.CamelotError(
                'Please specify mode as inbound/outbound')

        if mode == 'outbound' and no_of_calls:
            raise camelot.CamelotError(
                'No of calls is not a valid paramter with OUTBOUND call '
                'direction')

        if mode == 'inbound' and called_list and len(called_list) > 0:
            raise camelot.CamelotError(
                'called list is not a valid parameter for inbound mode')

        kwargs = {'mode': mode,
                  'delay': delay,
                  'called_list': called_list,
                  'no_of_calls': no_of_calls,
                  'timeout': timeout,
                  'timer_action': timer_action}

        return self._query_camelot(camelot.ENABLE_AUTO_SELECT_JOIN, **kwargs)

    def get_auto_select_join_called_list(self):
        '''returns the called list for auto select join on an endpoint

        :returns: Returns the called_list which is a list of disctionaries
         with called address, calling line_ref and talk_time. The format of
         list of dictionaries is :[{'CalledDN': '123', 'LineRef': '1',
         'Talktime': '1000'}, ...].

        >>> ep1.get_auto_select_join_called_list()
        [{'CalledDN': '123', 'LineRef': '1',
         'Talktime': '1000'}, ...]
        '''

        kwargs = {}
        return self._query_camelot(
            camelot.GET_AUTO_SELECT_JOIN_CALLED_LIST, **kwargs)

    def get_auto_select_join_delay(self):
        '''returns the time delay configured to commence the auto select join
        after the first call connected for an endpoint in milli seconds.

        :returns: returns delay time in milli seconds.

        >>> ep1.get_auto_select_join_delay()
        '200'
        '''
        kwargs = {}
        return self._query_camelot(
            camelot.GET_AUTO_SELECT_JOIN_DELAY, **kwargs)

    def get_auto_select_join_mode(self):
        '''Returns the comfigured mode for the auto_select_join for an
        endpoint.

        :returns: Returns the mode, the value can be either of 'inbound'
         or 'outbound'.

        >>> ep1.get_auto_select_join_mode()
        'inbound'
        '''
        kwargs = {}
        return self._query_camelot(
            camelot.GET_AUTO_SELECT_JOIN_MODE, **kwargs)

    def get_auto_select_join_no_of_calls(self):
        '''Returns the no of calls configured for auto_select_join for an
        endpoint.

        :returns: Returns the no of connected and hold calls on an
         endpoint.
        '''
        kwargs = {}
        return self._query_camelot(
            camelot.GET_AUTO_SELECT_JOIN_NO_OF_CALLS, **kwargs)

    def get_auto_select_join_status(self):
        '''returns the status of the auto select join configured
        on endpoint.

        :returns: Returns enabled if enable_auto_select_join is called
         otherwise disabled.

        >>> ep1.get_auto_select_join_status()
        'enabled'
        '''
        kwargs = {}
        return self._query_camelot(camelot.GET_AUTO_SELECT_JOIN_STATUS,
                                   **kwargs)

    def get_auto_select_join_time_out(self):
        '''Returns the timeout configured for auto select join.

        :returns: returns the time ion milli seconds.

        >>> ep1.get_auto_select_join_time_out()
        'enabled'
        '''
        kwargs = {}
        return self._query_camelot(camelot.GET_AUTO_SELECT_JOIN_TIME_OUT,
                                   **kwargs)

    def get_auto_select_join_timer_action(self):
        '''returns the timer_action configured for auto select join

        :returns: returns timer_action configred.

        >>> ep1.get_auto_select_join_timer_action()
        '''
        kwargs = {}
        return self._query_camelot(
            camelot.GET_AUTO_SELECT_JOIN_TIME_OUT_ACTION, **kwargs)

    def enable_auto_release(self):
        ''' Configures an endpoint to automatically release calls and
        streams when an outbound or inbound call or stream is present
        on an endpoint.

        Configures an endpoint to automatically release call and stream
        references when a new outbound or inbound call or stream is
        present on an endpoint.  This ensures call and stream references
        do not increase without bound as bulk calls are originated and/or
        terminated.

        :returns: Returns the current auto release status, enabled or disabled.

        >>> ep1.enable_auto_release()
        'enabled'
        '''

        return self._query_camelot(camelot.ENABLE_AUTO_RELEASE)

    def disable_auto_release(self):
        '''disables the auto release on endpoint

        :returns: Returns disabled on success.
        >>> disable_auto_release()
        'disabled'
        '''
        return self._query_camelot(camelot.DISABLE_AUTO_RELEASE)

    def get_auto_release_status(self):
        '''Returns the status of auto release on endpoint.

        :returns: Returns 'enabled' if auto release is enabled otherwise
            disabled.

        >>> ep1.get_auto_release_status()
        'enabled'
        '''
        return self._query_camelot(camelot.AUTO_RELEASE_STATUS)

    def enable_auto_fax(self, mode, filename=None, prefix=None):
        '''Configures an endpoint to transfer a fax

        Configures an endpoint to initiate a fax session when a call connects.
        The mode option indicates whether the session will be a sending or
        receiving. If sending,the filename option must be specified to indicate
        which tiff file to send (see the Camelot/lib/media directory). If
        receiving, the prefix option may optionally be specified to prefix
        the received file with an arbitrary string.  If no filename is given
        prefix is mandatory to place the received file in a default
        location (/usr/camelot/lib/).  If filename is specified, the received
        file will be stored in the mentioned path

        :parameter mode:  can take two values. 'send' to send a fax,
         'receive' to receive a fax
        :parameter filename: Name of the file with absolute path
                            to be sent through fax or received.
        :parameter prefix: string prefixed to received files

        :returns: returns 'enabled' if auto fax is enabled otherwise
         'disabled'.

         >>> ep1.vapi.enable_auto_fax(mode='send', filename='/Fax/myfax.tiff')
         >>> True

         >>> ep1.vapi.enable_auto_fax(mode='receive',
                                     filename='/Fax/myfaxout.tiff')
         >>> True
        '''
        log.debug('autofax mode = %s, url = %s, prefix=%s' %
                  (mode, filename, prefix))
        if mode not in ['send', 'receive']:
            raise camelot.CamelotError('invalid mode')
        if mode == 'send' and not filename:
            raise camelot.CamelotError('filename not specified')
        if mode == 'receive':
            if not filename and not prefix:
                raise camelot.CamelotError('prefix mandagory when no filename')

        kwargs = {'mode': mode,
                  'url': filename,
                  'prefix': prefix}

        return self._query_camelot(camelot.ENABLE_AUTO_FAX, **kwargs)

    def disable_auto_fax(self):
        '''disables the auto fax on an endpoint

        :returns: Returns disabled on success.
        >>> ep1.disable_auto_fax()
        'disabled'
        '''
        return self._query_camelot(camelot.DISABLE_AUTO_FAX)

    def get_auto_fax_mode(self):
        '''Returns the auto fax mode configured on enadpoint.

        :returns: returns the mode configured for auto fax, can be of
         'send' or 'recieve'.

        >>> ep1.get_auto_fax_mode()
        'send'
        '''
        return self._query_camelot(camelot.GET_AUTO_FAX_MODE)

    def get_auto_fax_url(self):
        ''' Returns the URL configured for auto fax.

        :returns: Returns the URL configured for auto fax.

        >>> ep1.get_auto_fax_url()
        'fax1@cisco.com'
        '''
        return self._query_camelot(camelot.GET_AUTO_FAX_URL)

    def get_auto_fax_status(self):
        '''Returns the status of auto_fax on endpoint

        :returns: Returns 'enabled' if auto_fax is enabled
         otherwise 'disabled'.

        >>> ep1.get_auto_fax_status()
        'enabled'
        '''
        return self._query_camelot(camelot.GET_AUTO_FAX_STATUS)

    def enable_auto_voice(self,
                          mode,
                          filename=None,
                          send_sample_rate=camelot.
                          DivaSamplingRate.DivaSamplingRateNormal,
                          recv_audio_format=camelot.DivaAudioFormat.
                          DivaAudioFormat_Raw_aLaw8K8BitMono):
        '''This method is exclusively for CAS endpoints. (For other endpoints,
        please use 'auto_traffic' method).It configures an endpoint to send a
        voice file or receive voice data when a CAS call connects.

        :parameter mode:  can take two values. 'send' to send a voice file,
         'receive' to receive voice data. Its a mendatory parameter.
        :parameter filename: Name of the file with absolute path.Mandatory
         and required only for 'send' mode.
        :parameter recv_audio_format: Optional parameter.
         Applicable for 'receive' mode only.
         Valid values are same as that of the values given for
         DivaAudioFormat enum in Diva Guide.
         This parameter is applicable for receive mode only.Default value is
         100 (Which is DivaAudioFormat_Raw_aLaw8K8BitMono).
        :parameter send_sample_rate: Optional parameter.
         Applicable for 'send' mode only.Valid values are same as that of
         the values given for DivaSamplingRate in Diva Guide.
         Also please refer to following wiki:
         'https://wiki.cisco.com/display/CAMELOT/Analog+ATA-190+Voice+Support'
         Default value will be DivaSamplingRateNormal=8000.

        :returns: If the command succeeds it returns enabled.
         Incase of error, returns the specific error.

        >>> ep1.vapi.enable_auto_voice(mode='send',
             filename='/tmp/Greeting.wav',
             send_sample_rate=camelot.DivaSamplingRate.DivaSamplingRateNormal)
        enabled
        >>> ep1.vapi.enable_auto_voice(mode='receive',
            recv_audio_format=
            camelot.DivaAudioFormat.DivaAudioFormat_Raw_aLaw8K8BitMono)
        enabled
        '''
        log.debug('autovoice mode = %s' %
                  (mode))
        if mode not in ['send', 'receive']:
            raise camelot.CamelotError('invalid mode')
        if mode == 'send':
            if not filename:
                raise camelot.CamelotError('filename not specified'
                                           'for send mode')
            log.debug('filename = %s send_sample_rate = %d' %
                      (filename, send_sample_rate.value))
        if mode == 'receive':
            filename = None
            log.debug('recv_audio_format = %d' %
                      (recv_audio_format.value))

        kwargs = {'mode': mode,
                  'filename': filename,
                  'send_sample_rate': send_sample_rate.value,
                  'recv_audio_format': recv_audio_format.value}

        return self._query_camelot(camelot.ENABLE_AUTO_VOICE, **kwargs)

    def disable_auto_voice(self):
        '''disables the auto voice on an endpoint

        :returns: If the command disables auto voice it returns disabled.
         Incase of error, returns the specific error.

        >>> ep1.disable_auto_voice()
        'disabled'
        '''
        return self._query_camelot(camelot.DISABLE_AUTO_VOICE)

    def enable_auto_emservice(self, delay=None, user=None, pin=None,
                              profile='$$$$$',
                              servicename='Extension Mobility'):
        '''Configure the endpoint to perform an Extension Mobility
        service automatically.

        Configures the endpoint to kick off an Extension Mobility service upon
        call termination. The endpoint will attempt to access the Extension
        Mobility service menu page and will attempt login/logout based on menu
        options. Note, the delay timer is started upon call disconnect event;
        if while delay timer is pending another call disconnect event occurs
        than the timer is restarted.

        :parameter delay: Delay in milliseconds to wait from call disconnect
         time before initiating the service.
        :parameter user: The user-id used for Extension Mobility service
         log on.
        :parameter pin: The PIN used for Extension Mobility log on.
        :parameter profile: Profile name to select. If not specified
         the first profile returned will be automatically selected.
        :parameter servicename: The service name to match. If not specified
         'Extension Mobility' will be attempted.

        :returns: The Current configuration 'enabled' or 'disabled'.
        '''
        if not user:
            raise camelot.CamelotError('user not specified')

        if not pin:
            raise camelot.CamelotError('pin not specified')

        if sys.version_info < (3, 5):
            if not isinstance(delay, (int, long)) or delay < 0:
                raise camelot.CamelotError('invalid delay specified')
        else:
            if not isinstance(delay, int) or delay < 0:
                raise camelot.CamelotError('invalid delay specified')

        kwargs = {'delay': delay,
                  'user': user,
                  'pin': pin,
                  'profile': profile,
                  'sname': servicename}

        return self._query_camelot(camelot.ENABLE_AUTO_EM_SERVICE, **kwargs)

    def disable_auto_emservice(self):
        '''disables the auto emservice on endpoint

        :returns: True on success otherwise False.
        '''
        return self._query_camelot(camelot.DISABLE_AUTO_EM_SERVICE)

    def get_auto_emservice_status(self):
        '''returns the status of auto emservice  configured on endpoint

        :returns: Returns 'enabled' if auto_emservice is enabled otherwise
         'disabled'.

        >>> ep1.get_auto_emservice_status()
        'enabled'
        '''
        return self._query_camelot(camelot.GET_AUTO_EM_STATUS)

    def enable_auto_script(self, string_list=None, trigger='connected'):
        '''Configures an endpoint to execute a simple script on the
        server when a call connected or alerting state. User can use trigger
        parameter to configure the same.
        Note: User can configure auto_script only once having
        trigger value as either 'connected' or 'alerting'

        Configures an endpoint to automatically execute a specified script when
        a call connected or alerting state. A script is specified as
        a list of commands, each command can have multiple arguments.
        The following script commands are supported:\n
        * wait -seconds sec -- delay/wait the specified number of seconds
        * dial -called digits -- dial the specified digits
        * pathconf -mode (initiator | responder) --perform path confirmation
        * traffic -type (audio | video) -mode (continuous | random | playonce)
          initiate bearer traffic
        * playtone -freq freq  -ontime  seconds - play a tone playmedia type
          (audio | video)
        * url url  -encoding encoding
        * checktone -freq freq  -timeout  seconds -check for the
          presence of a tone
        * check -field field  -value regexp -check endpoint information
        * checkcall -field field  -value regexp -check call information
        * checkstream  -type (audio | video)  -mode (inbound | outbound)
          -field field  -value regexp -check stream information
        * endcall -End the call manually; autodisconnect not required when
          this is used
        * checkprompt  -type (bin) -timeout seconds -pattern 'blob1' 'blob2'
          ... 'blob10'
        * playdtmf -digits digits -ontime ontime -offtime offtime -play
          digits as RFC 2833 DTMF packets on outbound audio RTP stream

          Wiki Link: https://wiki.cisco.com/display/CAMELOT/autoscript

        :parameter string_list: list of script commands
        :parameter trigger: string of call state when it triggers\n
            * connected - script triggers after call connected state
            * alerting - script triggers after call altering state\n
             connected is default. Other than these values script will throw
             an exception as invalid trigger specified.

        :returns: The current autoscript state, enabled or disabled.

        >>> mylist = [ "wait -seconds 10", "endcall" ]
        >>> ep1.enable_auto_script(string_list=mylist)
            'enabled'

           OR

        >>> ep.enable_auto_script(string_list=mylist, trigger='alerting')
            'enabled'
        '''
        if not string_list or len(string_list) <= 0:
            raise camelot.CamelotError('Script string array not specified.')

        trigg_types = ['connected', 'alerting']
        if (trigger not in trigg_types):
            raise camelot.CamelotError('invalid trigger specified.')
        kwargs = {'trigger': trigger}
        return self._query_camelot(camelot.ENABLE_AUTO_SCRIPT, string_list,
                                   **kwargs)

    def disable_auto_script(self):
        '''disables the auto script if enabled on endpoint

        :returns: disabled on success.
        >>> ep1.disable_auto_script()
        'disabled'
        '''
        return self._query_camelot(camelot.DISABLE_AUTO_SCRIPT)

    def get_auto_script_status(self):
        '''gets the auto_script status configured for an endpoint

        :returns: returns 'enabled' if auto_script is enabled otherwise
         'disabled'.

        ep1.get_auto_script_status()
        'enabled'
        '''
        return self._query_camelot(camelot.GET_AUTO_SCRIPT_STATUS)

    def get_auto_script_script(self):
        '''gets the script configured to run for an endpoint for auto_script

        :returns: returns the script which is list of commands if configured
         for an endpoint.
        '''
        return self._query_camelot(camelot.GET_AUTO_SCRIPT_SCRIPT)

    def enable_auto_move(self, delay, mute=0):
        '''Configures an endpoint to automatically perform the move method
           after the specified delay has expired.

        :returns: 'enabled'

        >>> ep1.enable_auto_move()
        'enabled'
        '''
        if sys.version_info < (3, 5):
            if not isinstance(delay, (int, long)) or delay < 0:
                raise camelot.CamelotError('delay value must be specified')
        else:
            if not isinstance(delay, int) or delay < 0:
                raise camelot.CamelotError('delay value must be specified')

        if sys.version_info < (3, 5):
            if not isinstance(mute, (int, long)) or mute not in [0, 1]:
                raise camelot.CamelotError('Invalid mute value specified')
        else:
            if not isinstance(mute, int) or mute not in [0, 1]:
                raise camelot.CamelotError('Invalid mute value specified')
        kwargs = {'delay': delay,
                  'mute': mute}
        return self._query_camelot(camelot.ENABLE_AUTO_MOVE, **kwargs)

    def disable_auto_move(self):
        '''Configures a CUMC  endpoint to automatically perform the move
           method after a specified delay.

        :returns: 'disabled'.

        >>> ep1.disable_auto_move()
        'disabled'
        '''
        return self._query_camelot(camelot.DISABLE_AUTO_MOVE)

    def get_auto_move_display(self):
        '''
        To retrieve the current setting of auto move.

        :returns: enabled or disabled, delay in milliseconds
                  and mute on or off

        >>> ep1.get_auto_move_display()
           'enabled'
        '''
        return self._query_camelot(camelot.GET_AUTO_MOVE_DISPLAY)

    def enable_auto_traffic(self, media_type, mode):
        '''Configures an endpoint to stream bearer traffic when the
        corresponding outbound stream opens

        Configures an endpoint to stream traffic when the corresponding
        outbound stream opens.  The media_type indicates whether audio or
        video traffic should be streamed.  This option is mandatory and must
        be specified on every autotraffic invocation.  Note, an endpoint can
        be configured to stream both audio and video traffic simultaneously.
        The -mode option indicates how the traffic should streamed, either
        continuously or intermittently.

        If autotraffic and autopathconf are both configured, audio traffic will
        begin streaming after path confirmation has completed.

        **Limitations:**
         Presently, with the exception of CTS eps, media for eps using AAC
         codec is not supported. If the ep is configured to use AAC codec,
         there will be no RTP packets sent over the media stream. With CTS ep,
         AAC media traffic will be sent, however, a pre-recorded file of RTP
         packet is played back and that there is no actual encoding/decoding of
         the media.

         Wiki Link: https://wiki.cisco.com/display/CAMELOT/autotraffic

        :parameter media_type: One of the following values
            * audio - record audio traffic
            * video - record video traffic.
            Specifying a type is mandatory for all invocations.
        :parameter mode: One of the following values
            * continuous - stream traffic continuously
            * random - stream traffic intermittently
            * playonce - stream traffic once

        :returns: The current autotraffic state, enabled or disabled

        >>> ep4.enable_auto_traffic(media_type = 'audio',
                                         mode = 'continuous')
        'enabled'
        '''
        mode_types = ['continuous', 'random', 'playonce']
        media_types = ['audio', 'video', 'slides']
        if (media_type not in media_types or mode not in mode_types):
            raise camelot.CamelotError(
                'Invalid media_type or mode')
        kwargs = {'mediatype': media_type,
                  'mode': mode}
        return self._query_camelot(camelot.ENABLE_AUTO_TRAFFIC, **kwargs)

    def disable_auto_traffic(self, media_type):
        '''
        Disables autotraffic

        :returns: The current autotraffic state, either enabled or disabled

        >>> ep4.disable_auto_traffic(media_type = 'audio')
        'disabled'

        '''
        media_types = ['audio', 'video']
        if media_type not in media_types:
            raise camelot.CamelotError('invalid media type specified')

        kwargs = {'mediatype': media_type}
        return self._query_camelot(camelot.DISABLE_AUTO_TRAFFIC, **kwargs)

    def get_auto_traffic_mode(self, media_type):
        '''
        The currently configured mode is returned

        :returns: The currently configured mode is returned

        >>> ep1.get_auto_traffic_mode()
        'continuos'
        '''
        media_types = ['audio', 'video']
        if media_type not in media_types:
            raise camelot.CamelotError('invalid media type specified')

        kwargs = {'mediatype': media_type}
        return self._query_camelot(camelot.GET_AUTO_TRAFFIC_MODE, **kwargs)

    def get_auto_traffic_status(self, media_type):
        '''
        The current autotraffic state, either enabled or disabled

        :returns: The current autotraffic state, either enabled or disabled

        >>> ep1.get_auto_traffic_status()
        'enabled'
        '''
        media_types = ['audio', 'video']
        if media_type not in media_types:
            raise camelot.CamelotError('invalid media type specified')

        kwargs = {'mediatype': media_type}
        return self._query_camelot(
            camelot.GET_AUTO_TRAFFIC_STATUS, **kwargs)

    def enable_auto_park(self, park_type, talk_time=10000,
                         disc_timeout=60000, status_timeout=60000,
                         button_number=None):
        '''
        Configures an endpoint to automatically parks and wait for park status
        Also please refer following Wiki \n
        https://wiki.cisco.com/display/CAMELOT/auto_park

        :parameter park_type: Type of park to initiate. Passible
         values \n
            * blfdpark    - for BLF dpark based park
            * softkey     - for softkey based park
            * parkmonitor - for park monitor

        :parameter talk_time: Delay in milliseconds from call
         connection until park is invoked.
         Default will be 10000\n

        :parameter disc_timeout: Timeout in milliseconds waiting to receive BYE
         for the call from CUCM after successful park initiation.\n
         Initiate call disconnect on this timer expiry

        :parameter status_timeout: Timeout in milliseconds waiting for park
         status notification from CUCM (REFER notify_display) after successful
         park initiation.\n
         Initiate call disconnect on this timer expiry,
         if call is not already disconnected.

        :parameter button_number: Button number of a BLF dpark configured.
         If the button_number did not match from
         get_button_blf() it will throw an exception to the user with error
         'can not enable auto_park: button number not configured for
         BLF dpark feature' etc.,

        :returns:  If the command enables auto_park
         configuration it returns enabled.\n
         For invalid parameter values, it returns like 'invalid park_type'\n
         For missing mandatory parameter, it returns like 'talk_time
         not specified'\n


        >>> enable_auto_park(park_type='blfdpark', talk_time=10000,
        disc_timeout=60000,status_timeout=61000, button_number=3)
        'enabled'
        '''

        log.debug('Entering enable_auto_park function')
        if park_type not in ['softkey',
                             'parkmonitor', 'blfdpark']:
            raise Exception('Invalid park_type')
        if not talk_time:
            # return 'talk time not specified'
            talk_time = '10000'
        elif not disc_timeout:
            # return 'disc_time not specifed'
            disc_timeout = '61000'
        elif not status_timeout:
            # return 'status_time not specified'
            status_timeout = '60000'

        kwargs = {'talktime': str(talk_time),
                  'parktype': str(park_type),
                  'disc_t': str(disc_timeout),
                  'status_t': str(status_timeout),
                  'buttonno': str(button_number)}

        return self._query_camelot(camelot.ENABLE_AUTO_PARK, **kwargs)

    def get_auto_park(self):
        '''
        returns the command status and other attributes
        of auto_park on endpoint

        :returns: Returns auto_park() enable status along with other
         attribites configured.

        >>> ep1.get_auto_park()
        {'auto_park_api_status': 'enabled',
         'park_type': 'blkdpark',
         'talk_time': '10000',
         'disc_timeout': '5000',
         'status_timeout': '5000',
         'button_number': '3'}

        >>> ep1.get_auto_park()
        {'auto_park_api_status': 'disabled',
         'park_type': '',
         'talk_time': '',
         'disc_timeout': '',
         'status_timeout': '',
         'button_number': ''}
        '''
        return self._query_camelot(camelot.GET_AUTO_PARK)

    def disable_auto_park(self):
        '''
        disables auto park for an endpoint.

        :returns: If the command disables autopark configuration it returns
         disabled.

        >>> ep1.disable_auto_park()
        'disabled'
        '''
        log.debug('Entering disable_auto_park function')
        return self._query_camelot(camelot.DISABLE_AUTO_PARK)

    def enable_auto_park_retrieve(self, park_type, park_number=None,
                                  button_number=None, trigger_time=10000,
                                  complete_timeout=20000,
                                  talk_time=10000):
        '''
        Configures an endpoint to automatically retrieve parked call and
        disconnects after retrieve success.

        :parameter park_type: Type of park to initiate. Passible
         values \n
            * blfdpark   - for BLF dpark based park
            * softkey    - for softkey based park

        :parameter park_number: Park number to dial to retrieve.
         Optional if retrieved from same phone.

        :parameter button_number: Button number of a BLF dpark configured
         to retrieve.

        :parameter trigger_time: This is the time duration in milliseconds
         used to trigger the retrieve after the park is complete.

        :parameter complete_timeout: Timeout in milliseconds waiting for
         the retrieve call gets connected (indicates retrieve is complete).\n
         Initiate call disconnect on this timer expiry

        :parameter talk_time: Delay in milliseconds from call
         connection after retrieve complete and trigger disconnect for
         the retrieval party.

        :returns:  Returns enabled on configuration success.\n
         For invalid parameter values, it returns like 'invalid park_type'\n


        >>> enable_auto_park_retrieve(park_type='blfdpark', button_number=3,
        trigger_time=10000, complete_timeout=20000, talk_time=10000)
        'enabled'
        '''

        log.debug('Entering enable_auto_park_retrieve function')

        if park_type not in ['softkey', 'blfdpark']:
            raise Exception('Invalid park_type')
        if (park_type == 'blfdpark' and
           park_number is None and
           button_number is None):
            msg = 'Either park_number or button_number is required'
            raise Exception(msg)
        if park_number is None:
            park_number = 0
        if not talk_time:
            talk_time = '10000'
        elif not trigger_time:
            trigger_time = '10000'

        kwargs = {'talktime': str(talk_time),
                  'parktype': str(park_type),
                  'parknum': str(park_number),
                  'triggertime': str(trigger_time),
                  'completetime': str(complete_timeout),
                  'buttonno': str(button_number)}

        return self._query_camelot(camelot.ENABLE_AUTO_PARK_RET, **kwargs)

    def get_auto_park_retrieve(self):
        '''
        returns the command status and other attributes
        of auto_park on endpoint

        :returns: Returns auto_park() enable status along with other
         attribites configured.

        >>> ep1.get_auto_park_retrieve()
        {'auto_park_api_status': 'enabled',
         'park_type': 'blkdpark',
         'talk_time': '10000',
         'disc_timeout': '5000',
         'status_timeout': '5000',
         'button_number': '3'}

        >>> ep1.get_auto_park_retrieve()
        {'auto_park_api_status': 'disabled',
         'park_type': '',
         'talk_time': '',
         'disc_timeout': '',
         'status_timeout': '',
         'button_number': ''}
        '''
        return self._query_camelot(camelot.GET_AUTO_PARK_RET)

    def disable_auto_park_retrieve(self):
        '''
        disables auto park retrieve for an endpoint.

        :returns: On command success, returns disabled.

        >>> ep1.disable_auto_park_retrieve()
        'disabled'
        '''
        log.debug('Entering disable_auto_park_retrieve function')
        return self._query_camelot(camelot.DISABLE_AUTO_PARK_RET)
