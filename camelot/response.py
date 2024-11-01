from camelot import camlogger

log = camlogger.getLogger(__name__)


class EndpointInfo(object):

    '''Represents Endpoint Info with following attributes

    * backup_cm
    * backup_cti
    * call_type
    * calls
    * current_cti
    * deploymentmodel
    * description
    * domain
    * esrstvernego
    * id
    * ipv4_address
    * ipv6_address
    * ix_enabled
    * last_error
    * lines
    * preferred_mode
    * primary_cm
    * primary_cti
    * sip_port
    * state
    * status
    * streams
    * type
    * userid
    * voice_mail_client_status
    '''

    _VM_CLIENT_STATUS = "voice mail client status"
    _BACKUP_CTI = "backup cti"
    _BACKUP_CM = "backup cm"
    _CALLS = "calls"
    _CALL_TYPE = "call type"
    _CURRENT_CTI = "current cti"
    _DEPLOYMENTMODEL = 'deploymentmodel'
    _DESCRIPTION = "description"
    _DOMAIN = "domain"
    _ESRSTVERNEGO = 'esrstvernego'
    _ID = "id"
    _IPV4ADDRESS = 'ipv4address'
    _IPV6ADDRESS = 'ipv6address'
    _IXENABLED = 'ixenabled'
    _LAST_ERROR = 'last error'
    _LINES = 'lines'
    _PREFFERED_MODE = "preferred mode"
    _PRIMARY_CM = "primary cm"
    _PRIMARY_CTI = "primary cti"
    _SIP_PORT = 'sip port'
    _STATE = "state"
    _STATUS = "status"
    _STREAMS = 'streams'
    _TYPE = "type"
    _USERID = 'userid'

    def __init__(self):
        self.backup_cm = None
        self.backup_cti = None
        self.call_type = None
        self.calls = None
        self.current_cti = None
        self.deploymentmodel = None
        self.description = None
        self.domain = None
        self.esrstvernego = None
        self.id = None
        self.ipv4_address = None
        self.ipv6_address = None
        self.ix_enabled = None
        self.last_error = None
        self.lines = None
        self.preferred_mode = None
        self.primary_cm = None
        self.primary_cti = None
        self.sip_port = None
        self.state = None
        self.status = None
        self.streams = None
        self.type = None
        self.userid = None
        self.voice_mail_client_status = None

    def _copy_from_dict(self, info_dict):
        if type(info_dict) == dict:
            if info_dict.get(EndpointInfo._BACKUP_CM):
                self.backup_cm = info_dict[EndpointInfo._BACKUP_CM]
            if info_dict.get(EndpointInfo._BACKUP_CTI):
                self.backup_cti = info_dict[EndpointInfo._BACKUP_CTI]
            if info_dict.get(EndpointInfo._CALL_TYPE):
                self.call_type = info_dict[EndpointInfo._CALL_TYPE]
            if info_dict.get(EndpointInfo._CALLS):
                self.calls = info_dict[EndpointInfo._CALLS]
            if info_dict.get(EndpointInfo._CURRENT_CTI):
                self.current_cti = info_dict[EndpointInfo._CURRENT_CTI]
            if info_dict.get(EndpointInfo._DEPLOYMENTMODEL):
                self.deploymentmodel = info_dict[EndpointInfo._DEPLOYMENTMODEL]
            if info_dict.get(EndpointInfo._DESCRIPTION):
                self.description = info_dict[EndpointInfo._DESCRIPTION]
            if info_dict.get(EndpointInfo._DOMAIN):
                self.domain = info_dict[EndpointInfo._DOMAIN]
            if info_dict.get(EndpointInfo._ESRSTVERNEGO):
                self.esrstvernego = info_dict[EndpointInfo._ESRSTVERNEGO]
            if info_dict.get(EndpointInfo._ID):
                self.id = info_dict[EndpointInfo._ID]
            if info_dict.get(EndpointInfo._IPV4ADDRESS):
                self.ipv4_address = info_dict[EndpointInfo._IPV4ADDRESS]
            if info_dict.get(EndpointInfo._IPV6ADDRESS):
                self.ipv6_address = info_dict[EndpointInfo._IPV6ADDRESS]
            if info_dict.get(EndpointInfo._IXENABLED):
                self.ix_enabled = info_dict[EndpointInfo._IXENABLED]
            if info_dict.get(EndpointInfo._LAST_ERROR):
                self.last_error = info_dict[EndpointInfo._LAST_ERROR]
            if info_dict.get(EndpointInfo._LINES):
                self.lines = info_dict[EndpointInfo._LINES]
            if info_dict.get(EndpointInfo._PREFFERED_MODE):
                self.preferred_mode = info_dict[EndpointInfo._PREFFERED_MODE]
            if info_dict.get(EndpointInfo._PRIMARY_CM):
                self.primary_cm = info_dict[EndpointInfo._PRIMARY_CM]
            if info_dict.get(EndpointInfo._PRIMARY_CTI):
                self.primary_cti = info_dict[EndpointInfo._PRIMARY_CTI]
            if info_dict.get(EndpointInfo._SIP_PORT):
                self.sip_port = info_dict[EndpointInfo._SIP_PORT]
            if info_dict.get(EndpointInfo._STATE):
                self.state = info_dict[EndpointInfo._STATE]
            if info_dict.get(EndpointInfo._TYPE):
                self.type = info_dict[EndpointInfo._TYPE]
            if info_dict.get(EndpointInfo._STATUS):
                self.status = info_dict[EndpointInfo._STATUS]
            if info_dict.get(EndpointInfo._STREAMS):
                self.streams = info_dict[EndpointInfo._STREAMS]
            if info_dict.get(EndpointInfo._USERID):
                self.userid = info_dict[EndpointInfo._USERID]
            if info_dict.get(EndpointInfo._VM_CLIENT_STATUS):
                vm_status = info_dict[EndpointInfo._VM_CLIENT_STATUS]
                self.voice_mail_client_status = vm_status
        else:
            log.error('passed parameter is not of type dict')
            return


