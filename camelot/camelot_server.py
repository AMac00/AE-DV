import camelot
from camelot.encoder import encoder
from camelot import camlogger
from camelot.endpoint import CamelotEndpoint
from camelot.utils.rawendpoint_helper import (OutActionObject, InActionObject)
from threading import Thread
from camelot.utils.vapi_ei_utils import VAPIEIUtils
from camelot.utils.camelot_version_validator import CamelotCrypto

log = camlogger.getLogger(__name__)


class CamelotServer(object):

    def __init__(self, ip, port, server_key,
                 version=VAPIEIUtils.CLIENT_VERSION):
        self._ip = ip
        self._port = port
        self.__server_key = server_key
        self.__version = version
        self.ver_validator = CamelotCrypto()
        self.ver_validator.validate_version()
        self._server_conn = camelot._get_camelot_connection(self._ip,
                                                            self._port,
                                                            self.__version)
        self._callback = None
        self.__endpoints = {}
        self.__reconnect_callback = None
        self._tng_cleanup_required = False

    def clean_up_eps(self):
        log.info("clean_up_eps called for ip:{} , port:{}".format(
            self._ip, self._port))
        if self._tng_cleanup_required:
            log.info("cleaning up TNG pi end points.....")
            for ep_key, ep in self.__endpoints.items():
                ep.outofservice()
                ep.uninit_ep()
                ep._release_ep()

    def _get_all_endpoints(self):
        return self.__endpoints

    def _get_server_conn(self):
        '''
        returns the connection if not stopped. if stopped it recreates the new
        connection to the camelot server running on self._ip:self._port.
        if reconnect is successful then it calls the _reconnect_callback
        registered.
        '''

        if (self._server_conn._stopped):
            self._server_conn = camelot._get_camelot_connection(self._ip,
                                                                self._port,
                                                                self.__version)

            if self.__reconnect_callback is not None:
                log.info('connection to camelot server is re-established')
                self._reconnect_thread = Thread(
                    target=self._run_reconnect_callback)
                self._reconnect_thread.start()

            for ep_key, ep in self.__endpoints.items():
                # Marking as invalid as no endpoint exists in the restarted
                # camelot.
                # Endpoints will be valid when user calls create new endpoint
                # after the connection is re-established.
                log.debug('making endpoint validity as false after '
                          ' camelot server is re-established')
                ep._is_valid = False

        return self._server_conn

    def _run_reconnect_callback(self):
        self.__reconnect_callback()

    def register_reconnect_callback(self, callback):
        '''
        Camelot calls this function when the connect to restarted camelot
        server is successful. User can have script relavant initialization
        code in callback which should be executed on connect to restarted
        camleot server is successful
        '''
        self.__reconnect_callback = callback

    def _get_endpoint(self, ep_id):
        if ep_id not in self.__endpoints:
            raise (camelot.CamelotError(
                'endpoint index invalid or out of bounds'))
        return self.__endpoints.get(ep_id, None)

    def get_server_os(self):
        '''Queries currently running Camelot server for its host OS.

        :returns: string indicating the server's host OS.

        >>> serv = camelot.create_camelot_server('10.12.10.180', '5001')
        >>> serv
        <camelot.camelot_server.CamelotServer object at 0x1445550>
        >>> serv.get_server_os()
        Linux
        '''
        log.debug('Entering init function : get_server_os')

        res = self._get_server_conn().execute_camelot_command(
            camelot.GET_SERVER_OS, 'os', request_type='server')
        return res.server_os

    def get_vapiei_version(self):
        '''Fetches the compatible vapiei version
        '''
        res = self._get_server_conn().execute_camelot_command(
            camelot.GET_VAPIEI_VERSION, 'vv', request_type='server')
        return res.vapiei_version

    def get_server_version(self):
        '''Queries currently running Camelot server for its version.


        :returns: string indicating the server's Camelot version.

        >>> serv = camelot.create_camelot_server('10.12.10.180', '5001')
        >>> serv
        <camelot.camelot_server.CamelotServer object at 0x1445550>
        >>> serv.get_server_version('10.1.2.56', 9988)
        9.5.0.0.15.8
        '''

        res = (self._get_server_conn().execute_camelot_command
               (camelot.GET_SERVER_VERSION, 'vr', request_type='server'))
        return res.server_version

    def server_exit(self):
        '''Exit/Kill the Camelot server remotely.

        Note:: Careful while using with TNGpi, as all connection to the server
         will be closed.
        '''

        res = (self._get_server_conn().execute_camelot_command
               (camelot.SERVER_EXIT, 'ex;', request_type='server'))
        if res:
            log.info('Camelot server exited successfully!!')
        return res

    def get_compat_versions(self):
        '''Queries Currently running Camelot server for the
        compatiblity versions of various app servers.

        :returns: dictionary of the app and version pairs

        >>> serv = camelot.create_camelot_server('10.12.10.180', '5001')
        >>> serv
        <camelot.camelot_server.CamelotServer object at 0x1445550>
        >>> serv.get_compat_versions()
        {'CTMS': '1.1.0', 'CME': '9.1', 'CUCM': '9.0.0',
         'VAPIEI': '9.5.0.0.15.8', 'CUP': '8.5'}
        '''

        res = (self._get_server_conn().execute_camelot_command(
            camelot.GET_COMPAT_VERSIONS, 'cv', request_type='server'))
        return res.compat_version

    def create_new_endpoint(self, ep_type, *args, **kwargs):
        '''Creates a new endpoint for the Camelot server.

        :parameter ep_type: endpoint type.  Possible values:\n
            * sk - SCCP (Skinny) audio-only endpoint\n
            * skm - SCCP (Skinny) multimedia (audio, video, and data) endpoint
            * sks - SCCP (Skinny) IP-STE endpoint\n
            * sipx - SIP TNP endpoint for use with CCM\n
            * sip - SIP user agent (audio-only)\n
            * sipv - SIP user agent (video and audio)\n
            * cupc - Cisco Unified Personal Communicator client\n
            * cupcd - CUPC in Deskphone mode\n
            * csfd - CSF in deskphone mode\n
            * cumc - Cisco Unified Mobile Client\n
            * h323 - H.323 endpoint\n
            * pri - ISDN PRI T1/E1 trunk\n
            * cas - CAS T1/E1/Analog trunk (includes analog loop
              start i.e. POTS)\n
            * raw - Non protocol-specific endpoint for use with protocol
              transport services, see Transport Query and Control.\n
            * tandbergsip - Tandberg Sip endpoint (MXP 1000, MXP 1700, E20)\n
            * imsclient - SIP IMS Client\n
            * dmc - Dual mode single registration mobile client\n
        :parameter args: endpoint type specific arguments

        :returns: CamelotEndpoint object on successful creation of the endpoint
         else camelot.CamelotError

        >>> serv = camelot.create_camelot_server('10.12.10.180', '5001')
        >>> serv
        <camelot.camelot_server.CamelotServer object at 0x1445550>
        >>> ep1 = serv.create_new_endpoint( 'sipx','SEPBAACBAAC7001')
        >>> ep1
        <camelot.endpoint.CamelotEndpoint object at 0x29ed490>
        '''

        ep_class = kwargs.setdefault('ep_class', CamelotEndpoint)
        ep_params = kwargs.setdefault('ep_params', {})
        if ep_type == 'cas' and 'cas_board_id' in kwargs:
            log.debug('camserv:createep cas ep')
            cas_board = kwargs.get('cas_board_id')
            cas_trunk = kwargs.get('cas_line_id')
            cas_country = kwargs.get('cas_country')
            cas_protocol = kwargs.get('cas_protocol', 'nocc')
            cas_line = kwargs.get('cas_line_num', '')
            log.debug('camserv createp cas parm is %s' % kwargs)
            if all([cas_board, cas_trunk, cas_country]):
                encoded_msg = encoder.encode(
                    camelot.NEW_ENDPOINT, ep_type, str(cas_board),
                    str(cas_trunk), str(cas_protocol),
                    str(cas_country), str(cas_line))
            else:
                raise camelot.CamelotError("Invalid CAS arguments")
        else:
            log.debug('camserv createp through args: %s' % str(args))
            encoded_msg = encoder.encode(camelot.NEW_ENDPOINT, ep_type, *args)

        if not issubclass(ep_class, CamelotEndpoint):
            raise (camelot.CamelotError
                   ('ep_class: %s not a subclass of CamelotEndpoint'))
        ep = self._get_server_conn().execute_camelot_command(
            camelot.NEW_ENDPOINT, encoded_msg, request_type='ep',
            ep_class=ep_class, ep_params=ep_params)
        self.__endpoints[ep.ep_id] = ep
        ep.ep_type = ep_type
        return ep

    def log_mask(self, level=None, moduleid=None, device=None, reset=False,
                 endpoint_level=None):
        '''
        Set or get the current server logging level.

        :parameter moduleid: the functional component to which the setting is
                             being applied. Modules defined:\n
                             * cupc - CUPC endpoint related events
                             * cupcd - CUPC-Deskphone mode events
                             * csfd - Client Services Framework Deskphone mode
                               events
                             * http - HTTP related log events
                             * media - IP media related events
                             * mediatransp - IP media transport events.
                               Warning! enabling info
                               level logging or lower may result in huge amount
                               of log information and may impact server
                               performance.
                             * qbe - QBE related log events
                             * qbetransp - QBE line protocols related log
                               events
                             * sccp - SCCP endpoints related events
                             * sccptransp - SCCP protocol level events
                             * sip - SIP endpoints related events
                             * siptransp - SIP protocol level events
                             * tftp - TFTP protocol events
                             * tvs - Trust Verification Service client events
                             * vapi - VAPI client handler events.
                             * auto - incoming auto methods from camelot-pi.
                               Enabled by default.
                             * method - all incoming methods other than auto
                               and config from camelot-pi. Enabled by default.
                               Disabled if camelot  is started with -load
                               option.
                             * config - all incoming config methods from
                               camelot-pi. Enabled by default.
                               is started with -load option.
                             * '*' - global filter
                               Warning! enabling info level logging or lower
                               may result in huge amount of log information and
                               may impact server performance.
                             * '~' - log messages that do not belong to any of
                               the listed modules

        :parameter level: the log level being applied to a specific module.
                          Levels defined:\n
                          * none - disable logging
                          * error - error level log events
                          * info - high level informational events
                          * debug_1 through debug_5 - debug information \
                            (debug_5 being the most detailed)

        :parameter device: either file or console.

        :parameter reset: reset all log settings.

        :parameter endpoint_level: enable logs only for
                                   endpoint level, if value is True.

        :returns: When trying to apply new settings a status string is
                  returned. On success Log Level Set is returned; otherwise an
                  informative exception raised.

        >>>
        Example1 - To set server level logs.
        >>> serv.log_mask(moduleid="*", level="debug_5", device="file")
        To reset server level logs.
        >>> serv.log_mask(reset=True)

        >>> Example2 - To set endpoint level logs, on server object.
        >>> serv.log_mask(moduleid="*", level="debug_5", device="file",
                endpoint_level=True)
        To reset endpoint level logs, which we enabled on server object.
        >>> serv.log_mask(reset=True, endpoint_level=True)

        >>> Example3 - To set both server & endpoint level logs
        >>> serv.log_mask(moduleid="*",level="debug_5",device="file",
                endpoint_level=True)
        >>> serv.log_mask(moduleid="*",level="debug_5",device="file")
        '''
        kwargs = {
            'moduleid': moduleid or '',
            'level': level or '',
            'device': device or '',
            'reset': reset,
            'eplevel': endpoint_level
        }
        return self._query_camelot(camelot.LOG_MASK, None, **kwargs)

    def log_dir(self):
        '''Returns the server's execution logs directory path on
        Camelot server.

        :returns: The execution log folder's path.

        >>> serv = camelot.create_camelot_server(CamelotServerIp,
                CamelotServerPort)
        >>> serv.log_dir()
        '/tmp/'
        '''
        kwargs = {
        }
        return self._query_camelot(camelot.LOG_DIR, None, **kwargs)

    def log_filesz(self, size=None):
        '''
        Set or get the current server log file size.
        Default file value is 1024KB

        :parameter size: size in kbytes

        :returns: The current set log file size or 0 on error.

        Fetching the current file size

        >>> serv = camelot.create_camelot_server(CamelotServerIp,
         CamelotServerPort)
        >>> serv.log_filesz()
        '1024'

        Changing the current file size

        >>> serv.log_filesz('2048')
        '2048'

        Note: If Camelot server is started with json format enable. \
               The output will be in Json format.

        >>> ep1.log_filesz()
        {'file_size': '1024'}
        '''
        kwargs = {
            'size': size
        }
        return self._query_camelot(camelot.LOG_FILESZ, None, **kwargs)

    def max_log_files(self, numfiles=None):
        '''The command sets a limit on the number of log files in log folder.

        :parameter numfiles: number of files

        :returns: The current log files limit

        Note: If Camelot server is started with json format enable. \
               The output will be in Json format.

        >>> ep1.max_log_files()
        {'max_files': '1024'}
        '''
        kwargs = {
            'numfiles': numfiles
        }
        return self._query_camelot(camelot.LOG_MAX_FILES, None, **kwargs)

    def log_file_prefix(self, prefix=None):
        '''Changes the current log file name prefix.

        The command sets or returns the log file prefix.

        :parameter prefix: filename prefix.

        :returns: The current log file name prefix.

        Fetching the current file prefix

        >>> serv = camelot.create_camelot_server(CamelotServerIp,
                                        CamelotServerPort)
        >>> serv.log_file_prefix()
        ''

        Changing the current file prefix

        >>> serv.log_file_prefix('log')
        'log'

        Note: If Camelot server is started with json format enable. \
               The output will be in Json format.

        >>> ep1.log_file_prefix()
        {'file_prefix': 'camlog'}
        '''
        kwargs = {
            'prefix': prefix
        }
        return self._query_camelot(camelot.LOG_FILE_PREFIX, None, **kwargs)

    def log_book_mark(self, book_mark_text):
        ''' Insert a user defined bookmark string to the current log
         file

        :returns: An informative status message;
         on success bookmark inserted is returned

        Note: If Camelot server is started with json format enable. \
               The output will be in Json format.

        >>> ep1.log_book_mark()
        {'bookmark': 'bookmark inserted'}
        '''
        kwargs = {
            'bookmark_text': book_mark_text
        }
        return self._query_camelot(camelot.LOG_BOOKMARK, None, **kwargs)

    def load_prompt_cache(self, cachepathargs):
        ''' Load prompt cache used for signature-based prompt detection.

        :parameter cachepathargs: path to directory containing pre-chunked
         prompts or paths to original prompts directory
         _and_ directory to receive chunked prompts.
         N.B. Relative paths are relative to directory containing
         camserv.exe.  Include one or more --vs to increase
         signature-specific debugging which will be written
         to a file named 'widlog.txt' in the same directory
         as camserv.exe.    Include -fmt g711alaw to change
         default wire format from g711ulaw (use with Unity's 16-bit
         prompts in European telephony configurations).

        :returns: a handle for cache on success and raises an error exception
         otherwise.Cache handle is in turn supplied as --cache parameter to
         startpromptdetector for signature-based (-type sig) prompt detection
         on an audio stream.
        '''
        if cachepathargs:
            out_msg = '%s %s@' % ('loadpromptcache', str(cachepathargs))
        else:
            out_msg = 'loadpromptcache@'
        return self._send_msg_to_server('f', out_msg)

    def _send_msg_to_server(self, msg_type, outmsg=None):
        if not outmsg:
            return
        if not msg_type:
            log.error('No message type passed to send to server, Returning..')
            return
        hex_len = self._get_message_length_hex(outmsg)
        send_msg = ('%s:00000000:%s:%s' % (msg_type, hex_len, outmsg))
        try:
            result = self._camelot_query(send_msg)
            return result
        except Exception:
            log.exception('sending failed:')
            log.error('Coulndnt send the message to Camelot server')
            return

    def _is_valid_decimal(self, dec_str):
        try:
            float(dec_str)
            return True
        except ValueError:
            return False

    def _get_message_length_hex(self, message):
        if not message:
            log.warning('No message passed to get Hex length')
            return
        msg_len = len(message)
        hex_val_in_str = hex(msg_len)
        len_hex = len(hex_val_in_str)
        if len_hex == 3:
            hex_val_in_str = hex_val_in_str.replace('0x', '000')
        if len_hex == 4:
            hex_val_in_str = hex_val_in_str.replace('0x', '00')
        elif len_hex == 5:
            hex_val_in_str = hex_val_in_str.replace('0x', '0')
        len_hex = len(hex_val_in_str)
        return hex_val_in_str[(len_hex - 4):len_hex]

    def _send_message(self, sendMsg, functionStr):
        hex_len = self._get_message_length_hex(sendMsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, sendMsg)
        return self._camelot_query(rawmessage)

    def _send_query(self, sendMsg, functionStr):
        hex_len = self._get_message_length_hex(sendMsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, sendMsg)
        return self._camelot_query(rawmessage)

    def _camelot_query(self, encoded_msg):
        with self._get_server_conn().command_lock:
            ret = self._get_server_conn()._send_and_receive(encoded_msg)
            if ret.message:
                return ret.message

    def _query_camelot(self, request, *args, **kwargs):
        encoded_msg = encoder.encode(
            request, *args, **kwargs)
        return self._get_server_conn().execute_camelot_command(
            request, encoded_msg, request_type='ep')

    def _create_tone_seq(self, addr, port, tone_list, codec='g711ulaw',
                         leader='~', duration='~', trailer='~'):
        log.debug('Entering method create_tone_seq()')
        if ' ' in codec:
            log.error('invalid codec name')
            return
        if leader != '~' and not self._is_valid_decimal(leader):
            log.error('Invalid leader value')
            return
        if duration != '~' and not self._is_valid_decimal(duration):
            log.error('Invalid duration value')
            return
        if trailer != '~' and not self._is_valid_decimal(trailer):
            log.error('Invalid trailer value')
            return
        if len(tone_list) < 1:
            log.error('No tone sequence provided in the tone_list')
            return
        tone_seq_str = ''
        for tone_seq in tone_list:
            if type(tone_seq) != dict:
                log.error('Tone sequence is not of type dict, returning..')
                return
            tone_dict = {'freq': None,
                         'offset': '~',
                         'duration': '~',
                         'volume': '~',
                         'rise': '~',
                         'fall': '~',
                         'phase': '~'}
            if tone_seq.get('freq'):
                if not self._is_valid_decimal(tone_seq.get('freq')):
                    log.error('Not a valid freq value, returning')
                    return
                tone_dict['freq'] = tone_seq['freq']
            else:
                log.error('freq is a mandatory parameter, returning')
                return
            if tone_seq.get('offset'):
                if not self._is_valid_decimal(tone_seq.get('offset')):
                    log.error('Not a valid offset value, returning')
                    return
                tone_dict['offset'] = tone_seq['offset']
            if tone_seq.get('duration'):
                if not self._is_valid_decimal(tone_seq.get('duration')):
                    log.error('Not a valid duration value, returning')
                    return
                tone_dict['duration'] = tone_seq['duration']
            if tone_seq.get('volume'):
                if not self._is_valid_decimal(tone_seq.get('volume')):
                    log.error('Not a valid volume value, returning')
                    return
                tone_dict['volume'] = tone_seq['volume']
            if tone_seq.get('rise'):
                if not self._is_valid_decimal(tone_seq.get('rise')):
                    log.error('Not a valid rise value, returning')
                    return
                tone_dict['rise'] = tone_seq['rise']
            if tone_seq.get('fall'):
                if not self._is_valid_decimal(tone_seq.get('fall')):
                    log.error('Not a valid fall value, returning')
                    return
                tone_dict['fall'] = tone_seq['fall']
            if tone_seq.get('phase'):
                if not self._is_valid_decimal(tone_seq.get('phase')):
                    log.error('Not a valid phase value, returning')
                    return
                tone_dict['phase'] = tone_seq['phase']

            tone_str = ' {} {} {} {} {} {} {}'.format(
                tone_dict['freq'], tone_dict['offset'], tone_dict['volume'],
                tone_dict['rise'], tone_dict['duration'], tone_dict['fall'],
                tone_dict['phase'])
            tone_seq_str += tone_str

        kwargs = {'codec': codec,
                  'leader': leader,
                  'duration': duration,
                  'trailer': trailer,
                  'length': str(len(tone_list)),
                  'tone_seq_str': tone_seq_str
                  }

        return self._query_camelot(
            camelot.CREATE_TONE_SEQUENCE, None, **kwargs)

    def register_event_callback(self, callback):
        '''Register a event callback that can be notified when a event
        occurs on a currently running server. This calback will be
        called when an event is received from camelot server for an
        endpoint on which callback wasn't registered,
        otherwise the python framework calls the callback on
        an endpoint for which this event was sent.

        event will be a dictionary with following falues:
            :camelot_ip: Camelot server ip
            :camelot_port: Camelot server port
            :endpoint_id: Camelot endpoint id
            :event_type: type of the event
            :event_sub_type: sub type of the event
            :message: following message from the even

        :parameter callback: callback method which can be invoked by SDK

        >>> def event_callback(event):
        ...     print 'Received Event: %s' % event
        ...
        >>> serv = camelot.create_camelot_server('10.12.10.180, '5001')
        >>> serv
        >>> <camelot.camelot_server.CamelotServer object at 0x1445550>
        >>> serv.register_event_callback(event_callback)
        >>> ep1 = serv.create_new_endpoint( 'sipx',
        ...                                 'SEPBAACBAAC7001')
        >>> ep1
        <camelot.endpoint.CamelotEndpoint object at 0x29ed490>
        >>> ep1.start_info_events()
        True
        >>> ep1.start_station_events()
        True
        >>> ep1.init()
        'outofservice'
        >>> ep1.inservice()
        'inservicepending'
        >>> Received Event: {'event_sub_type': 'ccmreg',
                'event_type': 'station',
                'camelot_ip': '10.106.248.199', 'endpoint_id': '00000003',
                'camelot_port': 5004, 'message':
                '17:27:33:314 ccmreg {registration ok} 10.20.1.21'}
            Received Event: {'event_sub_type': None, 'event_type': 'state',
                'camelot_ip': '10.106.248.199', 'endpoint_id': '00000003',
                'camelot_port': 5004, 'message': ''}
        '''
        self._callback = callback

    def load_sss(self, script, scripttype='tcl'):
        '''load script on to the current camelot server.

        :parameter script: Path of the script file
        :parameter scripttype: SSS script is written in tcl or python.\n
                               Possible values are\n
                                * tcl (default)
                                * python
        '''
        encoded_msg = encoder.encode(camelot.LOAD_SSS, script, scripttype)

        res = self._get_server_conn().execute_camelot_command(
            camelot.LOAD_SSS, encoded_msg)
        return res

    def unload_sss(self, shandle):
        '''unload sss script from the camelot server

        :parameter shandle: script handled returned by loadsss
        '''

        encoded_msg = encoder.encode(camelot.UNLOAD_SSS, shandle)

        res = self._get_server_conn().execute_camelot_command(
            camelot.UNLOAD_SSS, encoded_msg)
        return res

    def get_sss_list(self, shandle):
        '''get sss script info

        :parameter shandle: script handled returned by loadsss
        '''

        encoded_msg = encoder.encode(camelot.GET_SSS_LIST, shandle)

        res = self._get_server_conn().execute_camelot_command(
            camelot.GET_SSS_LIST, encoded_msg)
        return res

    def get_sss_script(self, shandle):
        '''get sss script

        :parameter shandle: script handled returned by loadsss
        '''
        encoded_msg = encoder.encode(camelot.GET_SSS_SCRIPT, shandle)

        res = self._get_server_conn().execute_camelot_command(
            camelot.GET_SSS_SCRIPT, encoded_msg)
        return res

    def get_sss_load_state(self, shandle):
        '''get sss load state

        :parameter shandle: script handled returned by loadsss
        '''

        encoded_msg = encoder.encode(camelot.GET_SSS_LOAD_STATE, shandle)

        res = self._get_server_conn().execute_camelot_command(
            camelot.GET_SSS_LOAD_STATE, encoded_msg)
        return res

    def get_endpoint(self, ep_id_or_name, get_from_server=False):
        '''Find an endpoint
        Returns information about a previously created endpoint.
        The specified id can be a endpoint name or endpoint id.
        If endpoint exists in camelot-pi current process , only
        then it will be returned else an exception will be thrown.
        If the requirement is to get the endpoint on a different process
        either set get_from_server to True or refer attach_endpoint.

        :parameter ep_id_or_name: epid of the endpoint. Possible values \n
            * epid - Hex value as a string '00000001' ... '0000000n' is in
              the sequence in which the endpoint were created.
            * epname - arbitrary string set by ep.set_client_data(data)
        :parameter get_from_server: to attach an endpoint in a different
                                    process set it to True.

        :returns object: endpoint object if exists is returned else
                        an exception is thrown.

        >>> serv = camelot.create_camelot_server('10.12.10.180, '5001')
        >>> serv
        >>> <camelot.camelot_server.CamelotServer object at 0x1445550>
        >>> ep1 = serv.create_new_endpoint( 'sipx',
        ...                                 'SEPBAACBAAC7001')
        >>> ep1
        <camelot.endpoint.CamelotEndpoint object at 0x29ed490>
        >>> ep1.set_client_data('phone1')
        'phone1'
        >>> ret = serv.get_end_point('phone1')
        >>> print ret
        <camelot.endpoint.CamelotEndpoint object at 0x29ed490>
        '''
        if get_from_server:
            return self.attach_endpoint(ep_id_or_name)
        try:
            int(ep_id_or_name, 16)
        except ValueError as e:
            # epname or client data provided, so need to get the ep_id
            # from server first.  The decode will then return the endpoint
            # by calling _get_endpoint
            log.debug('get_endpoint: getting from camelot server:%s' % e)
            encoded_msg = encoder.encode(
                camelot.GET_ENDPOINT, str(ep_id_or_name))
            return self._get_server_conn().execute_camelot_command(
                camelot.GET_ENDPOINT, encoded_msg, request_type='ep')
        log.debug('get_endpoint: getting locally')
        return self._get_endpoint(ep_id_or_name)

    def _default_event_callback(self, event):
        found_ep_callback = False
        log.debug("inside default callback: event: %s \n" % event)
        log.debug("event epid: %s eventtype: %s \n" %
                  (event.endpoint_id, event.event_type))

        if self.__endpoints and event.endpoint_id in self.__endpoints:
            ep = self.__endpoints[event.endpoint_id]
            if (ep._callback is not None):
                ep._callback(event)
                found_ep_callback = True
            else:
                key = "{}:{}".format(event.event_type, event.event_sub_type)
                if (key in ep._callbackdict):
                    processThread = Thread(
                        target=ep._callbackdict[key],
                        args=(event, ep._callbackarg))
                    processThread.start()
                    found_ep_callback = True

            if found_ep_callback is True:
                log.debug(" ep call back is registered")
            else:
                log.debug("ep call back is not registered ")

        if (found_ep_callback is not True):
            log.debug(" ep event call back is not registered")
            if (self._callback is not None):
                log.debug("calling server level callback")
                self._callback(event)
            else:
                log.debug(" no callback registered on server side.. \
                so ignoring the event")

    def attach_endpoint(self, ep_id_or_name, *args, **kwargs):
        '''
        Returns information about a previously created endpoint.
        The specified id can be a endpoint name or endpoint id.
        This queries camelot server and gets the endpoint.

        :parameter ep_id_or_name: id of the endpoint. Possible values \n
            * epid - Hex value as a string '00000001' ... '0000000n' is in
              the sequence in which the endpoint were created.
            * epname - arbitrary string set by ep.set_client_data(data)

        :returns object: endpoint object on camelot server is returned else
                        an exception is thrown.

        >>> serv = camelot.create_camelot_server('10.12.10.180, '5001')
        >>> serv
        >>> <camelot.camelot_server.CamelotServer object at 0x1445550>
        >>> ret = serv.attach_endpoint('phone1')
        >>> print ret
        <camelot.endpoint.CamelotEndpoint object at 0x29ed490>
        '''
        # ep_id_or_name could be the actual ep index that camelot
        # keeps, or the client data
        log.debug('in attach_endpoint method')
        try:
            # Convert to int if possible
            ep_id_or_name = int(ep_id_or_name, 16)
        except ValueError as e:
            # epname or client data provided, so send as is
            log.debug(
                'using endpoint name {} to attach'.format(ep_id_or_name)
            )
        else:
            log.debug('using endpoint id {} to attach'.format(ep_id_or_name))

        ep_class = kwargs.setdefault('ep_class', CamelotEndpoint)
        ep_params = kwargs.setdefault('ep_params', {})
        if not issubclass(ep_class, CamelotEndpoint):
            raise (camelot.CamelotError
                   ('ep_class: %s not a subclass of CamelotEndpoint'))
        encoded_msg = encoder.encode(camelot.ATTACH_ENDPOINT, ep_id_or_name)
        ep = self._get_server_conn().execute_camelot_command(
            camelot.ATTACH_ENDPOINT, encoded_msg, request_type='ep',
            ep_class=ep_class, ep_params=ep_params)
        self.__endpoints[ep.ep_id] = ep
        return ep

    def get_message_length_hex(self, message):
        if message is None:
            log.warning('No message passed to get Hex length')
            return
        msg_len = len(message)
        hex_val_in_str = hex(msg_len)
        len_hex = len(hex_val_in_str)
        if len_hex == 3:
            hex_val_in_str = hex_val_in_str.replace('0x', '000')
        if len_hex == 4:
            hex_val_in_str = hex_val_in_str.replace('0x', '00')
        elif len_hex == 5:
            hex_val_in_str = hex_val_in_str.replace('0x', '0')
        len_hex = len(hex_val_in_str)
        return hex_val_in_str[(len_hex - 4):len_hex]

    def create_out_action_set(self):
        '''
        Create a blank set of actions as a place holder for all the messages.
        Then using different command one can keep on adding different action
        for addition/deletion or modification of original message.

        NOTE: This API can be used for Simulated Endpoints as well.
              i.e., the endpoint need not to be RawEndpoint.

        >>> out_action_valid_ep1 = self.srv.create_out_action_set()
        >>> out_action_valid_ep1.add_sdp_attrib(typestr='z', value='0 0')
        >>> out_action_valid_ep1.add_sdp_attrib('audio', 'a', 'ptime',
                                                 '100')
        >>> out_action_valid_ep1.add_sdp_attrib('audio', 'a', value='100')
        >>> out_action_valid_ep1.add_sdp_attrib('audio', 'a', value='200')
        >>> ep1.apply_out_action_set(out_action_valid_ep1,
                                      method='INVITE')
        '''
        createmsg = 'createtemplatemessage NONE NONE@'

        hex_len = self.get_message_length_hex(createmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, createmsg)
        try:
            with_new_line = self._camelot_query(rawmessage)
            if with_new_line:
                actionObject = OutActionObject(self, with_new_line)
                if actionObject:
                    return actionObject
        except Exception as e:
            log.error('Create out Action Object Failed reason:%s' % e)
            return

    def delete_out_action_set(self, actionObj):
        '''
        Deletes the outaction object created.
        :parameter actionObj: actionObj returned by
                                 create_out_action_set().

        :returns: True Upon success, else Exception is thrown.

        >>> out_action_valid_ep1 = self.srv.create_out_action_set()
        >>> out_action_valid_ep1.modify_sip_header('Max-Forwards','105')
        >>> out_action_valid_ep1.modify_sip_header(ALLOW_EVENTS,
                ALLOW_EVENTS_VALID_VALUE_OUT)
        >>> out_action_valid_ep1.modify_sip_header(SUPPORTED,
                SUPPORTED_VALID_VALUE_OUT)
        >>> out_action_valid_ep1.add_sip_header(SUBJECT,
                SUBJECT_VALID_VALUE_OUT)
        >>> self.ep1.apply_out_action_set(out_action_valid_ep1,
                method='INVITE')
        >>> self.ep1.remove_out_action_set(out_action_valid_ep1,
                method='INVITE')
        >>> self.srv.delete_out_action_set(out_action_valid_ep1)
        '''
        delmsg = 'deletemessage {0}@'.format(actionObj.msgid)
        hex_len = self.get_message_length_hex(delmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, delmsg)
        try:
            with_new_line = self._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
        except Exception:
            log.error('Delete Action Set Failed')
            return

    def create_in_action_set(self):
        '''
        Create a blank set of verification as a place holder
        Then using different command one can keep on adding actions
        for verification of original message.

        NOTE: This API can be used for Simulated Endpoints as well.
              i.e., the endpoint need not to be RawEndpoint.

        >>> in_action_ep1_ring = self.srv.create_in_action_set()
        >>> in_action_ep1_ring.add_verify_sip_header('Allow-Events',
                'telephone-event',mode=0)
        >>> in_action_ep1_ring.add_verify_sip_header('Server',
                'Cisco-SIPGateway',mode=0)
        >>> self.ep1.start_verify_event(self.verifyRing,
                in_action_ep1_ring,method='180')
        >>> self.ep1.stop_verify_event(in_action_ep1_ring,method='180')
        '''
        createmsg = 'createtemplatemessage NONE NONE@'

        hex_len = self.get_message_length_hex(createmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, createmsg)
        try:
            with_new_line = self._camelot_query(rawmessage)
            if with_new_line:
                actionObj = InActionObject(self, with_new_line)
                if actionObj:
                    return actionObj
        except Exception as e:
            log.error('Create in Action Object Failed=%s' % e)
            return

    def delete_in_action_set(self, validationObj):
        '''
        Deletes the inaction object created.
        :parameter validationObj: inaction returned by
                                 create_in_action_set().

        :returns: True Upon success, else Exception is thrown.

        >>> in_action_valid_ep2 = self.srv.create_in_action_set()
        >>> in_action_valid_ep2.add_verify_sip_header(ALLOW_EVENTS,
                ALLOW_EVENTS_VALID_VALUE_IN, mode=1)
        >>> in_action_valid_ep2.add_verify_sip_header(SUPPORTED,
                SUPPORTED_VALID_VALUE_IN)
        >>> in_action_valid_ep2.add_verify_sip_header(USER_AGENT,
                USER_AGENT_VALID_VALUE_IN)
        >>> self.ep2.start_verify_event(self.verify_all_valid_headers,
                in_action_valid_ep2, method='INVITE')
        >>> self.ep2.stop_verify_event(in_action_valid_ep2,
                method='INVITE')
        >>> self.srv.delete_in_action_set(in_action_valid_ep2)
        '''

        delmsg = 'deletemessage {0}@'.format(validationObj.msgid)
        hex_len = self.get_message_length_hex(delmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, delmsg)
        try:
            with_new_line = self._camelot_query(rawmessage)
            if with_new_line:
                return with_new_line
        except Exception:
            log.error('Delete Action Set Failed')
            return

    def detach_endpoint(self, ep_id):
        ep = self.__endpoints[ep_id]
        del self.__endpoints[ep_id]
        return ep
