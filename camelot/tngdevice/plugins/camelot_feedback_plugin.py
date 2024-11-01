import logging
import copy
from tng.plugins.feedback_plugin import (FeedbackReceiver, FeedbackNamespace,
                                         FeedbackPlugin)
from twisted.internet import threads

log = logging.getLogger('CamelotFeedbackPlugin')


class CamelotFeedbackNamespace(FeedbackNamespace):

    def __init__(self, *args, **kwargs):
        super(CamelotFeedbackNamespace, self).__init__(*args, **kwargs)

    def feedback_receiver_factory(self, device):
        return CamelotFeedbackReceiver(device)

    def register_feedback(self):
        return True


class CamelotFeedbackReceiver(FeedbackReceiver):

    def __init__(self, device):
        super(CamelotFeedbackReceiver, self).__init__(device)
        self.device = device
        self.cached_call_info = []
        self.is_stopped = False

    def start_listening(self, loop_call=False):
        log.info('In Feedback Listenting Method')
        '''if loop_call:
            return threads.deferToThread(self.start_looping_call)
        else:'''
        self.is_stopped = False
        return True

    def _receive_event(self, event):
        log.debug('Received event on: [%r], Event: %s' % (
            self.device, event.__dict__))
        try:
            self.on_event_callback(event)
        except Exception as e:
            log.debug('Exception while processing feedback on [%r]: %s' % (
                self.device, e))

    def stop_listening(self, loop_call=False):
        log.info('In Stop Listenting Method')
        self.is_stopped = True
        return True

    def start_looping_call(self):
        pass

    def read_events(self):
        def handle_error(err):
            log.debug('In read_events: deferred failed with error = %s:%s' %
                      (type(err), err))

        d = threads.deferToThread(self.on_event_callback, 'loopcall')
        d.addErrback(handle_error)
        return d

    def received(self, ip, data):
        pass

    def _get_call_info(self):
        call_info = []
        call_list = self.device.vapi.get_calls()
        for call in call_list:
            if call['CallState'] == 'disconnected':
                continue
            call_data = {}
            call_data['status'] = call['CallState']
            call_data['ref'] = call['Ref']
            call_detailed_info = self.device.vapi.get_call_info(call['Ref'])
            call_data['CallingName'] = call_detailed_info['calling name']
            call_data['CalledName'] = call_detailed_info['called name']
            call_data['CallingDN'] = call_detailed_info['calling address']
            call_data['CalledDN'] = call_detailed_info['called address']
            call_data['type'] = call_detailed_info['type']
            if not call_data['CallingDN'] or not call_data['CalledDN']:
                continue
            call_info.append(call_data)
        return call_info

    def _get_list_difference(self, list1, list2):
        if not list1:
            return None
        if not list2:
            new_list = list1[:]
            return new_list
        list2_call_refs = set([d['ref'] for d in list2])
        ret_list = [d for d in list1 if (d['ref']) not in list2_call_refs]
        new_list = ret_list[:]
        return new_list

    def on_event_callback(self, event_type):
        if self.is_stopped:
            return
        events = list()
        current_call_info = self._get_call_info()
        current_call_info.sort()
        self.cached_call_info.sort()
        temp_call_info = copy.deepcopy(current_call_info)

        log.debug('In on_read_events1: cached_call_info = %s'
                  % self.cached_call_info)
        log.debug('In on_read_events2: current_call_info = %s'
                  % current_call_info)

        for call in current_call_info:
            if call['status'] == 'disconnected':
                current_call_info.remove(call)
                events.append(call)

        # Raise ONHOOK event
        call_ended = self._get_list_difference(self.cached_call_info,
                                               current_call_info)
        if call_ended:
            for cal in call_ended:
                self.cached_call_info.remove(cal)
                cal['status'] = 'ONHOOK'
                events.append(cal)

        new_calls = self._get_list_difference(current_call_info,
                                              self.cached_call_info)
        if new_calls:
            for cal in new_calls:
                '''Raise new call event'''
                events.append(cal)
                current_call_info.remove(cal)

        # Raise call state changed events like RINGIN, RINGOUT etc
        self.cached_call_info.sort()
        current_call_info.sort()
        for call in self.cached_call_info:
            if call['CallingName'] == 'Conference':
                call['CallingDN'] = 'Conference'
            if call['CalledName'] == 'Conference':
                call['CalledDN'] = 'Conference'
            for call2 in current_call_info:
                if call2['CallingName'] == 'Conference':
                    call2['CallingDN'] = 'Conference'
                if call2['CalledName'] == 'Conference':
                    call2['CalledDN'] = 'Conference'
                if call['ref'] == call2['ref']:
                    if call2['status'] == call['status']:
                        if (call2['status'] == 'connected' and
                                (call2['CallingDN'] != call['CallingDN'] or
                                 call2['CalledDN'] != call['CalledDN'])):
                            call2['status'] = 'TRANSFERRED'
                            events.append(call2)
                        else:
                            pass
                    else:
                        if (call2['status'] == 'connected' and
                            (call2['CalledDN'] == 'Conference' or
                             call2['CallingDN'] == 'Conference') and
                            (call2['CallingDN'] != call['CallingDN'] or
                             call2['CalledDN'] != call['CalledDN'])):
                            call2['status'] = 'TRANSFERRED'
                        events.append(call2)
                    current_call_info.remove(call2)

        self.cached_call_info = temp_call_info
        if events:
            self.callback(events)

    def modify_temp_call_info(self, call_info, call_ref, status):
        for call in call_info:
            if call['ref'] == call_ref:
                call['status'] = status
                return


class CamelotFeedbackPlugin(FeedbackPlugin):
    required_attrs = []
    namespace_factory = CamelotFeedbackNamespace
    feedback_receiver_factory = CamelotFeedbackReceiver

    def __init__(self, vapi_plugin, **kwargs):
        super(CamelotFeedbackPlugin, self).__init__(**kwargs)
        self.vapi_plugin = vapi_plugin
        self.dependencies |= {vapi_plugin}
