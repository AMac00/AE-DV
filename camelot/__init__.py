# Camelot Requests
import sys
from threading import RLock
from camelot import camlogger
import atexit
from camelot.utils.vapi_ei_utils import VAPIEIUtils
from enum import Enum
import threading


GET_SERVER_OS = 'server_os'
GET_SERVER_VERSION = 'server_version'
GET_COMPAT_VERSIONS = 'compat_versions'
GET_VAPIEI_VERSION = 'vapiei_version'
SERVER_EXIT = 'server_exit'
NEW_ENDPOINT = 'new_ep'
ATTACH_ENDPOINT = 'attachendpoint'
CONFIG = 'config'
INIT = 'init'
IN_SERVICE = 'inservice'
CLIENT_SUSPEND = 'client_suspend'
CLIENT_FOREGROUND = 'client_foreground'
RELEASE_EP = 'releaseep'
UNINIT = 'uninit'
OUT_OF_SERVICE = 'outofservice'
GET_INFO = 'getinfo'
GET_TFTP_INFO = 'gettftpinfo'
GET_LOCATION = 'getlocation'
GET_SIP_REGISTER = 'getsipregister'
GET_INFO_EXT = 'getinfoext'
GET_SRST_INFO = 'getsrstinfo'
GET_BFCP_INFO = 'getbfcpinfo'
GET_CALL_CRYPTO_INFO = 'getcallcryptoinfo'
GET_EDGE_INFO = 'getedgeinfo'
GET_VMWS_INFO = 'getvmwsinfo'
GET_SUPPORTED_CONVERSATION_INFO = 'getsupportedconversationsinfo'
GET_RTCP_STREAM_INFO = 'getrtcpstreaminfo'
GET_STREAM_ICE = 'getstreamice'
GET_SERVICE_INFO = 'getserviceinfo'
GET_SERVICE_INFO_EXT = 'getserviceinfoext'
GET_SERVICES_URLS = 'getservicesurls'
GET_SSO_INFO = 'getssoinfo'
GET_SSO_STATS = 'getssostats'
GET_TIMING_STATS = 'gettimingstats'
GET_IMP_INFO = 'getimpinfo'
GET_LINES = 'getlines'
GET_CALLS = 'getcalls'
GET_STREAMS = 'getstreams'
GET_CONFID_LIST = 'getconfidlist'
CLEAR_INACTIVE_CONFERENCE = 'clearinactiveconference'
GET_CONF_CALLS = 'getconfcalls'
GET_CONF_STREAMS = 'getconfstreams'
GET_STREAM_INFO = 'getstreaminfo'
GET_XULPFECUC_INFO = 'getxulpfecucinfo'
GET_STREAM_INFO_EXT = 'getstreaminfoext'
GET_CALL_INFO = 'getcallinfo'
GET_CALL_INFO_EXT = 'getcallinfoext'
GET_CUSTOM_DATA = 'getcustomdata'
SET_CUSTOM_DATA = 'setcustomdata'
GET_CALL_STATS = 'getcallstats'
PLACE_CALL = 'placecall'
DIAL = 'dial'
ANSWER_CALL = 'answer'
END_CALL = 'endcall'
END_NULL = 'null@'
HOLD = 'hold'
RESUME = 'resume'
HEDGE_REVOKE_OAUTH = 'hedgerevokeoauth'
FAX_SWITCHTO = 'faxswitchto'
START_CAPF = 'startcapf'
STOP_CAPF = 'stopcapf'
GET_CAPF_INFO = 'getcapfinfo'
TRANSFER = 'transfer'
CONFERENCE = 'conference'
SET_CLIENT_DATA = 'setclientdata'
GET_CLIENT_DATA = 'getclientdata'
GET_ENDPOINT = 'getendpoint'
SET_CLIENT_DESC = 'setclientdesc'
GET_CLIENT_DESC = 'getclientdesc'
GET_INFO_TRANSACTION = 'getinfotransaction'
GET_ONBOARDING = 'getonboarding'
# sip msg
DELETE_SIP_MESSAGES = 'deletesipmessages'
GET_SIP_MESSAGES = 'getsipmessages'
GET_SIP_HEADERS = 'getsipheaders'
GET_CONTENT_BODY_LIST = 'getcontentbodylist'
GET_CONTENT_BODY_OBJ = 'getcontentbodyobj'
GET_CONTENT_BODY = 'getcontentbody'
GET_SIP_HEADER = 'getsipheader'
# Events
CALL_INFO_EVENT = 'callinfoevent'
STREAM_INFO_EVENT = 'streaminfoevent'
TRANSPORT_INFO_EVENT = 'transportinfoevent'
START_STATION_EVENTS = 'startstationevents'
STOP_STATION_EVENTS = 'stopstationevents'
START_INFO_EVENTS = 'startinfoevents'
STOP_INFO_EVENTS = 'stopinfoevents'
START_CALL_EVENTS = 'callevent on'
STOP_CALL_EVENTS = 'callevent off'
START_CALLBACK_EVENTS = 'callbackevent on'
STOP_CALLBACK_EVENTS = 'callbackevent off'
START_STREAM_EVENTS = 'streamevent on'
STOP_STREAM_EVENTS = 'streamevent off'
START_USER_EVENTS = 'userevent on'
STOP_USER_EVENTS = 'userevent off'
START_TRACE_EVENTS = 'starttraceevents'
STOP_TRACE_EVENTS = 'stoptraceevents'
START_TRANSPORT_EVENTS = 'starttransportevents'
STOP_TRANSPORT_EVENTS = 'stoptransportevents'
GET_TRANSPORT_INFO = 'gettransportinfo'
GET_TRANSPORTS = 'gettransports'
START_TONE_DETECTOR = 'starttonedetector'
STOP_TONE_DETECTOR = 'stoptonedetector'
START_CADENCE_DETECTOR = 'startcadencedetector'
STOP_CADENCE_DETECTOR = 'stopcadencedetector'
CREATE_TONE_SEQUENCE = 'createtoneseq'
START_TONE_PLAYER = 'starttoneplayer'
STOP_TONE_PLAYER = 'stoptoneplayer'
START_TRAFFIC_PLAYER = 'starttrafficplayer'
STOP_TRAFFIC_PLAYER = 'stoptrafficplayer'
GET_UDS_INFO = 'getudsinfo'
GET_SECURE_UDS_USERS_ACCESS_URL_INFO = 'get_secure_uds_users_access_url_info'
GET_WEB_SERVICE_INFO = 'get_web_service_info'
STOP_RECORD = 'stoprecord'
ENABLE_AUTO_ANSWER = 'enableautoanswer'
DISABLE_AUTO_ANSWER = 'diableautoanswer'
AUTO_ANSWER_INFO = 'autoanswerinfo'
DEESCALATE = 'deescalate'
ESCALATE = 'escalate'
CONFIG_HEADER = 'configheader'
UPDATE_CALL = 'updatecall'
GET_INFO_EXT_CLEAR_MWI = 'getinfoext clearmwistats'

