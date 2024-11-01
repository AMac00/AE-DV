import logging


log = logging.getLogger('CamelotRawEndpoint')


class SipTemplateMethods:
    SIP_INVITE = 'SIP_INVITE'
    SIP_100 = 'SIP_100'
    SIP_180 = 'SIP_180'
    SIP_200 = 'SIP_200'
    SIP_ACK = 'SIP_ACK'
    SIP_BYE = 'SIP_BYE'


class Media:
    audio = 'audio'
    video = 'video'
    none = 'none'


class SipHeaders:
    StatusLine = 'Status-Line'
    Via = 'Via'
    RemotePartyID = 'Remote-Party-ID'
    From = 'From'
    To = 'To'
    Date = 'Date'
    CallID = 'Call-ID'
    Supported = 'Supported'
    MinSE = 'Min-SE'
    UserAgent = 'User-Agent'
    AcceptLanguage = 'Accept-Language'
    Allow = 'Allow'
    Accept = 'Accept'
    RecvInfo = 'Recv-Info'
    CSeq = 'CSeq'
    MaxForwards = 'Max-Forwards'
    Timestamp = 'Timestamp'
    Contact = 'Contact'
    Expires = 'Expires'
    AllowEvents = 'Allow-Events'
    ContentType = 'Content-Type'
    ContentLenght = 'Content-Length'