class EndpointInfoExt(object):

    '''Represents Endpoint Info Ext with following attributes

    * feature_control_policy
    * voice_mail_client_info
    * control_devices
    * cumc_op_mode
    * intercom
    * media_state
    * mobile_connect
    * mr_state
    * mwi
    * mwi_line
    * mwi_stats
    * notify
    * presence_interface_status
    * prompt
    * softkeys
    * speeddials
    * subsevtdialog
    * subsevtpresence
    '''
    _FEATURE_CONTROL_POLICY = 'Feature Control Policy'
    _VOICE_MAIL_CLINET_INFO = 'Voice Mail client info'
    _CONTROL_DEVICES = 'ctrldevices'
    _CUMC_OP_MODE = 'cumcopmode'
    _INTERCOM = 'intercom'
    _MEDIA_STATE = 'mediastate'
    _MOBILE_CONNECT = 'mobileconnect'
    _MR_STATE = 'mrstate'
    _MWI = 'mwi'
    _MWI_LINE = 'mwi line'
    _MWI_STATS = 'mwi stats'
    _NOTIFY = 'notify'
    _PRESENCE_INTERFACE_STATUS = 'presence interface status'
    _PROMPT = 'prompt'
    _SOFTKEYS = 'softkeys'
    _SPEED_DIALS = 'speeddials'
    _SUBSEVT_DIALOG = 'subsevtdialog'
    _SUBSEVT_PRESENCE = 'subsevtpresence'

    def __init__(self):
        self.feature_control_policy = None
        self.voice_mail_client_info = None
        self.control_devices = None
        self.cumc_op_mode = None
        self.intercom = None
        self.media_state = None
        self.mobile_connect = None
        self.mr_state = None
        self.mwi = None
        self.mwi_line = None
        self.mwi_stats = None
        self.notify = None
        self.presence_interface_status = None
        self.prompt = None
        self.softkeys = None
        self.speeddials = None
        self.subsevtdialog = None
        self.subsevtpresence = None

    def _copy_from_dict(self, info_ext_dict):
        if type(info_ext_dict) == dict:
            if info_ext_dict.get(EndpointInfoExt._FEATURE_CONTROL_POLICY):
                tmp = info_ext_dict[EndpointInfoExt._FEATURE_CONTROL_POLICY]
                self.feature_control_policy = tmp
            if info_ext_dict.get(EndpointInfoExt._VOICE_MAIL_CLINET_INFO):
                tmp = info_ext_dict[EndpointInfoExt._VOICE_MAIL_CLINET_INFO]
                self.voice_mail_client_info = tmp
            if info_ext_dict.get(EndpointInfoExt._CONTROL_DEVICES):
                tmp = info_ext_dict[EndpointInfoExt._CONTROL_DEVICES]
                self.control_devices = tmp
            if info_ext_dict.get(EndpointInfoExt._CUMC_OP_MODE):
                self.cumc_op_mode = info_ext_dict[
                    EndpointInfoExt._CUMC_OP_MODE]
            if info_ext_dict.get(EndpointInfoExt._INTERCOM):
                self.intercom = info_ext_dict[EndpointInfoExt._INTERCOM]
            if info_ext_dict.get(EndpointInfoExt._MEDIA_STATE):
                self.media_state = info_ext_dict[EndpointInfoExt._MEDIA_STATE]
            if info_ext_dict.get(EndpointInfoExt._MOBILE_CONNECT):
                tmp = info_ext_dict[EndpointInfoExt._MOBILE_CONNECT]
                self.mobile_connect = tmp
            if info_ext_dict.get(EndpointInfoExt._MR_STATE):
                self.mr_state = info_ext_dict[EndpointInfoExt._MR_STATE]
            if info_ext_dict.get(EndpointInfoExt._MWI):
                self.mwi = info_ext_dict[EndpointInfoExt._MWI]
            if info_ext_dict.get(EndpointInfoExt._MWI_LINE):
                self.mwi_line = info_ext_dict[EndpointInfoExt._MWI_LINE]
            if info_ext_dict.get(EndpointInfoExt._MWI_STATS):
                self.mwi_stats = info_ext_dict[EndpointInfoExt._MWI_STATS]
            if info_ext_dict.get(EndpointInfoExt._NOTIFY):
                self.notify = info_ext_dict[EndpointInfoExt._NOTIFY]
            if info_ext_dict.get(EndpointInfoExt._PRESENCE_INTERFACE_STATUS):
                tmp = info_ext_dict[EndpointInfoExt._PRESENCE_INTERFACE_STATUS]
                self.presence_interface_status = tmp
            if info_ext_dict.get(EndpointInfoExt._PROMPT):
                self.prompt = info_ext_dict[EndpointInfoExt._PROMPT]
            if info_ext_dict.get(EndpointInfoExt._SOFTKEYS):
                self.softkeys = info_ext_dict[EndpointInfoExt._SOFTKEYS]
            if info_ext_dict.get(EndpointInfoExt._SPEED_DIALS):
                self.speeddials = info_ext_dict[EndpointInfoExt._SPEED_DIALS]
            if info_ext_dict.get(EndpointInfoExt._SUBSEVT_DIALOG):
                tmp = info_ext_dict[EndpointInfoExt._SUBSEVT_DIALOG]
                self.subsevtdialog = tmp
            if info_ext_dict.get(EndpointInfoExt._SUBSEVT_PRESENCE):
                tmp = info_ext_dict[EndpointInfoExt._SUBSEVT_PRESENCE]
                self.subsevtpresence = tmp
        else:
            log.error('passed parameter is not of type dict')
            return