# auto commands for cell pickup
DISABLE_AUTO_CELL_PICKUP = 'disableautocellpickup'
GET_AUTO_CELL_PICKUP_DELAY = 'getautocellpickupdelay'
GET_AUTO_CELL_PICKUP_STATUS = 'getautocellpickupstatus'
ENABLE_AUTO_CELL_PICKUP = 'enableautocellpickup'
# auto dial commands
ENABLE_AUTO_DIAL = 'enableautodial'
DISABLE_AUTO_DIAL = 'disableautodial'
GET_AUTO_DIAL_CALLED_LIST = 'getautodialcalledlist'
GET_AUTO_DIAL_EVENT = 'getautodialevent'
GET_AUTO_DIAL_STATUS = 'getautodialstatus'
# auto conference commands
ENABLE_AUTO_CONFERENCE = 'enableautoconference'
DISABLE_AUTO_CONFERENCE = 'disableautoconference'
GET_AUTO_CONFERENCE_MODE = 'getautoconferencemode'
GET_AUTO_CONFERENCE_STATUS = 'getautoconferencestatus'
GET_AUTO_CONFERENCE_TALK_TIME = 'getautconferencetalktime'
GET_AUTO_CONFERENCE_TARGET = 'getautoconferencetarget'
# auto transfer commands
ENABLE_AUTO_TRANSFER = 'enableautotransfer'
DISABLE_AUTO_TRANSFER = 'disableautotransfer'
GET_AUTO_TRANSFER_MODE = 'getautotransfermode'
GET_AUTO_TRANSFER_STATUS = 'getautotransferstatus'
GET_AUTO_TRANSFER_TALK_TIME = 'getautotransfertalktime'
GET_AUTO_TRANSFER_TARGET = 'getautotransfertarget'
# auto park commands
ENABLE_AUTO_PARK = 'enableautopark'
DISABLE_AUTO_PARK = 'disableautopark'
GET_AUTO_PARK = 'getautoparkstatus'
ENABLE_AUTO_PARK_RET = 'enableautoparkretrieve'
DISABLE_AUTO_PARK_RET = 'disableautoparkretrieve'
GET_AUTO_PARK_RET = 'getautoparkretrievestatus'
# autoresume commands
ENABLE_AUTO_RESUME = 'enableautoresume'
DISABLE_AUTO_RESUME = 'disableautoresume'
GET_AUTO_RESUME_HOLD_TIME = 'getautoresumeholdtime'
GET_AUTO_RESUME_STATUS = 'getautoresumestatus'
# vvm commands
SHOW_VVM_IDS = 'showvvmids'
SHOW_VVM_INFO = 'showvvminfo'
FETCH_VVM = 'fetchvvm'
VVM_QUERY_RESPONSE = 'vvmqueryresponse'
SEND_VVM = 'sendvvm'
RECORD_VVM = 'recordvvm'
RUN_CONVERSATION = 'runconversation'
ADD_RECIPIENT_VVM = 'addrecipient'
PLAY_VVM = 'playvvm'
DELETE_VVM = 'deletevvm'
VVM_CLEAR_RESPONSE = 'vvmclearresponse'
ENABLE_AUTO_DISCONNECT = 'enableautodisconnect'
DISABLE_AUTO_DISCONNECT = 'diableautodisconnect'
AUTO_DISCONNECT_STATUS = 'autodisconnectstatus'
AUTO_DISCONNECT_DELAY = 'autodisconnectdelay'
ISENDPOINTBCGREADY = 'isendpointbcgready'
ISENDPOINTVMONREADY = 'isendpointvmonready'
SEND_REINVITE = 'sendreinvite'
SEND_NON_INVITE = 'sendnoninvitemsg'
LOAD_SSS = 'loadsss'
UNLOAD_SSS = 'unloadsss'
PLACE_SCRIPT = 'placescript'
ENABLE_AUTO_SSS = 'autosss'
GET_SSS_LOAD_STATE = 'getsssloadstate'
GET_SSS_LIST = 'getssslist'
GET_SSS_SCRIPT = 'getsssscript'
GET_SCRIPT_INFO = 'getscriptinfo'
GET_RPID = 'getrpid'
GET_CALL_HISTORY = 'get_call_history'
GET_CONN_INFO = 'get_conn_info'

