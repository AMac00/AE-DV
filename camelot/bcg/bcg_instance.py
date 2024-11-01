import time
import threading

import camelot
from camelot.camelot_server import CamelotServer
from camelot.endpoint import CamelotEndpoint
from camelot import camlogger

log = camlogger.getLogger(__name__)


class BcgEndpoint(CamelotEndpoint):
    def __init__(self, ep_id, *args, **kwargs):
        self.description = kwargs.get('description')
        self.autocmd_type = None
        self.ep_type = None

        camelot_server_conn = args[0]
        CamelotEndpoint.__init__(self, ep_id, camelot_server_conn)

    def reset_to_default(self, camelot_server_conn):
        '''This resets the endpoint to default when connection
        to camelot is restablised , It can be overridden by the user
        to reset the endpoint to default'''
        self.description = ''
        self.autocmd_type = None
        super(BcgEndpoint, self).reset_to_default(camelot_server_conn)


class BcgRateCalc(threading.Thread):

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        if(len(args) == 1):
            self.bcg = args[0]
        self.runable = True

    def start_rate_calc_timer(self):
        while self.runable:
            self.handle_calc_rate()
            time.sleep(self.bcg.ratesample / 1000)

    def handle_calc_rate(self):
        log.debug('end time stamp - %s start stamp %s' % (
            self.bcg.endstamp, self.bcg.startstamp))
        temp = self.bcg.endstamp - self.bcg.startstamp
        self.bcg.elapsed = temp - temp % (1000 / self.bcg.cursetrate)
        # self.bcg.elapsed = self.bcg.endstamp - self.bcg.startstamp
        self.bcg.startstamp = self.bcg.endstamp
        if self.bcg.elapsed != 0:
            self.bcg.instantrate = (
                float(self.bcg.rateattempts * 1000) / float(self.bcg.elapsed))
        else:
            self.bcg.instantrate = 0.0

        self.bcg.rateattempts = 0

    def run(self):
        self.start_rate_calc_timer()

    def stop(self):
        self.runable = False


class BcgScheduler(threading.Thread):

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        if(len(args) == 1):
            self.bcg = args[0]
        self.kwargs = kwargs
        self.runable = True
        self.rateTimer = None
        self.rateCalcTimer = None

    def update_rate_calc_timer(self, timestamp):
        if self.bcg.startstamp == 0 and self.bcg.endstamp == 0:
            self.bcg.startstamp = timestamp

        self.bcg.endstamp = timestamp
        self.bcg.rateattempts = self.bcg.rateattempts + 1

    def do_next_call(self):
        if (len(self.bcg.schedulerq)) > 0:
            epref = self.bcg.schedulerq.pop(0)
            ep = self.bcg.members[epref]
            tstamp = int(round(time.time() * 1000))
            try:
                if ep.autocmd_type == 'call':
                    ep.place_call()
                elif ep.autocmd_type == 'script':
                    ep.place_script()
                elif ep.autocmd_type == 'camelot_api':
                    ep.run_bcg_auto_cmd()
                self.bcg.attempts = self.bcg.attempts + 1
                self.update_rate_calc_timer(tstamp)
                if (ep.ep_type == "siptrunk"):
                    self.bcg.schedulerq.append(epref)
            except Exception as e:
                self.bcg.failure = self.bcg.failure + 1
                self.bcg.lastabortedep = epref
                self.bcg.lastabortedreason = e.message

            return tstamp

        else:
            tstamp = int(round(time.time() * 1000))
            return tstamp

    def handle_rate_timer(self, start):
        stamp = self.do_next_call()
        if start == 1:
            self.bcg.nextstamp = stamp
        self.bcg.nextstamp = self.bcg.nextstamp + self.bcg.rateperiod
        # CAM-964, in-sync with TCL, sleep relative time instead of fixed
        pause = self.bcg.nextstamp - int(round(time.time() * 1000))
        # pause = self.bcg.rateperiod
        if (pause < 0):
            self.bcg.nextstamp = int(
                round(time.time() * 1000)) + self.bcg.rateperiod
            pause = 0.000
        time.sleep(float(float(pause) / 1000))

    def start_rate_timer(self):
        self.handle_rate_timer(1)
        while self.runable:
            self.handle_rate_timer(0)

    def run(self):
        if self.bcg.state == 'idle':
            self.bcg.state = 'running'
            self.start_rate_timer()

    def stop(self):
        log.debug('Stopping bcg start calc timer')
        self.runable = False


