'''
Created on 16-Sep-2013

@author: smaturi
'''
import camelot
import re
import json
from camelot.decoder.decode_helper import CamelotDecodeHelper
from camelot import camlogger
from camelot.utils.vapi_ei_utils import VAPIEIUtils
from camelot.utils import common_utils

log = camlogger.getLogger(__name__)

commands = {}
decode_helper = CamelotDecodeHelper()


def request(cmd):
    log.debug("request for: %s" % cmd)

    def wrap(fn):
        log.debug('wrap %s' % fn)
        commands[cmd] = fn
        return fn
    return wrap


@request(camelot.GET_SERVER_OS)
def decode_server_os(request, response, **kargs):
    ret = camelot.CamelotMessage()
    output_format = kargs.get('output_format')
    if output_format == 'json':
        ret.server_os = decode_helper.jsonify_string(response.message)
    else:
        ret.server_os = response.message
    return ret


@request(camelot.GET_SERVER_VERSION)
def decode_server_version(request, response, **kargs):
    ret = camelot.CamelotMessage()
    output_format = kargs.get('output_format')
    if output_format == 'json':
        ret.server_version = decode_helper.jsonify_string(response.message)
    else:
        ret.server_version = response.message
    return ret


@request(camelot.GET_COMPAT_VERSIONS)
def decode_compat_version(request, response, **kargs):
    ret = camelot.CamelotMessage()
    output_format = kargs.get('output_format')
    if output_format == 'json':
        ret.compat_version = decode_helper.jsonify_string(response.message)
    else:
        ret.compat_version = _parse_compat_versions(response.message)
    return ret


@request(camelot.GET_VAPIEI_VERSION)
def decode_vapiei_version(request, response, **kargs):
    ret = camelot.CamelotMessage()
    output_format = kargs.get('output_format')
    if output_format == 'json':
        ret.vapiei_version = decode_helper.jsonify_string(response.message)
    else:
        ret.vapiei_version = response.message
    return ret


@request(camelot.NEW_ENDPOINT)
@request(camelot.ATTACH_ENDPOINT)
def decode_new_endpoint(request, response, **kargs):
    ep_cls = kargs['ep_class']
    ep_cls_params = kargs['ep_params']
    serv = camelot.get_camelot_server(kargs['ip'], kargs['port'])
    if serv is None:
        raise camelot.CamelotError('Camelot server is not found')
    try:
        serv._get_endpoint(response.epAddress)
    except camelot.CamelotError as e:
        log.debug('endpoint does not exist locally, creating new one: %s' % e)
        return ep_cls(
            response.epAddress, serv._server_conn, **ep_cls_params)
    raise camelot.CamelotError(
        'endpoint {} already exists'.format(response.epAddress))


@request(camelot.GET_ENDPOINT)
def decode_getendpoint(request, response, **kargs):
    serv = camelot.get_camelot_server(kargs['ip'], kargs['port'])
    if not serv:
        raise camelot.CamelotError(
            'Camelot server at {}:{} not found'
            ''.format(kargs['ip'], kargs['port'])
        )
    return serv._get_endpoint(response.epAddress)


@request(camelot.ADD_BUDDY)
@request(camelot.ADD_GROUP)
@request(camelot.REMOVE_GROUP)
@request(camelot.REMOVE_ALL_BUDDIES)
@request(camelot.IMP_CLEAR_RESPONSE)
@request(camelot.VVM_CLEAR_RESPONSE)
@request(camelot.SEND_IM)
@request(camelot.IMP_CLEAR_RESPONSE)
@request(camelot.SET_PRESENCE)
@request(camelot.PRESENCE_CLEAR_RESPONSE)
@request(camelot.HTTP_QUERY_REQ)
@request(camelot.HTTP_CLEAR_RESPONSE)
@request(camelot.CONFIG)
@request(camelot.GET_TRANSPORTS)
@request(camelot.START_TRACE_EVENTS)
@request(camelot.SEND_LOCATION_INFO)
@request(camelot.REMOVE_BUDDY)
@request(camelot.MOVE_BUDDY_TO_GROUPS)
@request(camelot.REMOVE_BUDDY_FROM_GROUPS)
@request(camelot.ADD_BUDDY_TO_GROUPS)
def decode_config(request, response, **kargs):
    return response.message