DND = 'dnd'
GET_FAX_STATS = 'getfaxstats'
REFRESH_REGISTER = 'refreshregister'
INITIAL_REGISTER = 'initialregister'
REFRESH_SUBSCRIBE = 'refreshsubscribe'
GET_METHODS = 'getmethods'
GET_ALL_SUBSCRIBE_CUBE = 'getallsubscribescube'
RELEASE_CALLS = 'releasecalls'
RELEASE_STREAMS = 'releasestreams'
OFFHOOK = 'offhook'
ONHOOK = 'onhook'
NEWCALL = 'newcall'
SELECT_LINE = 'selectline'
SELECT_PLK = 'selectplk'
REJECT = 'reject'
DIAL_VIA_OFFICE = 'dialviaoffice'
SET_PREF_MODE = 'setprefmode'
SET_CALL_TYPE = 'setcalltype'
SET_CALL_SUBJECT = 'setcallsubject'
GET_CALL_SUBJECT = 'getcallsubject'
SEND_USER_ANSWER = 'senduseranswer'
GET_MOBILE_IDENTITY = 'getmobileidentity'
DMC_HANDIN = 'dmchandin'
ENABLE_MOBILE_CONNECT = 'enablemobileconnect'
GET_CALL_TIME_STATS = 'getcalltimestats'
GET_CAS_VOICE_STATS = 'getcasvoicestats'
START_BLF_STATUS = 'startblfstatus'
STOP_BLF_STATUS = 'stopblfstatus'
SET_TRAFFIC = 'settraffic'
GET_BLF_INFO = 'getblfinfo'
GET_FAX_INFO = 'getfaxinfo'
GET_ICE_INFO = 'geticeinfo'
GET_ICE_DETAILS = 'geticedetails'
BLIND_TRANSFER = 'blindtransfer'
CME_HW_CONFERENCE = 'cmehwconference'
GET_UNITY_INFO = 'getunityinfo'
PARK = 'park'
PICKUP = 'pickup'
GPICKUP = 'gpickup'
CELL_PICKUP = 'cellpickup'
OPICKUP = 'opickup'
RMLSTC = 'rmlstc'
MEETME = 'meetme'
REDIAL = 'redial'
CFWDALL = 'cfwdall'
IDIVERT = 'idivert'
BARGE = 'barge'
CBARGE = 'cbarge'
GET_SINGLE_BUTTON_BARGE = 'getsinglebuttonbarge'
GET_SIP_CALL_FEATURES = 'getsipcallfeatures'
SELECT = 'select'
PRIVACY = 'privacy'
JOIN = 'join'
DIRECT_TRANSFER = 'directtransfer'
CALL_BACK = 'callback'
CONFLIST = 'conflist'
FLASH = 'flash'
HLOG = 'hlog'
LIVE_RECORD = 'liverecord'
RECORD = 'record'
STOP_RECORD = 'stoprecord'
TRANSFER_VM = 'transfervm'
LOGIN = 'login'
START_FAX_SEND = 'startfaxsend'
START_FAX_RECEIVE = 'startfaxreceive'
RELEASE_CALLREF = 'releasecallref'
RELEASE_STREAM_REF = 'releasestreamref'
REFRESH_TEMPLATE_MESSAGE = 'refreshtemplatemessage'
MOVE_TO_MOBILE = 'movetomobile'
BLFCALLPARK = 'blfcallpark'
EXEC_MEDIATOR_CMD = "execmediatorcmd"
INTERCOM = 'intercom'
TALK_BACK = 'talkback'
MOVE = 'move'
GET_URIS = 'geturis'
GET_RTP_RX_STAT = 'getrtprxstats'
GET_RTP_TX_STAT = 'getrtptxstats'
GET_BUDDY_LIST = 'getbuddylist'
GET_BUDDIES_BY_GROUP = 'getbuddiesbygroup'
GET_UDS_USER = 'get_uds_user'
GET_JABBER_PROFILE = 'getjabberprofile'
GET_USER_INFO = 'getuserinfo'
ENABLE_AUTO_CALL_GUARD = 'enableautocallguard'
DISABLE_AUTO_CALL_GUARD = 'disableautocallguard'
GET_AUTO_CALL_GUARD_STATUS = 'getautocallguardstatus'
GET_AUTO_CALL_GUARD_DELAY = 'getautocallguarddelay'
# auto conf path command
ENABLE_AUTO_PATH_CONF = 'enableautopathconf'
DISABLE_AUTO_PATH_CONF = 'disableautopathconf'
GET_AUTO_PATH_CONF_STATUS = 'getautopathconfstatus'
GET_AUTO_PATH_CONF_DELAY = 'getautopathconfdelay'
GET_AUTO_PATH_CONF_MODE = 'getautopathconfmode'
ENABLE_AUTO_PATH_CONF_VIDEO = 'enableautopathconfvideo'
# autorecord commands
ENABLE_AUTO_RECORD = 'enableautorecord'
DISABLE_AUTO_RECORD = 'disableautorecord'
GET_AUTO_RECORD_STATUS = 'getautorecordstatus'
GET_AUTO_RECORD_PREFIX = 'getautorecordprefix'
# auto hold command
ENABLE_AUTO_HOLD = 'enableautohold'
DISABLE_AUTO_HOLD = 'disableautohold'
GET_AUTO_HOLD_HOLD_TIME = 'getautoholdholdtime'
GET_AUTO_HOLD_TALK_TIME = 'getautoholdtalktime'
GET_AUTO_HOLD_STATUS = 'getautoholdstatus'
GET_AUTO_HOLD_HOLD_TIME = 'getautoholdholdtime'
GET_AUTO_HOLD_TALK_TIME = 'getautoholdtalktime'
AUTO_SELECT_JOIN_STR = 'autoselectjoin'
ENABLE_AUTO_SELECT_JOIN = 'enableautoselectjoin'
DISABLE_AUTO_SELECT_JOIN = 'disableautoselectjoin'
GET_AUTO_SELECT_JOIN_CALLED_LIST = 'getautoselectjoincalledlist'
GET_AUTO_SELECT_JOIN_DELAY = 'getautoselectjoindelay'
GET_AUTO_SELECT_JOIN_MODE = 'getautoselectjoinmode'
GET_AUTO_SELECT_JOIN_NO_OF_CALLS = 'getautoselectjoinnoofcalls'
GET_AUTO_SELECT_JOIN_STATUS = 'getautoselectjoinstatus'
GET_AUTO_SELECT_JOIN_TIME_OUT = 'getautoselectjointimeout'
GET_AUTO_SELECT_JOIN_TIME_OUT_ACTION = 'getautoselectjointimeraction'
ENABLE_AUTO_RELEASE = 'enableautorelease'
DISABLE_AUTO_RELEASE = 'disableautorelease'
AUTO_RELEASE_STATUS = 'autoreleasestatus'
ENABLE_AUTO_FAX = 'enableautofax'
DISABLE_AUTO_FAX = 'disableautofax'
ENABLE_AUTO_VOICE = 'enableautovoice'
DISABLE_AUTO_VOICE = 'disableautovoice'
GET_AUTO_FAX_MODE = 'getautofaxmode'
GET_AUTO_FAX_URL = 'getautofaxurl'
GET_AUTO_FAX_STATUS = 'getautofaxstatus'
ENABLE_AUTO_EM_SERVICE = 'enableautoemservice'
DISABLE_AUTO_EM_SERVICE = 'disableautoemservice'
GET_AUTO_EM_STATUS = 'getautoemstatus'
ENABLE_AUTO_SCRIPT = 'enableautoscript'
DISABLE_AUTO_SCRIPT = 'disableautoscript'
GET_AUTO_SCRIPT_STATUS = 'getautoscriptstatus'
GET_AUTO_SCRIPT_SCRIPT = 'getautoscriptscript'
ENABLE_AUTO_MOVE = 'enableautomove'
DISABLE_AUTO_MOVE = 'disableautomove'
GET_AUTO_MOVE_DISPLAY = 'getautomovedisplay'
ENABLE_AUTO_TRAFFIC = 'enableautotraffic'
DISABLE_AUTO_TRAFFIC = 'disableautotraffic'
GET_AUTO_TRAFFIC_STATUS = 'getautotrafficstatus'
GET_AUTO_TRAFFIC_MODE = 'getautotrafficmode'
GEN_CERT_KEY = 'gencertkey'
GET_CERT_INFO = 'getcertinfo'
GET_HEDGE_INFO = 'gethedgeinfo'
GET_HEADSET = 'getheadset'
GET_HEADSET_SERVICES = 'getheadsetservices'
GET_HEADSET_CC_AGENTSTATE = 'get_headset_cc_agentstate'
CHANGE_HEADSET_STATUS = 'change_headset_status'
HEADSET_CC_AGENTSTATE = 'changeheadsetccagentstate'
HTTP_RESPONSE = 'httpresponse'
GET_DEVICE_CONFIG = 'getdeviceconfig'
GET_HLOG_STATUS = 'gethlogstatus'
GET_TOKEN = 'gettoken'
ADD_BUDDY = "addbuddy"
ADD_BUDDY_TO_GROUPS = "addbuddytogroups"
MOVE_BUDDY_TO_GROUPS = "movebuddytogroups"
REMOVE_BUDDY_FROM_GROUPS = "removebuddyfromgroups"
REMOVE_BUDDY = "removebuddy"
ADD_GROUP = "addgroup"
REMOVE_GROUP = "removegroup"
REMOVE_ALL_BUDDIES = "removeallbuddies"
SHOW_GROUPS = "showgroups"
SEND_IM = "sendim"
IM_CLEAR_RESPONSE = "imclearresponse"
IM_QUERY_RESPONSE = 'getimqueryresponse'
GET_PRESENCE = "getpresence"
SET_PRESENCE = "setpresence"
PRESENCE_QUERY_RESPONSE = 'presencequeryresponse'
PRESENCE_CLEAR_RESPONSE = 'presenceclearresponse'
GET_IM_INFO = "getiminfo"
IMP_QUERY_RESPONSE = "impqueryresponse"
IMP_CLEAR_RESPONSE = "impclearresponse"
HTTP_QUERY_REQ = "httpqueryreq"
HTTP_QUERY_RESPONSE = "httpqueryresponse"
HTTP_CLEAR_RESPONSE = "httpclearresponse"
XMPP_CLOSE_IM = 'closeim'
EMLOGOUT = 'emlogout'
EMSERVICE = 'emservice'
SSO_LOGIN = 'ssologin'
SET_OUTPUT_FORMAT = 'outputformat'
# dtmf commands
SET_REINVITE_RESPONSE = 'setreinviteresponse'
START_DTMF_DETECTOR = 'startdtmfdetector'
START_DTMF_PLAYER = 'startdtmfplayer'
STOP_DTMF_DETECTOR = 'stopdtmfdetector'
STOP_DTMF_PLAYER = 'stop_dtmf_player'
DTMF_CONFERENCE = 'dtmfconference'
DTMF_DUST = 'dtmfdust'
DTMF_EXCLUSIVE_HOLD = 'dtmfexclusive_hold'
DTMF_HOLD = 'dtmfhold'
DTMF_RESUME = 'dtmfresume'
DTMF_TRANSFER = 'dtmftransfer'
CTI_GET_RESPONSE_STATUS = 'get_cti_response'
CTI_CLEAR_RESPONSE = 'cticlearresponse'