class BcgInstance(object):
    def __init__(self, ip, port, *args, **kwargs):
        self.bcgref = kwargs['bcgref']
        log.debug("new bcg instance created: {}".format(self.bcgref))
        self.bcgname = ''
        self.ratetimer = 0
        self.actualrate = 0
        self.state = 'idle'
        self.bcg = ''
        self.port = port
        self.ip = ip
        self.members = {}
        self.schedulerq = []  # queue of eprefs
        self.epIndex = 0
        self.bcg_scheduler = None
        self.bcg_ratecalc = None
        self.attempts = 0
        self.failure = 0
        self.monitor_events = ['lostconn', 'bcgready', 'state']
        self.lastabortedep = ''
        self.lastabortedreason = ''
        self.instantrate = 0
        self.cursetrate = 1
        self.rateperiod = 1000
        self.startstamp = 0
        self.endstamp = 0
        self.elapsed = 0
        self.nextstamp = 0
        self.ratesample = 4000
        self.rateattempts = 0
        self.stopbcg = 0
        self.epBcgType = {}

    def register_event_callback(self, ep, event_type=None):
        msg = 'register event callback success'
        try:
            ep.register_event_callback(self.handle_event)
            '''
            ep.register_event_callback(self.handle_event, "info", "bcgready")
            ep.register_event_callback(self.handle_event, "info", "state")
            ep.register_event_callback(self.handle_event, "info", "lostconn")
            '''
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
        for event in self.monitor_events:
            if not ep.start_info_events(event):
                msg = {
                    'rc': False,
                    'msg': 'failed to start monitoring '
                           '{} event'.format(event)
                }
                msg = ret['msg'] + '; ' + msg
                log.error(msg)
                return {'rc': False, 'msg': msg}
        return {'rc': True, 'msg': msg}

    def stop_monitoring_events(self, epref):
        ep = self.members[epref]
        msg = 'stop monitoring events success'
        for event in self.monitor_events:
            if not ep.stop_info_events(event):
                msg = 'failed to stop monitoring {} event'.format(event)
                log.error(msg)
                return {'rc': False, 'msg': msg}
        return {'rc': True, 'msg': msg}

    def set_bcg(self, params):
        if 'name' in list(params.keys()):
            self.bcgname = params['name']
        elif 'bcgrate' in list(params.keys()):
            self.cursetrate = float(params['bcgrate'])
            self.rateperiod = int(1000.0 / self.cursetrate)
        elif 'sampleperiod' in list(params.keys()):
            self.ratesample = int(params['sampleperiod']) * 1000
        else:
            return {'rc': False, 'msg': 'set bcg failed, invalid parameter'}
        return {'rc': True, 'msg': 'set bcg success'}

    def start_bcg(self):
        self.bcg_scheduler = BcgScheduler(self)
        self.bcg_scheduler.start()
        self.bcg_ratecalc = BcgRateCalc(self)
        self.bcg_ratecalc.start()
        return {'rc': True, 'msg': 'bcg start success'}

    def stop_bcg(self):
        self.stopbcg = 1
        self.state = 'idle'
        self.instantrate = 0.0
        self.startstamp = 0.0
        self.rateattempts = 0
        self.endstamp = 0.0
        if self.bcg_scheduler:
            self.bcg_scheduler.stop()
        if self.bcg_ratecalc:
            self.bcg_ratecalc.stop()
        return {'rc': True, 'msg': 'bcg stop success'}

    def set_camelot_api(self, epref, params):
        cmd = params['cmd']
        args = params['args']
        if epref not in list(self.members.keys()):
            return {'rc': False, 'msg': 'set_camelot_api failed'}
        ep = self.members[epref]
        ep.func_generic_cmd = getattr(ep, cmd)
        ep.args_generic_cmd = args
        return {'rc': True, 'msg': 'set_camelot_api passed'}

    def add_to_bcg(self, epref, *args, **kwargs):
        server_class = kwargs.get('server_class', CamelotServer)
        server_params = kwargs.get('server_params', {})
        params = kwargs.get('bcg_params', {})
        if not issubclass(server_class, CamelotServer):
            raise CamelotError('server_class not subclass of CamelotServer')

        (camserv_ip, camserv_port, ep_id) = str(epref).split(':')
        server = None
        try:
            server = camelot.get_camelot_server(camserv_ip,
                                                camserv_port)
        except Exception as e:
            pass

        if server is None:
            try:
                server = camelot.create_camelot_server(
                    camserv_ip,
                    camserv_port,
                    server_class=server_class,
                    serv_params=server_params
                )
            except Exception as e:
                err_msg = (
                    'unable to create camelot server in add_to_bcg, '
                    'ip={}, port={}'.format(camserv_ip, camserv_port)
                )
                log.exception(err_msg)
                return {'rc': False, 'msg': err_msg}

        try:
            ep = server.attach_endpoint(ep_id, ep_class=BcgEndpoint)
        except Exception as e:
            err_msg = (
                'could not attach endpoint with ep_id={}, '
                'err={}'.format(ep_id, e)
            )
            log.exception(err_msg)
            return {'rc': False, 'msg': err_msg}

        ep.autocmd_type = params.get('autocmd_type', 'call')
        ep.ep_type = params.get('ep_type')

        # Check in members dict
        # Add it in if not present
        # Also allow the add even if monitoring events failed
        # This will at least allow us to keep track of it
        msg = 'endpoint already exists'
        if epref not in list(self.members.keys()):
            self.members[epref] = ep
            msg = 'endpoint added successfully'

        # Monitor for events
        ret = self.start_monitoring_events(epref)

        # If monitoring failed, there is no reason to schedule the endpoint
        if not ret['rc']:
            return {'rc': False, 'msg': msg + '; ' + ret['msg']}

        # Check in schedulerq
        if epref not in self.schedulerq:
            if ep.is_endpoint_bcg_ready():
                self.schedulerq.append(epref)
                msg += '; endpoint is ready and scheduled'
            else:
                msg += '; endpoint is not ready'
        else:
            msg += '; endpoint is already scheduled'
        return {'rc': True, 'msg': ret['msg'] + '; ' + msg}

    def remove_from_bcg(self, epref):
        log.debug('removing ep {} from bcg server'.format(epref))

        if epref not in list(self.members.keys()):
            log.debug('epref {} not in members'.format(epref))
            return {'rc': True, 'msg': 'endpoint not found'}

        # Remove from member list first (so it can't be added
        # to the schedulerq in betweeen)
        ret1 = self.stop_monitoring_events(epref)
        del self.members[epref]
        (rc1, msg1) = (ret1['rc'], ret1['msg'] + '; endpoint removed')

        # Remove from schedulerq
        msg2 = 'endpoint not descheduled'
        if epref in self.schedulerq:
            self.schedulerq.remove(epref)
            msg2 = 'endpoint descheduled'

        # Also remove from CamelotServer
        (camserv_ip, camserv_port, ep_id) = str(epref).split(':')
        camserv = camelot.get_camelot_server(camserv_ip, camserv_port)
        try:
            camserv.detach_endpoint(ep_id)
        except Exception as e:
            # Just warn that it could not be found
            log.warn('unable to remove ep from server obj; err={}'.format(e))
        return {'rc': rc1, 'msg': msg1 + '; ' + msg2}

    def release_bcg(self):
        msg = 'all endpoint(s) released'
        ret_list = []
        for epref in list(self.members.keys()):
            ret_list.append(self.remove_from_bcg(epref))
        fail_count = [ret['rc'] for ret in ret_list].count(False)
        rc = all([ret['rc'] for ret in ret_list])
        if not rc:
            msg = '{} endpoint(s) not released'.format(fail_count)
        return {'rc': rc, 'msg': msg}

    def get_bcg_info(self):
        msg = {}
        log.debug('length of bcgqueue is %s' % len(self.schedulerq))
        msg['state'] = self.state
        msg['set rate'] = round(self.cursetrate, 6)
        msg['actual rate'] = round(self.instantrate, 6)
        msg['endpoints queue'] = len(self.schedulerq)
        return {'rc': True, 'msg': msg}

    def get_bcg_stats(self):
        msg = {}
        msg['attempts'] = self.attempts
        msg['aborts'] = self.failure
        msg['aborted endpoint'] = self.lastabortedep
        msg['aborted reason'] = self.lastabortedreason
        return {'rc': True, 'msg': msg}

    def get_members(self):
        return {'rc': True, 'msg': list(self.members.keys())}

    def handle_event(self, event):
        log.debug('event sub type is %s in bcg %s' % (
            event.event_sub_type, self.bcg))
        server_ip = event.camelot_ip
        port = event.camelot_port
        ep_id = event.endpoint_id
        epref = '%s:%s:%s' % (server_ip, port, ep_id)

        server = camelot.get_camelot_server(server_ip, port)
        ep = server.get_endpoint(ep_id)

        if event.event_type == 'info' and event.event_sub_type == 'state':
            log.debug('received state event for {}'.format(epref))
            try:
                ep_state = ep.get_info()['state']
            except Exception as e:
                log.error('unable to get endpoint state for {}'.format(epref))
                return
            if ep_state != 'inservice':
                if epref in self.schedulerq:
                    self.schedulerq.remove(epref)
                    log.debug(
                        'endpoint {} not inservice; '
                        'removed from schedulerq'.format(epref)
                    )
            else:
                if epref not in self.schedulerq:
                    self.schedulerq.append(epref)
                    log.debug(
                        'endpoint {} inservice; '
                        'added to schedulerq'.format(epref)
                    )

        if event.event_type == 'info' and event.event_sub_type == 'bcgready':
            log.debug('received bcgready event for {}'.format(epref))
            if epref not in self.schedulerq:
                self.schedulerq.append(epref)
                log.debug('endpoint {} added to schedulerq'.format(epref))