class CallInfo(object):

    '''Represents Call Info with following attributes
    * call_reference
    * line_reference
    * direction_outbound
    * newdirection
    * type
    * state_connected
    * callid
    * calling_address
    * calling_name
    * called_address
    * called_name
    * original_called_address
    * original_called_name
    * last_redirecting_address
    * last_redirecting_name
    * last_redirecting_reason
    * original_called_redirecting_reason
    * calling_mail_box
    * called_mail_box
    * last_redirecting_mail_box
    * original_called_mail_box
    * call_security_status
    * not_authenticated
    * network_domain
    * precedence_domain
    * precedence_level
    * recording_type
    * recording_status
    * confidential_access_level_text
    * date
    * start
    * end
    * dialtone_time
    * setup_time
    * connect_time
    * disconnect_time
    * cut_through_time
    * disconnect_reason
    * cause_code
    * last_pathconf_trigger
    * status
    * callsetup_pc_attempts
    * callsetup_pc_successes
    * callsetup_pc_failures
    * midcall_pc_attempts
    * midcall_pc_successes
    * midcall_pc_failures
    * remoteinuse_events
    * failure_status
    * last_media_error
    '''

    _CALL_REFERENCE = 'call reference'
    _LINE_REFERENCE = 'line reference'
    _DIRECTION_OUTBOUND = 'direction outbound'
    _NEWDIRECTION = 'newdirection'
    _TYPE = 'type'
    _STATE_CONNECTED = 'state connected'
    _CALLID = 'callid'
    _CALLING_ADDRESS = 'calling address'
    _CALLING_NAME = 'calling name'
    _CALLED_ADDRESS = 'called address'
    _CALLED_NAME = 'called name'
    _ORIGINAL_CALLED_ADDRESS = 'original called address'
    _ORIGINAL_CALLED_NAME = 'original called name'
    _LAST_REDIRECTING_ADDRESS = 'last redirecting address'
    _LAST_REDIRECTING_NAME = 'last redirecting name'
    _LAST_REDIRECTING_REASON = 'last redirecting reason'
    _ORIGINAL_CALLED_REDIRECTING_REASON = 'original called redirecting reason'
    _CALLING_MAIL_BOX = 'calling mail box'
    _CALLED_MAIL_BOX = 'called mail box'
    _LAST_REDIRECTING_MAIL_BOX = 'last redirecting mail box'
    _ORIGINAL_CALLED_MAIL_BOX = 'original called mail box'
    _CALL_SECURITY_STATUS = 'call security status'
    _NOT_AUTHENTICATED = 'not authenticated'
    _NETWORK_DOMAIN = 'network domain'
    _PRECEDENCE_DOMAIN = 'precedence domain'
    _PRECEDENCE_LEVEL = 'precedence level'
    _RECORDING_TYPE = 'recording type'
    _RECORDING_STATUS = 'recording status'
    _CONFIDENTIAL_ACCESS_LEVEL_TEXT = 'confidential access level text'
    _DATE = 'date'
    _START = 'start'
    _END = 'end'
    _DIALTONE_TIME = 'dialtone time'
    _SETUP_TIME = 'setup time'
    _CONNECT_TIME = 'connect time'
    _DISCONNECT_TIME = 'disconnect time'
    _CUT_THROUGH_TIME = 'cut-through time'
    _DISCONNECT_REASON = 'disconnect reason'
    _CAUSE_CODE = 'cause code'
    _LAST_PATHCONF_TRIGGER = 'last pathconf trigger'
    _STATUS = 'status'
    _CALLSETUP_PC_ATTEMPTS = 'callsetup pc attempts'
    _CALLSETUP_PC_SUCCESSES = 'callsetup pc successes'
    _CALLSETUP_PC_FAILURES = 'callsetup pc failures'
    _MIDCALL_PC_ATTEMPTS = 'midcall pc attempts'
    _MIDCALL_PC_SUCCESSES = 'midcall pc successes'
    _MIDCALL_PC_FAILURES = 'midcall pc failures'
    _REMOTEINUSE_EVENTS = 'remoteinuse events'
    _FAILURE_STATUS = 'failure status'
    _LAST_MEDIA_ERROR = 'last media error'

    def __init__(self):

        self.call_reference = None
        self.line_reference = None
        self.direction_outbound = None
        self.newdirection = None
        self.type = None
        self.state_connected = None
        self.callid = None
        self.calling_address = None
        self.calling_name = None
        self.called_address = None
        self.called_name = None
        self.original_called_address = None
        self.original_called_name = None
        self.last_redirecting_address = None
        self.last_redirecting_name = None
        self.last_redirecting_reason = None
        self.original_called_redirecting_reason = None
        self.calling_mail_box = None
        self.called_mail_box = None
        self.last_redirecting_mail_box = None
        self.original_called_mail_box = None
        self.call_security_status = None
        self.not_authenticated = None
        self.network_domain = None
        self.precedence_domain = None
        self.precedence_level = None
        self.recording_type = None
        self.recording_status = None
        self.confidential_access_level_text = None
        self.date = None
        self.start = None
        self.end = None
        self.dialtone_time = None
        self.setup_time = None
        self.connect_time = None
        self.disconnect_time = None
        self.cut_through_time = None
        self.disconnect_reason = None
        self.cause_code = None
        self.last_pathconf_trigger = None
        self.status = None
        self.callsetup_pc_attempts = None
        self.callsetup_pc_successes = None
        self.callsetup_pc_failures = None
        self.midcall_pc_attempts = None
        self.midcall_pc_successes = None
        self.midcall_pc_failures = None
        self.remoteinuse_events = None
        self.failure_status = None
        self.last_media_error = None

    def _copy_from_dict(self, call_info):
        if type(call_info) == dict:
            if call_info.get(CallInfo._CALL_REFERENCE):
                self.call_reference = call_info[CallInfo._CALL_REFERENCE]
            if call_info.get(CallInfo._LINE_REFERENCE):
                self.line_reference = call_info[CallInfo._LINE_REFERENCE]
            if call_info.get(CallInfo._DIRECTION_OUTBOUND):
                self.direction_outbound = call_info[
                    CallInfo._DIRECTION_OUTBOUND]
            if call_info.get(CallInfo._NEWDIRECTION):
                self.newdirection = call_info[CallInfo._NEWDIRECTION]
            if call_info.get(CallInfo._TYPE):
                self.type = call_info[CallInfo._TYPE]
            if call_info.get(CallInfo._STATE_CONNECTED):
                self.state_connected = call_info[CallInfo._STATE_CONNECTED]
            if call_info.get(CallInfo._CALLID):
                self.callid = call_info[CallInfo._CALLID]
            if call_info.get(CallInfo._CALLING_ADDRESS):
                self.calling_address = call_info[CallInfo._CALLING_ADDRESS]
            if call_info.get(CallInfo._CALLING_NAME):
                self.calling_name = call_info[CallInfo._CALLING_NAME]
            if call_info.get(CallInfo._CALLED_NAME):
                self.called_name = call_info[CallInfo._CALLED_NAME]
            if call_info.get(CallInfo._CALLED_ADDRESS):
                self.called_address = call_info[CallInfo._CALLED_ADDRESS]
            if call_info.get(CallInfo._ORIGINAL_CALLED_ADDRESS):
                self.original_called_address = call_info[
                    CallInfo._ORIGINAL_CALLED_ADDRESS]
            if call_info.get(CallInfo._ORIGINAL_CALLED_NAME):
                self.original_called_name = call_info[
                    CallInfo._ORIGINAL_CALLED_NAME]
            if call_info.get(CallInfo._LAST_REDIRECTING_ADDRESS):
                self.last_redirecting_address = call_info[
                    CallInfo._LAST_REDIRECTING_ADDRESS]
            if call_info.get(CallInfo._LAST_REDIRECTING_NAME):
                self.last_redirecting_name = call_info[
                    CallInfo._LAST_REDIRECTING_NAME]
            if call_info.get(CallInfo._LAST_REDIRECTING_REASON):
                self.last_redirecting_reason = call_info[
                    CallInfo._LAST_REDIRECTING_REASON]
            if call_info.get(CallInfo._ORIGINAL_CALLED_REDIRECTING_REASON):
                self.original_called_redirecting_reason = call_info[
                    CallInfo._ORIGINAL_CALLED_REDIRECTING_REASON]
            if call_info.get(CallInfo._CALLING_MAIL_BOX):
                self.calling_mail_box = call_info[CallInfo._CALLING_MAIL_BOX]
            if call_info.get(CallInfo._CALLED_MAIL_BOX):
                self.called_mail_box = call_info[CallInfo._CALLED_MAIL_BOX]
            if call_info.get(CallInfo._LAST_REDIRECTING_MAIL_BOX):
                self.last_redirecting_mail_box = call_info[
                    CallInfo._LAST_REDIRECTING_MAIL_BOX]
            if call_info.get(CallInfo._ORIGINAL_CALLED_MAIL_BOX):
                self.original_called_mail_box = call_info[
                    CallInfo._ORIGINAL_CALLED_MAIL_BOX]
            if call_info.get(CallInfo._CALL_SECURITY_STATUS):
                self.call_security_status = call_info[
                    CallInfo._CALL_SECURITY_STATUS]
            if call_info.get(CallInfo._NOT_AUTHENTICATED):
                self.not_authenticated = call_info[CallInfo._NOT_AUTHENTICATED]
            if call_info.get(CallInfo._NETWORK_DOMAIN):
                self.network_domain = call_info[CallInfo._NETWORK_DOMAIN]
            if call_info.get(CallInfo._PRECEDENCE_DOMAIN):
                self.precedence_domain = call_info[CallInfo._PRECEDENCE_DOMAIN]
            if call_info.get(CallInfo._PRECEDENCE_LEVEL):
                self.precedence_level = call_info[CallInfo._PRECEDENCE_LEVEL]
            if call_info.get(CallInfo._RECORDING_TYPE):
                self.recording_type = call_info[CallInfo._RECORDING_TYPE]
            if call_info.get(CallInfo._RECORDING_STATUS):
                self.recording_status = call_info[CallInfo._RECORDING_STATUS]
            if call_info.get(CallInfo._CONFIDENTIAL_ACCESS_LEVEL_TEXT):
                self.confidential_access_level_text = call_info[
                    CallInfo._CONFIDENTIAL_ACCESS_LEVEL_TEXT]
            if call_info.get(CallInfo._DATE):
                self.date = call_info[CallInfo._DATE]
            if call_info.get(CallInfo._START):
                self.start = call_info[CallInfo._START]
            if call_info.get(CallInfo._END):
                self.end = call_info[CallInfo._END]
            if call_info.get(CallInfo._DIALTONE_TIME):
                self.dialtone_time = call_info[CallInfo._DIALTONE_TIME]
            if call_info.get(CallInfo._SETUP_TIME):
                self.setup_time = call_info[CallInfo._SETUP_TIME]
            if call_info.get(CallInfo._CONNECT_TIME):
                self.connect_time = call_info[CallInfo._CONNECT_TIME]
            if call_info.get(CallInfo._DISCONNECT_TIME):
                self.disconnect_time = call_info[CallInfo._DISCONNECT_TIME]
            if call_info.get(CallInfo._CUT_THROUGH_TIME):
                self.cut_through_time = call_info[CallInfo._CUT_THROUGH_TIME]
            if call_info.get(CallInfo._DISCONNECT_REASON):
                self.disconnect_reason = call_info[CallInfo._DISCONNECT_REASON]
            if call_info.get(CallInfo._CAUSE_CODE):
                self.cause_code = call_info[CallInfo._CAUSE_CODE]
            if call_info.get(CallInfo._LAST_PATHCONF_TRIGGER):
                self.last_pathconf_trigger = call_info[
                    CallInfo._LAST_PATHCONF_TRIGGER]
            if call_info.get(CallInfo._STATUS):
                self.status = call_info[CallInfo._STATUS]
            if call_info.get(CallInfo._CALLSETUP_PC_ATTEMPTS):
                self.callsetup_pc_attempts = call_info[
                    CallInfo._CALLSETUP_PC_ATTEMPTS]
            if call_info.get(CallInfo._CALLSETUP_PC_FAILURES):
                self.callsetup_pc_failures = call_info[
                    CallInfo._CALLSETUP_PC_FAILURES]
            if call_info.get(CallInfo._CALLSETUP_PC_SUCCESSES):
                self.callsetup_pc_successes = call_info[
                    CallInfo._CALLSETUP_PC_SUCCESSES]
            if call_info.get(CallInfo._MIDCALL_PC_ATTEMPTS):
                self.midcall_pc_attempts = call_info[
                    CallInfo._MIDCALL_PC_ATTEMPTS]
            if call_info.get(CallInfo._MIDCALL_PC_FAILURES):
                self.midcall_pc_failures = call_info[
                    CallInfo._MIDCALL_PC_FAILURES]
            if call_info.get(CallInfo._MIDCALL_PC_SUCCESSES):
                self.midcall_pc_successes = call_info[
                    CallInfo._MIDCALL_PC_SUCCESSES]
            if call_info.get(CallInfo._REMOTEINUSE_EVENTS):
                self.remoteinuse_events = call_info[
                    CallInfo._REMOTEINUSE_EVENTS]
            if call_info.get(CallInfo._FAILURE_STATUS):
                self.failure_status = call_info[CallInfo._FAILURE_STATUS]
            if call_info.get(CallInfo._LAST_MEDIA_ERROR):
                self.last_media_error = call_info[CallInfo._LAST_MEDIA_ERROR]
        else:
            log.error('passed parameter is not of type dict')
            return