GET_ICE_CONFIG = 'geticeconfig'
CONF_ICE_CAND = 'configicecandidateorder'
GET_TURN_CONFIG = 'getturnconfig'

GET_IPPS_MULTIMEDIA = 'getippsmultimedia'
GET_IPPS_RTP_STREAM = 'getippsrtpstream'
START_MEDIA_EVENTS = 'startmediaevents'
STOP_MEDIA_EVENTS = 'stopmediaevents'
START_MEDIA_PLAYER = 'startmediaplayer'
STOP_MEDIA_PLAYER = 'stopmediaplayer'
START_MEDIA_RECORDER = 'startmediarecorder'
STOP_MEDIA_RECORDER = 'stopmediarecorder'
START_PROMPT_DETECTOR = 'startpromptdetector'
STOP_PROMPT_DETECTOR = 'stoppromptdetector'
START_SHARE = 'startshare'
STOP_SHARE = 'stopshare'
START_RAW_EVENTS = 'startrawevents'
STOP_RAW_EVENTS = 'stoprawevents'

# BCG commands
NEW_BCG = 'new_bcg'
ADD_TO_BCG = 'add_to_bcg'
SET_CAMELOT_API = 'set_camelot_api'
SET_BCG = 'set_bcg'
REMOVE_FROM_BCG = 'remove_from_bcg'
GET_BCG_NAME = 'get_bcg_name'
GET_BCG_MEMBERS = 'get_bcg_members'
GET_BCG_STATE = 'get_bcg_state'
START_BCG = 'start_bcg'
STOP_BCG = 'stop_bcg'
DELETE_BCG = 'delete_bcg'
GET_BCG_INFO = 'get_bcg_info'
GET_BCG_STATS = 'get_bcg_stats'
GET_BCGS = 'get_bcgs'
# button
GET_BUTTON = 'getbutton'
GET_BUTTON_BLF = 'getbuttonblf'
PRESS_BUTTON = 'pressbutton'
# VMON commands
ADD_TO_MONITOR = 'add_to_monitor'
GET_MONITOR_INFO = 'get_monitor_info'
GET_MONITOR_MEMBERS = 'get_monitor_members'
GET_MONITORS = 'get_monitors'
RELEASE_MONITOR = 'release_monitor'
SET_MONITOR = 'set_monitor'
CLEAR_MONITOR = 'clear_monitor'
START_MONITOR = 'start_monitor'
NEW_MONITOR = 'new_monitor'
STOP_MONITOR = 'stop_monitor'
REMOVE_FROM_MONITOR = 'remove_from_monitor'
DELETE_MONITOR = 'delete_monitor'
SEND_LOCATION_INFO = 'sendlocationinfo'

