'''
Created on 16-Sep-2013

@author: smaturi
'''
import camelot
import os
from camelot import camlogger, CamelotError

FORMAT = "%s:%s:%s:%s"  # Format for
log = camlogger.getLogger(__name__)


class CamelotEncodeHelper(object):

    def _get_message_length_hex(self, message):
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

    def get_load_sss_msg(self, *args, **kwargs):
        ''' returns the load sss message
        eg: f:00000000:000E:loadsss texts@
        '''
        # text = ''
        fpath, fname = os.path.split(args[0])
        with open(args[0], 'r') as content:
            text = content.read()
        if args[1] is 'python':
            formated_str_string = '%s %s$%s$%s@' % ('loadsss', text,
                                                    fname, args[1])
        else:
            formated_str_string = '%s %s@' % ('loadsss', text)
        len_msg_in_hex = self._get_message_length_hex(formated_str_string)
        outmsg = FORMAT % (
            'f', '00000000', len_msg_in_hex, formated_str_string)
        return outmsg

    def get_control_sss_msg(self, request, *args, **kwargs):
        ''' returns the unload sss message
        eg: f:0000000:0012:unloadsss 0x123432@
        '''
        formated_str_string = '%s %s@' % (request, args[0])
        len_msg_in_hex = self._get_message_length_hex(formated_str_string)
        outmsg = FORMAT % (
            'f', '00000000', len_msg_in_hex, formated_str_string)
        return outmsg

    def get_invoke_sss_msg(self, request, *args, **kwargs):
        num_args = 0
        sargs = ''
        if len(args) < 2:
            raise camelot.CamelotError('EP ID is not passed')
        if len(args) == 3:
            if args[2]:
                args_list = args[2].split(' ')
                num_args = len(args_list)
                sargs = args[2]
            if request == 'placescript' and args[1] == 'null':
                config_request = request + ' ' + args[1] + '@'
            else:
                config_request = '{} {} {} {}@'.format(
                    request, args[1], num_args, sargs)
        else:
            if request == 'getscriptinfo':
                config_request = request + ' ' + args[1] + '@'

        return self.get_out_msg(config_request, args[0])

    def get_endpoint_msg(self, *args):
        '''returns camelot get endpoint msg
        eg: g:00000000:0007:phone1@
        '''
        if len(args) < 1:
            raise camelot.CamelotError('Invalid index/data')

        formated_str_string = '%s@' % (args[0])
        len_msg_in_hex = self._get_message_length_hex(formated_str_string)
        outmsg = FORMAT % (
            'g', '00000000', len_msg_in_hex, formated_str_string)
        return outmsg

    def get_attach_endpoint_msg(self, *args):
        '''returns camelot attach endpoint msg
        eg: p:00000000:0007:phone1@
        '''
        if len(args) < 1:
            raise camelot.CamelotError('invalid index/data')
        ep_id_or_name = args[0]
        formated_str_string = '%s@' % ep_id_or_name
        len_msg_in_hex = self._get_message_length_hex(formated_str_string)
        outmsg = FORMAT % (
            'p', '00000000', len_msg_in_hex, formated_str_string)
        return outmsg

    def get_call_stat_msg(self, message, *args):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        if len(args) == 2 and args[1]:
            formated_str_string = '%s clear@' % message
        else:
            formated_str_string = '%s@' % message

        return self.get_out_msg(formated_str_string, args[0])

    def get_out_msg(self, message, ep_id, msg_type=None):
        len_msg_in_hex = self._get_message_length_hex(message)
        if ep_id:
            return FORMAT % (
                'm', ep_id, len_msg_in_hex, message)
        elif msg_type:
            out_msg = '{}:00000000:{}:{}'.format(
                msg_type, len_msg_in_hex, message)
            return out_msg

    def get_out_camelot_msg(self, message):
        hex_len = self._get_message_length_hex(message)
        out_msg = '{}{}{}{}'.format('f:00000000:', hex_len, ':', message)
        return out_msg

    def get_escalate_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError('EP ID/call_ref is not passed')
        call_ref = args[1]
        option = kwargs.get('option')

        msg = '{} {} {}@'.format(message, call_ref, option)

        return self.get_out_msg(msg, args[0])

    def get_config_header_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        log.debug('get_config_header_msg : '
                  'args{}\n kwargs{}\n'.format(args, kwargs))
        param = str(kwargs.get('param'))
        value = str(kwargs.get('value'))
        msg = "{}{}{}{}".format(
            'configheader ', param, ' ', value, '@')
        return self.get_out_msg(msg, args[0])

    def get_log_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Serv/EP ID is not passed')
        msg = ''
        if message == camelot.LOG_MASK:
            moduleid = kwargs.get('moduleid')
            level = kwargs.get('level')
            device = kwargs.get('device')
            reset = kwargs.get('reset')
            eplevel = kwargs.get('eplevel')

            if reset:
                msg = 'logmask reset^{}^{}'.format(
                    eplevel, '@')
            elif moduleid or level or device:
                msg = '{} {}^{}^{}^{}^{}'.format(
                    'logmask', moduleid, level, device, eplevel, '@')
            else:
                msg = 'logmask@'

        elif message == camelot.LOG_DIR:
            msg = 'logdir@'

        elif message == camelot.LOG_FILESZ:
            size = kwargs.get('size')
            if size:
                msg = 'logfilesz ' + str(size) + '@'
            else:
                msg = 'logfilesz@'

        elif message == camelot.LOG_MAX_FILES:
            numfiles = kwargs.get('numfiles')
            if numfiles:
                msg = 'maxlogfiles ' + str(numfiles) + '@'
            else:
                msg = 'maxlogfiles@'

        elif message == camelot.LOG_FILE_PREFIX:
            prefix = kwargs.get('prefix')
            if prefix:
                msg = 'logfileprefix ' + str(prefix) + '@'
            else:
                msg = 'logfileprefix@'

        elif message == camelot.LOG_BOOKMARK:
            bookmark_text = kwargs.get('bookmark_text')
            if bookmark_text:
                msg = 'logbookmark ' + str(bookmark_text) + '@'
            else:
                msg = 'logbookmark@'

        if not args[0]:
            len_msg_in_hex = self._get_message_length_hex(msg)
            return '{}:00000000:{}:{}'.format(
                'l', len_msg_in_hex, msg)
        return self.get_out_msg(msg, args[0])

    def get_endpoint_create_msg(self, ep_type, *args):
        ''' returns camelot ep create msg
        eg: c:00000000:0015:sipx SEPBAACBAAC7001@
        '''
        mac_addr = args
        if 'jabberguest' in ep_type:
            mac_addr = 'DUMMY111111111111'
        formated_str_string = '%s %s@' % (ep_type, ' '.join(mac_addr))
        '''
        if not mac and not len(args_list):
            log.error('Valid MAC or arguments are not passed')
            return
        if mac and not len(args_list):
            type_mac_string = '' + protocol + ' ' + mac + '@'
        elif protocol == 'nativeims' and args_list[0]:
            type_mac_string = '' + protocol + ' ' + args_list[0] + '@'
        else:
            type_mac_string = '' + protocol
            for arg in args_list:
                type_mac_string += ' ' + arg
            type_mac_string += '@'
        '''
        len_msg_in_hex = self._get_message_length_hex(formated_str_string)
        outmsg = FORMAT % (
            'c', '00000000', len_msg_in_hex, formated_str_string)
        return outmsg

    def get_control_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')

        if message == camelot.GET_BFCP_INFO:
            msg = '{} {}{}'.format(
                camelot.GET_BFCP_INFO, args[1], '@')
        elif message == camelot.GET_CALL_CRYPTO_INFO:
            mtype = kwargs.get('mtype')
            tag = kwargs.get('tag')
            local = kwargs.get('local')
            if local:
                local = 0
            else:
                local = 1
            msg = '{} {}^{}^{}^{}@'.format(
                'getcallcryptoinfo', args[1], mtype, tag, local)
        elif message == camelot.GET_CALLS:
            key = kwargs.get('key', None)
            value = kwargs.get('value', None)
            if value:
                msg = '{} {} {}@'.format(message, key, value)
            else:
                msg = '%s@' % message
        elif message == camelot.GET_CALL_INFO:
            key = kwargs.get('key')
            value = kwargs.get('value')
            if value:
                msg = '{} {} {}@'.format(message, key, value)
            else:
                msg = '{} {}@'.format(message, args[1])
        elif message == camelot.CTI_GET_RESPONSE_STATUS:
            req_id = kwargs.get('req_id')
            no_clear = kwargs.get('no_clear')
            msg = '{} {} {}@'.format(message, req_id, no_clear)
        elif message == camelot.GET_DEVICE_CONFIG:
            msg = '{} {}@'.format(message, args[1])
        elif message == camelot.GET_CERT_INFO:
            file_name = args[1]
            if file_name:
                msg = '{} {}@'.format(message, file_name)
            else:
                msg = '%s@' % message
        elif message == camelot.HTTP_RESPONSE:
            url_name = args[1]
            if url_name:
                msg = '{} {}@'.format(message, url_name)
            else:
                msg = '%s@' % message
        elif message == camelot.CLIENT_FOREGROUND:
            key = kwargs.get('type')
            value = kwargs.get('value')
            if key and value:
                msg = '{} {} {}@'.format(message, key, value)
            else:
                msg = '%s@' % message
        elif message == camelot.REMOVE_CONF_PARTICIPANT:
            callref = args[1]
            key = kwargs.get('type')
            value = kwargs.get('value')
            if key and value:
                msg = '{} {} {} {}@'.format(message, callref, key, value)
            else:
                msg = '{}@'.format(message)
        else:
            msg = '%s@' % message

        return self.get_out_msg(msg, args[0])

    def get_sendreinvite_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP CallRef is not passed')
        w_last_sdp = kwargs.get('last_sdp')
        timeout = kwargs.get('timeout')
        contents = kwargs.get('contents')
        formated_str_string = '{} {} {} {}^{}@'.format(
            message, args[1], w_last_sdp, timeout, contents)

        len_msg_in_hex = self._get_message_length_hex(formated_str_string)
        outmsg = FORMAT % (
            'm', args[0], len_msg_in_hex, formated_str_string)
        return outmsg

    def get_detector_request(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError('EP ID is not passed')
        msg = ''
        stream_ref = args[1]

        if message == camelot.START_DTMF_DETECTOR:
            msg = '{} {}@'.format(camelot.START_DTMF_DETECTOR, stream_ref)

        elif message == camelot.STOP_DTMF_DETECTOR:
            msg = '{} {}@'.format(camelot.STOP_DTMF_DETECTOR, stream_ref)

        elif message == camelot.START_PROMPT_DETECTOR:
            prompt_type = kwargs.get('prompt_type')
            cache = kwargs.get('cache')
            pattern_list = kwargs.get('pattern_list')
            if cache:
                msg = '{} {} {} {}@'.format(
                    camelot.START_PROMPT_DETECTOR,
                    stream_ref, prompt_type, cache)
            else:
                if len(pattern_list):
                    msg = '{} {} {}'.format(
                        camelot.START_PROMPT_DETECTOR, stream_ref, prompt_type)
                    for pattern in pattern_list:
                        msg += (' ' + pattern)
                    msg += '@'
                else:
                    msg = '{} {} {} {}@'.format(
                        camelot.START_PROMPT_DETECTOR, stream_ref,
                        prompt_type, 'null')

        elif message == camelot.STOP_PROMPT_DETECTOR:
            msg = '{} {}@'.format(
                camelot.STOP_PROMPT_DETECTOR, stream_ref)

        elif message == camelot.START_TONE_DETECTOR:
            tone_id = kwargs.get('tone_id')
            freq = kwargs.get('freq')
            bw = kwargs.get('bw')
            freq2 = kwargs.get('freq2')
            bw2 = kwargs.get('bw2')
            msg = '{} {} {} {} {} {} {}{}'.format(
                camelot.START_TONE_DETECTOR, stream_ref, tone_id, freq,
                bw, freq2, bw2, '@')

        elif message == camelot.STOP_TONE_DETECTOR:
            tone_id = kwargs.get('tone_id')
            msg = '{} {} {}{}'.format(
                camelot.STOP_TONE_DETECTOR, stream_ref, tone_id, '@')

        elif message == camelot.START_CADENCE_DETECTOR:
            tone_id = kwargs.get('tone_id')
            freq = kwargs.get('freq')
            freq2 = kwargs.get('freq2')

            msg = '{} {} {} {} {} {}'.format(
                camelot.START_CADENCE_DETECTOR, stream_ref, tone_id, freq,
                freq2, '@')

        elif message == camelot.STOP_CADENCE_DETECTOR:
            tone_id = kwargs.get('tone_id')
            msg = '{} {} {}{}'.format(
                camelot.STOP_CADENCE_DETECTOR, stream_ref, tone_id, '@')

        return self.get_out_msg(msg, args[0])

    def get_media_request(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError('EP ID is not passed')
        msg = ''
        stream_ref = args[1]
        if message == camelot.START_MEDIA_EVENTS:
            msg = 'startmediaevents ' + str(stream_ref) + '@'

        elif message == camelot.STOP_MEDIA_EVENTS:
            msg = 'stopmediaevents ' + str(stream_ref) + '@'

        elif message == camelot.START_MEDIA_PLAYER:
            encoding = kwargs.get('encoding')
            url = kwargs.get('url')
            mode = kwargs.get('mode')
            msg = '{} {} {} {} {}{}'.format(
                'startmediaplayer', stream_ref, url, encoding, mode, '@')

        elif message == camelot.STOP_MEDIA_PLAYER:
            msg = 'stopmediaplayer ' + str(stream_ref) + '@'

        elif message == camelot.START_MEDIA_RECORDER:
            prefix = kwargs.get('prefix')
            msg = '{} {} {}{}'.format(
                'startmediarecorder', str(stream_ref), str(prefix), '@')

        elif message == camelot.STOP_MEDIA_RECORDER:
            msg = 'stopmediarecorder ' + str(stream_ref) + '@'

        return self.get_out_msg(msg, args[0])

    def get_raw_request(self, message, *args, **kwargs):
        msg_type = None
        ep_id = args[0]
        encoded_msg = None
        if message == camelot.SEND_RAW_REQUEST:
            ccb = kwargs.get('ccb')
            scb = kwargs.get('scb')
            method = kwargs.get('method')
            body_xml = kwargs.get('body_xml')
            withsdp = kwargs.get('withsdp')
            encoded_msg = "rawsendrequest {}^{}^{}^{}^{}@".format(
                ccb, scb, method, body_xml, withsdp)
        elif message == camelot.VERIFY_REQ_SEND_RESP:
            msgid = kwargs.get('msgid')
            method = kwargs.get('method')
            header_filter = kwargs.get('header_filter')
            content_filter = kwargs.get('content_filter')
            status_code = kwargs.get('status_code')
            reason_phrase = kwargs.get('reason_phrase')
            resp_continue = kwargs.get('resp_continue')
            encoded_msg = '{} {}\n{}\n{}\n{}\n{}\n{}\n{}\n{}@'.format(
                'verifyRequestsendResponse', msgid, method, method,
                header_filter, content_filter,
                status_code, reason_phrase, resp_continue)
        elif message == camelot.CREATE_TEMPLATE_MSG:
            encoded_msg = 'createtemplatemessage NONE NONE@'
            msg_type = 'f'
            ep_id = None
        elif message == camelot.REMOVE_INACTION_OBJ:
            msg_id = args[1]
            encoded_msg = '{} {}@'.format(
                camelot.REMOVE_INACTION_OBJ, msg_id)
        log.debug("encoded_msg={}".format(encoded_msg))
        return self.get_out_msg(encoded_msg, ep_id, msg_type)

    def get_sip_request(self, message, *args, **kwargs):
        if len(args) <= 1:
            raise camelot.CamelotError('EP ID is not passed')
        call_ref = args[1]
        if message == camelot.GET_SIP_MESSAGES:
            mode = args[2]
            msg = 'getsipmessages %s %s@' % (call_ref, mode)

        elif message == camelot.GET_SIP_HEADERS:
            msg_id = kwargs.get('msg_id')
            msg = 'getsipheaders ' + str(call_ref) + ' ' + str(msg_id) + '@'

        elif message == camelot.DELETE_SIP_MESSAGES:
            msg = 'deletesipmessages {}@'.format(call_ref)

        elif message == camelot.GET_SIP_HEADER:
            msg_id = kwargs.get('msg_id')
            header_val = kwargs.get('header_val')
            msg = '{} {} {} {}{}'.format(
                'getsipheader', call_ref, msg_id, header_val, '@')

        elif message == camelot.GET_CONTENT_BODY_LIST:
            msg = call_ref + '@'

        elif message == camelot.GET_CONTENT_BODY:
            msg_id = kwargs.get('msg_id')
            method_name = kwargs.get('method_name')
            msg = '{} {} {} {}{}'.format(
                'getcontentbody', call_ref, msg_id, method_name, '@')

        return self.get_out_msg(msg, args[0])

    def get_player_request(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        stream_ref = args[1]
        msg = ''
        if message == camelot.START_DTMF_PLAYER:
            medium = kwargs.get('medium')

            ontime = kwargs.get('ontime')
            offtime = kwargs.get('offtime')
            digits = kwargs.get('digits')
            call_ref = kwargs.get('call_ref')

            if medium == 'inband':
                msg = '{} {} {} {} {} {}{}'.format(
                    'startdtmfplayer', medium,
                    stream_ref, digits, ontime, offtime, '@')
            elif medium == 'oob':
                msg = '{} {} {} {}{}'.format(
                    'startdtmfplayer', medium, call_ref, digits, '@')

        elif message == camelot.STOP_DTMF_PLAYER:
            msg = '{} {}{}'.format('stopdtmfplayer', stream_ref, '@')

        elif message == camelot.START_TONE_PLAYER:
            len_tone_seq = kwargs.get('len_tone_seq')
            tone_seq_str = kwargs.get('tone_seq_str')
            msg = 'starttoneplayer {} {} {}{}'.format(
                stream_ref, len_tone_seq, tone_seq_str.strip(), '@')

        elif message == camelot.STOP_TONE_PLAYER:
            msg = '{} {}{}'.format(
                'stoptoneplayer', stream_ref, '@')

        elif message == camelot.START_TRAFFIC_PLAYER:
            mode = kwargs.get('mode')
            msg = '{} {} {}{}'.format(
                'starttrafficplayer', stream_ref, mode, '@')

        elif message == camelot.STOP_TRAFFIC_PLAYER:
            msg = '{} {}{}'.format(
                'stoptrafficplayer', stream_ref, '@')

        return self.get_out_msg(msg, args[0])

    def get_ipps_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        if message == camelot.GET_IPPS_MULTIMEDIA:
            request = "{} ipps_ref {}@".format(message, args[1])
        else:
            request = "{}@".format(message)
        return self.get_out_msg(request, args[0])

    def get_auto_dial_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        msg = 'autodial'

        if message == camelot.ENABLE_AUTO_DIAL:
            msg += ' enable '
            if kwargs.get('dial_list') and isinstance(
                    kwargs.get('dial_list')[0], dict):
                dial_call_list = kwargs.get('dial_list')
                for item in dial_call_list:
                    if not item.get('called address'):
                        raise CamelotError("Missing called address")
                    called_address = item['called address']
                    calling_address = item.get('calling address', 'null')
                    calling_line = item.get('calling line', '0')
                    msg += (
                        "{}^ {} {} ".format(
                            called_address, calling_line, calling_address
                        )
                    )
                event = kwargs.get('auto_dial_event')
            else:
                # Based on original code, it is only expecting 1 item
                # in dial list.  The below code mimics the "{}^ {} {}"
                # format for a dial string
                # (what goes between two dial string formats? space? carat?)
                # This code would have to be re-visited when that
                # functionality is needed
                dial_list = kwargs.get('dial_list')
                if not dial_list:
                    msg += ' called'
                else:
                    for dial_str in dial_list:
                        dial_params = dial_str.split(':')
                        msg += "{}^ {} {}".format(
                            dial_params[0],
                            next(iter(dial_params[1:]), '0'),
                            next(iter(dial_params[2:]), 'null')
                        )
                event = kwargs['event']
            if event:
                msg += " event^{}".format(event)
            msg += '@'
        elif message == camelot.DISABLE_AUTO_DIAL:
            msg = 'autodial disable@'
        elif message == camelot.GET_AUTO_DIAL_CALLED_LIST:
            msg = 'autodial called@'
        elif message == camelot.GET_AUTO_DIAL_EVENT:
            msg = 'autodial event@'
        elif message == camelot.GET_AUTO_DIAL_STATUS:
            msg = 'autodial status@'
        return self.get_out_msg(msg, args[0])

    def get_auto_conference_msg(self, message, *args, **kargs):

        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')

        if message == camelot.DISABLE_AUTO_CONFERENCE:
            config_request = 'autoconference disable@'

        elif message == camelot.GET_AUTO_CONFERENCE_MODE:
            config_request = 'autoconference mode@'

        elif message == camelot.GET_AUTO_CONFERENCE_STATUS:
            config_request = 'autoconference status@'

        elif message == camelot.GET_AUTO_CONFERENCE_TALK_TIME:
            config_request = 'autoconference talktime@'

        elif message == camelot.GET_AUTO_CONFERENCE_TARGET:
            config_request = 'autoconference target@'

        elif message == camelot.ENABLE_AUTO_CONFERENCE:
            talk_time = kargs.get('talktime', None)
            target = kargs.get('target', None)
            line_ref = kargs.get('lineref', None)
            mode = kargs.get('mode', None)

            config_request = 'autoconference status@'

            if talk_time and target and mode and line_ref:
                config_request = '{} enable {} {} {} {}@'.format(
                    'autoconference', talk_time, target, mode, line_ref)

            elif not line_ref and (talk_time and mode and target):
                config_request = '{} enable {} {} {}@'.format(
                    'autoconference', talk_time, target, mode)

            elif not mode and (talk_time and target and line_ref):
                config_request = '{} enable {} {}@'.format(
                    'autoconference', talk_time, target)

            elif ((not(mode and line_ref)) and ((talk_time and target))):
                config_request = '{} enable {} {}@'.format(
                    'autoconference', talk_time, target)

            elif talk_time and (not(target and mode and line_ref)):
                config_request = '{} {}@'.format(
                    'autoconference', talk_time)

            elif target and (not (talk_time and mode and line_ref)):
                config_request = '{} {}@'.format(
                    'autoconference', target)

            elif mode and (not (talk_time and target and line_ref)):
                config_request = '{} {}@'.format(
                    'autoconference', mode)

        return self.get_out_msg(config_request, args[0])

    def get_auto_transfer_msg(self, message, *args, **kargs):

        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')

        if message == camelot.DISABLE_AUTO_TRANSFER:
            config_request = 'autotransfer disable@'

        elif message == camelot.GET_AUTO_TRANSFER_MODE:
            config_request = 'autotransfer mode@'

        elif message == camelot.GET_AUTO_TRANSFER_STATUS:
            config_request = 'autotransfer status@'

        elif message == camelot.GET_AUTO_TRANSFER_TALK_TIME:
            config_request = 'autotransfer talktime@'

        elif message == camelot.GET_AUTO_TRANSFER_TARGET:
            config_request = 'autotransfer target@'

        elif message == camelot.ENABLE_AUTO_TRANSFER:
            talk_time = kargs.get('talktime', None)
            target = kargs.get('target', None)
            line_ref = kargs.get('lineref', None)
            mode = kargs.get('mode', None)

            config_request = 'autotransfer status@'

            if talk_time and target and mode and line_ref:
                config_request = '{} enable {} {} {} {}@'.format(
                    'autotransfer', talk_time, target, mode, line_ref)

            elif not line_ref and (talk_time and mode and target):
                config_request = '{} enable {} {} {}@'.format(
                    'autotransfer', talk_time, target, mode)

            elif talk_time and (not(target and mode and line_ref)):
                config_request = '{} {}@'.format(
                    'autotransfer', talk_time)

            elif target and (not (talk_time and mode and line_ref)):
                config_request = '{} {}@'.format(
                    'autotransfer', target)

            elif mode and (not (talk_time and target and line_ref)):
                config_request = '{} {}@'.format(
                    'autotransfer', mode)

        return self.get_out_msg(config_request, args[0])

    def get_auto_park_msg(self, message, *args, **kargs):

        # print 'get_auto_park_msg -> %s' % args
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')

        if message == camelot.DISABLE_AUTO_PARK:
            config_request = 'autopark disable@'

        elif message == camelot.GET_AUTO_PARK:
            config_request = 'autopark status@'

        elif message == camelot.ENABLE_AUTO_PARK:
            talk_time = kargs.get('talktime', None)
            disc_t = kargs.get('disc_t', None)
            status_t = kargs.get('status_t', None)
            button_no = kargs.get('buttonno', None)
            mode = kargs.get('parktype', None)

            config_request = 'autopark status@'
            if button_no == 'None':
                button_no = '0'

            if talk_time and disc_t and status_t and mode and button_no:
                config_request = '{} enable {} {} {} {} {}@'.format(
                    'autopark', talk_time, disc_t, status_t, button_no, mode)

            elif not mode:
                config_request = '{} enable {} {} {} {}@'.format(
                    'autopark', talk_time, disc_t, status_t, button_no)

        return self.get_out_msg(config_request, args[0])

    def get_auto_park_ret_msg(self, message, *args, **kargs):

        # print 'get_auto_park_ret_msg -> %s' % args
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')

        if message == camelot.DISABLE_AUTO_PARK_RET:
            config_request = 'autoparkretrieve disable@'

        elif message == camelot.GET_AUTO_PARK_RET:
            config_request = 'autoparkretrieve status@'

        elif message == camelot.ENABLE_AUTO_PARK_RET:
            talk_t = kargs.get('talktime', None)
            trigger_t = kargs.get('triggertime', None)
            park_num = kargs.get('parknum', None)
            button_no = kargs.get('buttonno', None)
            comp_t = kargs.get('completetime', None)
            mode = kargs.get('parktype', None)

            config_request = 'autoparkretrieve status@'
            if button_no == 'None':
                button_no = '0'

            if park_num == 'None':
                park_num = '0'

            if park_num and trigger_t and comp_t and mode and button_no:
                config_request = '{} enable {} {} {} {} {} {}@'.format(
                    'autoparkretrieve', park_num, button_no,
                    trigger_t, comp_t, talk_t, mode)

            elif not mode:
                config_request = '{} enable {} {} {} {}@'.format(
                    'autoparkretrieve', park_num, button_no,
                    trigger_t, comp_t, talk_t)

        return self.get_out_msg(config_request, args[0])

    def get_auto_resume_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')

        if message == camelot.DISABLE_AUTO_RESUME:
            config_request = 'autoresume disable@'

        elif message == camelot.GET_AUTO_RESUME_STATUS:
            config_request = 'autoresume status@'

        elif message == camelot.GET_AUTO_RESUME_HOLD_TIME:
            config_request = 'autoresume holdtime@'

        elif message == camelot.ENABLE_AUTO_RESUME:
            hold_time = args[1]
            if(hold_time > 0):
                config_request = '{} enable {}@'.format(
                    'autoresume', str(hold_time))
            elif(hold_time == 0):
                config_request = 'autoresume holdtime@'
            else:
                config_request = 'autoresume status@'

        return self.get_out_msg(config_request, args[0])

    def get_auto_answer_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')

        line_ref = kargs.get('lineref', None)
        calling_list = kargs.get('calling', None)
        delay = kargs.get('delay', None)

        if not line_ref:
            line_ref = '0'
        elif (not self._is_valid_integer(line_ref) or int(line_ref) < 0):
            log.error('enable_auto_answer: Valid Line reference not provided')
            return

        if message == camelot.ENABLE_AUTO_ANSWER:
            calling_str = ''
            if (calling_list and (type(calling_list) == list and
                                  len(calling_list) > 0)):
                for reg_ex in calling_list:
                    calling_str += reg_ex + '^'
            else:
                calling_str = "(null)"

            if not delay:
                delay = '0'
            elif not self._is_valid_integer(delay):
                log.error('enable_auto_answer: invalid delay specified')
                return

            config_request = 'autoanswer enable %s %s %s@' % (line_ref,
                                                              calling_str,
                                                              delay)
        elif message == camelot.DISABLE_AUTO_ANSWER:
            config_request = 'autoanswer disable %s@' % (line_ref)

        elif message == camelot.AUTO_ANSWER_INFO:
            config_request = 'autoanswer info %s@' % (line_ref)

        return self.get_out_msg(config_request, args[0])

    def get_auto_cell_pickup_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')

        delay = kargs.get('delay', None)

        if not delay:
            delay = '0'

        if message == camelot.ENABLE_AUTO_CELL_PICKUP:
            config_request = 'autocellpickup enable %s@' % delay
        elif message == camelot.DISABLE_AUTO_CELL_PICKUP:
            config_request = 'autocellpickup disable@'
        elif message == camelot.GET_AUTO_CELL_PICKUP_DELAY:
            config_request = 'autocellpickup delay@'
        elif message == camelot.GET_AUTO_CELL_PICKUP_STATUS:
            config_request = 'autocellpickup status@'

        return self.get_out_msg(config_request, args[0])

    def get_vvm_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        request = ''
        if message == camelot.SHOW_VVM_IDS:
            request = '{} {}@'.format(message, args[1])
        elif message in [camelot.SHOW_VVM_INFO,
                         camelot.FETCH_VVM]:
            request = '{} msgid {}@'.format(message, args[1])
        elif message == camelot.DELETE_VVM:
            if args[1]:
                request = '{} {}@'.format(message, args[1])
            else:
                request = message + '@'
        elif message == camelot.SEND_VVM:
            request = '{}@'.format(message)
        elif message == camelot.RECORD_VVM:
            record_mode = kargs.get('record_mode')
            record_time = kargs.get('record_time')
            request = '{} {} {}@'.format(message, record_mode, record_time)
        elif message == camelot.RUN_CONVERSATION:
            conversation = kargs.get('conversation')
            prop_id_num = kargs.get('prop_id_num')
            prop_info = kargs.get('prop_info')
            request = '{} {} {} {}@'.format(
                message, conversation, prop_id_num, prop_info)
        elif message == camelot.ADD_RECIPIENT_VVM:
            called_number = kargs.get('called_number')
            called_name = kargs.get('called_name')
            request = '{} {} {}@'.format(
                message, called_number, called_name)
        elif message == camelot.PLAY_VVM:
            time = kargs.get('time')
            blob = kargs.get('blob')
            startpos = kargs.get('startpos')
            if time:
                request = '{} msgid {} time{}@'.format(message, args[1], time)
            elif blob:
                request = '{} msgid {} blob@'.format(message, args[1], blob)
            elif startpos:
                request = '{} msgid {} startpos@'.format(message, args[1],
                                                         startpos)
            else:
                request = '{} msgid {}@'.format(message, args[1])

        return self.get_out_msg(request, args[0])

    def get_auto_disconnect_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')

        if message == camelot.ENABLE_AUTO_DISCONNECT:
            hold_time = kargs.get('holdtime', None)
            if (not hold_time or not self._is_valid_integer(hold_time) or
                    int(hold_time) < 0):
                log.error('enable_auto_disconnect: Invalid Hold time')
                return

            config_request = 'autodisconnect enable %s@' % (hold_time)

        elif message == camelot.DISABLE_AUTO_DISCONNECT:
            config_request = 'autodisconnect disable@'

        elif message == camelot.AUTO_DISCONNECT_DELAY:
            config_request = 'autodisconnect delay@'

        elif message == camelot.AUTO_DISCONNECT_STATUS:
            config_request = 'autodisconnect status@'

        return self.get_out_msg(config_request, args[0])

    def get_info_event_msg(self, message, *args, **kwargs):
        if len(args) != 2:
            raise camelot.CamelotError('EP ID/Type is not passed: %s' % args)
        if message == camelot.START_INFO_EVENTS:
            formated_str_string = 'infoevent %s on@' % args[1]
        elif message == camelot.STOP_INFO_EVENTS:
            formated_str_string = 'infoevent %s off@' % args[1]
        else:
            key = kwargs.get('type')
            value = kwargs.get('state')
            formated_str_string = '{} {} {} {}@'.format(
                message, args[1], key, value)
        return self.get_out_msg(formated_str_string, args[0])

    def get_streams_msg(self, message, *args):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        mifc_type = None
        type_num = '0'
        if len(args) >= 2:
            mifc_type = args[1]

        if not mifc_type:
            type_num = '0'
        elif mifc_type == 'line':
            type_num = '1'
        elif mifc_type == 'phoneconfcap':
            type_num = '2'
        elif mifc_type == 'recordnearend':
            type_num = '3'
        elif mifc_type == 'recordfarend':
            type_num = '4'
        else:
            log.error('Unknown media interface type')
            raise camelot.CamelotError('Unknown media interface type: %s' % (
                mifc_type))
        formated_str_string = '%s %s@' % (message, type_num)
        return self.get_out_msg(formated_str_string, args[0])

    def get_conf_calls_msg(self, message, *args):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        confid = None
        if len(args) >= 2:
            confid = args[1]

        formated_str_string = '%s confid %s@' % (message, confid)
        return self.get_out_msg(formated_str_string, args[0])

    def get_conf_streams_msg(self, message, *args):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        mifc_type = None
        type_num = '0'
        confid = None
        if len(args) >= 2:
            confid = args[1]
        if not mifc_type:
            type_num = '0'
        elif mifc_type == 'line':
            type_num = '1'
        elif mifc_type == 'phoneconfcap':
            type_num = '2'
        elif mifc_type == 'recordnearend':
            type_num = '3'
        elif mifc_type == 'recordfarend':
            type_num = '4'
        else:
            log.error('Unknown media interface type')
            raise camelot.CamelotError('Unknown media interface type: %s' % (
                mifc_type))
        formated_str_string = '%s %s confid %s@' % (message, type_num, confid)
        return self.get_out_msg(formated_str_string, args[0])

    def get_placecall_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        line_ref = kargs.get('lineref', '0')
        dialstr = kargs.get('called', 'null')
        calling = kargs.get('calling', 'null')
        calltype = kargs.get('calltype', '0')
        dial_str = "placecall %s %s^ %s^ %s@" % (
            line_ref, dialstr, calltype, calling)

        return self.get_out_msg(dial_str, args[0])

    def get_dial_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP id not passed')
        if len(args) < 2:
            raise camelot.CamelotError('Call Reference not passed')
        ep_id = args[0]
        call_ref = args[1]
        dialstr = kargs.get('called', '0')
        calling = kargs.get('calling', None)

        if not dialstr:
            log.error('Invalid dial string given, returning..')
            return
        if not self._is_valid_call_ref(call_ref):
            log.error('invalid call reference, returning..')
            return
        if calling:
            dial_str = "dial %s %s^ %s@" % (call_ref, dialstr,
                                            calling)
        else:
            dial_str = "dial %s %s^@" % (call_ref, dialstr)

        return self.get_out_msg(dial_str, args[0])

    def get_transfer_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP id not passed')
        if len(args) < 2:
            raise camelot.CamelotError('Call Reference not passed')
        ep_id = args[0]
        call_ref = args[1]
        msg = '%s %s' % (message, int(call_ref, 16))
        mode = kargs.get('mode', None)
        line_reference = kargs.get('lineref', None)
        if mode:
            if mode == 'consultative' or mode == 'connected':
                msg += ' ' + mode
            else:
                log.error('Invalid transfer mode, Returning.. ')
                return
        if line_reference:
            if isinstance(line_reference, int) and line_reference > 0:
                msg += ' ' + str(line_reference)
            else:
                log.error('Transfer: Invalid line reference.')
                return
        msg += '@'
        return self.get_out_msg(msg, args[0])

    def _is_valid_integer(self, int_str):
        try:
            int(int_str)
            return True
        except (ValueError, TypeError):
            return False

    def _is_valid_call_ref(self, call_ref_str):
        try:
            int(call_ref_str, 16)
            return True
        except (ValueError, TypeError):
            return False

    def get_config_msg(self, *args, **kargs):
        if len(args) < 2:
            raise camelot.CamelotError('Config parameter is not passed')
        ep_id = args[0]
        param = args[1]
        value = None
        if len(args) >= 3:
            value = args[2]
        if value:
            msg = 'config %s value %s@' % (param, value)
        else:
            msg = 'config %s@' % param
        return self.get_out_msg(msg, args[0])

    def press_button_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Config parameter is not passed')
        ep_id = args[0]
        button_id = kwargs.get('button_id')
        button_val = kwargs.get('button_val')
        callref = kwargs.get('callref')
        msg = ''
        if id:
            if button_id in ['feature', 'button', 'buttonblf']:
                msg = button_id
        else:
            return
        msg = '{} {} {} {}@'.format(message, msg, button_val, callref)
        return self.get_out_msg(msg, ep_id)

    def get_button_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Config parameter is not passed')
        ep_id = args[0]
        button_id = kwargs.get('button_id')
        button_val = kwargs.get('button_val')
        msg = ''
        if id:
            if button_id in ['button', 'buttonblf']:
                msg = button_id
        else:
            return
        msg = '{} {} {}@'.format(message, msg, button_val)
        return self.get_out_msg(msg, ep_id)

    def get_mediator_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Config parameter is not passed')
        ep_id = args[0]
        value = None
        cmd = kwargs.get('cmd')
        output = kwargs.get('output')
        delay = kwargs.get('delay')
        msg = message + ' ' + str(cmd)
        if output:
            msg += '^1'
        else:
            msg += '^0'
        msg += '^' + str(delay) + '@'
        return self.get_out_msg(msg, args[0])

    def get_tone_seq(self, message, *args, **kwargs):
        value = None
        codec = kwargs.get('codec')
        leader = kwargs.get('leader')
        duration = kwargs.get('duration')
        length = kwargs.get('length')
        tone_seq_str = kwargs.get('tone_seq_str')
        trailer = kwargs.get('trailer')

        msg = '{} {} {} {} {} {}{}@'.format(
            message, codec, leader, duration, trailer, length, tone_seq_str)
        return self.get_out_camelot_msg(msg)

    def get_raw_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Config parameter is not passed')
        ep_id = args[0]
        value = None

        callid_filter = kwargs.get('callid_filter')
        method_filter = kwargs.get('method_filter')
        cseq_filter = kwargs.get('cseq_filter')
        assist = kwargs.get('assist')
        msg = '{0} {1}\n{2}\n{3}\n{4}@'.format(
            message, callid_filter,
            method_filter, cseq_filter, assist)

        return self.get_out_msg(msg, args[0])

    def get_call_control_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP id not passed')
        if len(args) < 2:
            raise camelot.CamelotError('arguments not passed')
        ep_id = args[0]
        call_ref = args[1]
        if message in [camelot.DND, camelot.OFFHOOK,
                       camelot.PICKUP, camelot.GPICKUP,
                       camelot.OPICKUP, camelot.CELL_PICKUP,
                       camelot.REDIAL, camelot.HLOG,
                       camelot.LIVE_RECORD, camelot.RECORD,
                       camelot.STOP_RECORD, camelot.TRANSFER_VM,
                       camelot.BLFCALLPARK, camelot.CFWDALL,
                       camelot.STOP_SENDING, camelot.HEADSET_CC_AGENTSTATE]:
            if call_ref:
                msg = '%s %s@' % (message, call_ref)
            else:
                msg = '%s@' % message
        elif message in [camelot.HOLD,
                         camelot.RESUME,
                         camelot.END_CALL]:
            other_param = args[2]
            msg = '%s %s %s@' % (message, call_ref, other_param)
        elif message in [camelot.IDIVERT,
                         camelot.PARK,
                         camelot.START_DETECT_SILENCE]:
            other_param = args[2]
            if other_param:
                msg = '%s %s %s@' % (message, call_ref, other_param)
            else:
                msg = '%s %s@' % (message, call_ref)
        elif message == camelot.SEND_VOICE:
            file_name = args[2]
            if not file_name:
                raise camelot.CamelotError('File not passed')
            is_continue = args[3]
            if not is_continue:
                raise camelot.CamelotError('is_continue not passed')
            sampling_rate = args[4]
            if not sampling_rate:
                raise camelot.CamelotError('sampling_rate not passed')
            msg = '%s %s %s %s %s@' % (message, call_ref,
                                       file_name, is_continue, sampling_rate)
        elif message == camelot.RECORD_VOICE:
            file_name = args[2]
            if not file_name:
                raise camelot.CamelotError('File not passed')
            audio_format = args[3]
            if not audio_format:
                raise camelot.CamelotError('audio_format not passed')
            msg = '%s %s %s %s@' % (message, call_ref,
                                    file_name, audio_format)
        elif message == camelot.MOVE:
            mute = kargs.get('mute')
            msg = '%s %s^%s@' % (camelot.MOVE, call_ref, mute)
        elif message == camelot.REJECT:
            response_code = kargs.get('response_code')
            reason = kargs.get('reason')
            retry_after = kargs.get('retry_after')
            # adding space before reason parameter to solve string token
            # problems in server side
            msg = '%s %s %s^ %s^%s@' % (
                camelot.REJECT, call_ref, response_code, reason, retry_after)
        elif message == camelot.FLASH:
            flash_length = kargs.get('flash_length')
            time_out = kargs.get('time_out')
            msg = '%s %s %s %s@' % (
                camelot.FLASH, call_ref, flash_length, time_out)
        else:
            msg = '%s %s@' % (message, call_ref)
        return self.get_out_msg(msg, args[0])

    def get_buddy_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP id not passed')
        if len(args) < 2:
            raise camelot.CamelotError('arguments not passed')
        ep_id = args[0]
        msg = "{} {}^@".format(message, args[1])
        return self.get_out_msg(msg, ep_id)

    def get_privacy_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('not enough parameters passed')

        ep_id = args[0]
        msg = message + '@'
        return self.get_out_msg(msg, ep_id)

    def get_reinvite_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('not enough parameters passed')

        ep_id = args[0]
        call_ref = args[1]

        value = kwargs.get('value')
        reason_phrase = kwargs.get('reason_phrase')
        repeat = kwargs.get('repeat')
        initial_invite = kwargs.get('initial_invite')

        msg = '{} {}^{}^{}^{}^{}@'.format(
            message, call_ref, value, reason_phrase, repeat, initial_invite)
        return self.get_out_msg(msg, args[0])

    def get_updatemedia_msg(self, message, *args, **kwargs):
        if message == camelot.CTI_CLEAR_RESPONSE:
            if not args[1]:
                req_id = -1
            else:
                req_id = args[1]
            msg = '{} {}@'.format(message, req_id)
            return self.get_out_msg(msg, args[0])

        if len(args) < 3:
            raise camelot.CamelotError('not enough parameters passed')

        ep_id = args[0]
        call_ref = args[1]
        if message == camelot.CTI_SEND_DTMF:
            DTMF_digits = args[2]
            play_rate = args[3]
            msg = '%s %s %s %s@' % (message, call_ref, DTMF_digits, play_rate)
            return self.get_out_msg(msg, args[0])
        option = args[2]
        if option:
            msg = '%s %s %s@' % (message, call_ref, option)
        else:
            msg = '%s %s@' % (message, call_ref)
        return self.get_out_msg(msg, args[0])

    def get_refreshregister_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP Id is not given')
        ep_id = args[0]
        ip = kwargs.get('ip', 'null')
        ipv6 = kwargs.get('ipv6', 'null')
        tcpdrop = kwargs.get('tcpdrop', '0')
        msg = '%s %s^ %s^ %s^@' % (message, ip, ipv6, tcpdrop)
        return self.get_out_msg(msg, args[0])

    def get_refreshsubscribe_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError('EP id not available')

        ep_id = args[0]
        event = args[1]
        eventstr = kwargs.get('eventstr', 'null')
        unsubs = kwargs.get('unsubscribe', 0)
        clear = kwargs.get('clear', 0)
        msg = message
        if not event:
            if eventstr == 'null':
                if clear:
                    if unsubs:
                        raise camelot.CamelotError(
                            'Unsubscribe all is not supported')
                    else:
                        msg = '%s eventall cleardisp^@' % message
                else:
                    if unsubs:
                        raise camelot.CamelotError(
                            'Unsubscribe all is not supported')
                    else:
                        msg = '%s event 3^@' % (message)
            else:
                if unsubs and clear:
                    msg = '%s eventstr %s unsubs cleardisp^@' % (
                        message, eventstr)
                elif unsubs:
                    msg = '%s eventstr %s unsubs^@' % (message, eventstr)
                elif clear:
                    msg = '%s eventstr %s cleardisp^@' % (message, clear)
                else:
                    msg = '%s eventstr %s^@' % (message, eventstr)
        else:
            msg = '%s event %s^@' % (message, event)

        return self.get_out_msg(msg, args[0])

    def get_request_only_msg(self, message, *args, **kwargs):
        msg = '{}@'.format(message)
        return self.get_out_msg(msg, args[0])

    def get_release_calls_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError(
                'EP Id is not avaialble/Invalid arguments')
        arg = args[1]
        ep_id = args[0]
        if arg:
            msg = '%s %s@' % (message, arg)
        else:
            msg = '%s@' % message

        return self.get_out_msg(msg, args[0])

    def get_bfl_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError(
                'EP Id is not avaialble/Invalid arguments')
        ep_id = args[0]
        called = args[1]
        msg = '%s %s@' % (message, called)
        return self.get_out_msg(msg, args[0])

    def get_ep_misc_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError(
                'EP Id is not available/Invalid arguments')
        ep_id = args[0]
        callref = args[1]
        called = kwargs.get('called', 'null')
        mode = kwargs.get('mode')
        callbackno = kwargs.get('callbackno', 'null')
        if not callbackno:
            msg = '{} {} {}^ {}@'.format(message, callref, called, mode)
        else:
            msg = '{} {} {}^ {} {}@'.format(
                message, callref, called, mode, callbackno)
        return self.get_out_msg(msg, args[0])

    def get_dmc_handin_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError(
                'EP Id is not available/Invalid arguments')
        ep_id = args[0]
        called = args[1]
        calling = kwargs.get('calling', 'null')
        calltype = kwargs.get('calltype', 0)
        lineref = kwargs.get('lineref', 0)

        msg = '%s %s %s^ %s^ %s@' % (
            message, lineref, called, calltype, calling)

        return self.get_out_msg(msg, args[0])

    def get_sso_info_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError(
                'EP Id is not available/Invalid arguments')
        ep_id = args[0]
        sso_service = args[1]

        if message == camelot.GET_SSO_INFO:
            msg = "getssoinfo " + str(sso_service) + '@'
        elif message == camelot.GET_SSO_STATS:
            clear = kwargs.get('clear')
            msg = '{} {} {}{}'.format('getssostats', clear, sso_service, '@')
        return self.get_out_msg(msg, args[0])

    def get_call_time_stats_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError(
                'EP Id is not available/Invalid arguments')
        ep_id = args[0]
        clear = args[1]
        if clear:
            msg = '%s clear@' % message
        else:
            msg = '%s@' % message

        return self.get_out_msg(msg, args[0])

    def get_cas_voice_stats_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError(
                'EP Id is not available/Invalid arguments')
        ep_id = args[0]
        msg = '%s@' % message

        return self.get_out_msg(msg, args[0])

    def get_set_ice_cands_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        if len(args) < 2:
            raise camelot.CamelotError('cand list not found')
        cand_present = 0
        ep_id = args[0]
        ope = args[1]
        cand = args[2]
        if message == camelot.CONF_ICE_CAND:
            if len(cand) >= 1:
                cand_present = 1

            if cand_present:
                msg = '{} {} {}@'.format(message, ope, cand)
            else:
                msg = '{} {}@'.format(message, ope)

        return self.get_out_msg(msg, args[0])

    def get_iceinfo_msg(self, message, *args, **kargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP ID is not passed')
        if len(args) < 2:
            raise camelot.CamelotError('call_ref is not available')
        call_ref = args[1]
        ep_id = args[0]
        if message == camelot.GET_ICE_DETAILS:
            icemsg = "{} {}@".format(message, call_ref)
        elif message == camelot.GET_ICE_INFO:
            mtype = kargs.get('type', 'none')
            subtype = kargs.get('subtype', 'none')
            fixup = kargs.get('fixup', '0')
            icemsg = "geticeinfo %s %s %s %s@" % (
                call_ref, mtype, fixup, subtype)

        return self.get_out_msg(icemsg, args[0])

    def get_fax_send_msg(self, message, *args, **kargs):
        msg = ''
        prefix = ''
        filename = ''
        if message is camelot.START_FAX_SEND:
            if len(args) < 3:
                raise camelot.CamelotError('Invalid arguments')
            msg = '{} {} {}@'.format(message, args[1], args[2])
        else:
            if len(args) < 4:
                raise camelot.CamelotError('Invalid arguments')
            prefix = args[2]
            filename = args[3]
            msg = '{} {} {} {}@'.format(message, args[1],
                                        prefix, filename)
        log.debug('encoded sendtone message to be sent to camelot(%s)' % (msg))
        return self.get_out_msg(msg, args[0])

    def get_intercom_msg(self, message, *args, **kargs):
        if len(args) < 2:
            raise camelot.CamelotError('Invalid arguments')

        ep_id = args[0]
        line_ref = args[1]
        calling = kargs.get('calling', 'null')
        called = kargs.get('called', 'null')
        msg = '%s %s %s^ %s@' % (message, line_ref, called, calling)
        return self.get_out_msg(msg, args[0])

    def get_uris_msg(self, message, *args, **kargs):
        if len(args) < 2:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        line = args[1]
        primary = kargs.get('primary', 'all')
        uri = kargs.get('uri', -1)
        msg = '%s %s %s %s@' % (message, line, primary, uri)
        return self.get_out_msg(msg, args[0])

    def get_rtprx_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        mtype = args[1]
        msg = '%s %s^%s^@' % (message, 'all', mtype)
        return self.get_out_msg(msg, args[0])

    def get_userifo_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        jid = args[1]
        username = kwargs.get('username', None)
        emailid = kwargs.get('emailid', None)
        phonenumber = kwargs.get('phonenumber', None)
        if username:
            field = 'username'
            value = username
        elif jid:
            field = 'jid'
            value = jid
        elif emailid:
            field = 'emailid'
            value = emailid
        elif phonenumber:
            field = 'phonenumber'
            value = phonenumber
        else:
            raise camelot.CamelotError('Invalid arguments')
        msg = '%s %s %s^ %s@' % (message, field, value, "")
        return self.get_out_msg(msg, args[0])

    def get_auto_call_guard_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        delay = args[1]
        msg = 'autocallguard'
        if message == camelot.ENABLE_AUTO_CALL_GUARD:
            if delay:
                msg = msg + ' enable ' + str(delay) + '@'
            else:
                msg = msg + ' delay@'

        elif message == camelot.GET_AUTO_CALL_GUARD_STATUS:
            msg = msg + ' status@'

        elif message == camelot.GET_AUTO_CALL_GUARD_DELAY:
            msg = msg + ' delay@'

        else:
            msg = msg + ' disable@'

        return self.get_out_msg(msg, args[0])

    def get_auto_pathconf_msg(self, message, *args, **kwargs):
        if len(args) < 2:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        startdelay = args[1]
        mode = kwargs.get('mode', None)
        trigger = kwargs.get('trigger')
        media = kwargs.get('media', 'audio')
        msg = ''

        if media == 'audio':
            msg = 'autopathconf'
        else:
            msg = 'autopathconfvideo'

        if message == camelot.DISABLE_AUTO_PATH_CONF:
            if trigger:
                msg = msg + ' disable ' + str(trigger) + '@'
            else:
                msg = msg + ' disable both@'

        elif message == camelot.GET_AUTO_PATH_CONF_DELAY:
            msg = msg + ' startdelay ' + str(trigger) + '@'

        elif message == camelot.GET_AUTO_PATH_CONF_MODE:
            msg = msg + ' mode ' + str(trigger) + '@'

        elif message == camelot.GET_AUTO_PATH_CONF_STATUS:
            msg = msg + ' status ' + str(trigger) + '@'

        elif message == camelot.ENABLE_AUTO_PATH_CONF_VIDEO:
            start_delay = kwargs.get('start_delay')
            msg = '{} {} {} {} {}@'.format(
                msg, 'enable', trigger, mode, start_delay)

        elif message == camelot.ENABLE_AUTO_PATH_CONF:
            if trigger and startdelay and not mode:
                msg = msg + ' startdelay ' + str(trigger) + '@'
            elif mode and trigger and not startdelay:
                msg = msg + ' mode ' + str(trigger) + '@'
            elif mode and startdelay and trigger:
                msg = msg + ' enable ' + str(trigger) + ' ' + \
                    str(mode) + ' ' + str(startdelay) + '@'
            else:
                msg = msg + ' status ' + str(trigger) + '@'
        else:
            msg = msg + ' status ' + str(trigger) + '@'

        return self.get_out_msg(msg, args[0])

    def get_auto_record_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        mtype = kwargs.get('type')
        prefix = kwargs.get('prefix', '')
        msg = 'autorecord ' + str(mtype) + ' '

        if message == camelot.GET_AUTO_RECORD_STATUS:
            msg = msg + 'status@'

        elif message == camelot.DISABLE_AUTO_RECORD:
            msg = msg + 'disable@'

        elif message == camelot.GET_AUTO_RECORD_PREFIX:
            msg = msg + 'prefix@'

        else:
            if not prefix:
                msg = msg + 'status@'
            else:
                msg = msg + 'enable ' + str(prefix) + '@'

        return self.get_out_msg(msg, args[0])

    def get_auto_hold_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        talk_time = kwargs.get('talk_time')
        hold_time = kwargs.get('hold_time')
        msg = 'autohold '

        if message == camelot.GET_AUTO_HOLD_STATUS:
            msg = msg + 'status@'

        elif message == camelot.DISABLE_AUTO_HOLD:
            msg = msg + 'disable@'

        elif message == camelot.ENABLE_AUTO_HOLD:
            try:
                int(talk_time)
                int(hold_time)
            except Exception:
                raise camelot.CamelotError(
                    'Invalid TalkTime: %s or HoldTime: %s' % (
                        talk_time, hold_time))
            msg = msg + 'enable ' + str(talk_time) + ' ' + \
                        str(hold_time) + '@'

        elif message == camelot.GET_AUTO_HOLD_HOLD_TIME:
            msg = msg + 'holdtime@'

        elif message == camelot.GET_AUTO_HOLD_TALK_TIME:
            msg = msg + 'talktime@'
        return self.get_out_msg(msg, args[0])

    def get_auto_select_join_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        timer_action_types = ['proceed', 'abort']
        msg = camelot.AUTO_SELECT_JOIN_STR

        if kwargs:
            mode = kwargs.get('mode', None)
            delay = kwargs.get('delay', 0)
            called_list = kwargs.get('called_list', None)
            no_of_calls = kwargs.get('no_of_calls', None)
            timeout = kwargs.get('timeout', None)
            timer_action = kwargs.get('timer_action', None)

        if message == camelot.DISABLE_AUTO_SELECT_JOIN:
            msg = msg + ' disable'

        elif message == camelot.ENABLE_AUTO_SELECT_JOIN:
            if mode == 'inbound':
                if (delay and no_of_calls and timeout and timer_action and
                        timer_action in timer_action_types and
                        (not called_list or len(called_list) < 0)):
                    msg = (msg +
                           ' enable inbound ' + str(delay) + ' ' +
                           str(no_of_calls) + ' ' + timer_action)
                elif (not delay and no_of_calls and timeout and
                      timer_action and timer_action in timer_action_types and
                      (not called_list or len(called_list) < 0)):
                    delay = 0
                    msg = (msg +
                           ' enable inbound ' + str(delay) + ' ' +
                           str(no_of_calls) + ' ' + str(timeout) + ' ' +
                           timer_action)
                elif (not delay and no_of_calls and not timeout and
                      not timer_action and
                      (not called_list or len(called_list) < 0)):
                    delay = 0
                    msg = (msg +
                           ' enable inbound ' + str(delay) + ' ' +
                           str(no_of_calls) + ' -1')
                elif (delay and no_of_calls and not timeout and
                      not timer_action and
                      (not called_list or len(called_list) < 0)):
                    msg = (msg +
                           ' enable inbound ' + str(delay) + ' ' +
                           str(no_of_calls) + ' -1')

            elif mode == 'outbound':
                if (not no_of_calls and delay and not timeout and
                        not timer_action and
                        (called_list and len(called_list) > 0)):
                    msg = '%s enable outbound %s' % (
                        camelot.AUTO_SELECT_JOIN_STR, str(delay))

                    for call in called_list:

                        if (call['CalledDN'] and not call['LineRef'] and
                                not call['Talktime']):
                            msg += ' ' + call['CalledDN'] + '^ 1 0'

                        elif (call['CalledDN'] and
                              (isinstance(call['LineRef'], int) and
                               call['LineRef'] > 0) and call['Talktime']):
                            msg += (' ' + call['CalledDN'] + '^ ' +
                                    str(call['LineRef']) + ' ' +
                                    str(call['Talktime']))

                        elif (call['CalledDN'] and
                              (isinstance(call['LineRef'], int) and
                               call['LineRef'] > 0)):
                            msg += (' ' + call['CalledDN'] + '^ 1' +
                                    str(call['LineRef']))

        elif message == camelot.GET_AUTO_SELECT_JOIN_STATUS:
            msg = msg + ' status'

        elif message == camelot.GET_AUTO_SELECT_JOIN_CALLED_LIST:
            msg = msg + ' called'

        elif message == camelot.GET_AUTO_SELECT_JOIN_DELAY:
            msg = msg + ' delay'

        elif message == camelot.GET_AUTO_SELECT_JOIN_MODE:
            msg = msg + ' mode'

        elif message == camelot.GET_AUTO_SELECT_JOIN_NO_OF_CALLS:
            msg = msg + ' noofcalls'

        elif message == camelot.GET_AUTO_SELECT_JOIN_TIME_OUT:
            msg = msg + 'timeout'

        elif message == camelot.GET_AUTO_SELECT_JOIN_TIME_OUT_ACTION:
            msg = msg + 'timeraction'

        msg = msg + '@'
        return self.get_out_msg(msg, args[0])

    def get_auto_release_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        msg = 'autorelease'

        if message == camelot.ENABLE_AUTO_RELEASE:
            msg = msg + ' enable@'
        elif message == camelot.DISABLE_AUTO_RELEASE:
            msg = msg + ' disable@'
        else:
            msg = msg + ' status@'

        hex_len = self._get_message_length_hex(msg)
        outmsg = FORMAT % ('m', ep_id, hex_len, msg)
        return outmsg

    def get_auto_fax_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        msg = 'autofax'

        if message == camelot.DISABLE_AUTO_FAX:
            msg = msg + ' disable@'
        elif message == camelot.GET_AUTO_FAX_STATUS:
            msg = msg + ' status@'
        elif message == camelot.GET_AUTO_FAX_MODE:
            msg = msg + ' mode@'
        elif message == camelot.GET_AUTO_FAX_URL:
            msg = msg + ' url@'
        else:
            mode = kwargs.get('mode')
            url = kwargs.get('url', 'none')
            prefix = kwargs.get('prefix', 'none')
            msg = '{} {} {} {} {}@'.format(msg, 'enable', mode, url, prefix)
        log.debug('encoded imp message to be sent to camelot(%s) ' % (msg))
        return self.get_out_msg(msg, args[0])

    def get_auto_voice_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        msg = 'autovoice'

        if message == camelot.DISABLE_AUTO_VOICE:
            msg = msg + ' disable@'
        else:
            mode = kwargs.get('mode')
            filename = kwargs.get('filename', 'none')
            samplerate = kwargs.get('send_sample_rate')
            audioformat = kwargs.get('recv_audio_format')

            msg = '{} {} {} {} {} {}@'.format(msg, 'enable',
                                              mode,
                                              filename, samplerate,
                                              audioformat)
        log.debug('encoded imp message to be sent to camelot(%s) ' % (msg))
        return self.get_out_msg(msg, args[0])

    def get_auto_em_service_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        msg = 'autoemservice'

        if message == camelot.DISABLE_AUTO_EM_SERVICE:
            msg = msg + ' disable@'
        elif message == camelot.ENABLE_AUTO_EM_SERVICE:
            delay = kwargs.get('delay')
            user = kwargs.get('user')
            pin = kwargs.get('pin')
            profile = kwargs.get('profile')
            sname = kwargs.get('sname')
            msg = (msg + ' ' + str(delay) + '^' +
                   user + '^' + pin + '^' + profile + '^' + sname + '@')
        else:
            msg = msg + ' @'

        return self.get_out_msg(msg, args[0])

    def get_auto_script_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        msg = 'autoscript'
        trigger = kwargs.get('trigger')

        if message == camelot.ENABLE_AUTO_SCRIPT:
            string_list = args[1]
            msg = msg + ' enable '
            for strc in string_list:
                msg += '{' + strc + '} '
            msg = msg[0:len(msg) - 1]
            msg += '^' + trigger + '@'
        elif message == camelot.DISABLE_AUTO_SCRIPT:
            msg = msg + ' disable@'
        elif message == camelot.GET_AUTO_SCRIPT_SCRIPT:
            msg = msg + ' script@'
        else:
            msg = msg + ' status@'

        return self.get_out_msg(msg, args[0])

    def get_suppl_request(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        call_ref = args[1]

        if message in [camelot.START_SHARE, camelot.STOP_SHARE]:
            secvidtype = kwargs.get('secvidtype')
            msg = '{} {} {}{}'.format(
                message, call_ref, secvidtype, '@')

        elif message in [camelot.STOP_RECORD,
                         camelot.GET_TIMING_STATS,
                         camelot.REFRESH_TEMPLATE_MESSAGE
                         ]:
            msg = '{} {}@'.format(
                message, call_ref)
        elif message == camelot.GET_TRANSPORT_INFO:
            field = kwargs.get('field')
            if field:
                msg = '{} {} {}@'.format(
                    message, call_ref, field)
            else:
                msg = '{} {}@'.format(
                    message, call_ref)

        return self.get_out_msg(msg, args[0])

    def get_dtmfsuppl_request(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        call_ref = args[1]

        if message in [camelot.DTMF_CONFERENCE,
                       camelot.DTMF_DUST,
                       camelot.DTMF_EXCLUSIVE_HOLD,
                       camelot.DTMF_HOLD,
                       camelot.DTMF_RESUME,
                       camelot.DTMF_TRANSFER]:
            msg = '{} {}@'.format(
                message, call_ref)

        return self.get_out_msg(msg, args[0])

    def get_trace_request(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')

        if message == camelot.START_TRACE_EVENTS:
            mask = args[1]
            if mask:
                msg = 'trace ' + mask + '@'
            else:
                msg = 'trace@'
        elif message == camelot.STOP_TRACE_EVENTS:
            msg = 'trace ' + '00@'

        return self.get_out_msg(msg, args[0])

    def get_transport_request(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        transport_ref = args[1]
        decimal_val = int(transport_ref, 16)
        if message == camelot.START_TRANSPORT_EVENTS:
            msg = '{} {} 1@'.format('transportevent', decimal_val)

        elif message == camelot.STOP_TRANSPORT_EVENTS:
            msg = '{} {} 0@'.format('transportevent', decimal_val)

        return self.get_out_msg(msg, args[0])

    def get_auto_move_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        msg = 'automove'
        if message == camelot.ENABLE_AUTO_MOVE:
            delay = kwargs.get('delay')
            mute = kwargs.get('mute', 0)
            msg = msg + ' enable^' + str(delay) + '^' + str(mute) + '@'
        elif message == camelot.DISABLE_AUTO_MOVE:
            msg = msg + ' disable@'
        else:
            msg = msg + 'display@'

        return self.get_out_msg(msg, args[0])

    def get_auto_traffic_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        msg = 'autotraffic'
        mtype = kwargs.get('mediatype')
        if message == camelot.ENABLE_AUTO_TRAFFIC:
            mode = kwargs.get('mode')
            msg = msg + ' ' + mtype + ' enable' + ' ' + mode + '@'
        elif message == camelot.DISABLE_AUTO_TRAFFIC:
            msg = msg + ' ' + mtype + ' disable@'
        elif message == camelot.GET_AUTO_TRAFFIC_MODE:
            msg = msg + ' ' + mtype + ' mode@'
        else:
            msg = msg + ' ' + mtype + ' status@'

        return self.get_out_msg(msg, args[0])

    def get_imp_cmnds_msg(self, request, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        if request in [camelot.XMPP_CLOSE_IM,
                       camelot.REMOVE_BUDDY]:
            msg = request + ' ' + args[1] + '@'
        elif request == camelot.SSO_LOGIN:
            # ssologin $username $mode $invokingtype $implogin $jsessionid
            # $jsessionidsso
            user_name = kwargs.get('user_name')
            user_mode = kwargs.get('user_mode')
            # login_type = kwargs.get('login_type')
            imp_login = kwargs.get('imp_login')
            jsession_id = kwargs.get('jsession_id')
            jsession_id_sso = kwargs.get('jsession_id_sso')
            msg = '{} {} {} {} {} {}@'.format(
                request, user_name, user_mode,
                imp_login, jsession_id, jsession_id_sso)
        else:
            msg = args[1] + '@'
        log.debug('encoded imp message to be sent to'
                  'camelot(%s) ' % (msg))
        return self.get_out_msg(msg, ep_id)

    def sip_simplified_msg_encode(self, request, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        if request in [camelot.SIP_CUSTOM_HEADERS,
                       camelot.SIP_MESSAGE_DETAILED]:
            msg = args[1] + '@'
        elif request == camelot.CLEAR_CUSTOM_HEADERS:
            msg = camelot.CLEAR_CUSTOM_HEADERS + " " + args[1] + '@'
        log.debug('encoded message from sip_simplified_msg_encode to be sent'
                  'to camelot(%s) ' % (msg))
        return self.get_out_msg(msg, ep_id)

    def get_em_cmnds_msg(self, request, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('Invalid arguments')
        ep_id = args[0]
        if request == camelot.EMLOGOUT:
            msg = request + '@'
        else:
            user = kwargs.get('user')
            pin = kwargs.get('pin')
            profile = kwargs.get('profile')
            transport = kwargs.get('transport')
            servicename = kwargs.get('servicename')
            title = kwargs.get('title')

            msg = '{} {}^{}^{}^{}^{}^{}@'.format(
                request, user, pin, profile, transport, servicename, title)

        log.debug('encoded imp message to be sent to'
                  'camelot(%s) ' % (msg))
        return self.get_out_msg(msg, args[0])

    def get_send_tones_msg(self, request, *args, **kwargs):
        log.debug("encldoing sendtones message")
        log.debug("kwargs received in send_tone is %s" % kwargs)
        if len(args) < 2:
            raise camelot.CamelotError('Invalid arguments')
        tone_type = kwargs.get('tone_type')
        stream_ref = args[1]
        msg = '{} {} {}'.format(request, stream_ref, tone_type)
        tone_duration = kwargs.get('tone_duration')
        if tone_type == 0:
            continuous_tone = kwargs.get('continuous_tone')
            if not continuous_tone:
                raise camelot.CamelotError('Continuous tone id is missing')
            if not tone_duration:
                raise camelot.CamelotError('duration for continuous missing')
            msg = '{} {} {}'.format(msg, continuous_tone, tone_duration)
        elif tone_type == 1:
            multi_frequencies = kwargs.get('mf_frequencies')
            if not multi_frequencies:
                raise camelot.CamelotError('not received frequency list')
            if type(multi_frequencies) is not list:
                raise camelot.CamelotError("frequencies is not in list type")
            if not len(multi_frequencies):
                raise camelot.CamelotError("no frequencies in list")
            for freq in multi_frequencies:
                msg = '{} {}'.format(msg, freq.value)
        elif tone_type == 2:
            frequencyA = kwargs.get('frequencyA')
            amplituteA = kwargs.get('amplituteA')
            if not frequencyA:
                raise camelot.CamelotError('frequencyA is missing')
            if not amplituteA:
                raise camelot.CamelotError('amplituteA is missing')
            msg = '{} {} {} {}'.format(msg, frequencyA, amplituteA,
                                       tone_duration)
        elif tone_type == 3:
            frequencyA = kwargs.get('frequencyA')
            amplituteA = kwargs.get('amplitureA')
            frequencyB = kwargs.get('frequencyB')
            amplituteB = kwargs.get('amplitureB')
            if not frequencyA:
                raise camelot.CamelotError('frequencyA is missing')
            if not amplituteA:
                raise camelot.CamelotError('amplituteA is missing')
            if not frequencyB:
                raise camelot.CamelotError('frequencyB is missing')
            if not amplituteB:
                raise camelot.CamelotError('amplituteB is missing')
            msg = '{} {} {} {} {} {}'.format(msg, frequencyA, amplituteA,
                                             frequencyB, amplituteB,
                                             tone_duration)
        else:
            raise camelot.CamelotError('Invalid tone type')
        msg = msg + '@'
        log.debug('encoded sendtone message to be sent to'
                  'camelot(%s) ' % (msg))
        return self.get_out_msg(msg, args[0])

    def get_set_eptiming_msg(self, request, *args, **kwargs):
        log.debug("encodoing set_eptiming message")
        log.debug("kwargs received in detect_tone is %s" % kwargs)
        timer_type = kwargs.get('timer_type')
        tmin = kwargs.get('tmin')
        trange = kwargs.get('trange')
        increment = kwargs.get('increment')
        honor_header = kwargs.get('honor_header')
        msg = '{} {} {} {} {} {}@'.format(request,
                                          timer_type.value,
                                          tmin,
                                          trange,
                                          increment,
                                          honor_header)
        log.debug('encoded set_eptiming message to be sent to'
                  'camelot(%s) ' % (msg))
        return self.get_out_msg(msg, args[0])

    def get_detect_tone_msg(self, request, *args, **kwargs):
        log.debug("encldoing sendtones message")
        log.debug("kwargs received in detect_tone is %s" % kwargs)
        if len(args) < 2:
            raise camelot.CamelotError('Invalid arguments')
        tone_type = kwargs.get('tone_type')
        stream_ref = args[1]
        msg = '{} {} {}'.format(request, stream_ref, tone_type)
        report_flag = kwargs.get('report_flag')
        min_duration = kwargs.get('min_duration')
        min_snr = kwargs.get('min_snr')
        min_level = kwargs.get('min_level')
        max_highlow_am = kwargs.get('max_highlow_am')
        max_lowhigh_fm = kwargs.get('max_lowhigh_fm')
        if tone_type in [4, 5]:
            tone_type = tone_type
        else:
            if tone_type == 0:
                continuous_tone = kwargs.get('continuous_tone')
                if not continuous_tone:
                    raise camelot.CamelotError('Continuous tone id is missing')
                msg = '{} {}'.format(msg, continuous_tone)
            elif tone_type == 1:
                multi_frequencies = kwargs.get('mf_frequencies')
                if not multi_frequencies:
                    raise camelot.CamelotError('not received frequency list')
                if type(multi_frequencies) is not list:
                    raise camelot.CamelotError("frequencies is not in list"
                                               " type")
                if not len(multi_frequencies):
                    raise camelot.CamelotError("no frequencies in list")
                for freq in multi_frequencies:
                    msg = '{} {}'.format(msg, freq.value)
            elif tone_type in [2, 3]:
                msg = '{} {} {} {} {} {} {}'.format(msg,
                                                    report_flag,
                                                    min_duration,
                                                    min_snr,
                                                    min_level,
                                                    max_highlow_am,
                                                    max_lowhigh_fm)
            else:
                raise camelot.CamelotError('Invalid tone type')
        msg = msg + '@'
        log.debug('encoded sendtone message to be sent to'
                  'camelot(%s) ' % (msg))
        return self.get_out_msg(msg, args[0])

    def get_setup_line_msg(self, request, *args, **kwargs):
        log.debug("encoding setup_line message")
        if len(args) < 3:
            raise camelot.CamelotError('Invalid arguments')
        msg = '{} {} {} {}@'.format(request, args[1], args[2], args[3])
        log.debug('encoded setupline message to be setn to'
                  'camelot(%s) ' % (msg))
        return self.get_out_msg(msg, args[0])

    def get_setup_fax_line_msg(self, request, *args, **kwargs):
        log.debug("encoding setup_fax_line message")
        if len(args) < 2:
            raise camelot.CamelotError("Invalid arguments")
        fax_profile = args[1]
        fax_options = 0
        if fax_profile:
            for f in fax_profile.diva_fax_options:
                fax_options |= f.value
            msg = '{} {} {} {} {} {} {}@'.format(request,
                                                 fax_profile.local_number,
                                                 fax_profile.local_sub_address,
                                                 fax_profile.local_fax_id,
                                                 fax_profile.fax_headline,
                                                 fax_profile.default_fax_speed.
                                                 value,
                                                 fax_options)
        else:
            raise camelot.CamelotError("Invalid argument. faxProfile mising")
        log.debug('encoded sendtone message to be sent to'
                  'camelot(%s) ' % (msg))
        return self.get_out_msg(msg, args[0])

    def get_setup_fax_call_option_msg(self, request, *args, **kwargs):
        log.debug("encoding setup_fax_line message")
        if len(args) < 3:
            raise camelot.CamelotError("Invalid arguments")
        fax_profile = args[2]
        fax_options = 0
        msg = ''
        if fax_profile:
            for f in fax_profile.diva_fax_options:
                fax_options |= f.value
            msg = '{} {} {} {} {} {}'.format(request, args[1], fax_options,
                                             fax_profile.local_fax_id,
                                             fax_profile.fax_headline,
                                             fax_profile.default_fax_speed.
                                             value)
        else:
            msg = '{} {} {}'.format(request, args[1], fax_options)
        msg = msg + '@'
        log.debug('encoded sendtone message to be sent to'
                  'camelot(%s) ' % (msg))
        return self.get_out_msg(msg, args[0])

    def get_cm_commands_msg(self, request, *args, **kwargs):
        log.debug("encoding get_cm_commands_msg message")

        if request == camelot.CM:

            if len(args) < 3:
                raise camelot.CamelotError("Invalid arguments")

            msg = '{} {} {}@'.format(request, args[1], args[2])

        elif request == camelot.CMSTATS:
            msg = '{}@'.format(request)

        return self.get_out_msg(msg, args[0])

    def get_sendnoninvite_msg(self, message, *args, **kwargs):
        if len(args) < 1:
            raise camelot.CamelotError('EP CallRef is not passed')
        method = kwargs.get('method_type')
        timeout = kwargs.get('timeout')
        contents = kwargs.get('contents')
        headers = kwargs.get('headers')
        formated_str_string = '{} {} {} {}^{}^{}@'.format(
            message, args[1], method, timeout, contents, headers)

        len_msg_in_hex = self._get_message_length_hex(formated_str_string)
        outmsg = FORMAT % (
            'm', args[0], len_msg_in_hex, formated_str_string)
        return outmsg