@request(camelot.INIT)
@request(camelot.RELEASE_EP)
@request(camelot.GET_CLIENT_DATA)
@request(camelot.GET_CALL_SUBJECT)
@request(camelot.GET_CLIENT_DESC)
@request(camelot.GEN_CERT_KEY)
def decode_init(request, response, **kargs):
    return response.message


@request(camelot.IN_SERVICE)
@request(camelot.CLIENT_SUSPEND)
@request(camelot.CLIENT_FOREGROUND)
def decode_inservice(request, response, **kargs):
    return response.message


@request(camelot.UNINIT)
def decode_uninit(request, response, **kargs):
    return response.message


@request(camelot.OUT_OF_SERVICE)
@request(camelot.CONFIG_HEADER)
def decode_outofservice(request, response, **kargs):
    return response.message


@request(camelot.SHOW_VVM_IDS)
@request(camelot.FETCH_VVM)
@request(camelot.PLAY_VVM)
@request(camelot.SEND_VVM)
@request(camelot.RECORD_VVM)
@request(camelot.RUN_CONVERSATION)
@request(camelot.ADD_RECIPIENT_VVM)
@request(camelot.DELETE_VVM)
def decode_vvm_response(request, response, **kargs):
    if response.message:
        if request in [camelot.FETCH_VVM,
                       camelot.DELETE_VVM]:
            if response.message.isalpha():
                raise camelot.CamelotError('%s' % response.message)
            else:
                return response.message
        else:
            return response.message.replace('{', '').replace('}', '').split()


@request(camelot.GET_BLF_INFO)
@request(camelot.GET_FAX_INFO)
@request(camelot.GET_SCRIPT_INFO)
@request(camelot.GET_ICE_INFO)
@request(camelot.GET_RTP_RX_STAT)
@request(camelot.GET_RTP_TX_STAT)
@request(camelot.GET_USER_INFO)
@request(camelot.GET_EDGE_INFO)
@request(camelot.GET_VMWS_INFO)
@request(camelot.GET_SUPPORTED_CONVERSATION_INFO)
@request(camelot.IMP_QUERY_RESPONSE)
@request(camelot.IM_QUERY_RESPONSE)
@request(camelot.GET_PRESENCE)
@request(camelot.PRESENCE_QUERY_RESPONSE)
@request(camelot.GET_BFCP_INFO)
@request(camelot.GET_SSO_INFO)
@request(camelot.GET_SSO_STATS)
@request(camelot.GET_TIMING_STATS)
@request(camelot.GET_UDS_INFO)
@request(camelot.GET_SECURE_UDS_USERS_ACCESS_URL_INFO)
@request(camelot.GET_WEB_SERVICE_INFO)
@request(camelot.SHOW_VVM_INFO)
@request(camelot.GET_CALL_HISTORY)
def decode_get_info(request, response, **kargs):
    ret = None
    if response.message:
        ret = decode_helper.parse_info(response.message)
    return ret


@request(camelot.GET_SINGLE_BUTTON_BARGE)
def decode_supplementary_button(request, response, **kargs):
    res = None
    if response.message and response.message.isdigit():
        res = int(response.message)
    return res


@request(camelot.GET_ICE_DETAILS)
@request(camelot.CTI_GET_RESPONSE_STATUS)
@request(camelot.GET_HEDGE_INFO)
@request(camelot.GET_HEADSET)
@request(camelot.GET_HEADSET_SERVICES)
@request(camelot.GET_HEADSET_CC_AGENTSTATE)
@request(camelot.HTTP_RESPONSE)
@request(camelot.GET_CERT_INFO)
@request(camelot.GET_STREAM_ICE)
@request(camelot.GET_CAS_CALL_TIME_STATISTICS)
@request(camelot.GET_CAS_CALL_INFO)
@request(camelot.GET_CAS_VOICE_STATS)
@request(camelot.GET_ICE_CONFIG)
@request(camelot.GET_TURN_CONFIG)
@request(camelot.GET_DEVICE_CONFIG)
@request(camelot.GET_UDS_USER)
@request(camelot.GET_JABBER_PROFILE)
@request(camelot.GET_LOCATION)
@request(camelot.GET_SIP_REGISTER)
@request(camelot.GET_INFO_TRANSACTION)
@request(camelot.GET_ONBOARDING)
@request(camelot.SIP_CUSTOM_HEADERS)
@request(camelot.SIP_MESSAGE_DETAILED)
def decode_json_from_camelot(request, response, **kargs):
    res = None
    if response.message:
        res = json.loads(response.message)
    return res