class CallInfoExt(object):

    '''Represents Call Info Ext object with following attributes
    * softkeys
    * prompt
    * selected
    * did
    * h235_encryption_algorithm
    * attribute
    * holdreversionreq
    * protocol_disc_reason
    * monitor_mode
    * monitor_DN
    * cumccallmode
    * history_info
    * participant
    * x_refci
    * x_nearenddevice
    * x_farendrefci
    * x_farenddevice
    * x_farendaddr
    * x_nearendaddr
    * x_nearendguid
    * x_farendguid
    * x_nearendclusterid
    * x_farendclusterid
    '''

    _SOFTKEYS = 'softkeys'
    _PROMPT = 'prompt'
    _SELECTED = 'selected'
    _DID = 'did'
    _H235_ENCRYPTION_ALGORITHM = 'h235 encryption algorithm'
    _ATTRIBUTE = 'attribute'
    _HOLDREVERSION = 'holdreversionreq'
    _PROTOCOL_DISC_REASON = 'protocol disc reason'
    _MONITOR_MODE = 'monitor mode'
    _MONITOR_DN = 'monitor DN'
    _CUMCCALLMODE = 'cumccallmode'
    _HISTORY_INFO = 'history-info'
    _PARTICIPANT = 'participant'
    _X_REFCI = 'x-refci'
    _X_NEARENDDEVICE = 'x-nearenddevice'
    _X_FARENDREFCI = 'x-farendrefci'
    _X_FARENDDEVICE = 'x-farenddevice'
    _X_FARENDADDR = 'x-farendaddr'
    _X_NEARENDADDR = 'x-nearendaddr'
    _X_NEARENDGUID = 'x-nearendguid'
    _X_FARENDGUID = 'x-farendguid'
    _X_NEARENDCLUSTERID = 'x-nearendclusterid'
    _X_FARENDCLUSTERID = 'x-farendclusterid'

    def __init__(self):

        self.softkeys = None
        self.prompt = None
        self.selected = None
        self.did = None
        self.h235_encryption_algorithm = None
        self.attribute = None
        self.protocol_disc_reason = None
        self.monitor_mode = None
        self.monitor_DN = None
        self.cumccallmode = None
        self.history_info = None
        self.participant = None
        self.x_refci = None
        self.x_nearenddevice = None
        self.x_farendrefci = None
        self.x_farenddevice = None
        self.x_farendaddr = None
        self.x_nearendaddr = None
        self.x_nearendguid = None
        self.x_farendguid = None
        self.x_nearendclusterid = None
        self.x_farendclusterid = None

    def _copy_from_dict(self, call_info_ext):
        if type(call_info_ext) == dict:
            if call_info_ext.get(CallInfoExt._SOFTKEYS):
                self.softkeys = call_info_ext[CallInfoExt._SOFTKEYS]
            if call_info_ext.get(CallInfoExt._PROMPT):
                self.prompt = call_info_ext[CallInfoExt._PROMPT]
            if call_info_ext.get(CallInfoExt._SELECTED):
                self.selected = call_info_ext[CallInfoExt._SELECTED]
            if call_info_ext.get(CallInfoExt._DID):
                self.did = call_info_ext[CallInfoExt._DID]
            if call_info_ext.get(CallInfoExt._H235_ENCRYPTION_ALGORITHM):
                self.h235_encryption_algorithm = call_info_ext[
                    CallInfoExt._H235_ENCRYPTION_ALGORITHM]
            if call_info_ext.get(CallInfoExt._ATTRIBUTE):
                self.attribute = call_info_ext[CallInfoExt._ATTRIBUTE]
            if call_info_ext.get(CallInfoExt._HOLDREVERSION):
                self.holdreversion = call_info_ext[CallInfoExt._HOLDREVERSION]
            if call_info_ext.get(CallInfoExt._PROTOCOL_DISC_REASON):
                self.protocol_disc_reason = call_info_ext[
                    CallInfoExt._PROTOCOL_DISC_REASON]
            if call_info_ext.get(CallInfoExt._MONITOR_MODE):
                self.monitor_mode = call_info_ext[CallInfoExt._MONITOR_MODE]
            if call_info_ext.get(CallInfoExt._MONITOR_DN):
                self.monitor_DN = call_info_ext[CallInfoExt._MONITOR_DN]
            if call_info_ext.get(CallInfoExt._CUMCCALLMODE):
                self.cumccallmode = call_info_ext[CallInfoExt._CUMCCALLMODE]
            if call_info_ext.get(CallInfoExt._HISTORY_INFO):
                self.history_info = call_info_ext[CallInfoExt._HISTORY_INFO]
            if call_info_ext.get(CallInfoExt._PARTICIPANT):
                self.participant = call_info_ext[CallInfoExt._PARTICIPANT]
            if call_info_ext.get(CallInfoExt._X_REFCI):
                self.x_refci = call_info_ext[CallInfoExt._X_REFCI]
            if call_info_ext.get(CallInfoExt._X_FARENDADDR):
                self.x_farendaddr = call_info_ext[CallInfoExt._X_FARENDADDR]
            if call_info_ext.get(CallInfoExt._X_FARENDCLUSTERID):
                self.x_farendclusterid = call_info_ext[
                    CallInfoExt._X_FARENDCLUSTERID]
            if call_info_ext.get(CallInfoExt._X_FARENDDEVICE):
                self.x_farenddevice = call_info_ext[
                    CallInfoExt._X_FARENDDEVICE]
            if call_info_ext.get(CallInfoExt._X_FARENDGUID):
                self.x_farendguid = call_info_ext[CallInfoExt._X_FARENDGUID]
            if call_info_ext.get(CallInfoExt._X_FARENDREFCI):
                self.x_farendrefci = call_info_ext[CallInfoExt._X_FARENDREFCI]
            if call_info_ext.get(CallInfoExt._X_NEARENDADDR):
                self.x_nearendaddr = call_info_ext[CallInfoExt._X_NEARENDADDR]
            if call_info_ext.get(CallInfoExt._X_NEARENDCLUSTERID):
                self.x_nearendclusterid = call_info_ext[
                    CallInfoExt._X_NEARENDCLUSTERID]
            if call_info_ext.get(CallInfoExt._X_NEARENDDEVICE):
                self.x_nearenddevice = call_info_ext[
                    CallInfoExt._X_NEARENDDEVICE]
            if call_info_ext.get(CallInfoExt._X_NEARENDGUID):
                self.x_nearendguid = call_info_ext[CallInfoExt._X_NEARENDGUID]
        else:
            log.error('passed parameter is not of type dict')
            return


