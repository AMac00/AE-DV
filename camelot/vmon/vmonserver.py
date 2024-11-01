import sys
import os
import time
import getopt
from getopt import GetoptError
import socket
import socketserver
import threading
import json
import importlib

import camelot
from camelot.utils import vapi_ei_utils
from camelot.endpoint import CamelotEndpoint
from camelot.vmon.vmon_instance import VmonInstance
from camelot import camlogger

if sys.version_info < (3, 5):
    import future
BYTEWINDOW = 2048

log = camlogger.getLogger(__name__)


class VmonRequestHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.
    """

    def handle(self):
        if sys.version_info < (3, 5):
            self.data = self.request.recv(BYTEWINDOW).strip()
        else:
            self.data = self.request.recv(BYTEWINDOW).decode().strip()
        (ser_ip, ser_port) = self.server.server_address
        msg = self.process_vmon_command(self.data, ser_ip, ser_port)
        log.debug('sending to client: {}'.format(msg))
        if sys.version_info < (3, 5):
            self.request.sendall(json.dumps(msg))
        else:
            self.request.sendall(json.dumps(msg).encode())

    def process_vmon_command(self, cmd, ser_ip, ser_port):
        log.debug(
            'processing vmon command {} received from {}'.format(
                cmd, self.client_address
            )
        )
        if not str(cmd):
            return {'rc': True, 'msg': 'no command received'}

        command = json.loads(str(cmd))
        request_type = command['request']

        vmon_params = command.get('vmon_params', {})

        # Instead of doing endpoint reference check in every method
        # on the instance itself, do it here
        epref = vmon_params.get('epref')
        if epref:
            if len(str(epref).split(':')) != 3:
                return {
                    'rc': False,
                    'msg': 'invalid endpoint reference: %s' % epref
                }
            del vmon_params['epref']

        # Same with vmon reference
        vmonref = vmon_params.get('vmonref')
        if vmonref:
            if len(str(vmonref).split(':')) != 4:
                return {'rc': False,
                        'msg': 'invalid vmon reference: %s' % vmonref}
            del vmon_params['vmonref']

        # Common error message if vmon doesn't exist
        vmon_not_exist_errmsg = {
            'rc': False,
            'msg': '{}: vmon {} not found'.format(request_type, vmonref)
        }

        if request_type == 'new_monitor':
            log.debug('new monitor')
            vmoninstance_str = command['vmoninstance']
            klass = VmonInstance
            try:
                if vmoninstance_str:
                    (vmoninst_mod_str, vmoninst_klass_str) = \
                        vmoninstance_str.rsplit('.', 1)
                    vmoninst_mod = importlib.import_module(vmoninst_mod_str)
                    klass = getattr(vmoninst_mod, vmoninst_klass_str)
                    if not issubclass(klass, VmonInstance):
                        err_msg = (
                            '{} not a subclass of '
                            'VmonInstance'.format(vmoninst_klass_str))
                        log.exception(err_msg)
                        return {'rc': False, 'msg': err_msg}

                log.debug('creating new monitor')
                VmonServer.VMON_INSTANCE += 1
                vmonref = 'vmon:{}:{}:vmon{}'.format(
                    str(ser_ip), str(ser_port), str(VmonServer.VMON_INSTANCE))
                vmon = klass(ser_ip, ser_port,
                             vmonref=vmonref, vmon_params=vmon_params)
            except Exception as e:
                err_msg = 'failed to create vmon instance; err={}'.format(e)
                log.exception(err_msg)
                return {'rc': False, 'msg': err_msg}

            VmonServer.vmon_instances[vmonref] = vmon
            msg = 'new vmon instance created: {}'.format(vmonref)
            log.debug(msg)

            # Setting the path separately as we don't want it to block
            # creating the vmon object
            ret = vmon.setup_path()
            if not ret['rc']:
                return ret

            return {'rc': True, 'msg': vmonref}

        elif request_type == 'delete_monitor':
            if vmonref in VmonServer.vmon_instances:
                vmon = VmonServer.vmon_instances.pop(vmonref)
                ret = vmon.stop_monitor()
                ret = vmon.release_monitor()
                msg = 'vmon instance deleted: {}'.format(vmonref)
                log.debug(msg)
                return {'rc': True, 'msg': msg}
            else:
                log.error(vmon_not_exist_errmsg)
                return vmon_not_exist_errmsg

        elif request_type == 'add_to_monitor':
            if vmonref in VmonServer.vmon_instances:
                vmon = VmonServer.vmon_instances[vmonref]
                return vmon.add_to_monitor(epref, vmon_params=vmon_params)
            else:
                log.error(vmon_not_exist_errmsg)
                return vmon_not_exist_errmsg

        elif request_type == 'remove_from_monitor':
            if vmonref in VmonServer.vmon_instances:
                vmon = VmonServer.vmon_instances[vmonref]
                return vmon.remove_from_monitor(epref)
            else:
                log.error(vmon_not_exist_errmsg)
                return vmon_not_exist_errmsg

        elif request_type == 'start_monitor':
            if vmonref in VmonServer.vmon_instances:
                vmon = VmonServer.vmon_instances[vmonref]
                return vmon.start_monitor()
            else:
                log.error(vmon_not_exist_errmsg)
                return vmon_not_exist_errmsg

        elif request_type == 'stop_monitor':
            if vmonref in VmonServer.vmon_instances:
                vmon = VmonServer.vmon_instances[vmonref]
                return vmon.stop_monitor()
            else:
                log.error(vmon_not_exist_errmsg)
                return vmon_not_exist_errmsg

        elif request_type == 'release_monitor':
            if vmonref in VmonServer.vmon_instances:
                vmon = VmonServer.vmon_instances[vmonref]
                return vmon.release_monitor()
            else:
                log.error(vmon_not_exist_errmsg)
                return vmon_not_exist_errmsg

        elif request_type == 'get_monitor_info':
            if vmonref in VmonServer.vmon_instances:
                vmon = VmonServer.vmon_instances[vmonref]
                return vmon.get_monitor_info()
            else:
                log.error(vmon_not_exist_errmsg)
                return vmon_not_exist_errmsg

        elif request_type == 'get_monitor_members':
            if vmonref in VmonServer.vmon_instances:
                vmon = VmonServer.vmon_instances[vmonref]
                return vmon.get_members()
            else:
                log.error(vmon_not_exist_errmsg)
                return vmon_not_exist_errmsg

        elif request_type == 'set_monitor':
            if vmonref in VmonServer.vmon_instances:
                vmon = VmonServer.vmon_instances[vmonref]
                return vmon.set_monitor(vmon_params)
            else:
                log.error(vmon_not_exist_errmsg)
                return vmon_not_exist_errmsg

        elif request_type == 'clear_monitor':
            if vmonref in VmonServer.vmon_instances:
                vmon = VmonServer.vmon_instances[vmonref]
                return vmon.clear_monitor(vmon_params)
            else:
                log.error(vmon_not_exist_errmsg)
                return vmon_not_exist_errmsg

        elif request_type == 'get_monitors':
            msg = {}
            msg['vmonref'] = list(VmonServer.vmon_instances.keys())
            return {'rc': True, 'msg': msg}

        err_msg = 'unknown request_type: {}'.format(request_type)
        return {'rc': False, 'msg': err_msg}


class VmonServer(socketserver.TCPServer, object):
    # Allow reuse of port if immediately restarting
    allow_reuse_address = True
    VMON_INSTANCE = 0
    vmon_instances = {}

    def stop_monitors(self):
        for k in list(VmonServer.vmon_instances.keys()):
            vmon_instance = VmonServer.vmon_instances[k]
            if vmon_instance:
                vmon_instance.stop_monitor()

    def server_close(self):
        self.stop_monitors()
        super(VmonServer, self).server_close()


def start_server(ip=None, port=None, *args, **kwargs):
    ''' start_server
    starts the vmon server in the given ip and port.
    :Parameter port : port to start the vmon server
    :parameter ip   : IP of the vmon server
    example: camelot.vmon.vmonserver.start_server('10.12.10.133', 9001)
    '''
    if ip is None:
        ip = '0.0.0.0'
    if port is None:
        port = 9001

    request_handler_class = kwargs.get('server_class', VmonRequestHandler)

    try:
        IP = socket.gethostbyname(str(ip))
        vmon_server = VmonServer((IP, port), request_handler_class)
        ver_msg = 'camelot vapiei version is {}'.format(
            vapi_ei_utils.VAPIEIUtils.CLIENT_VERSION)

        if __name__ == '__main__':
            print('vmon server listening on {}'.format(port))
            print(ver_msg)
        else:
            log.info("vmon server started")
            log.info(ver_msg)
        vmon_server.serve_forever()

    except socket.error as e:
        raise camelot.CamelotError(e)

    except KeyboardInterrupt:
        log.debug('vmonserver is stopped by the user')
        msg = 'Stopping the vmonserver...'
        if __name__ == '__main__':
            print(msg)
        else:
            log.debug(msg)
        vmon_server.server_close()
        vmon_server.shutdown()

    except Exception as e:
        raise camelot.CamelotError(e)


def main(argv):
    opts, arg = getopt.getopt(
        argv, 'h:p:l:', ['port=', 'help', 'host=', 'loglevel=']
    )

    ip = None
    port = None
    for opt, arg in opts:
        if opt == '--help':
            print('vmonserver.py --host <ip> --port <port> --loglevel <LEVEL>')
            sys.exit()
        if opt in ('-p', '--port'):
            port = int(arg)
        if opt in ('-h', '--host'):
            ip = str(arg)
        if opt in ('-l', '--loglevel'):
            camlogger.setLevel(arg)

    start_server(ip, port)


if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit()