@request(camelot.CONF_ICE_CAND)
def decode_config_ice_cand(request, response, **kargs):
    res = None
    if response.message:
        res = json.loads(response.message)
    return res


@request(camelot.PRESS_BUTTON)
def decode_press_button(request, response, **kargs):
    res = False
    if response.message and response.message.lower() == 'true':
        res = True
    return res


@request(camelot.GET_BUTTON)
@request(camelot.GET_BUTTON_BLF)
@request(camelot.GET_SIP_CALL_FEATURES)
@request(camelot.GET_IPPS_MULTIMEDIA)
@request(camelot.GET_IPPS_RTP_STREAM)
@request(camelot.GET_CONN_INFO)
def decode_ordered_json_camelot(request, response, **kargs):
    res = None
    if response.message:
        return decode_helper.jsonify_string(response.message)


@request(camelot.GET_CALL_CRYPTO_INFO)
def decode_get_call_crypto_info(request, response, **kargs):
    res = response.message
    if res.count('tag ') > 1:
        ret = []
        out_lines = decode_helper.complex_parse_return_lines(res)
        for line in out_lines:
            record = decode_helper.complex_parse(line[1:-1])
            ret.append(record)
        return ret
    elif res:
        return decode_helper.complex_parse(response.message)
    return None


@request(camelot.GET_SIP_HEADER)
@request(camelot.DISP_TVS_TRUSTLIST)
def decode_get_sip_header(request, response, **kargs):
    res = response.message
    if res == '{}':
        return []
    res_list = res.split("\n")
    for idx in range(0, len(res_list)):
        if res_list[idx] == '':
            res_list.remove(res_list[idx])
    return res_list


@request(camelot.GET_INFO)
@request(camelot.GET_INFO_EXT)
@request(camelot.GET_SRST_INFO)
@request(camelot.GET_CAPF_INFO)
@request(camelot.GET_INFO_EXT_CLEAR_MWI)
@request(camelot.GET_CALL_STATS)
@request(camelot.GET_FAX_STATS)
@request(camelot.HTTP_QUERY_RESPONSE)
@request(camelot.VVM_QUERY_RESPONSE)
@request(camelot.GET_IM_INFO)
@request(camelot.GET_IMP_INFO)
@request(camelot.GET_RTCP_STREAM_INFO)
@request(camelot.GET_SERVICE_INFO_EXT)
@request(camelot.GET_TRANSPORT_INFO)
@request(camelot.GET_MOBILE_IDENTITY)
@request(camelot.GET_UNITY_INFO)
@request(camelot.DISP_TVS_CACHE)
@request(camelot.GET_TVS_SERVERSTATS)
@request(camelot.GET_TVS_INFO)
@request(camelot.GET_OAUTH_INFO)
def decode_detail_info(request, response, **kargs):
    ret = None
    if response.message:
        ret = decode_helper.complex_parse(response.message)
    return ret


@request(camelot.CMSTATS)
def decode_cmstats(request, response, **kargs):
    ret = None
    if response.message:
        ret = decode_helper.parse_cmstats(response.message)
    return ret


@request(camelot.GET_TFTP_INFO)
def decode_get_tftp_info(request, response, **kargs):
    ret = None
    if response.message:
        ret = decode_helper.complex_parse(response.message,
                                          camelot.GET_TFTP_INFO)
    return ret


@request(camelot.GET_RPID)
def decode_rpid_info(request, response, **kargs):
    ret = None
    if response.message:
        ret = eval(response.message)
    return ret


@request(camelot.GET_CALL_HISTORY)
def decode_call_history_info(request, response, **kargs):
    ret = None
    if response.message:
        ret = decode_helper.parse_list_of_dict(response.message)
    return ret


@request(camelot.GET_STREAM_INFO)
@request(camelot.GET_TVS_CLIENTSTATS)
def decode_get_stream_info(request, response, **kargs):
    ret = None
    if response.message:
        ret = decode_helper.complex_parse_stream_info(response.message)
    return ret


@request(camelot.GET_CONFID_LIST)
def decode_get_confid_list(request, response, **kargs):
    ret = []
    if hasattr(response, 'message') and response.message:
        ret = decode_helper.parse_get_confid_list(response.message)
    return ret