SEND_TONES = 'sendtones'
SETUP_LINE = 'setupline'
DETECT_TONES = 'detecttones'
SET_EPTIMING = 'set_eptiming'
SEND_DTMF = 'senddtmf'
GET_CAS_CALL_INFO = 'getcascallinfo'
GET_CAS_LLSA_INFO = 'getcasllsainfo'
GET_CAS_CALL_TIME_STATISTICS = 'getcascalltimestatistics'
START_DETECT_SILENCE = 'startdetectsilence'
SEND_VOICE = 'sendvoice'
STOP_SENDING = 'stopsending'
RECORD_VOICE = 'recordvoice'
SETUP_FAX_LINE = 'setupfaxline'
SETUP_FAX_CALL_OPTIONS = 'setupfaxcalloptions'
CTI_SEND_DTMF = 'send_cti_dtmf'
# raw requests
SEND_RAW_REQUEST = 'rawsendrequest'
VERIFY_REQ_SEND_RESP = 'verifyRequestsendResponse'
CREATE_TEMPLATE_MSG = 'createtemplatemessage'
REMOVE_INACTION_OBJ = 'removeinactionobject'
# Sip Custom Headers
SIP_CUSTOM_HEADERS = 'sipcustomheaders'
CLEAR_CUSTOM_HEADERS = 'clearsipcustomheaders'
SIP_MESSAGE_DETAILED = 'sipmessagedetailed'
# Server-level and Endpoint-level logging
LOG_MASK = 'logmask'
LOG_DIR = 'logdir'
LOG_FILESZ = 'logfilesz'
LOG_MAX_FILES = 'maxlogfiles'
LOG_FILE_PREFIX = 'logfileprefix'
LOG_BOOKMARK = 'logbookmark'

