import sys
import getopt
from getopt import GetoptError
import socket
import json

import camelot
from camelot.utils import vapi_ei_utils, common_utils
from camelot.endpoint import CamelotEndpoint
from camelot.bcg.bcg_instance import BcgInstance
from camelot import camlogger

import socketserver
if sys.version_info < (3, 5):
    import future
BYTEWINDOW = 2048

log = camlogger.getLogger(__name__)


class BcgRequestHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.
    """

    def handle(self):
        if sys.version_info < (3, 5):
            self.data = self.request.recv(BYTEWINDOW).strip()
        else:
            self.data = self.request.recv(BYTEWINDOW).decode().strip()
        (ser_ip, ser_port) = self.server.server_address
        msg = self.process_bcg_command(self.data, ser_ip, ser_port)
        log.debug('sending to client: {}'.format(msg))
        if sys.version_info < (3, 5):
            self.request.sendall(json.dumps(msg))
        else:
            self.request.sendall(json.dumps(msg).encode())

    def process_bcg_command(self, cmd, ser_ip, ser_port):
        log.debug(
            "processing bcg command '{}' received from {}".format(
                cmd, self.client_address
            )
        )
        if not str(cmd):
            return {'rc': True, 'msg': 'no command received'}

        command = json.loads(
            str(cmd), object_pairs_hook=common_utils.CamelotOrderedDict)
        request_type = command['request']

        bcg_params = command.get('bcg_params', {})

        # Instead of doing endpoint reference check in every method
        # on the instance itself, do it here
        epref = bcg_params.get('epref')
        if epref is not None:
            if len(str(epref).split(':')) != 3:
                return {
                    'rc': False,
                    'msg': 'invalid endpoint reference: %s' % epref
                }
            del bcg_params['epref']

        # Same with bcg reference
        bcgref = bcg_params.get('bcgref')
        if bcgref is not None:
            if len(str(bcgref).split(':')) != 4:
                return {
                    'rc': False,
                    'msg': 'invalid bcg reference: %s' % bcgref
                }
            del bcg_params['bcgref']

        # Common error message if bcg doesn't exist
        bcg_not_exist_errmsg = {
            'rc': False,
            'msg': '{}: bcg {} not found'.format(request_type, bcgref)
        }

        if request_type == 'new_bcg':
            log.debug('new bcg')
            bcginstance_str = command['bcginstance']
            klass = BcgInstance
            try:
                if bcginstance_str:
                    (bcginst_mod_str, bcginst_klass_str) = \
                        bcginstance_str.rsplit('.', 1)
                    bcginst_mod = importlib.import_module(bcginst_mod_str)
                    klass = getattr(bcginst_mod, bcginst_klass_str)

                    if not issubclass(klass, BcgInstance):
                        err_msg = (
                            '{} not a subclass of '
                            'BcgInstance'.format(bcginst_klass_str)
                        )
                        log.exception(err_msg)
                        return {'rc': False, 'msg': err_msg}

                log.debug('creating new bcg')
                BcgServer.BCG_INSTANCE += 1
                bcgref = 'bcg:{}:{}:bcg{}'.format(
                    str(ser_ip), str(ser_port), str(BcgServer.BCG_INSTANCE)
                )
                bcg = klass(ser_ip, ser_port,
                            bcgref=bcgref, bcg_params=bcg_params)
            except Exception as e:
                err_msg = 'failed to create bcg instance; err={}'.format(e)
                log.exception(err_msg)
                return {'rc': False, 'msg': err_msg}

            BcgServer.bcg_instances[bcgref] = bcg
            msg = 'new bcg instance created: {}'.format(bcgref)
            log.debug(msg)
            return {'rc': True, 'msg': bcgref}

        elif request_type == 'delete_bcg':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances.pop(bcgref)
                ret = bcg.stop_bcg()
                ret = bcg.release_bcg()
                msg = 'bcg instance deleted: {}'.format(bcgref)
                log.debug(msg)
                return {'rc': True, 'msg': msg}
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'add_to_bcg':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return bcg.add_to_bcg(epref, bcg_params=bcg_params)
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'remove_from_bcg':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return bcg.remove_from_bcg(epref)
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'start_bcg':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return bcg.start_bcg()
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'stop_bcg':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return bcg.stop_bcg()
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'set_bcg':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return bcg.set_bcg(bcg_params)
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'set_camelot_api':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return bcg.set_camelot_api(epref, bcg_params)
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'get_bcg_name':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return {'rc': True, 'msg': bcg.bcgname}
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'get_bcg_state':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return {'rc': True, 'msg': bcg.state}
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'get_bcg_info':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return bcg.get_bcg_info()
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'get_bcg_members':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return bcg.get_members()
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'get_bcg_stats':
            if bcgref in BcgServer.bcg_instances:
                bcg = BcgServer.bcg_instances[bcgref]
                return bcg.get_bcg_stats()
            else:
                log.error(bcg_not_exist_errmsg)
                return bcg_not_exist_errmsg

        elif request_type == 'get_bcgs':
            msg = {}
            msg['bcgref'] = list(BcgServer.bcg_instances.keys())
            return {'rc': True, 'msg': msg}

        err_msg = 'unknown request_type: {}'.format(request_type)
        return {'rc': False, 'msg': err_msg}


class BcgServer(socketserver.TCPServer, object):
    # Allow reuse of port if immediately restarting
    allow_reuse_address = True
    BCG_INSTANCE = 0
    bcg_instances = {}

    def stop_bcgs(self):
        for k in list(BcgServer.bcg_instances.keys()):
            bcg_instance = BcgServer.bcg_instances[k]
            if bcg_instance:
                bcg_instance.stop_bcg()

    def server_close(self):
        self.stop_bcgs()
        super(BcgServer, self).server_close()


def start_server(ip=None, port=None, *args, **kwargs):
    ''' start_server
    starts the bcg server in the given ip and port.
    :Parameter port : port to start the bcg server
    :parameter ip   : IP of the bcg server
    example: camelot.bcg.bcgserver.start_server('10.12.10.133', 9001)
    '''
    if ip is None:
        ip = '0.0.0.0'
    if port is None:
        port = 9001

    request_handler_class = kwargs.get('server_class', BcgRequestHandler)

    try:
        IP = socket.gethostbyname(str(ip))
        bcg_server = BcgServer((IP, port), request_handler_class)
        ver_msg = 'camelot vapiei version is {}'.format(
            vapi_ei_utils.VAPIEIUtils.CLIENT_VERSION)

        if __name__ == '__main__':
            print('bcg server listening on {}'.format(port))
            print(ver_msg)
        else:
            log.info("bcg server started")
            log.info(ver_msg)
        bcg_server.serve_forever()

    except socket.error as e:
        raise camelot.CamelotError(e)

    except KeyboardInterrupt:
        log.debug('bcgserver is stopped by the user')
        msg = 'Stopping the bcgserver...'
        if __name__ == '__main__':
            print(msg)
        else:
            log.debug(msg)
        bcg_server.server_close()
        bcg_server.shutdown()

    except Exception as e:
        raise camelot.CamelotError(e)


def main(argv):
    opts, arg = getopt.getopt(
        argv, "h:p:l:", ['port=', 'help', 'host=', 'loglevel=']
    )

    ip = None
    port = None
    for opt, arg in opts:
        if opt == '--help':
            print('bcgserver.py --host <ip> --port <port> --loglevel <LEVEL>')
            sys.exit()
        if opt in ('-p', '--port'):
            port = int(arg)
        if opt in ('-h', '--host'):
            ip = str(arg)
        if opt in ('-l', '--loglevel'):
            camlogger.setLevel(arg)

    start_server(ip, port)


if __name__ == '__main__':
    main(sys.argv[1:])
    sys.exit()