class OutActionObject(object):

    def __init__(self, camelotconn, msgstr):
        self.vapi = camelotconn
        self.msgid = msgstr
        self.event_type = ''

    def add_sip_header(self, headername, value):
        '''
        Queued an action for adding given header to the original message

        :parameter headername: name of header needs to be added to original
            message. This can be suffixed with a optional index
        :parameter value: value of header given in headername and need to be
            added to original message

        >>> actions = self.srv.create_action_set()
        >>> actions.add_sip_header('To','NewTo')
        >>> actions.add_sip_header('To:0', 'FirstTo')

        Above example will add Two new 'To' Header to original message on which
        this action will be applied. First 'To' Header with value NewTo will be
        added at the end as no Index is specified. Second 'To' Header with
        value 'FirstTo' will be added as the first 'To' as index given is zero.
        If index provided is greater than equal to the number of headers
        already provided then that value is added as last value for that header
        '''

        reqMsg = 'addsipheader {0} 0 {1} 0 {2}@'.format(
            self.msgid, headername, value)
        ''' 0 is added in message to tell that this header needs
        to be added in original message. second 0 is dummy '''

        return self.vapi._send_message(reqMsg, 'add_sip_header')

    def remove_sip_header(self, headername, value=''):
        '''Queued an action for removing given header from the original message

        :parameter headername: name of header that needs to be removed from
            original message
        :parameter value: value of header need to be matched for deletion
            of header

        >>> actions = self.srv.create_action_set()
        >>> actions.remove_sip_header('From')
        >>> actions.remove_sip_header('From','OldFrom')
        >>> actions.remove_sip_header('From:0')
        >>> actions.remove_sip_header('From:0','delFrom')

        Above example shows four different ways of using remove_sip_header.
        First without index and value, this one will delete all header with
        given header name.
        Second with a value, this one will delete all 'From' Header which
        contain OldFrom in their value.
        Third with an index will delete given header at the given index. In
        this example First From header will be deleted.
        Forth with both index and value will only consider index as index
        take precedence over value, and if both are provided only index
        is considered
        '''
        reqMsg = 'addsipheader {0} 1 {1} 0 {2}@'.format(
            self.msgid, headername, value)
        ''' 1 is added at the end of message to tell that this header needs to
        be deleted from original message. second 0 is dummy '''

        return self.vapi._send_message(reqMsg, 'remove_sip_header')

    def modify_sip_header(self, headername, value, oldValue='',
                          exclude_tag=False):
        '''Queued an action for removing given header from the original message

        :parameter headername: name of header that needs to be modified in
            original message
        :parameter value: New value of header given in headername and need to
            be put in original message
        :parameter oldValue: Value need to be matched in original message
        :parameter exclude_tag: Exclude From/To tag from owerwritting

        >>> actions = self.srv.create_action_set()
        >>> actions.modify_sip_header('Call-ID','newCallID')
        >>> actions.modify_sip_header('Call-ID','newCallID','oldCallID')
        >>> actions.modify_sip_header('Call-ID:0','newCallID')
        >>> actions.modify_sip_header('Call-ID:0','newCallID','oldCallID')

        Above example shows four different ways of using modify_sip_header
        First without index and without old value, this one will modify all
        header with given header name.
        Second with an old value, this one will modify all 'Call-ID' Header
        which contain OldCallID in their value.
        Third with an index will modify given header at the given index.
        In this example First(index 0) Call-ID header is deleted.
        Forth with both index and an old value will only consider index as
        index take precedence over value, and if both are provided only index
        is considered

        >>> actions.modify_sip_header('From','newValue', exclude_tag=True)

        Above example will modify 'From' header without replacing tag value.
        Here it will use old tag value as it is.
        '''
        if exclude_tag:
            exclude = '1'
        else:
            exclude = '0'

        if oldValue != '':
            msgTail = '\n{0}@'.format(oldValue)
        else:
            msgTail = '@'

        reqMsg = 'addsipheader {0} 2 {1} {2} {3} {4}'.format(
            self.msgid, headername, exclude, value, msgTail)

        ''' 2 is added at the end of message to tell that this header needs to
        be modified in original message '''

        return self.vapi._send_message(reqMsg, 'modify_sip_header')

    def add_sdp_attrib(self, media='none', typestr='',
                       attrib='', value=''):
        '''Adding sdp attrib with value given

        :parameter media: Value of the media. Default is session level
        :parameter typestr: Type of attribute.
        :parameter attrib: Name of attribute.
        :parameter value: Value of the attribute.

        >>> actions = self.srv.create_out_action_set()
        >>> actions.add_sdp_header(typestr='v',value='camelot')
        >>> actions.add_sdp_header('audio','a','fmtp','100')
        '''
        reqMsg = 'addsdpheader {0} 7 {1}:{2}:{3}:{4}@'.format(
            self.msgid, media, typestr, attrib, value)
        return self.vapi._send_message(reqMsg, 'add_sdp_attrib')

    def remove_sdp_session_attrib(self, typestr='', attrib='none', value=''):
        '''
        Retrieve SDP attributes for given values

        :parameter typestr: Type of attribute. If not provided all types will
                            be considered
        :parameter attrib: Name of attribute. If not provided all attributes
                            will be considered
        :parameter value: Value of the attribute. If not provided all
                          attributes will be considered.

        All parameters are optional.

        >>> actions = self.srv.create_out_action_set()
        >>> actions.remove_sdp_session_attrib('v')

        '''
        reqMsg = 'addsdpheader {0} 3 none:{1}:{2}:{3}@'.format(
            self.msgid, typestr, attrib, value)
        return self.vapi._send_message(reqMsg, 'remove_sdp_session_attrib')

    def remove_sdp_media_attrib(self, media='none', typestr='',
                                attrib='none', value=''):
        '''
        Retrieve SDP attributes for given values

        :parameter media: Value of the media. If not provided all
                          media will be considered.
        :parameter typestr: Type of attribute. If not provided all types will
                            be considered
        :parameter attrib: Name of attribute. If not provided all attributes
                            will be considered
        :parameter value: Value of the attribute. If not provided all
                          attributes will be considered.

        All parameters are optional.

        >>> serv = camelot.create_camelot_server(CamelotIp, CamelotPort)
        >>> out_action_obj = serv.create_out_action_set()
        >>> out_action_obj.modify_sdp_media_attrib(media='audio',
                                                    typestr='a',
                                                    value='sendrecv',
                                                    newvalue='sendonly')
        >>> actions.remove_sdp_media_attrib('video', 'a', 'rtpmap',
                                              value='125 UNKNOWN/0')
        >>> actions.remove_sdp_media_attrib('video_slides', 'a', 'rtpmap',
                                              value='125 UNKNOWN/0')
        >>> ep1.apply_out_action_set(actionset=out_action_obj,method='INVITE')

        First call to remove_sdp_media_attrib will remove all attributes
        under audio
        '''
        reqMsg = 'addsdpheader {0} 4 {1}:{2}:{3}:{4}@'.format(
            self.msgid, media, typestr, attrib, value)
        return self.vapi._send_message(reqMsg, 'remove_sdp_media_attrib')

    def modify_sdp_session_attrib(self, typestr='', attrib='none', value='',
                                  newvalue=''):
        '''
        Retrieve SDP attributes for given values

        :parameter typestr: Type of attribute. If not provided all types will
                            be considered
        :parameter attrib: Name of attribute. If not provided all attributes
                            will be considered
        :parameter value: Value of the attribute. If not provided all
                          attributes will be considered.
        :parameter newvalue: new Value of the attribute.

        All parameters are optional.

        >>> actions = self.srv.create_out_action_set()
        >>> actions.modify_sdp_session_attrib('t', value='0 0', newvalue='1 2')

        '''
        reqMsg = 'addsdpheaderoao {0} 5 none:{1}:{2}:{3}:{4}@'.format(
            self.msgid, typestr, attrib, value, newvalue)
        return self.vapi._send_message(reqMsg, 'modify_sdp_session_attrib')

    def modify_sdp_media_attrib(self, media='none', typestr='',
                                attrib='none', value='', newvalue=''):
        '''
        Retrieve SDP attributes for given values

        :parameter media: Type of media. audio or video or video_slides
        :parameter typestr: Type of attribute. If not provided all types will
                            be considered
        :parameter attrib: Name of attribute. If not provided all attributes
                            will be considered
        :parameter value: Value of the attribute. If not provided all
                          attributes will be considered.
        :parameter newvalue: new Value of the attribute.

        All parameters are optional.

        >>> actions = self.srv.create_out_action_set()
        >>> actions.modify_sdp_media_attrib('audio', 'a', value='0 0',
                                            newvalue='1 2')
        >>> actions.modify_sdp_media_attrib('video', 'a', 'rtpmap',
                                             value='125 UNKNOWN/0',
                                             newvalue='125 AV1/90000')
        >>> actions.modify_sdp_media_attrib('video_slides', 'a', 'rtpmap',
                                             value='125 UNKNOWN/0',
                                             newvalue='125 AV1/90000')
        '''
        reqMsg = 'addsdpheaderoao {0} 6 {1}:{2}:{3}:{4}:{5}@'.format(
            self.msgid, media, typestr, attrib, value, newvalue)
        return self.vapi._send_message(reqMsg, 'modify_sdp_media_attrib')

    def add_sdp_lines_port0(self, sdp_list, m_index=-1):
        '''Add m= line with port 0 and corresponding m lines at the end of sdp.

        :parameter sdp_list: is a list containing sdp objects[m line,
         attributes]\n
         [sdpLineObject(mline),sdpLineObject(atr1),sdpLineObject(atr2)]
        :parameter m_index: index of m=line, where this port 0 m=line
         to be inserted. If not provided (default) inserted as a last
         m=line.

        NOTE: This API can be used for Simulated Endpoints as well.
              i.e., the endpoint need not to be RawEndpoint.


        >>> actions = self.srv.create_out_action_set()
        >>> actions.add_sdp_lines_port0(sdp_list, 3)
        '''
        try:
            for j in sdp_list:
                if isinstance(j, sdpLineObject):
                    if m_index == -1:
                        val = j.value
                    else:
                        val = str(m_index) + "@@" + j.value
                    if j.attrtype == 'm':
                        self.add_extra_sdp_line(
                            j.media, j.attrtype, value=val)
                    else:
                        self.add_extra_sdp_line(
                            j.media, j.attrtype, attrib=j.attr, value=val)
                else:
                    log.error('sdp passed is not an instance of sdpLineObject')
        except Exception as e:
            log.error('add_sdp_lines_port0 failed --->[%s]' % e)
            return False
        return True

    def add_extra_sdp_line(self, media='none', type_attr='',
                           attrib='', value=''):
        '''Adding sdp attrib with value given, at the end of sdp blindly.

        :parameter media: Value of the media. Default is session level
        :parameter type_attr: Type of attribute.
        :parameter attrib: Name of attribute.
        :parameter value: Value of the attribute.

        >>> actions = self.srv.create_out_action_set()
        >>> actions.add_extra_sdp_line(typestr='v',value='camelot')
        >>> actions.add_extra_sdp_line('audio','a','fmtp','100')
        '''
        reqMsg = 'addsdpheader {0} 8 {1}:{2}:{3}:{4}@'.format(
            self.msgid, media, type_attr, attrib, value)
        return self.vapi._send_message(reqMsg, 'add_sdp_attrib')

    def get_media_type(self, sdp_list):
        '''this gives the type of media line

        :parameter sdp_list: is a list contaning sdp objects[m line,
         attributes].
         [sdp(mline),sdp(atr1),sdp(atr2)]

        :returns: will be a string AUDIO, VIDEO, BFCP,PRESENTATION_VIDEO, IX
         or FECC.

        NOTE: This API can be used for Simulated Endpoints as well.
              i.e., the endpoint need not to be RawEndpoint.


        >>> actions = self.srv.create_out_action_set()
        >>> actions.get_media_type(sdp_list)
            BFCP
        '''
        sdp_type = None
        is_video = False

        for i in sdp_list:
            if i.media == 'application':
                if 'bfcp' in i.value.lower():
                    sdp_type = 'BFCP'
                    break
                elif 'ix' in i.value.lower():
                    sdp_type = 'IX'
                    break
                else:
                    sdp_type = 'FECC'
                    break
            elif i.media == 'video':
                isvideo = True
                if i.value.lower() in ['slides', 'speaker', 'alt']:
                    sdp_type = 'PRESENTATION_VIDEO'
                    break
            elif i.media == 'audio':
                sdp_type = 'AUDIO'
                break

        if is_video and sdp_type != 'PRESENTATION_VIDEO':
            sdp_type = 'VIDEO'

        return sdp_type