class CallState(object):
    NEW = 'new'
    OUTBOUND = 'outbound'
    OFFHOOK = 'offhook'
    DIALTONE = 'dialtone'
    DIALING = 'dialing'
    PROCEEDING = 'proceeding'
    ALERTING = 'alerting'
    CONNECTED = 'connected'
    DISCONNECTING = 'disconnecting'
    DISCONNECTED = 'disconnected'
    SEIZURE = 'seizure'
    RECDIGITS = 'recdigits'
    INCOMING = 'incoming'
    ANSWERING = 'answering'
    REJECTING = 'rejecting'
    REMOTEINUSE = 'remoteinuse'
    HELD = 'held'
    REMOTEHELD = 'remoteheld'
    MOVING = 'moving'


class EndpointState(object):
    UN_INITIALIZED = "uninitialized"
    OUT_OF_SERVICE = "outofservice"
    IN_SERVICE = "inservice"
    CLIENT_SUSPEND = "suspended"
    CLIENT_FOREGROUND = "foregroundpending"
    INIT_PENDING = "initpending"
    IN_SERVICE_PENDING = "inservicepending"
    OUT_OF_SERVICE_PENDING = "outofservicepending"


class VoiceMailClientState(object):

    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    CONNECTING = 'connecting'
    DISCONNECTING = 'disconnecting'
    INACTIVE = 'inactive'
    ACTIVE = 'active'