@request(camelot.GET_CALLS)
@request(camelot.GET_CONF_CALLS)
def decode_get_calls(request, response, **kargs):
    ret = []
    if hasattr(response, 'message') and response.message:
        ret = decode_helper.parse_getcalls(response.message)
    return ret


@request(camelot.GET_LINES)
def decode_get_lines(request, response, **kargs):
    ret = None
    if hasattr(response, 'message') and response.message:
        ret = decode_helper.parse_get_lines(response.message)
    return ret


@request(camelot.GET_STREAMS)
@request(camelot.GET_CONF_STREAMS)
def decode_get_streams(request, response, **kargs):
    ret = None
    if hasattr(response, 'message') and response.message:
        ret = decode_helper.parse_get_streams(response.message)
    return ret


@request(camelot.LOG_MASK)
@request(camelot.LOG_DIR)
@request(camelot.LOG_FILESZ)
@request(camelot.LOG_MAX_FILES)
@request(camelot.LOG_FILE_PREFIX)
@request(camelot.LOG_BOOKMARK)
def decode_log_msg(request, response, **kargs):
    ret = None
    if hasattr(response, 'message') and response.message:
        if request == camelot.LOG_MASK and '*' in response.message:
            ret = decode_helper.parse_logmask(response.message)
        else:
            ret = response.message
    return ret


@request(camelot.GET_CALL_INFO)
@request(camelot.GET_SERVICE_INFO)
@request(camelot.GET_XULPFECUC_INFO)
def decode_get_call_info(request, response, **kargs):
    ret = None
    if hasattr(response, 'message') and response.message:
        ret = decode_helper.parse_info(response.message, request)
    return ret


@request(camelot.GET_CALL_INFO_EXT)
@request(camelot.GET_STREAM_INFO_EXT)
@request(camelot.GET_CAS_LLSA_INFO)
def decode_call_info_ext(request, response, **kargs):
    ret = None
    if hasattr(response, 'message') and response.message:
        ret = decode_helper.detailed_parse_char_by_char(response.message)
    return ret


@request(camelot.GET_SSS_LIST)
@request(camelot.GET_CALL_TIME_STATS)
def decode_detailed_info(request, response, **kargs):
    ret = None
    if hasattr(response, 'message') and response.message:
        ret = decode_helper.parse_detailed(response.message)
    return ret


@request(camelot.START_DTMF_DETECTOR)
@request(camelot.STOP_DTMF_DETECTOR)
@request(camelot.START_DTMF_PLAYER)
@request(camelot.STOP_DTMF_PLAYER)
@request(camelot.START_MEDIA_EVENTS)
@request(camelot.STOP_MEDIA_EVENTS)
@request(camelot.START_MEDIA_PLAYER)
@request(camelot.STOP_MEDIA_PLAYER)
@request(camelot.START_MEDIA_RECORDER)
@request(camelot.STOP_MEDIA_RECORDER)
@request(camelot.START_PROMPT_DETECTOR)
@request(camelot.STOP_PROMPT_DETECTOR)
@request(camelot.STOP_SHARE)
@request(camelot.START_SHARE)
@request(camelot.START_TONE_DETECTOR)
@request(camelot.STOP_TONE_DETECTOR)
@request(camelot.START_CADENCE_DETECTOR)
@request(camelot.STOP_CADENCE_DETECTOR)
@request(camelot.START_TONE_PLAYER)
@request(camelot.STOP_TONE_PLAYER)
@request(camelot.START_TRAFFIC_PLAYER)
@request(camelot.STOP_TRAFFIC_PLAYER)
@request(camelot.ESCALATE)
@request(camelot.DEESCALATE)
@request(camelot.UPDATE_CALL)
@request(camelot.XMPP_CLOSE_IM)
@request(camelot.EMLOGOUT)
@request(camelot.REFRESH_TEMPLATE_MESSAGE)
@request(camelot.MOVE_TO_MOBILE)
@request(camelot.DIAL_VIA_OFFICE)
@request(camelot.DELETE_SIP_MESSAGES)
@request(camelot.SEND_TONES)
@request(camelot.DETECT_TONES)
@request(camelot.SETUP_LINE)
@request(camelot.CHANGE_HEADSET_STATUS)
@request(camelot.SEND_DTMF)
@request(camelot.SETUP_FAX_LINE)
@request(camelot.SETUP_FAX_CALL_OPTIONS)
@request(camelot.SET_EPTIMING)
@request(camelot.HEADSET_CC_AGENTSTATE)
def decode_generic_commands(request, response, **kargs):
    ret = False
    if hasattr(response, 'message') and response.message:
        if int(response.message) == 1:
            ret = True
    return ret


