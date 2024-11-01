'''
Created on 16-Sep-2013

@author: smaturi
'''
import camelot
from camelot.encoder.encoder_helper import CamelotEncodeHelper
from camelot import camlogger


log = camlogger.getLogger(__name__)
commands = {}
encode_helper = CamelotEncodeHelper()


def request(cmd):
    log.debug("request for: %s" % cmd)

    def wrap(fn):
        log.debug('wrap %s' % fn)
        commands[cmd] = fn
        return fn
    return wrap


@request(camelot.LOAD_SSS)
def encode_load_sss(request, *args, **kwargs):
    ret = encode_helper.get_load_sss_msg(*args, **kwargs)
    return ret


@request(camelot.UNLOAD_SSS)
@request(camelot.GET_SSS_LIST)
@request(camelot.GET_SSS_LOAD_STATE)
@request(camelot.GET_SSS_SCRIPT)
def encode_control_sss(request, *args, **kwargs):
    ret = encode_helper.get_control_sss_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_SSS)
@request(camelot.PLACE_SCRIPT)
@request(camelot.GET_SCRIPT_INFO)
def encode_invoke_sss(request, *args, **kwargs):
    ret = encode_helper.get_invoke_sss_msg(request, *args, **kwargs)
    return ret


@request(camelot.NEW_ENDPOINT)
def encode_new_endpont(request, *args, **kwargs):
    # _validate_new_endpont(*args, **kwargs)
    ret = encode_helper.get_endpoint_create_msg(*args, **kwargs)
    return ret


@request(camelot.ATTACH_ENDPOINT)
def encode_attach_endpoint(request, *args, **kwargs):
    ret = encode_helper.get_attach_endpoint_msg(*args, **kwargs)
    return ret


@request(camelot.GET_ENDPOINT)
def encode_get_endpoint(request, *args, **kwargs):
    ret = encode_helper.get_endpoint_msg(*args, **kwargs)
    return ret


@request(camelot.GET_BUTTON)
@request(camelot.GET_BUTTON_BLF)
def encode_get_button_request(request, *args, **kwargs):
    ret = encode_helper.get_button_msg(request, *args, **kwargs)
    return ret


@request(camelot.PRESS_BUTTON)
def encode_press_button_request(request, *args, **kwargs):
    ret = encode_helper.press_button_msg(request, *args, **kwargs)
    return ret


@request(camelot.CONFIG)
def encode_config(request, *args, **kwargs):
    ret = encode_helper.get_config_msg(*args, **kwargs)
    return ret


@request(camelot.SHOW_VVM_IDS)
@request(camelot.SHOW_VVM_INFO)
@request(camelot.FETCH_VVM)
@request(camelot.PLAY_VVM)
@request(camelot.DELETE_VVM)
@request(camelot.SEND_VVM)
@request(camelot.RECORD_VVM)
@request(camelot.RUN_CONVERSATION)
@request(camelot.ADD_RECIPIENT_VVM)
def encode_vvm_request(request, *args, **kwargs):
    ret = encode_helper.get_vvm_msg(request, *args, **kwargs)
    return ret


