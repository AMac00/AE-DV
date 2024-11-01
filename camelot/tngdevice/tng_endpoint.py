'''
Created on Jun 30, 2015

@author: smaturi
'''
from camelot.endpoint import CamelotEndpoint
import logging
from camelot.utils.vapi_ei_utils import VAPIEIUtils
from twisted.internet import threads
from camelot.utils.rawendpoint_helper import MsgObject

log = logging.getLogger(__name__)


class CamelotTngEndpoint(CamelotEndpoint):
    '''TNGpi Endpoint defination for Camelot
    '''
    def __init__(self, ep_id, camelot_server_conn):
        super(CamelotTngEndpoint, self).__init__(ep_id, camelot_server_conn)
        self.registered_events = []
        self.fb_receiver = None

    def parse_verify_events(self, values):
        ret_dict = {}
        ret_dict['event_type'] = 'verifyevent'
        token_list = values.split(" ")
        if len(token_list) < 2:
            log.error('Erronous verifyevent, returning..')
            return ret_dict

        ret_dict['timestamp'] = token_list[0]
        ret_dict['event_sub_type'] = token_list[1]
        ret_dict['msgid'] = token_list[2]
        ret_dict['result'] = token_list[3]
        ret_dict['detail'] = token_list[4]
        ret_dict['call_handler'] = token_list[5]
        ret_dict['subscription_handler'] = token_list[6]

        return ret_dict

    def parse_media_events(self, values):
        ret_dict = {}
        ret_dict['event_type'] = 'mediaevent'
        token_list = values.split()
        if len(token_list) < 3:
            log.error('Erronous media event, returning..')
            return ret_dict
        stream_ref = token_list[0]
        stream_ref = '0x' + stream_ref.lower()
        ret_dict['stream_ref'] = stream_ref
        ret_dict['timestamp'] = token_list[1]
        event_sub_type = token_list[2]
        ret_dict['event_sub_type'] = event_sub_type
        ret_dict['digit'] = 0
        ret_dict['tone_id'] = ''
        ret_dict['reason'] = ''
        ret_dict['url'] = ''

        if event_sub_type not in VAPIEIUtils.media_event_types:
            log.error('Unknown media event sub type, error while parsing')
            return ret_dict

        if event_sub_type == 'dtmfdetdone':
            ret_dict['reason'] = token_list[3]
            if len(token_list) == 5:
                ret_dict['err_string'] = token_list[4]
            else:
                ret_dict['err_string'] = None

        elif event_sub_type == 'digitbegin':
            if token_list[3].isdigit():
                ret_dict['digit'] = int(token_list[3])
            else:
                ret_dict['digit'] = token_list[3]

        elif event_sub_type == 'digitend':
            if token_list[3].isdigit():
                ret_dict['digit'] = int(token_list[3])
            else:
                ret_dict['digit'] = token_list[3]

        elif event_sub_type == 'tonedetstarted':
            ret_dict['tone_id'] = token_list[3]

        elif event_sub_type == 'tonedetdone':
            ret_dict['tone_id'] = token_list[3]
            ret_dict['reason'] = token_list[4]
            if len(token_list) == 6:
                ret_dict['err_string'] = token_list[5]
            else:
                ret_dict['err_string'] = None

        elif event_sub_type == 'tonebegin':
            ret_dict['tone_id'] = token_list[3]

        elif event_sub_type == 'toneend':
            ret_dict['tone_id'] = token_list[3]

        elif event_sub_type == 'recordstarted':
            ret_dict['url'] = token_list[3]

        elif event_sub_type == 'recorddone':
            ret_dict['reason'] = token_list[3]
            ret_dict['url'] = token_list[4]
            if len(token_list) == 6:
                ret_dict['err_string'] = token_list[5]
            else:
                ret_dict['err_string'] = None

        elif event_sub_type == 'tonedone':
            ret_dict['reason'] = token_list[3]
            if len(token_list) == 5:
                ret_dict['err_string'] = token_list[4]
            else:
                ret_dict['err_string'] = None

        elif event_sub_type == 'trafficdone':
            ret_dict['reason'] = token_list[3]
            if len(token_list) == 5:
                ret_dict['err_string'] = token_list[4]
            else:
                ret_dict['err_string'] = None

        elif event_sub_type == 'mediadone':
            ret_dict['reason'] = token_list[3]
            if len(token_list) == 5:
                ret_dict['err_string'] = token_list[4]
            else:
                ret_dict['err_string'] = None

        elif event_sub_type == 'prompt':
            ret_dict['prompt_path'] = token_list[3]
            ret_dict['prompt_name'] = token_list[4]
            ret_dict['byte_drop_max'] = token_list[5]
            ret_dict['num_expected_bytes'] = token_list[6]
            ret_dict['num_actual_bytes'] = token_list[7]

        elif event_sub_type == 'promptdetdone':
            ret_dict['reason'] = token_list[3]
            if len(token_list) == 5:
                ret_dict['err_string'] = token_list[4]
            else:
                ret_dict['err_string'] = None

        return ret_dict

    def parse_raw_events(self, values):
        ret_dict = {}
        ret_dict['event_type'] = 'siprawmsg'
        token_list = values.split(" ")
        if len(token_list) < 3:
            log.error('Erronous siprawmsg, returning..')
            return ret_dict

        ret_dict['timestamp'] = token_list[0]
        ret_dict['event_sub_type'] = token_list[1]
        msgstr = token_list[2]
        msgobj = MsgObject(self._device.vapi, msgstr)
        ret_dict['msgid'] = msgobj
        return ret_dict

    def _generic_callback_function(self, event_org):
        try:
            event_object = vars(event_org)
            log.debug('CamelotTNGpi Endpoint Event Receiver: %s' %
                      event_object)

            self.fb_receiver.on_event_callback(event_object)

            list_of_possible_events = []
            event_type = event_object['event_type']

            if event_type == 'verifymsg':
                parsed_obj = self.parse_verify_events(
                    event_object['message'])
            if event_type == 'siprawmsg':
                parsed_obj = self.parse_raw_events(
                    event_object['message'])
            if event_type == 'media':
                parsed_obj = self.parse_media_events(
                    event_object['message'])

            for registered_event in self.registered_events:
                if registered_event['event_type'] == event_type:
                    list_of_possible_events.append(registered_event)

            event_object['endpoint_obj'] = self._device

            for event in list_of_possible_events:
                if (event_object['event_type'] == 'verifymsg' or
                        event_object['event_type'] == 'siprawmsg'):
                    if (parsed_obj['event_sub_type'] ==
                            event['event_sub_type']):
                        event_object.update(parsed_obj)
                        event_object['event_type'] = 'rawevent'
                        cb = event['call_back']
                        threads.deferToThread(cb, event_object)
                        break
                elif (event_object['event_type'] == 'media'):
                    event_object.update(parsed_obj)
                    cb = event['call_back']
                    threads.deferToThread(cb, event_object)
                    break
                elif ((not event['event_sub_type']) or
                        (event_object['event_sub_type'] ==
                         event['event_sub_type'])):
                    cb = event['call_back']
                    threads.deferToThread(cb, event_object)
        except Exception as e:
            log.debug('Failed during feedback process: %s' % e)

    def register_to_event(self, event_type, event_sub_type=None,
                          call_back=None):
        '''Client script can register a call back to the endpoint for specific
        type of event collection. The registered call back will be invoked when
        an event occurs in Camelot with event dictionary passed to the callback

        :parameter event_type: type of the event, one of the following:
            * infoevent
            * stationevent
            * callevent
            * callinfoevent
            * streamevent
            * streaminfoevent
            * mediaevent
            * rawevent
            * verifyevent
        :parameter event_sub_type: sub type for a given event, if not passed
            will be registered to all types of the event
        :parameter call_back: callback method reference

        >>> def event_callback(event): # defining the call back function
        ...     print event
        ...
        >>> ep1.vapi.register_to_event('stationevent',
                                       call_back=event_callback)
        # This will start the station event collection on server
        >>> ep1.vapi.start_station_events()
        True
        '''

        if not call_back:
            log.error('Please specify a user callback function')
            return
        if event_type not in VAPIEIUtils.event_types:
            log.error('Unknown event type: %s' % event_type)
            return

        '''If infoevent, then the event_type itself is event_sub_type'''
        if event_type == 'infoevent':
            if event_sub_type and (event_sub_type not in
                                   VAPIEIUtils.info_event_types):
                log.error('Invalid infoevent type, returning...')
                return
            event_type = event_sub_type
            event_sub_type = None
        elif event_type == 'stationevent':
            if event_sub_type and (event_sub_type not in
                                   VAPIEIUtils.station_event_types):
                log.error('Invalid stationevent type, returning...')
                return
            event_type = 'station'
        elif event_type == 'callevent':
            if event_sub_type:
                log.error('No event_sub_type required for callevent')
                return
            event_type = 'call'
            event_sub_type = None
        elif event_type == 'streamevent':
            if event_sub_type:
                log.error('No event_sub_type required for streamevent')
                return
            event_type = 'stream'
        elif event_type == 'callinfoevent':
            if event_sub_type:
                log.error('No event_sub_type required for callinfoevent')
                return
            event_type = 'callstate'
            event_sub_type = None
        elif event_type == 'streaminfoevent':
            if event_sub_type:
                log.error('No event_sub_type required for streaminfoevent')
                return
            event_type = 'streamstate'
            event_sub_type = None
        elif event_type == 'mediaevent':
            event_type = 'media'
        elif event_type == 'traceevent':
            event_type = 'log'
        elif event_type == 'transportevent':
            event_type = 'tansport'
        elif event_type == 'transportinfoevent':
            event_type = 'transportstate'
        elif event_type == 'rawevent':
            event_type = 'siprawmsg'
        elif event_type == 'verifyevent':
            event_type = 'verifymsg'

        event_dict = {'event_type': event_type,
                      'event_sub_type': event_sub_type,
                      'call_back': call_back}

        '''Check if already registered'''
        for registered_event in self.registered_events:
            if registered_event['event_type'] == event_type:
                if event_sub_type:
                    if event_sub_type == registered_event['event_sub_type']:
                        log.warning(('Already registered to event_type %s and'
                                     'subtype %s') %
                                    (event_type, event_sub_type))
                        return
                else:
                    log.warning('Already registered to event type %s'
                                % event_type)
                    return
        self.registered_events.append(event_dict)

    def unregister_event(self, event_type, event_sub_type=None):
        if event_type not in VAPIEIUtils.event_types:
            log.error('Unknown event type: %s' % event_type)
            return
        event_to_remove = None

        '''If infoevent, then the event_type itself is event_sub_type'''
        if event_type == 'infoevent':
            if event_sub_type not in VAPIEIUtils.info_event_types:
                log.error('Unknown infoevent type, returning...')
                return
            event_type = event_sub_type
            event_sub_type = None
        elif event_type == 'stationevent':
            event_type = 'station'
            if event_sub_type and (event_sub_type not in
                                   VAPIEIUtils.station_event_types):
                log.error('Invalid stationevent type, returning...')
                return
        elif event_type == 'callevent':
            if event_sub_type:
                log.error('No event_sub_type required for callevent')
                return
            event_type = 'call'
            event_sub_type = None
        elif event_type == 'streamevent':
            if event_sub_type:
                log.error('No event_sub_type required for callevent')
                return
            event_type = 'stream'
        elif event_type == 'callinfoevent':
            if event_sub_type:
                log.error('No event_sub_type required for callinfoevent')
                return
            event_type = 'callstate'
            event_sub_type = None
        elif event_type == 'streaminfoevent':
            if event_sub_type:
                log.error('No event_sub_type required for streaminfoevent')
                return
            event_type = 'streamstate'
            event_sub_type = None
        elif event_type == 'mediaevent':
            event_type = 'media'
        elif event_type == 'traceevent':
            event_type = 'log'
        elif event_type == 'transportevent':
            event_type = 'tansport'
        elif event_type == 'transportinfoevent':
            event_type = 'transportstate'
        elif event_type == 'rawevent':
            event_type = 'siprawmsg'
        elif event_type == 'verifyevent':
            event_type = 'verifymsg'

        for registered_event in self.registered_events:
            if registered_event['event_type'] == event_type:
                if event_sub_type:
                    if event_sub_type == registered_event['event_sub_type']:
                        event_to_remove = registered_event
                        break
                else:
                    event_to_remove = registered_event
                    break

        if event_to_remove:
            self.registered_events.remove(event_to_remove)
        else:
            log.error('Event type %s:%s is not registered to unregister'
                      % (event_type, event_sub_type))