@request(camelot.DISABLE_AUTO_CELL_PICKUP)
@request(camelot.GET_AUTO_CELL_PICKUP_DELAY)
@request(camelot.GET_AUTO_CELL_PICKUP_STATUS)
@request(camelot.ENABLE_AUTO_CELL_PICKUP)
@request(camelot.GET_AUTO_CONFERENCE_MODE)
@request(camelot.GET_AUTO_CONFERENCE_STATUS)
@request(camelot.GET_AUTO_CONFERENCE_TALK_TIME)
@request(camelot.GET_AUTO_CONFERENCE_TARGET)
@request(camelot.GET_AUTO_DIAL_CALLED_LIST)
@request(camelot.GET_AUTO_DIAL_EVENT)
@request(camelot.GET_AUTO_DIAL_STATUS)
@request(camelot.PLACE_CALL)
@request(camelot.REJECT)
@request(camelot.ENABLE_AUTO_ANSWER)
@request(camelot.DISABLE_AUTO_ANSWER)
@request(camelot.AUTO_ANSWER_INFO)
@request(camelot.ENABLE_AUTO_DISCONNECT)
@request(camelot.DISABLE_AUTO_DISCONNECT)
@request(camelot.AUTO_DISCONNECT_DELAY)
@request(camelot.AUTO_DISCONNECT_STATUS)
@request(camelot.ENABLE_AUTO_DIAL)
@request(camelot.DISABLE_AUTO_DIAL)
@request(camelot.ENABLE_AUTO_CONFERENCE)
@request(camelot.DISABLE_AUTO_CONFERENCE)
@request(camelot.ENABLE_AUTO_TRANSFER)
@request(camelot.DISABLE_AUTO_TRANSFER)
@request(camelot.GET_AUTO_TRANSFER_MODE)
@request(camelot.GET_AUTO_TRANSFER_STATUS)
@request(camelot.GET_AUTO_TRANSFER_TALK_TIME)
@request(camelot.GET_AUTO_TRANSFER_TARGET)
@request(camelot.ENABLE_AUTO_PARK)
@request(camelot.DISABLE_AUTO_PARK)
@request(camelot.ENABLE_AUTO_PARK_RET)
@request(camelot.DISABLE_AUTO_PARK_RET)
@request(camelot.ENABLE_AUTO_RESUME)
@request(camelot.DISABLE_AUTO_RESUME)
@request(camelot.GET_AUTO_RESUME_HOLD_TIME)
@request(camelot.GET_AUTO_RESUME_STATUS)
@request(camelot.LOAD_SSS)
@request(camelot.ENABLE_AUTO_SSS)
@request(camelot.PLACE_SCRIPT)
@request(camelot.SET_CLIENT_DATA)
@request(camelot.SET_CLIENT_DESC)
@request(camelot.DND)
@request(camelot.REFRESH_REGISTER)
@request(camelot.INITIAL_REGISTER)
@request(camelot.REFRESH_SUBSCRIBE)
@request(camelot.GET_METHODS)
@request(camelot.RELEASE_CALLS)
@request(camelot.RELEASE_STREAMS)
@request(camelot.START_BLF_STATUS)
@request(camelot.STOP_BLF_STATUS)
@request(camelot.SET_TRAFFIC)
@request(camelot.OFFHOOK)
@request(camelot.NEWCALL)
@request(camelot.ONHOOK)
@request(camelot.SELECT_LINE)
@request(camelot.SELECT_PLK)
@request(camelot.DIAL_VIA_OFFICE)
@request(camelot.DMC_HANDIN)
@request(camelot.BLIND_TRANSFER)
@request(camelot.CME_HW_CONFERENCE)
@request(camelot.PARK)
@request(camelot.PICKUP)
@request(camelot.GPICKUP)
@request(camelot.CELL_PICKUP)
@request(camelot.OPICKUP)
@request(camelot.RMLSTC)
@request(camelot.MEETME)
@request(camelot.REDIAL)
@request(camelot.CFWDALL)
@request(camelot.IDIVERT)
@request(camelot.BARGE)
@request(camelot.CBARGE)
@request(camelot.SELECT)
@request(camelot.PRIVACY)
@request(camelot.JOIN)
@request(camelot.DIRECT_TRANSFER)
@request(camelot.CALL_BACK)
@request(camelot.CONFLIST)
@request(camelot.HLOG)
@request(camelot.LIVE_RECORD)
@request(camelot.RECORD)
@request(camelot.STOP_RECORD)
@request(camelot.TRANSFER_VM)
@request(camelot.LOGIN)
@request(camelot.START_FAX_SEND)
@request(camelot.START_FAX_RECEIVE)
@request(camelot.RELEASE_CALLREF)
@request(camelot.RELEASE_STREAM_REF)
@request(camelot.INTERCOM)
@request(camelot.TALK_BACK)
@request(camelot.MOVE)
@request(camelot.ENABLE_AUTO_CALL_GUARD)
@request(camelot.DISABLE_AUTO_CALL_GUARD)
@request(camelot.GET_AUTO_CALL_GUARD_STATUS)
@request(camelot.GET_AUTO_CALL_GUARD_DELAY)
@request(camelot.ENABLE_AUTO_PATH_CONF)
@request(camelot.DISABLE_AUTO_PATH_CONF)
@request(camelot.GET_AUTO_PATH_CONF_STATUS)
@request(camelot.GET_AUTO_PATH_CONF_DELAY)
@request(camelot.GET_AUTO_PATH_CONF_MODE)
@request(camelot.ENABLE_AUTO_RECORD)
@request(camelot.DISABLE_AUTO_RECORD)
@request(camelot.GET_AUTO_RECORD_STATUS)
@request(camelot.GET_AUTO_RECORD_PREFIX)
@request(camelot.ENABLE_AUTO_HOLD)
@request(camelot.DISABLE_AUTO_HOLD)
@request(camelot.GET_AUTO_HOLD_STATUS)
@request(camelot.GET_AUTO_HOLD_HOLD_TIME)
@request(camelot.GET_AUTO_HOLD_TALK_TIME)
@request(camelot.DISABLE_AUTO_SELECT_JOIN)
@request(camelot.ENABLE_AUTO_SELECT_JOIN)
@request(camelot.GET_AUTO_SELECT_JOIN_CALLED_LIST)
@request(camelot.GET_AUTO_SELECT_JOIN_DELAY)
@request(camelot.GET_AUTO_SELECT_JOIN_MODE)
@request(camelot.GET_AUTO_SELECT_JOIN_NO_OF_CALLS)
@request(camelot.GET_AUTO_SELECT_JOIN_STATUS)
@request(camelot.GET_AUTO_SELECT_JOIN_TIME_OUT)
@request(camelot.GET_AUTO_SELECT_JOIN_TIME_OUT_ACTION)
@request(camelot.ENABLE_AUTO_RELEASE)
@request(camelot.DISABLE_AUTO_RELEASE)
@request(camelot.AUTO_RELEASE_STATUS)
@request(camelot.ENABLE_AUTO_VOICE)
@request(camelot.DISABLE_AUTO_VOICE)
@request(camelot.ENABLE_AUTO_FAX)
@request(camelot.DISABLE_AUTO_FAX)
@request(camelot.GET_AUTO_FAX_MODE)
@request(camelot.GET_AUTO_FAX_URL)
@request(camelot.GET_AUTO_FAX_STATUS)
@request(camelot.ENABLE_AUTO_EM_SERVICE)
@request(camelot.DISABLE_AUTO_EM_SERVICE)
@request(camelot.GET_AUTO_EM_STATUS)
@request(camelot.ENABLE_AUTO_SCRIPT)
@request(camelot.DISABLE_AUTO_SCRIPT)
@request(camelot.GET_AUTO_SCRIPT_STATUS)
@request(camelot.GET_AUTO_SCRIPT_SCRIPT)
@request(camelot.ENABLE_AUTO_MOVE)
@request(camelot.DISABLE_AUTO_MOVE)
@request(camelot.GET_AUTO_MOVE_DISPLAY)
@request(camelot.ENABLE_AUTO_TRAFFIC)
@request(camelot.DISABLE_AUTO_TRAFFIC)
@request(camelot.GET_AUTO_TRAFFIC_STATUS)
@request(camelot.GET_AUTO_TRAFFIC_MODE)
@request(camelot.DTMF_CONFERENCE)
@request(camelot.DTMF_DUST)
@request(camelot.DTMF_EXCLUSIVE_HOLD)
@request(camelot.DTMF_HOLD)
@request(camelot.DTMF_RESUME)
@request(camelot.DTMF_TRANSFER)
@request(camelot.GET_CONTENT_BODY)
@request(camelot.GET_SERVICES_URLS)
@request(camelot.BLFCALLPARK)
@request(camelot.EMSERVICE)
@request(camelot.SSO_LOGIN)
@request(camelot.SET_REINVITE_RESPONSE)
@request(camelot.EXEC_MEDIATOR_CMD)
@request(camelot.START_RAW_EVENTS)
@request(camelot.STOP_RAW_EVENTS)
@request(camelot.FLASH)
@request(camelot.CREATE_TONE_SEQUENCE)
@request(camelot.SET_PREF_MODE)
@request(camelot.SET_CALL_TYPE)
@request(camelot.SET_CALL_SUBJECT)
@request(camelot.SEND_USER_ANSWER)
@request(camelot.GET_TOKEN)
@request(camelot.ENABLE_AUTO_PATH_CONF_VIDEO)
@request(camelot.GET_HLOG_STATUS)
@request(camelot.SET_CUSTOM_DATA)
@request(camelot.GET_CUSTOM_DATA)
@request(camelot.CREATE_TEMPLATE_MSG)
@request(camelot.CTI_SEND_DTMF)
@request(camelot.START_DETECT_SILENCE)
@request(camelot.CTI_CLEAR_RESPONSE)
@request(camelot.SEND_VOICE)
@request(camelot.STOP_SENDING)
@request(camelot.RECORD_VOICE)
@request(camelot.RESET_TVS_CACHE)
def decode_place_call(request, response, **kargs):
    ret = None
    if hasattr(response, 'message') and response.message:
        ret = response.message
    return ret


