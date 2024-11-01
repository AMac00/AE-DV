'''
Created on 11-Sep-2013

@author: smaturi
'''
from camelot import camlogger


log = camlogger.getLogger(__name__)


class VAPIEIUtils(object):
    ACK_DELIM = ":"
    CLIENT_VERSION_PROPERTY = "ClientVersion"
    DECIMAL_RADIX = 16
    CLIENT_VERSION = "14.0.37.0.0.0"
    CV_BASE = "gAAAAABhLzAocE84B5fn_8DK2cUnv5orRGnS2eFwl97kGgPsbHgwWw0Iz182"
    CV_PAD = "b2YkdbfOv_o5VhEwam3IkKLiS4p4w8412n7U2Q=="
    info_event_types = ['state', 'calls', 'primarycm', 'backupcm', 'bcgready',
                        'lostconn', 'transports']
    station_event_types = ['ring', 'starttone', 'stoptone', 'lamp', 'prompt',
                           'notify', 'blfack', 'blfnotify', 'callselect',
                           'keypad', 'userdata', 'ccmreg', 'ccmreset', 'cti',
                           'presencepublishstatus', 'presencenotification',
                           'imsendstatus', 'incomingim', 'voicemail',
                           'cellpickupStatus', 'presenceloginredirect',
                           'presencedecomposedlayout', 'presenceuserrehomed',
                           'presencecupfailed', 'envelope',
                           'implogincompleted', 'xmpplogincompleted',
                           'ssologincompleted', 'udslogincompleted',
                           'httpquerycompleted', 'ucxnssologincompleted',
                           'hedge']
    media_event_types = ['dtmfdetstarted', 'dtmfdetdone', 'digitbegin',
                         'digitend', 'tonedetstarted', 'tonedetdone',
                         'tonebegin', 'toneend', 'recordstarted', 'recorddone',
                         'tonestarted', 'tonedone', 'trafficstarted',
                         'trafficdone', 'mediastarted', 'mediadone',
                         'promptdetstarted', 'prompt', 'promptdetdone']
    trace_masks = [0x0, 0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]
    event_types = ['infoevent', 'stationevent', 'callevent', 'streamevent',
                   'callinfoevent', 'streaminfoevent', 'mediaevent',
                   'traceevent', 'transportevent', 'transportinfoevent',
                   'rawevent', 'verifyevent']
    json_cmd_list = ['getinfo', 'getinfoext', 'getcallinfo',
                     'getcallstats', 'getstreaminfo',
                     'getcallinfoext', 'getstreaminfoext', 'gethedgeinfo',
                     'getedgeinfo', 'getcalls', 'getstreams', 'getssoinfo',
                     'getssostats', 'getudsinfo', 'gettimingstats',
                     'getcalltimestats', 'getunityinfo', 'getimpstats',
                     'getimpinfo', 'getuserinfo', 'getiminfo', 'getheadset',
                     'getpresence', 'presencequeryresponse',
                     'getimpstats', 'getimqueryresponse',
                     'impqueryresponse', 'getcallcryptoinfo',
                     'get_secure_uds_users_access_url_info',
                     'get_web_service_info',
                     'getlines', 'getbuddylist',
                     'getrpid', 'geturis', 'getclientdata',
                     'getclientdesc', 'logmask', 'slog_mask', 'logdir',
                     'logfilesz', 'maxlogfiles',
                     'logfileprefix', 'logbookmark',
                     'eplogmask', 'eplogdir', 'eplogfilesz',
                     'epmaxlogfiles', 'eplogfileprefix',
                     'get_server_os', 'get_server_version',
                     'get_compat_versions', 'get_vapiei_version',
                     'getsupportedconversationsinfo', 'getcascallinfo',
                     'getfaxstats', 'getdeviceconfig', 'showvvminfo',
                     'getbfcpinfo', 'getrtcpstreaminfo', 'getrtprxstats'
                     'getrtptxstats']
    # add supported formats by camelot here
    supported_formats = ['json']

    rawtemplate_method_types = ['SIP_INVITE', 'SIP_100', 'SIP_180',
                                'SIP_200', 'SIP_ACK', 'SIP_BYE']

    device_id_map = {0: 'Camelot SIP Version 0.8',
                     1: 'CP7970G',
                     2: 'CP7970G-GE',
                     3: 'CP7971G',
                     4: 'CP7971G-GE',
                     5: 'CP7961G',
                     6: 'CP7961G-GE',
                     7: 'CP7941G',
                     8: 'CP7941G-GE',
                     9: 'CP7911G',
                     10: 'Unified Client',
                     11: 'Cts 1000 client',
                     12: 'CP7931G',
                     14: 'CP9971G',
                     15: 'Client Services Core',
                     16: 'SIP VoWiFi side of Tin Can Touch',
                     17: 'Legacy Telepresence Client',
                     18: 'Cts 500 client',
                     19: 'CP6961',
                     20: 'CP6941',
                     21: 'CP6921',
                     22: 'MXP1000',
                     23: 'MXP1700',
                     24: 'E20',
                     26: 'Android Dual Mode device 575',
                     27: 'CIUS 593',
                     30: 'CP3905 (Cinderella)',
                     31: 'CP6945',
                     32: 'CP8945',
                     33: 'CP8941',
                     34: 'Native E20',
                     35: 'CP8961',
                     36: 'IMSClient',
                     37: 'NativeIMSClient',
                     38: 'Cisco Jabber Client',
                     39: 'CIUS-SP 632',
                     40: 'Cisco Jabber for Tablet/iPad 652',
                     41: 'CP9951'}

    model_number_map = {584: 'EX90',
                        604: 'EX60',
                        621: '7821',
                        622: '7841',
                        623: '7861',
                        647: 'DX650'}
    skinny_device_type_map = {6: '7910',
                              7: '7960',
                              8: '7940',
                              9: '7935',
                              20000: '7905',
                              30002: '7920',
                              30006: '7970',
                              30007: '7912',
                              30008: '7902',
                              436: '7965',
                              30018: '7961',
                              30019: '7936',
                              348: '7931',
                              437: '7975',
                              404: '7962',
                              495: '6921',
                              496: '6941',
                              497: '6961',
                              376: 'Nokia S60 Dual-Mode',
                              564: '6945',
                              585: '8945',
                              586: '8941'}

    @staticmethod
    def message_length_to_decimal(message):
        '''
        Returns the message length in DEC format for Comelot.
        string length of the message and this field contains exactly
        4 hexidecimal digits<br>

        :parameter message: a message to be transfered to Camelot server

        :returns: converted length to 4 digit decimal
        '''
        if not message:
            log.warning("Un Expected message to crate message length")
            return
        return "%04d" % len(message)

    @staticmethod
    def is_valid_ipv4(ip):
        import socket
        try:
            socket.inet_aton(ip)
            if ip == '0.0.0.0':
                return False
            return True
        except socket.error:
            return False

    @staticmethod
    def is_valid_ipv6_address(address):
        import socket
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return False
        return True

    @staticmethod
    def get_message_length_hex(message):
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