class EndpointType(object):
    SIP = 'sip'
    SIPX = 'sipx'
    SIPV = 'sipv'
    SK = 'sk'
    SKM = 'skm'
    CUPC = 'cupc'
    CUPCLITE = 'cupclite'
    CUPCD = 'cupcd'
    CSFD = 'csfd'
    CUMC = 'cumc'
    CTS = 'cts'
    H323 = 'h323',
    PRI = 'pri'
    CAS = 'cas'
    RAW = 'raw'
    TANDBERGSIP = 'tandbergsip'
    SKS = 'sks'
    DMC = 'dmc'
    IMSCLIENT = 'imsclient'


class Stream(object):

    '''Represents Stream object with following params

    * stream_ref
    * call_ref
    * type
    * direction
    * state
    * mifctype
    '''
    _STREAM_REF = 'stream_ref'
    _CALL_REF = 'call_ref'
    _TYPE = 'type'
    _DIRECTION = 'direction'
    _STATE = 'state'
    _MIFC_TYPE = 'mifctype'

    def __init__(self):
        self.stream_ref = None
        self.call_ref = None
        self.type = None
        self.direction = None
        self.state = None
        self.mifctype = None

    def _copy_from_dict(self, streams_dict):
        if type(streams_dict) == dict:
            if streams_dict.get(Stream._CALL_REF):
                self.call_ref = streams_dict[Stream._CALL_REF]
            if streams_dict.get(Stream._DIRECTION):
                self.direction = streams_dict[Stream._DIRECTION]
            if streams_dict.get(Stream._MIFC_TYPE):
                self.mifctype = streams_dict[Stream._MIFC_TYPE]
            if streams_dict.get(Stream._TYPE):
                self.type = streams_dict[Stream._TYPE]
            if streams_dict.get(Stream._STATE):
                self.state = streams_dict[Stream._STATE]
            if streams_dict.get(Stream._STREAM_REF):
                self.stream_ref = streams_dict[Stream._STREAM_REF]
        else:
            log.error('passed parameter is not of type dict')
            return