@request(camelot.GET_AUTO_PARK)
@request(camelot.GET_AUTO_PARK_RET)
def decode_get_auto_park(request, response, **kargs):
    ret = None
    if hasattr(response, 'message') and response.message:
        ret = json.loads(response.message)
    return ret


@request(camelot.SEND_RAW_REQUEST)
@request(camelot.VERIFY_REQ_SEND_RESP)
@request(camelot.REMOVE_INACTION_OBJ)
def decode_raw_messages(request, response, **kargs):
    ret = False
    if hasattr(response, 'message') and response.message == '1':
        ret = True
    return ret


@request(camelot.GET_SIP_MESSAGES)
@request(camelot.GET_SIP_HEADERS)
@request(camelot.GET_CONTENT_BODY_LIST)
def decode_sip_messages(request, response, **kargs):
    ret = (response.message)
    if ret:
        ret = response.message.replace("{", "")
        ret = ret.replace("}", "")
        if request == camelot.GET_SIP_HEADERS:
            ret = ret.strip()
        else:
            ret = ret.strip().split(' ')
    return ret


@request(camelot.GET_BUDDY_LIST)
def decode_buddy_list(request, response, **kargs):
    ret = (response.message)
    if ret:
        if "{" not in ret:
            return ret
        ret = response.message.replace("{", "")
        ret = ret.replace("}", "")
        ret = ret.split(' ')
    return ret