@request(camelot.INIT)
@request(camelot.RELEASE_EP)
@request(camelot.IN_SERVICE)
@request(camelot.CLIENT_SUSPEND)
@request(camelot.CLIENT_FOREGROUND)
@request(camelot.UNINIT)
@request(camelot.OUT_OF_SERVICE)
@request(camelot.GET_INFO)
@request(camelot.GET_HLOG_STATUS)
@request(camelot.GET_UNITY_INFO)
@request(camelot.SEND_LOCATION_INFO)
@request(camelot.GET_BFCP_INFO)
@request(camelot.GET_CALL_CRYPTO_INFO)
@request(camelot.GET_INFO_EXT)
@request(camelot.GET_SRST_INFO)
@request(camelot.GET_LINES)
@request(camelot.GET_CALLS)
@request(camelot.GET_CALL_INFO)
@request(camelot.CTI_GET_RESPONSE_STATUS)
@request(camelot.START_STATION_EVENTS)
@request(camelot.STOP_STATION_EVENTS)
# call events
@request(camelot.STOP_CALL_EVENTS)
@request(camelot.START_CALL_EVENTS)
@request(camelot.STOP_CALLBACK_EVENTS)
@request(camelot.START_CALLBACK_EVENTS)
# stream events
@request(camelot.STOP_STREAM_EVENTS)
@request(camelot.START_STREAM_EVENTS)
# userevents
@request(camelot.START_USER_EVENTS)
@request(camelot.STOP_USER_EVENTS)
@request(camelot.ISENDPOINTBCGREADY)
@request(camelot.GET_CLIENT_DATA)
@request(camelot.GET_CLIENT_DESC)
@request(camelot.GET_CALL_SUBJECT)
@request(camelot.GET_METHODS)
@request(camelot.GET_BLF_INFO)
@request(camelot.LOGIN)
@request(camelot.GEN_CERT_KEY)
@request(camelot.GET_CERT_INFO)
@request(camelot.GET_HEDGE_INFO)
@request(camelot.GET_HEADSET)
@request(camelot.GET_HEADSET_SERVICES)
@request(camelot.GET_HEADSET_CC_AGENTSTATE)
@request(camelot.HTTP_RESPONSE)
@request(camelot.GET_TOKEN)
@request(camelot.GET_EDGE_INFO)
@request(camelot.GET_VMWS_INFO)
@request(camelot.GET_SUPPORTED_CONVERSATION_INFO)
@request(camelot.GET_IMP_INFO)
@request(camelot.GET_SERVICE_INFO)
@request(camelot.GET_SERVICE_INFO_EXT)
@request(camelot.GET_SERVICES_URLS)
@request(camelot.GET_TRANSPORTS)
@request(camelot.INITIAL_REGISTER)
@request(camelot.GET_UDS_INFO)
@request(camelot.GET_SECURE_UDS_USERS_ACCESS_URL_INFO)
@request(camelot.GET_WEB_SERVICE_INFO)
@request(camelot.GET_INFO_EXT_CLEAR_MWI)
@request(camelot.GET_TFTP_INFO)
@request(camelot.GET_MOBILE_IDENTITY)
@request(camelot.GET_CONFID_LIST)
@request(camelot.CLEAR_INACTIVE_CONFERENCE)
@request(camelot.STOP_CAPF)
@request(camelot.GET_CAPF_INFO)
@request(camelot.GET_CALL_HISTORY)
@request(camelot.GET_CONN_INFO)
@request(camelot.GET_CUSTOM_DATA)
@request(camelot.GET_SINGLE_BUTTON_BARGE)
@request(camelot.GET_SIP_CALL_FEATURES)
@request(camelot.GET_ICE_CONFIG)
@request(camelot.GET_TURN_CONFIG)
@request(camelot.GET_DEVICE_CONFIG)
@request(camelot.GET_UDS_USER)
@request(camelot.GET_JABBER_PROFILE)
@request(camelot.GET_LOCATION)
@request(camelot.GET_SIP_REGISTER)
@request(camelot.GET_INFO_TRANSACTION)
@request(camelot.GET_ONBOARDING)
@request(camelot.GET_OAUTH_INFO)
@request(camelot.GET_CONFERENCE_INFO)
@request(camelot.REMOVE_CONF_PARTICIPANT)
def encode_control_msg(request, *args, **kwargs):
    ret = encode_helper.get_control_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_TVS_INFO)
@request(camelot.DISP_TVS_CACHE)
@request(camelot.DISP_TVS_TRUSTLIST)
@request(camelot.RESET_TVS_CACHE)
@request(camelot.GET_TVS_CLIENTSTATS)
@request(camelot.GET_TVS_SERVERSTATS)
def encode_control_msg(request, *args, **kwargs):
    ret = encode_helper.get_control_msg(request, *args, **kwargs)
    return ret


@request(camelot.LOG_MASK)
@request(camelot.LOG_DIR)
@request(camelot.LOG_FILESZ)
@request(camelot.LOG_MAX_FILES)
@request(camelot.LOG_FILE_PREFIX)
@request(camelot.LOG_BOOKMARK)
def encode_log_msg(request, *args, **kwargs):
    ret = encode_helper.get_log_msg(request, *args, **kwargs)
    return ret


@request(camelot.CREATE_TONE_SEQUENCE)
def encode_tone_seq(request, *args, **kwargs):
    ret = encode_helper.get_tone_seq(request, *args, **kwargs)
    return ret


