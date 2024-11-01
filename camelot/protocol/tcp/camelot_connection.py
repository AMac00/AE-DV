'''
Created on 11-Sep-2013

@author: smaturi
'''
from threading import RLock
import socket
import sys
import time
from camelot.utils.server_utils import CamelotServerResponse
from camelot.decoder import decoder
import camelot
from camelot.protocol.tcp.camelot_event_connection import EventConnection
from camelot import camlogger
from camelot.utils.vapi_ei_utils import VAPIEIUtils


log = camlogger.getLogger(__name__)


class ConnectionError(Exception):
    pass


class CamelotSocket(object):
    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, name):
        if name in ['send', 'recv', 'sendall']:
            return eval('self.%s' % name)
        return eval('self._conn.%s' % name)

    def send(self, message):
        if sys.version_info < (3, 5):
            self._conn.send(message)
        else:
            self._conn.send(message.encode())

    def sendall(self, message):
        if sys.version_info < (3, 5):
            self._conn.sendall(message)
        else:
            self._conn.sendall(message.encode())

    def recv(self, bufsize, *args):
        if sys.version_info < (3, 5):
            return self._conn.recv(bufsize, *args)
        else:
            data = self._conn.recv(bufsize, *args)
            return data.decode()


class Connection(object):
    SOCKET_TIMEOUT = 4
    HAND_SHAKE_CHARS_TO_READ = 4
    HEX_TO_DIGIT_RADIX = 16
    MESSAGE_ACK_CHARS_TO_READ = 16
    MESSAGE_ACK_READ_ONE_CHAR = 1
    NO_OF_TOKENS_IN_MESSAGE_ACK = 3
    RE_TRYS = 3
    NO_OF_SOCKET_FAILURES_TO_RECONNECT = 3

    def __init__(self, servr_ip, server_port, connection_key, version):
        self.server_ip = servr_ip
        self.server_port = server_port
        self.connection_key = connection_key
        self.command_lock = RLock()
        self._stopped = False
        self.version = version
        self.output_format = 'non_json'

    def _check_json_support_version(self):
        i_ver = self.version
        i_ver = i_ver.split('.')
        i_ver = list(map(int, i_ver))
        if i_ver[0] > 11:
            return True
        elif self.version.startswith('11.0'):
            if i_ver[4] > 10:
                return True
            elif i_ver[4] == 10 and i_ver[5] > 10:
                return True
        if i_ver[0] == 11 and i_ver[1] > 0:
            return True
        return False

    def init_connection(self, conn_id):
        self._connection = CamelotSocket(socket.create_connection(
            (self.server_ip, self.server_port)))

        self._hand_shake_with_server()
        if self._check_json_support_version():
            self.output_format = self._set_output_format()
            log.debug("output_format in server has been set to:{}".format(
                self.output_format))
        else:
            log.debug("older version of camelot doesnt support json format")

        self.connection_id = conn_id

        log.debug("Created connection: " + self.connection_id)

    def _camelot_query(self, encoded_msg):
        self._connection.send(encoded_msg)
        char_to_read = 16
        output_format = self._connection.recv(char_to_read)
        if output_format:
            log.debug("Camelot response recevied for [%s]: [%s]" % (
                encoded_msg, output_format))
            camelot_list = output_format.split(':')
            log.debug("Message after spliting: [%s]" % camelot_list)
            if len(camelot_list) >= 3 and camelot_list[2]:
                char_to_read = int(camelot_list[2], 16)
                output_format = self._connection.recv(char_to_read)
                log.debug("Received Event port: %s" % output_format)
            else:
                raise ConnectionError('length received from'
                                      ' camelot is invalid')
        else:
            raise ConnectionError('Unable to fetch the Event '
                                  'Port from the Camelot server')
        return output_format

    def _set_output_format(self):
        ''' get output format from server side.
         Modules defined:
            * json - json format output from server side
         :returns: When trying to apply new settings a status string is
         returned. On success output forrmat is returned; otherwise an
         informative exception raised.
        '''
        try:
            out_msg = '{} setjson @'.format(camelot.SET_OUTPUT_FORMAT)
            hex_len = VAPIEIUtils.get_message_length_hex(out_msg)
            send_msg = ('%s:00000000:%s:%s' % ('l', hex_len, out_msg))
            return self._camelot_query(send_msg)
        except Exception as e:
            log.exception('_set_output_format failed [%s]', e)

    def _hand_shake_with_server(self):
        client_version = self.version
        log.info("Client Version: " + client_version)
        ver_exchange = "vcclientversion:%s:%s" % (
            VAPIEIUtils.message_length_to_decimal(client_version),
            client_version)

        log.debug("Vesion handshake message:" + ver_exchange)
        self._connection.send(ver_exchange)
        # self._connection.flush()

        buffer_to_read = 1
        data = self._connection.recv(buffer_to_read)

        log.debug("Version response received: %s" % data)

        hand_shake_res = data

        if not hand_shake_res or hand_shake_res[0] != 'a':
            data = self._connection.recv(Connection.HAND_SHAKE_CHARS_TO_READ)

            log.debug("Handshake failed, failure reason length: " + data)

            charsToRead = int(data)
            failReason = self._connection.recv(charsToRead)
            error_str = ("Client package: %s not compatible with server, "
                         "failure reason: %s" % (client_version, failReason))

            self._connection.close()
            raise ConnectionError(error_str)

        ver_H_User = '%s%s' % (VAPIEIUtils.message_length_to_decimal("root"),
                               "root")
        log.debug("Exchange User Name:" + ver_H_User)
        self._connection.send(ver_H_User)

        charsToRead = Connection.HAND_SHAKE_CHARS_TO_READ
        event_port_str = self._connection.recv(charsToRead)
        if not event_port_str:
            raise ConnectionError('Unable to fetch the Event '
                                  'Port from the Camelot server')
        log.debug("Received Event port: %s" % event_port_str)
        event_port = int(event_port_str, Connection.HEX_TO_DIGIT_RADIX)

        log.debug("Received Event port: %s" % event_port)
        self._event_socket = CamelotSocket(socket.create_connection(
            (self.server_ip, event_port),
            Connection.SOCKET_TIMEOUT))
        self._event_process = EventConnection(
            self._event_socket, self.server_ip, self.server_port, self)
        self._event_process.start()
        log.debug("Received Event socket connection: %s" % self._event_socket)

    def _send_and_receive_generic(self, command):
        retVal = ''
        res = None
        try:
            tmpSoc = CamelotSocket(socket.create_connection(
                (self.server_ip, self.server_port),
                timeout=Connection.SOCKET_TIMEOUT))
            tmpSoc.sendall(command)
            for i in range(Connection.RE_TRYS):
                try:
                    while True:
                        val = tmpSoc.recv(1)
                        if not val or val == '\n':
                            break
                        retVal = '%s%s' % (retVal, val)
                except Exception as ioe:
                    log.exception('_send_and_receive failed:')
                    log.error("Unable to send/receive message to Camelot "
                              "server %s" % ioe)
                    time.sleep(5)

        except Exception as ioe:
            log.exception('_send_and_receive retry failed:')
            log.error("Unable to send/receive message to Camelot server %s" % (
                ioe))

        if retVal:
            res = CamelotServerResponse()
            res.message = retVal
        return res

    def _read_header(self, command):
        ack_str = ''
        ep_id = None
        ack = None
        len_to_read = 0
        chars_to_read = Connection.MESSAGE_ACK_CHARS_TO_READ
        while True:
            ack_str = '{}{}'.format(ack_str, self._connection.recv(
                chars_to_read))
            if not ack_str:
                return ack, ep_id, len_to_read
            if ack_str[-1] != ':':
                chars_to_read = Connection.MESSAGE_ACK_READ_ONE_CHAR
                continue

            log.debug("ACK received for the command:[{}], ACK:[{}]".format(
                command, ack_str))
            ack_str = ack_str.strip()
            ack_str_list = ack_str.split(VAPIEIUtils.ACK_DELIM)
            if not ack_str_list or len(ack_str_list) < 3:
                log.error("Invalid ACK received for the command:[{}], ACK:[{}]"
                          " , and ACK List:[{}] ".format(command,
                                                         ack_str,
                                                         ack_str_list))
                return ack, ep_id, len_to_read
            ack = ack_str_list[0].upper()
            ep_id = ack_str_list[1]
            len_to_read = ack_str_list[2]
            return ack, ep_id, len_to_read

    def _send_and_receive(self, command):
        ret = None
        try:
            log.debug(
                "Start send and receive for the command: "
                "[{}], on Connection Id:[{}]".format(
                    command, self.connection_id))
            self._connection.send(command)
            ack_str = None
            ep_id = None
            ack = None
            len_to_read = 0
            extra_chars_read = None
            try:
                ack, ep_id, len_to_read = self._read_header(command)
                if not ack:
                    raise camelot.CamelotError('chars_to_read is None')
                else:
                    ret = CamelotServerResponse()
                    ret.ack = ack
                    ret.epAddress = ep_id

                    chars_to_read = int(
                        len_to_read, Connection.HEX_TO_DIGIT_RADIX)
                    ack_msg = ''
                    byte_recv = 0
                    while byte_recv < chars_to_read:
                        log.debug('Received bytes are less than: {} '
                                  'expected bytes: {}'.format(byte_recv,
                                                              chars_to_read))
                        if chars_to_read > 0:
                            temp_msg = self._connection.recv(
                                min(chars_to_read - byte_recv, 2048))

                            ack_msg = '{}{}'.format(ack_msg, temp_msg)
                            byte_recv += len(temp_msg)
                    log.debug("Message received, Message: {}".format(ack_msg))
                    ret.message = ack_msg
            except Exception as ioe:
                log.exception('_send_and_receive failed:')
        except Exception as ioe:
            log.exception('_send_and_receive retry failed:')
            log.error("Unable to send/receive message to Camelotserver2:[{}"
                      "]".format(ioe))

        if not ret:
            ret = CamelotServerResponse()
            ret.ack = 'N'
            ret.message = ('Unable to send/receive message to Camelot server,'
                           ' after retries')

        return ret

    def close_event_channel(self):

        if self._connection:
            try:
                self._connection.close()
                self._stopped = True
            except Exception:
                pass

        if self._event_process:
            self._event_process.stopped = True

        '''if self._event_socket:
            try:
                self._event_socket.close()
            except Exception:
                pass
        '''
        self._event_process.event_thread.join()

    def execute_camelot_command(
            self, request, encoded_command, request_type='ep', timeout=10,
            ep_class=None, ep_params=None):
        response_to_send = None

        if not encoded_command:
            raise camelot.CamelotError('Invalid command for the Camelot:%s' % (
                encoded_command))

        with self.command_lock:
            log.debug("Processing Command: %s on %s" % (
                encoded_command, self))

            response = None
            if request_type != 'ep':
                response = self._send_and_receive_generic(encoded_command)
                log.debug(
                    "Received Response from generic send/recv, response: {}"
                    "".format(response)
                )
            else:
                response = self._send_and_receive(encoded_command)
                log.debug(
                    "Received Response from send/recv, response: {}"
                    "".format(response)
                )

        if request == camelot.SERVER_EXIT and not response:
            return True

        if response:
            response_to_send = self._decode_response(
                request_type, request, response, ep_class=ep_class,
                ep_params=ep_params)

        if not response_to_send:
            log.debug(
                'Failed to decode the response, unable to send '
                'response to caller for'
                '\n\tRequest: {}'
                '\n\tResponse: {}'
                '\n\tResponse Vars: {}'.format(
                    request, response, vars(response))
            )
        return response_to_send

    def _decode_response(self, req_type, request, response, ep_class=None,
                         ep_params=None):

        log.debug("Request for decoding response")
        # Decoder decoder = DecoderFactory.getCamlotDecoder();
        # CamelotMessage retMsg = null;
        kargs = {'ip': self.server_ip,
                 'port': self.server_port,
                 'ep_class': ep_class,
                 'ep_params': ep_params,
                 'output_format': self.output_format}

        ret = decoder.decode(
            req_type, request, response, **kargs)

        log.debug("Decoded message: {}".format(ret))
        return ret