@request(camelot.GET_BUDDIES_BY_GROUP)
@request(camelot.SHOW_GROUPS)
def decode_buddy_grp_list(request, response, **kargs):
    ret = (response.message)
    if ret:
        ret = response.message.replace("{", "")
        ret = ret.replace("}", "")
        ret = ret.split(',')
    return ret


@request(camelot.ANSWER_CALL)
def decode_answer_call(request, response, **kargs):
    ret = False
    if hasattr(response, 'message') and response.message:
        if int(response.message) == 1:
            ret = True
    return ret


@request(camelot.START_USER_EVENTS)
@request(camelot.STOP_USER_EVENTS)
@request(camelot.STOP_TRACE_EVENTS)
@request(camelot.START_TRANSPORT_EVENTS)
@request(camelot.STOP_TRANSPORT_EVENTS)
@request(camelot.START_STATION_EVENTS)
@request(camelot.STOP_STATION_EVENTS)
def decode_generic_events(request, response, **kargs):
    ret = False
    if hasattr(response, 'message') and response.message:
        if int(response.message) == 1:
            ret = True
    return ret


@request(camelot.STOP_STREAM_EVENTS)
@request(camelot.START_STREAM_EVENTS)
@request(camelot.START_CALL_EVENTS)
@request(camelot.STOP_CALL_EVENTS)
@request(camelot.START_CALLBACK_EVENTS)
@request(camelot.STOP_CALLBACK_EVENTS)
@request(camelot.START_INFO_EVENTS)
@request(camelot.STOP_INFO_EVENTS)
@request(camelot.CALL_INFO_EVENT)
@request(camelot.STREAM_INFO_EVENT)
@request(camelot.TRANSPORT_INFO_EVENT)
@request(camelot.CM)
def decode_info_events(request, response, **kargs):
    return True