@request(camelot.IMP_QUERY_RESPONSE)
@request(camelot.IMP_CLEAR_RESPONSE)
@request(camelot.SEND_IM)
@request(camelot.IM_QUERY_RESPONSE)
@request(camelot.GET_IM_INFO)
@request(camelot.IMP_CLEAR_RESPONSE)
@request(camelot.SET_PRESENCE)
@request(camelot.GET_PRESENCE)
@request(camelot.PRESENCE_QUERY_RESPONSE)
@request(camelot.PRESENCE_CLEAR_RESPONSE)
@request(camelot.HTTP_QUERY_REQ)
@request(camelot.VVM_QUERY_RESPONSE)
@request(camelot.HTTP_QUERY_RESPONSE)
@request(camelot.HTTP_CLEAR_RESPONSE)
@request(camelot.VVM_CLEAR_RESPONSE)
@request(camelot.XMPP_CLOSE_IM)
@request(camelot.SSO_LOGIN)
def encode_imp_cmnds(request, *args, **kwargs):
    ret = encode_helper.get_imp_cmnds_msg(request, *args)
    return ret


@request(camelot.SIP_CUSTOM_HEADERS)
@request(camelot.CLEAR_CUSTOM_HEADERS)
@request(camelot.SIP_MESSAGE_DETAILED)
def encode_sip_simplified_msg(request, *args, **kwargs):
    ret = encode_helper.sip_simplified_msg_encode(request, *args)
    return ret


@request(camelot.EMSERVICE)
@request(camelot.EMLOGOUT)
def encode_em_cmnds(request, *args, **kwargs):
    ret = encode_helper.get_em_cmnds_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_CALL_STATS)
@request(camelot.GET_FAX_STATS)
def encode_call_stat_msg(request, *args, **kwargs):
    ret = encode_helper.get_call_stat_msg(request, *args)
    return ret


@request(camelot.GET_STREAMS)
def encode_get_streams(request, *args, **kwargs):
    ret = encode_helper.get_streams_msg(camelot.GET_STREAMS, *args)
    return ret


@request(camelot.GET_CONF_CALLS)
def encode_get_conf_calls(request, *args, **kwargs):
    # print 'Iam in encode_get_conf_calls', args
    ret = encode_helper.get_conf_calls_msg(camelot.GET_CONF_CALLS, *args)
    return ret


@request(camelot.GET_CONF_STREAMS)
def encode_get_conf_streams(request, *args, **kwargs):
    ret = encode_helper.get_conf_streams_msg(camelot.GET_CONF_STREAMS, *args)
    return ret


@request(camelot.PLACE_CALL)
def encode_place_call(request, *args, **kwargs):
    ret = encode_helper.get_placecall_msg(camelot.PLACE_CALL, *args, **kwargs)
    return ret


@request(camelot.DIAL)
def encode_dial(request, *args, **kwargs):
    ret = encode_helper.get_dial_msg(camelot.DIAL, *args, **kwargs)
    return ret


@request(camelot.DIAL_VIA_OFFICE)
def encode_ep_misc(request, *args, **kwargs):
    ret = encode_helper.get_ep_misc_msg(request, *args, **kwargs)
    return ret