class Call(object):

    '''Represents Call with following attributes

    * line_ref
    * call_ref
    * state
    '''
    _LINE_REF = 'line_ref'
    _CALL_REF = 'call_ref'
    _STATE = 'state'

    def __init__(self):
        self.line_ref = None
        self.call_ref = None
        self.state = None

    def _copy_from_dict(self, calls_dict):
        if type(calls_dict) == dict:
            if calls_dict.get(Call._CALL_REF):
                self.call_ref = calls_dict[Call._CALL_REF]
            if calls_dict.get(Call._LINE_REF):
                self.line_ref = calls_dict[Call._LINE_REF]
            if calls_dict.get(Call._STATE):
                self.state = calls_dict[Call._STATE]
        else:
            log.error('passed parameter is not of type dict')
            return


class Line(object):

    '''Represents a Line

    * line_num
    * full_address
    '''
    _LINE_NUM = 'line_num'
    _FULL_ADDRESS = 'full_address'

    def __init__(self):
        self.line_num = None
        self.full_address = None

    def _copy_from_dict(self, line_dict):
        if type(line_dict) == dict:
            if line_dict.get(Line._LINE_NUM):
                self.line_num = line_dict[Line._LINE_NUM]
            if line_dict.get(Line._FULL_ADDRESS):
                self.full_address = line_dict[Line._FULL_ADDRESS]
        else:
            log.error('passed parameter is not of type dict')
            return