class InActionObject(object):

    def __init__(self, camelotconn, msgstr):
        self.vapi = camelotconn
        self.msgid = msgstr
        self.event_type = ''
        self.sub_type = None

    def add_verify_sip_header(self, headername, value, mode=0):
        '''
        Queued an action for validating given header in the original message

        :parameter headername: name of header needs to be verified
        :parameter value: value of header given to be verified as
            value of given header
        :parameter mode: (optional) parameter mode is 1 if exact match is
            required else 0 (default value)

        >>> validation = self.srv.create_in_action_set()
        >>> validation.add_verify_sip_header('Allow-Events','kpml,dialog',1)
        >>> validation.add_verify_sip_header('Supported','X-cisco-serviceuri')
        >>> ep.start_validation_event(callback_handler,validation,
                                                     method='INVITE')

        Above example will validate two things
        1) If 'Allow-Events' value is exactly 'kpml,dialog' or not
        2) If 'Supported' value contains 'X-cisco-serviceuri' or not
        If both the conditions are true callback handler will get '1' else '0'
        '''

        reqMsg = 'addsipheader {0} {1} {2} 0 {3}@'.format(
            self.msgid, mode, headername, value)

        ''' 0 is dummy '''

        return self.vapi._send_message(reqMsg, 'add_verify_sip_header')

    def get_verify_sip_header(self, index):
        '''
        Get a validation header from InActionObject

        :parameter index: index of the header to be extracted

        >>> validation = self.srv.create_in_action_set()
        >>> validation.add_verify_sip_header('Allow-Events','kpml,dialog',1)
        >>> validation.add_verify_sip_header('Supported','X-cisco-serviceuri')
        >>> validation.get_verify_sip_header(1)

        Above example will get the header stored at first postion which
        may be different then header added first to the InActionSet
        '''
        reqMsg = 'getsipheaderatindex {0} {1}@'.format(self.msgid, index)
        response = self.vapi._send_query(reqMsg, 'get_verify_sip_header')
        if response == '{}':
            return {}
        res_list = response.split("\n")
        ret_dict = {}
        ret_dict['header'] = res_list[0]
        ret_dict['value'] = res_list[1]
        ret_dict['mode'] = res_list[2]

        return ret_dict