@request(camelot.ANSWER_CALL)
@request(camelot.END_CALL)
@request(camelot.HOLD)
@request(camelot.RESUME)
@request(camelot.HEDGE_REVOKE_OAUTH)
@request(camelot.START_CAPF)
@request(camelot.GET_RTCP_STREAM_INFO)
@request(camelot.GET_STREAM_ICE)
@request(camelot.GET_CALL_INFO_EXT)
@request(camelot.GET_STREAM_INFO)
@request(camelot.GET_XULPFECUC_INFO)
@request(camelot.GET_STREAM_INFO_EXT)
@request(camelot.SET_CLIENT_DATA)
@request(camelot.SET_CLIENT_DESC)
@request(camelot.DND)
@request(camelot.ONHOOK)
@request(camelot.OFFHOOK)
@request(camelot.NEWCALL)
@request(camelot.SET_TRAFFIC)
@request(camelot.SELECT_LINE)
@request(camelot.CHANGE_HEADSET_STATUS)
@request(camelot.SELECT_PLK)
@request(camelot.ENABLE_MOBILE_CONNECT)
@request(camelot.START_BLF_STATUS)
@request(camelot.STOP_BLF_STATUS)
@request(camelot.GET_FAX_INFO)
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
@request(camelot.JOIN)
@request(camelot.DIRECT_TRANSFER)
@request(camelot.CALL_BACK)
@request(camelot.CONFLIST)
@request(camelot.FLASH)
@request(camelot.HLOG)
@request(camelot.LIVE_RECORD)
@request(camelot.RECORD)
@request(camelot.STOP_RECORD)
@request(camelot.TRANSFER_VM)
@request(camelot.RELEASE_CALLREF)
@request(camelot.RELEASE_STREAM_REF)
@request(camelot.TALK_BACK)
@request(camelot.GET_BUDDY_LIST)
@request(camelot.REJECT)
@request(camelot.MOVE_TO_MOBILE)
@request(camelot.MOVE)
@request(camelot.BLFCALLPARK)
@request(camelot.SET_PREF_MODE)
@request(camelot.SET_CALL_TYPE)
@request(camelot.SET_CALL_SUBJECT)
@request(camelot.SEND_USER_ANSWER)
@request(camelot.GET_RPID)
@request(camelot.SET_CUSTOM_DATA)
@request(camelot.GET_CAS_CALL_INFO)
@request(camelot.GET_CAS_LLSA_INFO)
@request(camelot.GET_CAS_CALL_TIME_STATISTICS)
@request(camelot.START_DETECT_SILENCE)
@request(camelot.SEND_VOICE)
@request(camelot.STOP_SENDING)
@request(camelot.RECORD_VOICE)
@request(camelot.HEADSET_CC_AGENTSTATE)
def encode_call_control_msg(request, *args, **kwargs):
    ret = encode_helper.get_call_control_msg(request, *args, **kwargs)
    return ret


@request(camelot.SHOW_GROUPS)
@request(camelot.REMOVE_ALL_BUDDIES)
def encode_request_only_msg(request, *args, **kwargs):
    ret = encode_helper.get_request_only_msg(request, *args, **kwargs)
    return ret


@request(camelot.REMOVE_GROUP)
@request(camelot.ADD_GROUP)
@request(camelot.ADD_BUDDY)
@request(camelot.GET_BUDDIES_BY_GROUP)
@request(camelot.REMOVE_BUDDY)
@request(camelot.ADD_BUDDY_TO_GROUPS)
@request(camelot.MOVE_BUDDY_TO_GROUPS)
@request(camelot.REMOVE_BUDDY_FROM_GROUPS)
def encode_buddy_msg(request, *args, **kwargs):
    ret = encode_helper.get_buddy_msg(request, *args, **kwargs)
    return ret


@request(camelot.PRIVACY)
def encode_privacy_msg(request, *args, **kwargs):
    ret = encode_helper.get_privacy_msg(request, *args, **kwargs)
    return ret


@request(camelot.EXEC_MEDIATOR_CMD)
def encode_mediator_msg(request, *args, **kwargs):
    ret = encode_helper.get_mediator_msg(request, *args, **kwargs)
    return ret


@request(camelot.START_RAW_EVENTS)
@request(camelot.STOP_RAW_EVENTS)
def encode_raw_msg(request, *args, **kwargs):
    ret = encode_helper.get_raw_msg(request, *args, **kwargs)
    return ret


@request(camelot.SEND_REINVITE)
def encode_send_reinvite_msg(request, *args, **kwargs):
    ret = encode_helper.get_sendreinvite_msg(request, *args, **kwargs)
    return ret


@request(camelot.SEND_NON_INVITE)
def encode_send_non_invite_msg(request, *args, **kwargs):
    ret = encode_helper.get_sendnoninvite_msg(request, *args, **kwargs)
    return ret


@request(camelot.SET_REINVITE_RESPONSE)
def encode_reinvite_msg(request, *args, **kwargs):
    ret = encode_helper.get_reinvite_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_SSO_STATS)
@request(camelot.GET_SSO_INFO)
def encode_sso_info_msg(request, *args, **kwargs):
    ret = encode_helper.get_sso_info_msg(request, *args, **kwargs)
    return ret


@request(camelot.TRANSFER)
@request(camelot.CONFERENCE)
def encode_transfer_msg(request, *args, **kwargs):
    ret = encode_helper.get_transfer_msg(request, *args, **kwargs)
    return ret