@request(camelot.END_CALL)
@request(camelot.HOLD)
@request(camelot.RESUME)
@request(camelot.HEDGE_REVOKE_OAUTH)
@request(camelot.FAX_SWITCHTO)
@request(camelot.START_CAPF)
@request(camelot.STOP_CAPF)
@request(camelot.TRANSFER)
@request(camelot.CONFERENCE)
@request(camelot.DIAL)
@request(camelot.ISENDPOINTBCGREADY)
@request(camelot.SEND_REINVITE)
@request(camelot.SEND_NON_INVITE)
@request(camelot.CLEAR_INACTIVE_CONFERENCE)
@request(camelot.CLEAR_CUSTOM_HEADERS)
@request(camelot.GET_CONFERENCE_INFO)
@request(camelot.REMOVE_CONF_PARTICIPANT)
def decode_control_msg(request, response, **kargs):
    ret = False
    if hasattr(response, 'message') and response.message:
        if int(response.message) == 1:
            ret = True
    return ret


@request(camelot.GET_URIS)
def decode_get_uris(request, response, **kargs):
    ret = {}
    if hasattr(response, 'message') and response.message:
        if '{' in response.message:
            ret = decode_helper.parse_get_uris(response.message)
        else:
            ret = response.message
    return ret


def _parse_compat_versions(message):
    output = message.strip()
    pat = re.compile(r'{[\w\s.:@]*}')
    attribs = re.findall(pat, output)
    line_list = {}
    for attr in attribs:
        attr = attr.strip()
        value = attr[attr.index('{') + 1:attr.index('}')]
        arr = value.split(' ')
        if arr and len(arr) == 2:
            line_list[arr[0]] = arr[1]
    return line_list


def error_response(request, response, **kargs):
    if hasattr(response, 'message') and response.message:
        raise camelot.CamelotError(response.message)
    else:
        raise camelot.CamelotError('Recevied error response'
                                   ' from the Camelot[%s]' % vars(response))


def invalid_request(request, responce, **kargs):
    log.warning('Invalid Request %s to Decode' % request)


def decode(req_type, request, response, **kargs):
    log.debug(
        'Request for decoding response:'
        '\n\tType: {}'
        '\n\tRequest: {}'
        '\n\tResponse: {}'
        '\n\tResponse Vars: {}'
        '\n\tkargs: {}'.format(
            req_type, request, response, vars(response), kargs)
    )
    ack = 'A'
    if hasattr(response, 'ack'):
        ack = response.ack
    if ack == 'A' or req_type != 'ep':
        output_format = kargs.get('output_format')
        srv_resp = response.message
        json_ptrn_chk = any(i for i in ['{', '['] if i in srv_resp)
        if output_format == 'json' and json_ptrn_chk:
            try:
                log.debug("JSON decoding.....")
                if request not in camelot.non_json_supported_commands:
                    return decode_helper.jsonify_string(srv_resp)
                else:
                    return commands.get(request, invalid_request)(
                        request, response, **kargs)
            except Exception as e:
                log.warning('Decoding failed. Falling '
                            'back to non-json {}'.format(e))
                return commands.get(request, invalid_request)(
                    request, response, **kargs)
        elif request in [camelot.GET_CALLS,
                         camelot.GET_STREAMS,
                         camelot.GET_LINES]:
            return []
        else:
            return commands.get(request, invalid_request)(
                request, response, **kargs)
    else:
        return error_response(request, response, **kargs)