class MsgObject(object):

    def __init__(self, camelotconn, msgstr):
        self.vapi = camelotconn
        self.msgid = msgstr

    def __str__(self):
        createmsg = 'getsipmessage {0}@'.format(self.msgid)
        hex_len = self.vapi._get_message_length_hex(createmsg)
        rawmessage = 'f:00000000:{0}:{1}'.format(hex_len, createmsg)
        with_new_line = self.vapi._camelot_query(rawmessage)
        if with_new_line:
            return with_new_line

    def add_sip_header(self, headername, value):
        '''
        Add given header to Raw message

        :parameter headername: name of header needs to be added
        :parameter value: value of header given in headername

        :returns: returns header_id of added header

        >>> msg = self.srv.create_message()
        >>> msg.add_sip_header('To','<sip:[sip.raw.dn]@[sip.cm.cm1ip]>')

        Above example will add new 'To' Header to raw message.
        Header will be added at the end of similar headers, so
        if there are 'To' Headers already present, header added
        above will be added at the end
        While creating message or adding sip header all configuration
        parameters can be used. Along with them few special purpose
        configuration parameters are also present\n
        1) auto.sip.call.newcallid: This tag will generate a new call-id\n
        2) auto.sip.time.currtime: This will be used to generate value
                                    for Date field\n
        3) auto.sip.signalling.port: This port will place endpoint signalling
                                    port, used in via and contact\n
        4) auto.sip.call.contentlen: This will calculate length of SDP and put
                                    that value here\n
        5) auto.sip.via.branch: This will generate new branch for via\n
        6) auto.sip.tag: This will generate new tag which can be used in To or
                                    From\n
        '''
        reqMsg = 'addsipheader {0} 0 {1} 0 {2}@'.format(
            self.msgid, headername, value)
        return self.vapi._send_message(reqMsg, 'add_sip_header')

    def remove_sip_header(self, header):
        '''
        Remove given header from Raw message

        :parameter header: header name or header id to be removed

        >>> msg = self.srv.create_message(SipTemplateMethods.SIP_INVITE)
        >>> to_id = msg.add_sip_header('To','<sip:12345@[sip.cm.cm1ip]>')
        >>> msg.remove_sip_header(to_id)
        >>> msg.remove_sip_header('From')

        In above example
        First remove_sip_header will remove To header pointed by to_id
        if there are more 'To' headers added then also only the header
        pointed by to_id will be removed
        Second remove_sip_header will remove all 'From' header,
        i.e. if there are more than one 'From' header present all will be
        removed
        '''
        reqMsg = 'removesipheader {0} {1} @'.format(self.msgid, header)
        return self.vapi._send_message(reqMsg, 'remove_sip_header')

    def get_sip_header(self, headername):
        '''
        Get value(s) for given header

        :parameter header: header name or header id to be retrieved

        :returns: return dictionary with header_id as key and
                    header value as values

        >>> msg = self.srv.create_message(SipTemplateMethods.SIP_INVITE)
        >>> to_id = msg.add_sip_header('To','<sip:12345@[sip.cm.cm1ip]>')
        >>> msg.get_sip_header(to_id)
        >>> msg.get_sip_header('Via')

        In above example
        First get_sip_header will retrieve 'To' header pointed by to_id
        if there are more 'To' headers added then also the header
        pointed by to_id will be retrieved
        Second get_sip_header will retrieve all 'Via' header,
        i.e. if there are more than one 'Via' header present all will be
        retrieved
        '''
        ret_dict = {}
        reqMsg = 'getsipheader {0} {1}@'.format(self.msgid, headername)
        response = self.vapi._send_query(reqMsg, 'get_sip_header')

        if not response or response == '{}':
            return {}

        res_list = response.split("{")
        if res_list:
            for x in range(1, len(res_list)):
                res_list[x] = res_list[x].replace("}", "")
                if res_list[x]:
                    hdr = res_list[x].split("\n")
                    ret_dict[hdr[0]] = hdr[1]
        return ret_dict

        '''
        createmsg = 'getsipheader' + ' ' + self.msgid + ' ' + headername + '@'
        hex_len = self.vapi.get_message_length_hex(createmsg)
        rawmessage = 'f:' + '00000000:' + hex_len + ':' + createmsg
        with_new_line = self.vapi._camelot_query(rawmessage)
        if with_new_line:
                err_list = with_new_line.split(":", 3)
                if err_list[3] == "{}":
                    return ret_dict
                res_list = with_new_line.split("{")
                if res_list:
                    for x in range(1, len(res_list)):
                        res_list[x] = res_list[x].replace("}", " ")
                        if res_list[x]:
                            hdr = res_list[x].split("\n")
                            ret_dict[hdr[0]] = hdr[1]

                if ret_dict:
                    return ret_dict
                else:
                    log.error('Not able to parse Header')
        else:
            log.error('Connection to Camelot failed')
        '''

    def modify_sip_header(self, header, value, exclude_tag=False):
        '''
        Modify value for given header id

        :parameter header: header name or header id to be modified
        :parameter value: value of header given in header name
        :parameter exclude_tag: Exclude From/To tag from owerwritting

        >>> msg = self.srv.create_message(SipTemplateMethods.SIP_INVITE)
        >>> msg.modify_sip_header('To','<sip:12345@[sip.cm.cm1ip]>')
        >>> from_dict = msg.get_sip_header('From')
        >>> from_id = from_dict.keys[0]
        >>> msg.modify_sip_header(from_id)

        In above example
        First modify_sip_header will modify all 'To' headers to new value
        Second modify_sip_header will modify from header pointed by from_id

        >>> msg.modify_sip_header('From','newValue', exclude_tag=True)

        Above example will modify 'From' header without replacing tag value.
        Here it will use old tag value as it is.
        '''
        if exclude_tag:
            exclude = '1'
        else:
            exclude = '0'

        reqMsg = 'modifysipheader {0} {1} {2} {3}@'.format(
            self.msgid, header, exclude, value)
        return self.vapi._send_message(reqMsg, 'modify_sip_header')

    def add_sdp_attrib(self, media, typestr, attrib, value):
        '''
        Add SDP attrib in Raw Message

        :parameter media: Name of media in which attrib needs to be added
                            value will remain 'none' for session level attribs
        :parameter typestr: Type of attribute added values can be 'a/m/o' etc.
        :parameter attrib: Attribute which needs to be added, it can be blank
        :parameter value: Value of attribute to be added

        :returns: It returns attrib_id of newly added attribute

        Using this function a line in below format will be added
        under given media

        if attirb is not blank
            type=attrib:value

        if attrib is blank
            type=value

        >>> msg = self.srv.create_message(SipTemplateMethods.SIP_INVITE,
                                            'media'='audio')
        >>> msg.add_sdp_attrib('audio','a','ptime','20')
        >>> msg.add_sdp_attrib('audio','a','','sendonly')

        In above example
        First add_sdp_attrib will add a=ptime:20 in audio
        Second add_sdp_attrib will add a=sendonly in audio
        '''
        reqMsg = 'addsdpheader {0} 0 {1}:{2}:{3}:{4}@'.format(
            self.msgid, media, typestr, attrib, value)
        return self.vapi._send_message(reqMsg, 'add_sdp_attrib')

    def add_sdp_attrib_after(self, attr_id, media, typestr, attrib, value):
        '''
        Add SDP attrib after a particular sdp attribute

        :parameter attr_id: ID of attribute after which we want to add this
                            attribute
        :parameter media: Name of media in which attrib needs to be added
                            value will remain 'none' for session level attribs
        :parameter typestr: Type of attribute added values can be 'a/m/o' etc.
        :parameter attrib: Attribute which needs to be added, it can be blank
        :parameter value: Value of attribute to be added

        :returns: It returns attrib_id of newly added attribute

        This will create a new attribute and place it after attribute
        referred using attr_id

        >>> msg = self.srv.create_message(SipTemplateMethods.SIP_INVITE,
                                                        'media'='audio')
        >>> attr_id = msg.add_sdp_attrib('audio','a','ptime','20')
        >>> msg.add_sdp_attrib_after(attr_id,'audio','a','','sendonly')

        In above example
        add_sdp_attrib will add a=ptime:20 in audio
        add_sdp_attrib_after will add a=sendonly in audio just after
        attribute added in line above
        '''
        reqMsg = 'addsdpheaderafter {0} 0 {1} {2}:{3}:{4}:{5}@'.format(
            self.msgid, attr_id, media, typestr, attrib, value)
        return self.vapi._send_message(reqMsg, 'add_sdp_attrib_after')

    def modify_sdp_attrib(self, attr_id, value):
        '''
        Modify SDP attribute pointed by attr_id.

        :parameter attr_id: ID of attribute after which we want to add this
                            attribute.
        :parameter value: New value to be placed after modification.
                          This function will modify existing attribute

        >>> msg = self.srv.create_message(SipTemplateMethods.SIP_INVITE,
                                                        'media'='audio')
        >>> attr_id = msg.add_sdp_attrib('audio','a','ptime','20')
        >>> msg.modify_sdp_attrib(attr_id,'50')
        In above example first call to add_sdp_attrib will add a new attribute
        And then call to modify_sdp_attrib will change its value to 50
        Making resultant attribute
        a=ptime:50
        '''
        reqMsg = 'modsdpheader {0} {1} {2}@'.format(
            self.msgid, attr_id, value)
        return self.vapi._send_message(reqMsg, 'modify_sdp_attrib')

    def remove_sdp_attrib(self, attr_id):
        '''
        Remove SDP attribute pointed by attr_id

        :parameter attr_id: ID of attribute to be removed

        This fucntion will remove attribute line

        >>> msg = self.srv.create_message(SipTemplateMethods.SIP_INVITE,
                                                        'media'='audio')
        >>> sdp = get_sdp_attrib('audio','a')
        >>> for m in range(0, len(sdp)):
        >>>    if sdp[m].value == 'sendrecv'
        >>>        msg.remove_sdp_attrib(sdp[m].sdpid)
        >>>        break

        Above Example will remove sendrecv attrib
        '''
        reqMsg = 'removesdpheader {0} {1}@'.format(self.msgid, attr_id)
        return self.vapi._send_message(reqMsg, 'remove_sdp_attrib')

    def get_sdp_attrib(self, media='', typestr='', attrib='none', value=''):
        '''
        Retrieve SDP attributes for given values

        :parameter media: Name of media for which attributes need to be
                            retrieved. If not provided or left blank will
                            return attribute for all media including session
                            level attributes
        :parameter typestr: Type of attribute. If not provided all types will
                            be considered
        :parameter attrib: Name of attribute. If not provided all attributes
                            will be considered

        :returns: It returns list of attributes matching given condition

        All parameters are optional.

        >>> msg = self.srv.create_message(SipTemplateMethods.SIP_INVITE,
                                                        'media'='audio')
        >>> sdp_audio = get_sdp_attrib('audio','a')
        >>> sdp_all = get_sdp_attrib()

        First call to get_sdp_attrib will return all attributes of type 'a'
        under audio
        Second call to get_sdp_attrib will return all attributes in SDP
        '''
        media_list = list()
        reqMsg = 'getsdpheader {0} {1}:{2}:{3}:{4}@'.format(
            self.msgid, media, typestr, attrib, value)
        response = self.vapi._send_query(reqMsg, 'get_sdp_attrib')
        if response == '{}':
            return media_list

        res_list = response.split('{')
        if res_list:
            for x in range(1, len(res_list)):
                res_list[x] = res_list[x].replace('}', '')
                hdr = res_list[x].split('\n')
                mediaidx = hdr[0]
                lineid = hdr[1]
                mediatype = hdr[2]
                attrtype = hdr[3]
                attr = hdr[4]
                val = hdr[5]
                sdpline = sdpLineObject(mediaidx, lineid, mediatype, attrtype,
                                        attr, val)
                media_list.append(sdpline)

            return media_list

        '''
        addsdpattrib = ('getsdpheader' + ' ' + self.msgid + ' ' + media + ':' +
                        typestr + ':' + attrib + '@')
        hex_len = self.get_message_length_hex(addsdpattrib)
        rawmessage = 'f:' + '00000000:' + hex_len + ':' + addsdpattrib
        with_new_line = self.vapi._camelot_query(rawmessage)
        if with_new_line:
            err_list = with_new_line.split(':', 3)
            if err_list[3] == '{}':
                return media_list
            res_list = with_new_line.split('{')
            if res_list:
                for x in range(1, len(res_list)):
                    res_list[x] = res_list[x].replace('}', ' ')
                    hdr = res_list[x].split('\n')
                    lineid = hdr[0]
                    mediatype = hdr[1]
                    attrtype = hdr[2]
                    attr = hdr[3]
                    val = hdr[4]
                    sdpline = sdpLineObject(lineid, mediatype, attrtype, attr,
                                            val)
                    media_list.append(sdpline)

                return media_list
            else:
                log.error('get_sdp_sttrib failed')
        else:
            log.error('Camelot request for sdp attr failed')
        '''

    def add_raw_body(self, msgType, bodyStr):
        '''Add body other than SDP

        :parameter msgType: type of message,
                            this will be used in Content-Type field
        :parameter bodyStr: actual body which will be added in message

        >>> msgObj = self.srv.create_message(msgStr)
        >>> msgObj.add_raw_body(msgType,bodyStr)

        Above example will create a message with headers generated using msgStr
        and bodyStr will be added as it is in body
        and given msgType will be added to Content-Type
        '''

        reqMsg = 'addrawbody {0} {1} {2}@'.format(self.msgid, msgType, bodyStr)
        return self.vapi._send_message(reqMsg, 'remove_sdp_attrib')

    def remove_raw_body(self):
        '''Remove raw body if present and do nothing if raw body is not present

        >>> msgObj = self.srv.create_message(msgStr)
        >>> msgObj.remove_raw_body()

        In above example we are assuming that msgStr have rawbody included
        then call to remove_raw_body will remove that body
        '''
        reqMsg = 'removerawbody {0}@'.format(self.msgid)
        return self.vapi._send_message(reqMsg, 'remove_sdp_attrib')

    def get_raw_body(self):
        '''Get raw body added earlier '{}' will be returned
        if no raw body is added

        :returns: It returns a string consisting of raw body of message

        >>> msgObj = self.srv.create_message(msgStr)
        >>> msgObj.add_raw_body(msgType,bodyStr)
        >>> msgObj.get_raw_body()

        In above example get_raw_body will return a string consisting
        of raw body text
        '''

        reqMsg = 'getrawbody {0}@'.format(self.msgid)
        return self.vapi._send_query(reqMsg, 'get_sdp_attrib')

    def get_sdp_lines_port0(self, sdp_list):
        '''get all mlines with its attribute lines having port 0.

        :parameter sdp_list: this is a list of sdp message returned by
         get_sdp_attrib().

        :returns: is a list of lists with mline having port 0 .
         contaning sdp objects m line and corresponding attribute lines.
         [[sdpLineObject1(mline),sdpLineObject1(atr1),sdpLineObject1(atr2)],
         [sdpLineObject2(mline),sdpLineObject2(atr1),sdpLineObject2(atr2)]]

        NOTE: This API can be used for Simulated Endpoints as well.
              i.e., the endpoint need not to be RawEndpoint.


        >>> msgObj = self.srv.create_message(msgStr)
        >>> sdplist =  msgObj.get_sdp_attrib()
        >>> msgObj.get_sdp_lines_port0(sdplist)
        '''
        sdp_element = []
        port0_found = False
        sdp_main_list = []
        try:
            for i in sdp_list:
                if isinstance(i, sdpLineObject):
                    if i.attrtype == 'm':
                        if i.value.split()[0] == '0':
                            if port0_found:
                                sdp_main_list.append(sdp_element)
                                sdp_element = []
                            port0_found = True
                            sdp_element.append(i)
                        else:
                            port0_found = False
                    elif port0_found:
                        if i.attrtype == 'a':
                            sdp_element.append(i)
                else:
                    log.error('sdp passed is not an instance of sdpLineObject')
            if len(sdp_element):
                sdp_main_list.append(sdp_element)
        except Exception:
            log.exception('failed to extract reason:')
        return sdp_main_list


class sdpLineObject:

    def __init__(self, mediaidx, lineid, mediatype, attrtype, attr, value):
        self.mediaidx = mediaidx
        self.sdpid = lineid
        self.media = mediatype
        self.attrtype = attrtype
        self.attr = attr
        self.value = value