@request(camelot.START_INFO_EVENTS)
@request(camelot.STOP_INFO_EVENTS)
@request(camelot.CALL_INFO_EVENT)
@request(camelot.STREAM_INFO_EVENT)
@request(camelot.TRANSPORT_INFO_EVENT)
def encode_handle_info_events(request, *args, **kwargs):
    ret = encode_helper.get_info_event_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_ANSWER)
@request(camelot.DISABLE_AUTO_ANSWER)
@request(camelot.AUTO_ANSWER_INFO)
def encode_auto_answer_request(request, *args, **kwargs):
    ret = encode_helper.get_auto_answer_msg(request, *args, **kwargs)
    return ret


@request(camelot.DISABLE_AUTO_CELL_PICKUP)
@request(camelot.GET_AUTO_CELL_PICKUP_DELAY)
@request(camelot.GET_AUTO_CELL_PICKUP_STATUS)
@request(camelot.ENABLE_AUTO_CELL_PICKUP)
def encode_auto_cell_pickup_request(request, *args, **kwargs):
    ret = encode_helper.get_auto_cell_pickup_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_DISCONNECT)
@request(camelot.DISABLE_AUTO_DISCONNECT)
@request(camelot.AUTO_DISCONNECT_DELAY)
@request(camelot.AUTO_DISCONNECT_STATUS)
def encode_auto_disconnect_request(request, *args, **kwargs):
    ret = encode_helper.get_auto_disconnect_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_DIAL)
@request(camelot.DISABLE_AUTO_DIAL)
@request(camelot.GET_AUTO_DIAL_CALLED_LIST)
@request(camelot.GET_AUTO_DIAL_EVENT)
@request(camelot.GET_AUTO_DIAL_STATUS)
def encode_auto_dial_request(request, *args, **kwargs):
    ret = encode_helper.get_auto_dial_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_IPPS_MULTIMEDIA)
@request(camelot.GET_IPPS_RTP_STREAM)
def encode_ipps_request(request, *args, **kwargs):
    ret = encode_helper.get_ipps_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_CONFERENCE)
@request(camelot.DISABLE_AUTO_CONFERENCE)
@request(camelot.GET_AUTO_CONFERENCE_MODE)
@request(camelot.GET_AUTO_CONFERENCE_STATUS)
@request(camelot.GET_AUTO_CONFERENCE_TALK_TIME)
@request(camelot.GET_AUTO_CONFERENCE_TARGET)
def encode_auto_conference_request(request, *args, **kwargs):
    ret = encode_helper.get_auto_conference_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_TRANSFER)
@request(camelot.DISABLE_AUTO_TRANSFER)
@request(camelot.GET_AUTO_TRANSFER_MODE)
@request(camelot.GET_AUTO_TRANSFER_STATUS)
@request(camelot.GET_AUTO_TRANSFER_TALK_TIME)
@request(camelot.GET_AUTO_TRANSFER_TARGET)
def encode_auto_transfer_request(request, *args, **kwargs):
    ret = encode_helper.get_auto_transfer_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_PARK)
@request(camelot.DISABLE_AUTO_PARK)
@request(camelot.GET_AUTO_PARK)
def encode_auto_park_request(request, *args, **kwargs):
    ret = encode_helper.get_auto_park_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_PARK_RET)
@request(camelot.DISABLE_AUTO_PARK_RET)
@request(camelot.GET_AUTO_PARK_RET)
def encode_auto_park_ret_request(request, *args, **kwargs):
    ret = encode_helper.get_auto_park_ret_msg(request, *args, **kwargs)
    return ret


@request(camelot.START_DTMF_PLAYER)
@request(camelot.STOP_DTMF_PLAYER)
@request(camelot.START_TONE_PLAYER)
@request(camelot.STOP_TONE_PLAYER)
@request(camelot.START_TRAFFIC_PLAYER)
@request(camelot.STOP_TRAFFIC_PLAYER)
def encode_player_request(request, *args, **kwargs):
    ret = encode_helper.get_player_request(request, *args, **kwargs)
    return ret


@request(camelot.START_MEDIA_EVENTS)
@request(camelot.STOP_MEDIA_EVENTS)
@request(camelot.START_MEDIA_PLAYER)
@request(camelot.STOP_MEDIA_PLAYER)
@request(camelot.START_MEDIA_RECORDER)
@request(camelot.STOP_MEDIA_RECORDER)
def encode_media_request(request, *args, **kwargs):
    ret = encode_helper.get_media_request(request, *args, **kwargs)
    return ret