# Simulate Failover/Fallback
CM = 'cm'
CMSTATS = 'cmstats'


# TVS Commands
GET_TVS_INFO = 'gettvsinfo'
GET_TVS_CLIENTSTATS = 'gettvsclientstats'
GET_TVS_SERVERSTATS = 'gettvsserverstats'
DISP_TVS_CACHE = 'disptvscache'
RESET_TVS_CACHE = 'resettvscache'
DISP_TVS_TRUSTLIST = 'disptvstrustlist'

# OAuth commands
GET_OAUTH_INFO = 'getoauthinfo'

GET_CONFERENCE_INFO = 'getconferenceinfo'
REMOVE_CONF_PARTICIPANT = 'removeconfparticipant'

non_json_supported_commands = [GET_SERVER_OS,
                               GET_SERVER_VERSION,
                               GET_COMPAT_VERSIONS,
                               GET_VAPIEI_VERSION,
                               CONFIG, GET_SIP_MESSAGES,
                               GET_CONTENT_BODY_LIST,
                               GET_SIP_HEADERS,
                               SET_CLIENT_DESC, GET_CLIENT_DESC]


class EpTimer:
    class EpTimerType(Enum):
        retryafter = 1
        all = 2


class Tones:
    class ToneType(Enum):
        continuousTone = 0
        multiFrequencyTone = 1
        singleTone = 2
        dualTone = 3
        all = 4
        none = 5

    class DivaMF(Enum):
        tone0 = 0
        tone1 = 1
        tone2 = 2
        tone3 = 3
        tone4 = 4
        tone5 = 5
        tone6 = 6
        tone7 = 7
        tone8 = 8
        tone9 = 9
        toneStart = 11
        toneStop = 12


