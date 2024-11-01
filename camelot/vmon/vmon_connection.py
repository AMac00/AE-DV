from threading import RLock
import socket
import camelot
import sys
import errno
from camelot.utils.server_utils import VmonServerResponse
from camelot import camlogger
import json

log = camlogger.getLogger(__name__)


class Connection(object):
    SOCKET_TIMEOUT = 5

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.command_lock = RLock()
        self._connection = None

    def init_connection(self):
        if self._connection:
            return
        try:
            self._connection = socket.create_connection(
                (self.server_ip, self.server_port),
                timeout=Connection.SOCKET_TIMEOUT)
            log.debug(
                "Connection to VMON server ({}, {}) opened: {}".format(
                    self.server_ip, self.server_port, self._connection
                )
            )
        except socket.error:
            err_msg = (
                "Unable to create connection to VMON server at ({}, {})"
                "".format(self.server_ip, self.server_port)
            )
            raise camelot.CamelotError(err_msg)

    def close_connection(self):
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            log.debug(
                "Connection to VMON server ({}, {}) closed".format(
                    self.server_ip, self.server_port
                )
            )
            self._connection = None

    def _send_and_receive(self, command):
        self.init_connection()
        try:
            log.debug("Sending command: {}".format(command))
            if sys.version_info < (3, 5):
                self._connection.sendall(command)
            else:
                self._connection.sendall(command.encode())
        except Exception as e:
            log.exception(
                "Unable to send command '{}' to VMON server".format(command)
            )
            self.close_connection()
            raise

        buf = []
        while True:
            try:
                if sys.version_info < (3, 5):
                    chunk = self._connection.recv(1024)
                else:
                    chunk = self._connection.recv(1024).decode()
                log.debug("received some data: '{}'".format(chunk))
            except Exception as e:
                log.exception("Unable to receive response from VMON server")
                self.close_connection()
                raise
            if chunk:
                buf.append(chunk)
            else:
                break
        self.close_connection()
        return ''.join(buf).split('\n')[0]

    def execute_vmon_command(self, request, *args, **kwargs):
        command_req = {}
        command_req['request'] = request
        command_req['vmon_params'] = kwargs.get('vmon_params', {})
        if request == 'new_monitor':
            command_req['vmoninstance'] = args[0]
        encodereq = json.dumps(command_req)
        log.debug('encodereq: {}'.format(encodereq))

        msg = {'rc': False, 'msg': 'no response received from vmonserver'}
        with self.command_lock:
            log.debug("Processing vmon command: %s on %s" % (request, self))

            response = self._send_and_receive(encodereq)
            if response:
                log.debug(
                    "response: {} ({})".format(response, type(response))
                )
                msg = json.loads(response)

        return msg