@request(camelot.STOP_SHARE)
@request(camelot.START_SHARE)
@request(camelot.STOP_RECORD)
@request(camelot.GET_TIMING_STATS)
@request(camelot.GET_TRANSPORT_INFO)
@request(camelot.REFRESH_TEMPLATE_MESSAGE)
def encode_supplementary_request(request, *args, **kwargs):
    ret = encode_helper.get_suppl_request(request, *args, **kwargs)
    return ret


@request(camelot.START_TRACE_EVENTS)
@request(camelot.STOP_TRACE_EVENTS)
def encode_trace_request(request, *args, **kwargs):
    ret = encode_helper.get_trace_request(request, *args, **kwargs)
    return ret


@request(camelot.START_TRANSPORT_EVENTS)
@request(camelot.STOP_TRANSPORT_EVENTS)
def encode_transport_request(request, *args, **kwargs):
    ret = encode_helper.get_transport_request(request, *args, **kwargs)
    return ret


@request(camelot.START_DTMF_DETECTOR)
@request(camelot.STOP_DTMF_DETECTOR)
@request(camelot.START_PROMPT_DETECTOR)
@request(camelot.STOP_PROMPT_DETECTOR)
@request(camelot.START_TONE_DETECTOR)
@request(camelot.STOP_TONE_DETECTOR)
@request(camelot.START_CADENCE_DETECTOR)
@request(camelot.STOP_CADENCE_DETECTOR)
def encode_detector_request(request, *args, **kwargs):
    ret = encode_helper.get_detector_request(request, *args, **kwargs)
    return ret


@request(camelot.DELETE_SIP_MESSAGES)
@request(camelot.GET_SIP_MESSAGES)
@request(camelot.GET_SIP_HEADERS)
@request(camelot.GET_CONTENT_BODY_LIST)
@request(camelot.GET_CONTENT_BODY)
@request(camelot.GET_SIP_HEADER)
def encode_sip_request(request, *args, **kwargs):
    ret = encode_helper.get_sip_request(request, *args, **kwargs)
    return ret


@request(camelot.SEND_RAW_REQUEST)
@request(camelot.VERIFY_REQ_SEND_RESP)
@request(camelot.CREATE_TEMPLATE_MSG)
@request(camelot.REMOVE_INACTION_OBJ)
def encode_raw_request(request, *args, **kwargs):
    ret = encode_helper.get_raw_request(request, *args, **kwargs)
    return ret


@request(camelot.DTMF_CONFERENCE)
@request(camelot.DTMF_DUST)
@request(camelot.DTMF_EXCLUSIVE_HOLD)
@request(camelot.DTMF_HOLD)
@request(camelot.DTMF_RESUME)
@request(camelot.DTMF_TRANSFER)
def encode_dtmfsuppl_request(request, *args, **kwargs):
    ret = encode_helper.get_dtmfsuppl_request(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_RESUME)
@request(camelot.DISABLE_AUTO_RESUME)
@request(camelot.GET_AUTO_RESUME_HOLD_TIME)
@request(camelot.GET_AUTO_RESUME_STATUS)
def encode_auto_resume_request(request, *args, **kwargs):
    ret = encode_helper.get_auto_resume_msg(request, *args, **kwargs)
    return ret


@request(camelot.BLIND_TRANSFER)
@request(camelot.UPDATE_CALL)
@request(camelot.ESCALATE)
@request(camelot.DEESCALATE)
@request(camelot.SEND_DTMF)
@request(camelot.FAX_SWITCHTO)
@request(camelot.CTI_SEND_DTMF)
@request(camelot.CTI_CLEAR_RESPONSE)
def encode_escalate_message(request, *args, **kwargs):
    ret = encode_helper.get_updatemedia_msg(request, *args, **kwargs)
    return ret


@request(camelot.CONFIG_HEADER)
def encode_config_header_msg(request, *args, **kwargs):
    ret = encode_helper.get_config_header_msg(request, *args, **kwargs)
    return ret


@request(camelot.REFRESH_REGISTER)
def encode_refreshregister_message(request, *args, **kwargs):
    ret = encode_helper.get_refreshregister_msg(request, *args, **kwargs)
    return ret


