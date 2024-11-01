from camelot import camlogger

log = camlogger.getLogger(__name__)


class EventType(object):
    STATION_EVENT = "station"
    INFO_EVENT = "info"
    CALL_INFO_EVENT = "callstate"
    STREAM_INFO_EVENT = "streamstate"
    STREAM_EVENT = "stream"
    STATE = "state"
    CALLS = "calls"
    STREAMS = "streams"
    PRIMARY_CM = "primarycm"
    BACKUP_CM = "backupcm"
    BCG_READY = "bcgready"
    TRASNPORTS = "transports"
    LOST_CONN = "lostconn"
    MEDIA_EVENT = "media"
    TRACE_EVENT = "log"
    TRANSPORT_INFO_EVENT = "transportstate"
    CONNECTED = "connected"
    CONNECTION_ERROR = "connectionerror"
    CONNECTION_LOST = "connectionlost"
    CONNECTION_TERMINATED = "connectionterminated"
    CALL_EVENT = "callevent"


class InfoEventType(object):
    STATE = 'state'
    CALLS = 'calls'
    PRIMARYCM = 'primarycm'
    BACKUPCM = 'backupcm'
    BCGREADY = 'bcgready'
    LOSTCONN = 'lostconn'
    TRANSPORTS = 'transports'


class StationEventType(object):
    RING = 'ring'
    START_TONE = 'starttone'
    STOP_TONE = 'stoptone'
    LAMP = 'lamp'
    PROMPT = 'prompt'
    NOTIFY = 'notify'
    BLF_ACK = 'blfack'
    BLF_NOTIFY = 'blfnotify'
    CALL_SELECT = 'callselect'
    KEY_PAD = 'keypad'
    USER_DATA = 'userdata'
    CCM_REG = 'ccmreg'
    CCM_RESET = 'ccmreset'
    CTI = 'cti'
    PRESENCE_PUBLISH_STATUS = 'presencepublishstatus'
    PRESENCE_NOTIFICATION = 'presencenotification'
    IM_SEND_STATUS = 'imsendstatus'
    INCOMING_IM = 'incomingim'
    VOICEMAIL = 'voicemail'
    CALL_PICKUP_STATUS = 'cellpickupStatus'
    PRESENCE_LOGIN_REDIRECT = 'presenceloginredirect'
    PRESENCE_DECOMPOSED_LAYOUT = 'presencedecomposedlayout'
    PRESENCE_USER_REHOMED = 'presenceuserrehomed'
    PRESENCE_CUP_FAILED = 'presencecupfailed'
    ENVELOPE = 'envelope'


class Event(object):
    _CAMELOT_IP = 'camelot_ip'
    _CAMELOT_PORT = 'camelot_port'
    _ENDPOINT_ID = 'endpoint_id'
    _EVENT_TYPE = 'event_type'
    _EVENT_SUB_TYPE = 'event_sub_type'
    _MESSAGE = 'message'

    def __init__(self):
        self.camelot_ip = None
        self.camelot_port = None
        self.endpoint_id = None
        self.event_type = None
        self.event_sub_type = None
        self.message = None

    def _copy_from_dict(self, event_dict):
        if type(event_dict) == dict:
            if event_dict.get(Event._CAMELOT_IP):
                self.camelot_ip = event_dict[Event._CAMELOT_IP]
            if event_dict.get(Event._CAMELOT_PORT):
                self.camelot_port = event_dict[Event._CAMELOT_PORT]
            if event_dict.get(Event._ENDPOINT_ID):
                self.endpoint_id = event_dict[Event._ENDPOINT_ID]
            if event_dict.get(Event._EVENT_SUB_TYPE):
                self.event_sub_type = event_dict[Event._EVENT_SUB_TYPE]
            if event_dict.get(Event._EVENT_TYPE):
                self.event_type = event_dict[Event._EVENT_TYPE]
            if event_dict.get(Event._MESSAGE):
                self.message = event_dict[Event._MESSAGE]
        else:
            log.error('passed parameter is not of type dict')
            return