class DivaFaxOptions(Enum):
    DivaFaxOptionsDefault = 0x00000000
    DivaFaxOptionDisableHighResolution = 0x00000001
    DivaFaxOptionDisableMR = 0x00000002
    DivaFaxOptionDisableMMR = 0x00000004
    DivaFaxOptionDisableECM = 0x00000008
    DivaFaxOptionEnablePolling = 0x00000100
    DivaFaxOptionRequestPolling = 0x00000200
    DivaFaxOptionReverseSession = 0x00000400
    DivaFaxOptionMultipleDocument = 0x00000800
    DivaFaxOptionEnableColor = 0x00001000
    DivaFaxOptionEnableInterrupt = 0x00010000
    DivaFaxOptionRequestInterrupt = 0x00020000


class DivaFaxMaxSpeed(Enum):
    DivaFaxMaxSpeedAutomatic = 0
    DivaFaxMaxSpeed2400 = 2400
    DivaFaxMaxSpeed4800 = 4800
    DivaFaxMaxSpeed7200 = 7200
    DivaFaxMaxSpeed9600 = 9600
    DivaFaxMaxSpeed14400 = 14400
    DivaFaxMaxSpeed33600 = 33600


class FaxProfile:
    def __init__(self):
        self.local_number = '-1'
        self.local_sub_address = '-1'
        self.local_fax_id = '-1'
        self.fax_headline = 'camelot'
        self.default_fax_speed = DivaFaxMaxSpeed.DivaFaxMaxSpeedAutomatic
        self.diva_fax_options = [DivaFaxOptions.DivaFaxOptionsDefault]


class DivaSamplingRate(Enum):
    DivaSamplingRateMin = 1250
    DivaSamplingRateNormal = 8000
    DivaSamplingRateMax = 51200


class DivaAudioFormat(Enum):
    DivaAudioFormat_aLaw8K8BitMono = 0
    DivaAudioFormat_uLaw8K8BitMono = 1
    DivaAudioFormat_PCM_8K8BitMono = 2
    DivaAudioFormat_PCM_8K16BitMono = 3
    DivaAudioFormat_GSM_610 = 10
    DivaAudioFormat_G723_6_4 = 12
    DivaAudioFormat_G723_5_3 = 13
    DivaAudioFormat_Raw_aLaw8K8BitMono = 100
    DivaAudioFormat_Raw_uLaw8K8BitMono = 101
    DivaAudioFormat_Raw_PCM_8K8BitMono = 102
    DivaAudioFormat_Raw_PCM_8K16BitMono = 103
    DivaAudioFormat_Raw_ADPCM_8K4BitMono = 104
    DivaAudioFormat_Raw_ADPCM_6K4BitMono = 105
    DivaAudioFormat_Raw_GSM_610 = 106
    DivaAudioFormat_Raw_G729 = 107
    DivaAudioFormat_Raw_ILBC = 108
    DivaAudioFormat_Raw_AMR_4_75 = 109
    DivaAudioFormat_Raw_AMR_5_15 = 110
    DivaAudioFormat_Raw_AMR_5_9 = 111
    DivaAudioFormat_Raw_AMR_6_7 = 112
    DivaAudioFormat_Raw_AMR_7_4 = 113
    DivaAudioFormat_Raw_AMR_7_95 = 114
    DivaAudioFormat_Raw_AMR_10_2 = 115
    DivaAudioFormat_Raw_AMR_12_2 = 116
    DivaAudioFormat_Raw_G723_6_4 = 212
    DivaAudioFormat_Raw_G723_5_3 = 213
    DivaAudioFormat_Raw_G722 = 214
    DivaAudioFormat_Raw_PCM_16K16Bit = 215
    DivaAudioFormat_Raw_PCM_32K16Bit = 217
    DivaAudioFormat_Raw_PCM_48K16Bit = 216