@request(camelot.REFRESH_SUBSCRIBE)
def encode_refreshsubscribe_message(request, *args, **kwargs):
    ret = encode_helper.get_refreshsubscribe_msg(request, *args, **kwargs)
    return ret


@request(camelot.RELEASE_CALLS)
@request(camelot.RELEASE_STREAMS)
def encode_release_message(request, *args, **kwargs):
    ret = encode_helper.get_release_calls_msg(request, *args, **kwargs)
    return ret


@request(camelot.DMC_HANDIN)
def encode_dmchandin_msg(request, *args, **kwargs):
    ret = encode_helper.get_dmc_handin_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_CALL_TIME_STATS)
def encode_get_call_time_stats(request, *args, **kwargs):
    ret = encode_helper.get_call_time_stats_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_CAS_VOICE_STATS)
def encode_get_cas_voice_stats(request, *args, **kwargs):
    ret = encode_helper.get_cas_voice_stats_msg(request, *args, **kwargs)
    return ret


@request(camelot.CONF_ICE_CAND)
def encode_get_set_ice_cands_msg(request, *args, **kwargs):
    ret = encode_helper.get_set_ice_cands_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_ICE_DETAILS)
@request(camelot.GET_ICE_INFO)
def encode_get_ice_msg(request, *args, **kwargs):
    ret = encode_helper.get_iceinfo_msg(request, *args, **kwargs)
    return ret


@request(camelot.START_FAX_SEND)
@request(camelot.START_FAX_RECEIVE)
def encode_fax_send_msg(request, *args, **kwargs):
    ret = encode_helper.get_fax_send_msg(request, *args, **kwargs)
    return ret


@request(camelot.INTERCOM)
def encode_intercom_msg(request, *args, **kwargs):
    ret = encode_helper.get_intercom_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_RTP_RX_STAT)
@request(camelot.GET_RTP_TX_STAT)
def encode_rtp_rx_msg(request, *args, **kwargs):
    ret = encode_helper.get_rtprx_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_URIS)
def encode_get_uris_msg(request, *args, **kwargs):
    ret = encode_helper.get_uris_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_USER_INFO)
def encode_get_userinfo_msg(request, *args, **kwargs):
    ret = encode_helper.get_userifo_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_CALL_GUARD)
@request(camelot.DISABLE_AUTO_CALL_GUARD)
@request(camelot.GET_AUTO_CALL_GUARD_STATUS)
@request(camelot.GET_AUTO_CALL_GUARD_DELAY)
def encode_get_auto_call_guard_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_call_guard_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_PATH_CONF)
@request(camelot.DISABLE_AUTO_PATH_CONF)
@request(camelot.GET_AUTO_PATH_CONF_STATUS)
@request(camelot.GET_AUTO_PATH_CONF_DELAY)
@request(camelot.GET_AUTO_PATH_CONF_MODE)
@request(camelot.ENABLE_AUTO_PATH_CONF_VIDEO)
def encode_get_auto_path_conf_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_pathconf_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_RECORD)
@request(camelot.DISABLE_AUTO_RECORD)
@request(camelot.GET_AUTO_RECORD_STATUS)
@request(camelot.GET_AUTO_RECORD_PREFIX)
def encode_get_auto_record_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_record_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_HOLD)
@request(camelot.DISABLE_AUTO_HOLD)
@request(camelot.GET_AUTO_HOLD_STATUS)
@request(camelot.GET_AUTO_HOLD_HOLD_TIME)
@request(camelot.GET_AUTO_HOLD_TALK_TIME)
def encode_auto_hold_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_hold_msg(request, *args, **kwargs)
    return ret


