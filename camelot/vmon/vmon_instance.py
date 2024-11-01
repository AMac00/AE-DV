import os
import shutil
import json

import camelot
from camelot.utils import common_utils
from camelot.camelot_server import CamelotServer
from camelot.endpoint import CamelotEndpoint
from camelot import camlogger

log = camlogger.getLogger(__name__)


class VmonEndpoint(CamelotEndpoint):

    def __init__(self, ep_id, *args, **kwargs):
        self.description = kwargs.get('description', None)
        camelot_server_conn = args[0]
        CamelotEndpoint.__init__(self, ep_id, camelot_server_conn)

    def reset_to_default(self, camelot_server_conn):
        '''This resets the endpoint to default when connection
        to camelot is restablised , It can be overridden by the user
        to reset the endpoint to default'''
        self.description = ''
        super(VmonEndpoint, self).reset_to_default(camelot_server_conn)

    def _remove_undscr_tngpi(self, mod_dict):
        log.debug("Replacing spaces with underscores ...")
        new_dict = common_utils.CamelotOrderedDict()
        for key, value in list(mod_dict.items()):
            if ' ' in key.strip():
                key = key.replace(' ', '_')
            new_dict[key] = value
        return new_dict


class VmonInstance(object):

    def __init__(self, ip, port, *args, **kwargs):
        self.vmonref = kwargs['vmonref']
        vmon_params = kwargs.get('vmon_params', {})
        log.debug("new vmon instance created: {}".format(self.vmonref))
        self.numentries = 0
        self.dirpath = vmon_params.get('dirpath', '/tmp/vmon')
        self.filenum = 0
        self.entrythreshold = 500
        self.vmon = ''
        self.logevent = {'calls': False, 'streams': False, 'station': False,
                         'user': False, 'epstate': False}
        # Event list will contain list of sub-events for each of the events
        # A non-empty list will mean only those sub-events are of interest
        # An empty list will mean all the sub-events are of interest
        # Build the dict of lists directly from logevent
        self.eventlist = {d: [] for d in list(self.logevent.keys())}
        self.port = port
        self.ip = ip
        self.members = {}
        self.is_monitor_running = False

    def register_event_callback(self, ep, event_type=None):
        msg = 'register event callback success'
        try:
            ep.register_event_callback(self.handle_event)
        except Exception as e:
            msg = 'could not register endpoint for callback'
            log.error(msg)
            return {'rc': False, 'msg': msg}
        return {'rc': True, 'msg': msg}

    def start_monitoring_events(self, epref):
        ep = self.members[epref]
        ret = self.register_event_callback(ep)
        if not ret['rc']:
            return ret
        msg = 'start monitoring events success'
        if self.logevent['calls']:
            try:
                ep.start_call_events()
            except Exception as e:
                msg = ('failed to start monitoring call event; '
                       'err={}'.format(e))
                log.exception(msg)
                return {'rc': False, 'msg': ret['msg'] + '; ' + msg}
        if self.logevent['streams']:
            try:
                ep.start_stream_events()
            except Exception as e:
                msg = ('failed to start monitoring stream event; '
                       'err={}'.format(e))
                log.exception(msg)
                return {'rc': False, 'msg': ret['msg'] + '; ' + msg}
        if self.logevent['user']:
            try:
                ep.start_user_events()
            except Exception as e:
                msg = ('failed to start monitoring user event; '
                       'err={}'.format(e))
                log.exception(msg)
                return {'rc': False, 'msg': ret['msg'] + '; ' + msg}
        if self.logevent['station']:
            try:
                ep.start_station_events()
            except Exception as e:
                msg = ('failed to start monitoring station event; '
                       'err={}'.format(e))
                log.exception(msg)
                return {'rc': False, 'msg': ret['msg'] + '; ' + msg}
        if self.logevent['epstate']:
            try:
                ep.start_info_events('state')
            except Exception as e:
                msg = ('failed to start monitoring endpt state event; '
                       'err={}'.format(e))
                log.exception(msg)
                return {'rc': False, 'msg': ret['msg'] + '; ' + msg}
        return {'rc': True, 'msg': msg}

    def start_monitor(self):
        self.is_monitor_running = True
        for epref in list(self.members.keys()):
            ret = self.start_monitoring_events(epref)
            if not ret['rc']:
                return ret
        return {'rc': True, 'msg': 'start monitor success'}

    def stop_monitoring_calls(self, epref):
        ep = self.members[epref]
        msg = 'stop monitoring events success'
        if self.logevent['calls']:
            try:
                ep.stop_call_events()
            except Exception as e:
                msg = (
                    'failed to stop monitoring call event; err={}'
                    ''.format(e)
                )
                log.exception(msg)
                return {'rc': False, 'msg': msg}
        if self.logevent['streams']:
            try:
                ep.stop_stream_events()
            except Exception as e:
                msg = (
                    'failed to stop monitoring stream event; err={}'
                    ''.format(e)
                )
                log.exception(msg)
                return {'rc': False, 'msg': msg}
        if self.logevent['user']:
            try:
                ep.stop_user_events()
            except Exception as e:
                msg = (
                    'failed to stop monitoring user event; err={}'
                    ''.format(e)
                )
                log.exception(msg)
                return {'rc': False, 'msg': msg}
        if self.logevent['station']:
            try:
                ep.stop_station_events()
            except Exception as e:
                msg = (
                    'failed to stop monitoring station event; err={}'
                    ''.format(e)
                )
                log.exception(msg)
                return {'rc': False, 'msg': msg}
        if self.logevent['epstate']:
            try:
                ep.stop_info_events('state')
            except Exception as e:
                msg = (
                    'failed to stop monitoring endpt state event; err={}'
                    ''.format(e)
                )
                log.exception(msg)
                return {'rc': False, 'msg': msg}
        return {'rc': True, 'msg': msg}

    def stop_monitor(self):
        if not self.is_monitor_running:
            return {'rc': True, 'msg': 'monitor is not started'}
        self.is_monitor_running = False
        if self.filenum:
            self.filenum += 1
        for epref in list(self.members.keys()):
            ret = self.stop_monitoring_calls(epref)
            if not ret['rc']:
                return ret
        return {'rc': True, 'msg': 'stop monitor success'}

    def set_monitor(self, params):
        # Any change requires monitor to be stopped first
        if self.is_monitor_running:
            return {'rc': False,
                    'msg': 'monitor must be stopped before set'}
        supported_params = ['entries', 'mode', 'events']
        if set(params.keys()).isdisjoint(set(supported_params)):
            return {'rc': False, 'msg': 'invalid set monitor param(s)'}

        if 'events' in list(params.keys()) and params['events']:
            if 'mode' not in list(params.keys()) or not params['mode']:
                return {'rc': False,
                        'msg': 'set events not possible without mode'}
        if 'mode' in list(params.keys()) and params['mode']:
            mode = params['mode']
            if mode not in list(self.logevent.keys()):
                return {'rc': False, 'msg': 'invalid mode: {}'.format(mode)}
            self.logevent[mode] = True
            if 'events' in list(params.keys()) and params['events']:
                self.eventlist[mode] = params['events']
        if 'entries' in list(params.keys()) and params['entries']:
            self.entrythreshold = int(params['entries'])
        return {'rc': True, 'msg': 'set monitor success'}

    def clear_monitor(self, params):
        # Any change requires monitor to be stopped first
        if self.is_monitor_running:
            return {'rc': False,
                    'msg': 'monitor must be stopped before clear'}
        if not params or not any(params.values()):
            # If no params were provided, then clear everything
            self.entrythreshold = 500
            for mode in list(self.logevent.keys()):
                self.logevent[mode] = False
                self.eventlist[mode] = []
            return {'rc': True, 'msg': 'clear monitor success'}

        # If params were specified, then check individually
        supported_params = ['entries', 'mode', 'events']
        if set(params.keys()).isdisjoint(set(supported_params)):
            return {'rc': False, 'msg': 'invalid clear monitor param(s)'}
        if 'events' in list(params.keys()) and params['events']:
            if 'mode' not in list(params.keys()) or not params['mode']:
                return {'rc': False,
                        'msg': 'clear events not possible without mode'}
        if 'mode' in list(params.keys()):
            mode = params['mode']
            if mode not in list(self.logevent.keys()):
                return {'rc': False,
                        'msg': 'invalid mode: {}'.format(mode)}
            if 'events' in list(params.keys()):
                for event in params['events']:
                    self.eventlist[mode].remove(event)
                # After individual events are removed, if nothing left,
                # then disable its monitoring
                if not self.eventlist[mode]:
                    self.logevent[mode] = False
            else:
                self.logevent[mode] = False
                self.eventlist[mode] = []
        if 'entries' in list(params.keys()):
            self.entrythreshold = 500
        return {'rc': True, 'msg': 'clear monitor success'}

    def add_to_monitor(self, epref, *args, **kwargs):
        server_class = kwargs.get('server_class', CamelotServer)
        server_params = kwargs.get('server_params', {})
        params = kwargs.get('vmon_params', {})
        if not issubclass(server_class, CamelotServer):
            raise camelot.CamelotError(
                'server_class not subclass of CamelotServer')

        (camserv_ip, camserv_port, ep_id) = str(epref).split(':')
        server = None
        try:
            server = camelot.get_camelot_server(camserv_ip,
                                                camserv_port)
        except Exception as e:
            pass

        if not server:
            try:
                server = camelot.create_camelot_server(
                    camserv_ip,
                    camserv_port,
                    server_class=server_class,
                    serv_params=server_params)
            except Exception as e:
                err_msg = (
                    'unable to create camelot server in add_to_monitor, '
                    'ip={}, port={}'.format(camserv_ip, camserv_port)
                )
                log.exception(err_msg)
                return {'rc': False, 'msg': err_msg}

        try:
            ep = server.attach_endpoint(ep_id, ep_class=VmonEndpoint)
        except Exception as e:
            err_msg = (
                'could not attach endpoint with ep_id={}, '
                'err={}'.format(ep_id, e)
            )
            log.exception(err_msg)
            return {'rc': False, 'msg': err_msg}

        ep.description = params.get('description', '')

        # Check in members dict
        # Add it in if not present
        # Also allow the add even if monitoring events failed
        # This will at least allow us to keep track of it
        msg = 'endpoint already exists'
        if epref not in list(self.members.keys()):
            self.members[epref] = ep
            msg = 'endpoint added successfully'

        # If monitoring is not enabled, then we are done
        if not self.is_monitor_running:
            return {'rc': True, 'msg': msg}

        # Monitoring is enabled, so start monitoring on the endpoint
        ret = self.start_monitoring_events(epref)
        if not ret['rc']:
            return {'rc': False, 'msg': msg + '; ' + ret['msg']}
        return {'rc': True, 'msg': msg + '; ' + ret['msg']}

    def remove_from_monitor(self, epref):
        log.debug('removing ep {} from monitor server'.format(epref))

        if epref not in list(self.members.keys()):
            log.debug('epref {} not in members'.format(epref))
            return {'rc': True, 'msg': 'endpoint not found'}

        ret = self.stop_monitoring_calls(epref)
        del self.members[epref]
        (rc, msg) = (ret['rc'], ret['msg'] + '; endpoint removed')

        # Also remove from CamelotServer
        (camserv_ip, camserv_port, ep_id) = str(epref).split(':')
        camserv = camelot.get_camelot_server(camserv_ip, camserv_port)
        try:
            camserv.detach_endpoint(ep_id)
        except Exception as e:
            # Just warn that it could not be found
            log.warn('unable to remove ep from server obj; err={}'.format(e))
        return {'rc': True, 'msg': msg}

    def release_monitor(self):
        msg = 'all endpoint(s) released'
        ret_list = []
        for epref in list(self.members.keys()):
            ret_list.append(self.remove_from_monitor(epref))
        fail_count = [ret['rc'] for ret in ret_list].count(False)
        rc = all([ret['rc'] for ret in ret_list])
        if not rc:
            msg = '{} endpoint(s) not released'.format(fail_count)
        return {'rc': rc, 'msg': msg}

    def setup_path(self):
        if not self.dirpath:
            return {'rc': True, 'msg': 'directory not configured'}

        # Since path is specified, incr the filenum to start
        # it off with the next (mostly 1) number
        log.debug('setting up directory path: {}'.format(self.dirpath))
        if os.path.exists(self.dirpath):
            try:
                shutil.rmtree(self.dirpath)
            except Exception as e:
                err_msg = 'could not remove directory, err=: {}'.format(e)
                log.exception(err_msg)
                return {'rc': False, 'msg': err_msg}
        try:
            os.makedirs(self.dirpath)
        except Exception as e:
            err_msg = 'could not create directory, err=: {}'.format(e)
            log.exception(err_msg)
            return {'rc': False, 'msg': err_msg}
        self.filenum += 1
        return {'rc': True, 'msg': 'setup path success'}

    def get_monitor_info(self):
        msg = {}
        modes = [mode
                 for mode
                 in list(self.logevent.keys()) if self.logevent[mode]]
        mode = ', '.join(modes)
        msg['monitor directory'] = self.dirpath
        msg['current file'] = str(self.filenum) + '.txt'
        msg['mode'] = mode
        msg['entries per file'] = str(self.entrythreshold)
        msg['state'] = 'running' if self.is_monitor_running else 'idle'
        return {'rc': True, 'msg': msg}

    def get_members(self):
        return {'rc': True, 'msg': list(self.members.keys())}

    def handle_event(self, event):
        try:
            log.debug('event %s sub type is %s in vmon %s' % (
                event, event.event_sub_type, self.vmon))
            if event.event_type == 'call':
                self.write_call_logs_clbk(event)
            elif event.event_type == 'streams':
                self.write_streams_logs_clbk(event)
            elif event.event_type == 'userevents':
                self.write_userevent_logs_clbk(event)
            elif event.event_type == 'station':
                self.write_stationevent_logs_clbk(event)
            elif event.event_type == 'info':
                self.write_info_logs_clbk(event)
            return
        except Exception:
            log.exception('writing logs failed in handle_event reason:')

    def write_call_logs_clbk(self, event):
        # write logs to the vmon log folder
        server_ip = event.camelot_ip
        port = event.camelot_port
        ep_id = event.endpoint_id
        epref = '%s:%s:%s' % (server_ip, port, ep_id)

        server = camelot.get_camelot_server(server_ip, port)
        ep = server.get_endpoint(ep_id)
        (callref, callstate) = event.message.split(' ')
        callref = '0x' + callref
        try:
            call_data = ep.get_call_info(callref)
        except Exception as e:
            log.info('getcallinfo failed:%s' % e)
            return

        if event.message:
            filename = ''
            if self.numentries >= self.entrythreshold:
                self.filenum += 1
                self.numentries = 0
            filename = str(self.filenum) + '.txt'
            full_filename = os.path.join(self.dirpath, filename)
            f = open(full_filename, 'a')
            if f:
                line = '###############################################\n'
                f.write(line)
                line = 'date:' + call_data['date'] + '\n'
                f.write(line)
                line = 'start:' + call_data['start'] + '\n'
                f.write(line)
                line = 'end:' + call_data['end'] + '\n'
                f.write(line)
                line = 'endpoint' + ':' + str(ep.description) + '\n'
                f.write(line)
                del call_data['date']
                del call_data['start']
                del call_data['end']
                for i in call_data:
                    line = "{}:{}\n".format(i, call_data[i])
                    f.write(line)
                self.numentries += 1
                f.close()
            if callstate == 'end':
                ep.release_call_ref(callref)
        return

    def write_streams_logs_clbk(self, event):
        # write logs to the vmon log folder
        if event.message:
            log.debug('write_streams_logs_clbk=[%s]' % event.message)
        return

    def write_userevent_logs_clbk(self, event):
        # write logs to the vmon log folder
        if event.message:
            log.debug('write_userevent_logs_clbk=[%s]' % event.message)
        return

    def write_stationevent_logs_clbk(self, event):
        # write logs to the vmon log folder
        server_ip = event.camelot_ip
        port = event.camelot_port
        ep_id = event.endpoint_id
        epref = '%s:%s:%s' % (server_ip, port, ep_id)
        server = camelot.get_camelot_server(server_ip, port)
        ep = server.get_endpoint(ep_id)
        if self.eventlist[
            'station'] and event.event_sub_type not in self.eventlist[
                'station']:
            return
        if event.message:
            filename = ''
            if self.numentries >= self.entrythreshold:
                self.filenum += 1
                self.numentries = 0
            filename = str(self.filenum) + '.txt'
            full_filename = os.path.join(self.dirpath, filename)
            f = open(full_filename, 'a')
            if f:
                line = '###############################################\n'
                f.write(line)
                line = 'endpoint' + ':' + ep.description + '\n'
                f.write(line)
                line = 'station event: ' + event.message + '\n'
                f.write(line)
                self.numentries += 1
                f.close()
        return

    def write_info_logs_clbk(self, event):
        # write logs to the vmon log folder
        server_ip = event.camelot_ip
        port = event.camelot_port
        ep_id = event.endpoint_id
        epref = '%s:%s:%s' % (server_ip, port, ep_id)
        server = camelot.get_camelot_server(server_ip, port)
        ep = server.get_endpoint(ep_id)

        state = ep.get_info()['state']
        filename = ''
        if self.numentries >= self.entrythreshold:
            self.filenum += 1
            self.numentries = 0
        filename = str(self.filenum) + '.txt'
        full_filename = os.path.join(self.dirpath, filename)
        f = open(full_filename, 'a')
        if f:
            line = '###############################################\n'
            f.write(line)
            line = 'endpoint' + ':' + ep.description + '\n'
            f.write(line)
            line = 'state change event:' + state + '\n'
            f.write(line)
            self.numentries += 1
            f.close()
        return