# creating enumerations using class
class AgentStatusEnum(Enum):
    '''
    :Values:
        possible values are as follows:\n
        LOGIN = 0\n
        LOGOUT = 1\n
        NOT_READY = 2\n
        READY = 3\n
        TALKING = 4\n
        WORK = 5\n
        WORK_READY = 6\n
        BUSY_OTHER = 7\n
        RESERVED = 8\n
        UNKNOWN = 9\n
        HOLD = 10\n
        ACTIVE = 11\n
        PAUSED = 12\n
        INTERRUPTED = 13\n
        RESERVED_OUTBOUND = 15\n
        RESERVED_OUTBOUND_PREVIEW = 16\n

    >>> from camelot import AgentStatusEnum
    >>> print(AgentStatusEnum.LOGIN.value)
    >>> 0
    '''
    LOGIN = 0
    LOGOUT = 1
    NOT_READY = 2
    READY = 3
    TALKING = 4
    WORK = 5
    WORK_READY = 6
    BUSY_OTHER = 7
    RESERVED = 8
    UNKNOWN = 9
    HOLD = 10
    ACTIVE = 11
    PAUSED = 12
    INTERRUPTED = 13
    RESERVED_OUTBOUND = 15
    RESERVED_OUTBOUND_PREVIEW = 16


log = camlogger.getLogger(__name__)

__camelot_servers = {}

_connections_lock = RLock()
_camelot_servers_lock = RLock()
# camlogger.basicConfig()
camlogger.enable_logging()


def __exit_handler():
    log.info('Cleaning up Camelot-pi')
    stop_all()
    log.info('Exiting Camelot-pi')


atexit.register(__exit_handler)


def _get_camelot_connection(ip, port, version):
    connection_key = '%s:%s' % (ip, port)
    from camelot.protocol.tcp.camelot_connection import Connection
    with _connections_lock:

        conn = Connection(ip, port, connection_key, version)
        conn.init_connection(connection_key)
    return conn


class CamelotMessage(object):
    pass


class CamelotError(Exception):

    def __init__(self, message, e_type='External'):
        super(CamelotError, self).__init__(message)
        self.e_type = e_type
        self.message = message


def get_camelot_server(ip, port):
    '''
    returns the existing handle for camelot server object
    for given  ip and port.

    :parameter ip: ip address of Camelot server
    :parameter port: listening port of Camelot server

    :returns: on success returns camelot server handle else \
        throws CamelotError

    >>> serv = camelot.get_camelot_server('10.1.2.56', 9988)
    >>> serv
    <camelot.camelot_server.CamelotServer object at 0xb3a550>
    '''
    server_key = '%s:%s' % (ip, port)
    if server_key not in __camelot_servers:
        raise CamelotError('camserv not found')
    return __camelot_servers.get(server_key, None)


def create_camelot_server(ip, port, **kwargs):
    '''
    returns new handle for camelot server object if the
    camelot server is running on provided ip and port.
    otherwise thorws CamelotError.

    :parameter ip: ip address of Camelot server
    :parameter port: listening port of Camelot server
    :parameter server_class: custom type which is subclass of CamelotServer.
     Default value is CamelotServer

    :returns: on success returns camelot server handle else throws CamelotError

    >>> serv = camelot.create_camelot_server('10.12.10.180', '6666')
    >>> serv
    <camelot.camelot_server.CamelotServer object at 0x21deb10>

    >>> serv = camelot.create_camelot_server('10.12.10.180', '6666')
    CamelotError: camserv exists.Use get_camelot_server instead

    >>> serv_parms = { 'ip':'10.12.10.180', 'port':'5001'}
    kwargs = {'server_class':myClass, 'server_parms':serv_parms}
    camelot.create_camelot_server('10.12.10.180', '5001', **kwargs)
    Out[9]: <__main__.myClass at 0x2c32450>
    '''

    from camelot.camelot_server import CamelotServer

    server_class = kwargs.setdefault('server_class', CamelotServer)
    serv_params = kwargs.setdefault('server_params', {})
    version = kwargs.setdefault('version', VAPIEIUtils.CLIENT_VERSION)

    if not issubclass(server_class, CamelotServer):
        raise CamelotError('server_class not subclass of CamelotServer')

    server_key = '%s:%s' % (ip, port)
    serv = None
    with _camelot_servers_lock:
        if not ip or not port:
            raise CamelotError('either ip or port is invalid')

        if server_key in __camelot_servers:
            raise CamelotError(
                'camserv exists.Use get_camelot_server instead', 'Internal')
        else:
            serv = server_class(ip, port, server_key, version=version,
                                **serv_params)
            __camelot_servers[server_key] = serv

    if not serv:
        raise CamelotError('Camelot server not created \n')
    return serv


def stop_all():
    def cleanup_server(serv):
        serv.clean_up_eps()
        serv._server_conn.close_event_channel()

    stop_threads = []
    with _camelot_servers_lock:
        for s_key, serv in __camelot_servers.items():
            sr_thread = threading.Thread(target=cleanup_server, args=(serv,))
            sr_thread.start()
            stop_threads.append(sr_thread)

        # waiting for all stop threads to end
        for ch_th in stop_threads:
            try:
                if ch_th.isAlive():
                    ch_th.join()
            except Exception:
                pass

        __camelot_servers.clear()