@request(camelot.GET_AUTO_SELECT_JOIN_CALLED_LIST)
@request(camelot.GET_AUTO_SELECT_JOIN_DELAY)
@request(camelot.DISABLE_AUTO_SELECT_JOIN)
@request(camelot.ENABLE_AUTO_SELECT_JOIN)
@request(camelot.GET_AUTO_SELECT_JOIN_MODE)
@request(camelot.GET_AUTO_SELECT_JOIN_NO_OF_CALLS)
@request(camelot.GET_AUTO_SELECT_JOIN_STATUS)
@request(camelot.GET_AUTO_SELECT_JOIN_TIME_OUT)
@request(camelot.GET_AUTO_SELECT_JOIN_TIME_OUT_ACTION)
def encode_auto_select_join_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_select_join_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_RELEASE)
@request(camelot.DISABLE_AUTO_RELEASE)
@request(camelot.AUTO_RELEASE_STATUS)
def encode_auto_release_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_release_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_FAX)
@request(camelot.DISABLE_AUTO_FAX)
@request(camelot.GET_AUTO_FAX_MODE)
@request(camelot.GET_AUTO_FAX_URL)
@request(camelot.GET_AUTO_FAX_STATUS)
def encode_auto_fax_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_fax_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_VOICE)
@request(camelot.DISABLE_AUTO_VOICE)
def encode_auto_voice_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_voice_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_EM_SERVICE)
@request(camelot.DISABLE_AUTO_EM_SERVICE)
@request(camelot.GET_AUTO_EM_STATUS)
def encode_auto_em_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_em_service_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_SCRIPT)
@request(camelot.DISABLE_AUTO_SCRIPT)
@request(camelot.GET_AUTO_SCRIPT_STATUS)
@request(camelot.GET_AUTO_SCRIPT_SCRIPT)
def encode_auto_script_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_script_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_MOVE)
@request(camelot.DISABLE_AUTO_MOVE)
@request(camelot.GET_AUTO_MOVE_DISPLAY)
def encode_auto_move_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_move_msg(request, *args, **kwargs)
    return ret


@request(camelot.ENABLE_AUTO_TRAFFIC)
@request(camelot.DISABLE_AUTO_TRAFFIC)
@request(camelot.GET_AUTO_TRAFFIC_STATUS)
@request(camelot.GET_AUTO_TRAFFIC_MODE)
def encode_auto_traffic_msg(request, *args, **kwargs):
    ret = encode_helper.get_auto_traffic_msg(request, *args, **kwargs)
    return ret


@request(camelot.SEND_TONES)
def encode_send_tones_msg(request, *args, **kwargs):
    ret = encode_helper.get_send_tones_msg(request, *args, **kwargs)
    return ret


@request(camelot.SET_EPTIMING)
def encode_set_eptiming_msg(request, *args, **kwargs):
    ret = encode_helper.get_set_eptiming_msg(request, *args, **kwargs)
    return ret


@request(camelot.DETECT_TONES)
def encode_detect_tone_msg(request, *args, **kwargs):
    ret = encode_helper.get_detect_tone_msg(request, *args, **kwargs)
    return ret


@request(camelot.SETUP_LINE)
def encode_setup_line_msg(request, *args, **kwargs):
    ret = encode_helper.get_setup_line_msg(request, *args, **kwargs)
    return ret


@request(camelot.SETUP_FAX_LINE)
def encode_setup_fax_line_msg(request, *args, **kwargs):
    ret = encode_helper.get_setup_fax_line_msg(request, *args, **kwargs)
    return ret


@request(camelot.SETUP_FAX_CALL_OPTIONS)
def encode_setup_fax_call_option_msg(request, *args, **kwargs):
    ret = encode_helper.get_setup_fax_call_option_msg(request, *args, **kwargs)
    return ret


@request(camelot.CM)
@request(camelot.CMSTATS)
def encode_cm_commands(request, *args, **kwargs):
    ret = encode_helper.get_cm_commands_msg(request, *args, **kwargs)
    return ret


def invalid_request(request):
    log.warning('Invalid Request "%s" to encode' % request)
    raise camelot.CamelotError('Invalid Request "%s" to encode' % request)


def _validate_new_endpont(*args, **kwargs):
    if not args:
        raise camelot.CamelotError('Invalid Arguments passed')

    if args[0] not in ['sk',
                       'skm',
                       'sks',
                       'sipx',
                       'sip',
                       'sipv',
                       'cupc',
                       'cupcd',
                       'csfd',
                       'cumc',
                       'h323',
                       'pri',
                       'cas',
                       'raw',
                       'tandbergsip',
                       'imsclient',
                       'dmc',
                       'jabber',
                       'jabberguest',
                       'jabbermobile']:
        raise camelot.CamelotError('Invalid endpoint type passed: %s' % (
            args[0]))


def encode(request, *args, **kwargs):
    log.debug("Request for encoding response")
    fn = commands.get(request, invalid_request)
    if fn == invalid_request:
        fn(request)
    else:
        return fn(request, *args, **kwargs)
