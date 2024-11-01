'''
Created on 16-Sep-2013

@author: smaturi
'''
import re
import json
from camelot.response import CallInfoExt
from camelot.utils import common_utils
import camelot
from camelot import camlogger
from collections import OrderedDict

log = camlogger.getLogger(__name__)


class CamelotDecodeHelper(object):

    def parse_detailed(self, msg, msg_type=None):
        ret_dict = dict()
        l_index = msg.find('{')
        if l_index == -1:
            return
        char_index = 0
        send_line = ''
        while char_index < len(msg):
            r_index = msg.find('}', char_index)
            if r_index == -1 or char_index >= len(msg):
                return
            char_index = r_index + 1
            attr = msg[l_index:r_index + 1]
            send_line = attr
            ret_val = dict()
            if send_line.count('{') == send_line.count('}'):
                if '{attribute {{' in send_line:
                    val_index = send_line.find('{', 2)
                    val_end_index = send_line.rfind('}', 0, len(send_line))
                    ret_val['attribute'] = send_line[val_index:val_end_index]
                else:
                    ret_val = (self.
                               parse_single_line_to_key_value_pair(send_line))
                l_index = msg.find('{', char_index)
                send_line = ''
                for k in ret_val:
                    key = k
                    value = ret_val[k]
                if key:
                    ret_dict[key] = value
                pass
            else:
                continue

        if msg_type == camelot.GET_CALL_INFO_EXT:
            ret_obj = CallInfoExt()
            ret_obj._copy_from_dict(ret_dict)
            return ret_obj
        else:
            return ret_dict

    def complex_parse_return_lines(self, response):
        str_list = []
        response = response.strip()
        open_braces = 0
        start = response.index('{')
        i = start
        str_tmp = ''
        while i < len(response):
            tmp = response[i]
            if tmp == '{':
                open_braces += 1
            elif tmp == '}':
                open_braces -= 1
            i += 1
            str_tmp += tmp

            if open_braces == 0:
                str_list.append(str_tmp)
                str_tmp = ''
                try:
                    start = response.index('{', i)
                    i = start
                except Exception:
                    break
                if start == -1:
                    break
        return str_list

    def complex_parse_list_into_dict(self, str_list, msg_type=None):
        ret_dict = {}
        for stri in str_list:
            if '{{{' in stri:
                ind = stri.index('{')
                if stri[ind + 1] == '{':
                    key = stri[ind + 2:stri.index('}')]
                else:
                    try:
                        next_start = stri.index('{', ind + 1)
                        key = stri[ind + 1:next_start - 1]
                        key = key.strip()
                    except Exception:
                        next_blanc = stri.index('{', ind + 1)
                        key = stri[ind + 1:next_blanc]
                        key = key.strip()
                pass_str = stri[stri.index('{{{') + 1:stri.index('}}}') + 1]
                value = self.parse_info(pass_str, msg_type)
            else:
                ret_val = self.parse_single_line_to_key_value_pair(stri)
                for k in ret_val:
                    key = k
                    value = ret_val[k]
            if key:
                ret_dict[key] = value
        return ret_dict

    def complex_parse_stream_info(self, response):
        ret_dict = {}
        if not response:
            log.error('parse_complex_response: Response in NULL')
            return
        str_list = self.complex_parse_return_lines(response)
        if isinstance(str_list, list):
            ret_dict = self.parse_stream_info_list_into_dict(str_list)
        else:
            log.error('Failed to parse the event output')
            return
        return ret_dict

    def parse_stream_info_list_into_dict(self, str_list):
        ret_dict = {}
        for stri in str_list:
            if '{{{' in stri:
                ind = stri.index('{')
                if stri[ind + 1] == '{':
                    key = stri[ind + 2:stri.index('}')]
                else:
                    try:
                        next_start = stri.index('{', ind + 1)
                        key = stri[ind + 1:next_start - 1]
                        key = key.strip()
                    except Exception:
                        next_blanc = stri.index('{', ind + 1)
                        key = stri[ind + 1:next_blanc]
                        key = key.strip()
                pass_str = stri[stri.index('{{{') + 1:stri.index('}}}') + 1]
                value = self.parse_info(pass_str)
            elif 'floorId' in stri:
                key = stri[stri.index('{') + 1:stri.index(' ')]
                if key:
                    pass_str = stri[len(key) + 1 + 1:stri.rindex('}')]
                    value = self.complex_parse(pass_str)
                    for k in value:
                        value[k] = value[k].strip().split()
            elif 'simulcast codecs' in stri:
                key = stri[stri.index('{') + 1 + 1:stri.index('}')].strip()
                if stri[stri.rindex('}') - 1] == '}':
                    pass_str = stri[stri.index('}') + 2 + 1:stri.rindex(
                                    '}}')].strip()
                    value = self.parse_info(pass_str)
            else:
                ret_val = self.parse_single_line_to_key_value_pair(stri)
                for k in ret_val:
                    key = k
                    value = ret_val[k]
            if key:
                ret_dict[key] = value
        return ret_dict

    def complex_parse(self, response, msg_type=None):
        ret_dict = {}
        if not response:
            log.error('parse_complex_response: Response in NULL')
        str_list = self.complex_parse_return_lines(response)
        if isinstance(str_list, list):
            ret_dict = self.complex_parse_list_into_dict(str_list, msg_type)
        else:
            log.error('Failed to parse the event output')
        return ret_dict

    def parse_list_of_dict(self, response):
        ret_list = []
        if not response:
            log.error('parse_list_of_dict: Response is NULL')
            raise Exception("parse_list_of_dict: Response is NULL")
        str_list = self.complex_parse_return_lines(response)
        for list1 in str_list:
            ret_dict = self.parse_info(list1)
            ret_list.append(ret_dict)
        return ret_list

    def parse_logmask(self, response):
        pat = re.compile(r'{\w+\}|{\w+\s[0-9:/.]+}|{\w+\s\w+}|{{*[^{}]*}*')
        attribs = re.findall(pat, response)
        key_val = {}
        limit = len(attribs)
        for i in xrange(0, limit, 3):
            int_dict = {}
            if not attribs[i] or '(null)' in attribs[i]:
                continue
            mainkey = attribs[i][1:-1]
            fstkey = attribs[i + 1].split()[0][1::]
            val1 = attribs[i + 1].split()[1][:-1]
            sndkey = attribs[i + 2].split()[0][1::]
            val2 = attribs[i + 2].split()[1][:-1]
            val2 = val2.strip('}')
            int_dict[fstkey] = val1
            int_dict[sndkey] = val2
            key_val[mainkey] = int_dict
            if (i + 2) >= limit:
                break
            i += 2
        return key_val

    def parse_info(self, info, msg_type=None):

        pat = re.compile(r"""{\w+\s}|
                            {\w+\s[\w0-9:/.@-]+}|
                            {\w+\s\w+}|
                            {\w+\s\+\w+}|
                            {{*[^{}]*}*
                        """
                         '\s{*[^{}]*}*}', re.VERBOSE)
        attribs = re.findall(pat, info)
        ret_dict = {}
        for attr in attribs:
            ret_val = self.parse_single_line_to_key_value_pair(attr)
            for k in ret_val:
                if msg_type == camelot.GET_TFTP_INFO:
                    key = k
                else:
                    key = k.lower()
                value = ret_val[k]
            if key:
                ret_dict[key] = value
        '''
        if msg_type == camelot.GET_INFO:
            ret_obj = EndpointInfo()
            ret_obj._copy_from_dict(ret_dict)
            return ret_obj
        elif msg_type == camelot.GET_INFO_EXT:
            ret_obj = EndpointInfoExt()
            ret_obj._copy_from_dict(ret_dict)
            return ret_obj
        elif msg_type == camelot.GET_CALL_INFO:
            ret_obj = CallInfo()
            ret_obj._copy_from_dict(ret_dict)
            return ret_obj
        '''
        return ret_dict

    def parse_single_line_to_key_value_pair(self, line):
        attr = line
        attr = attr.strip()
        len_val = len(attr)
        val_start_index = attr.rindex('{')
        key_end_index = attr.index('}')
        key_start_index = attr.index('{')
        value = None
        if val_start_index < 2 and key_end_index == (len_val - 1):
            key = attr[val_start_index + 1: attr.index(' ')]
            value = attr[attr.index(' ') + 1:key_end_index]
        elif val_start_index < 2:
            key = attr[val_start_index + 1: key_end_index]
            value = attr[attr.index(' ', key_end_index) + 1: len_val - 1]
        elif key_end_index == (len_val - 2):
            key = attr[attr.index('{') + 1:attr.index(' ')]
            value = attr[val_start_index + 1:key_end_index]
        elif 'buttons' in line:
            key_end_index = attr.index('{', key_start_index + 1)
            key = attr[key_start_index + 1:key_end_index - 1]
            val_start_index = key_end_index
            val_end_index = attr.rindex('}')
            value = attr[val_start_index + 1:val_end_index - 2]
            valuelist = value.split('}')
            vlist = []
            if valuelist:
                for val in valuelist:
                    vlist.append(val.strip().strip('{'))
            value = vlist
        elif 'register_supported' in line:
            key_start_index = attr.index('{{')
            key_end_index = attr.index('}')
            key = attr[key_start_index + 2:key_end_index]
            # {{register_supported} {{X-cisco-sis-8.0.0}}}
            val_start_index = attr.rindex('{{')
            try:
                val_end_index = attr.index('}}}')
                value = attr[val_start_index + 2:val_end_index]
                valuelist = value.split('}')
                vlist = []
                if valuelist:
                    for val in valuelist:
                        vlist.append(val.strip().strip('{'))
                value = vlist
            except Exception:
                vlist = []
                value = vlist
        elif 'current calls' in line:
            key_start_index = attr.index('{')
            key_end_index = attr.index('}')
            key = attr[key_start_index + 2:key_end_index]
            len_val = len(attr)
            tmpVal = attr[key_end_index + 2:len_val]
            pat = re.compile(r'{\w+\s+\w}')
            valuelist = re.findall(pat, tmpVal)
            pat = re.compile(r'\w+\s\w')
            value = {}
            for v in valuelist:
                vkey = re.findall(pat, v)
                if len(vkey) == 1:
                    data = vkey[0].split(' ')
                    if len(data) == 2:
                        value[data[0]] = data[1]

        elif 'missedcallinfo' in line or \
             'placedcallinfo' in line:
            value = {}
            key_start_index = attr.index('{')
            key_end_index = attr.index('{', key_start_index + 1)
            key = attr[key_start_index + 1:key_end_index - 1]
            if 'from' in line or \
               'to' in line:
                value_end_index = len_val
                tmpVal = attr[key_end_index + 2:value_end_index]
                vlist = tmpVal.split('} {')
                for v in vlist:
                    values = v.split(' ')
                    if len(values) == 2:
                        if ('missedcalls' in v or
                                'placedcalls' in v or 'on' in v):
                            value[values[0]] = values[1]
                        elif 'from' in v:
                            value[values[0][1:]] = values[1]
                        elif 'at' in v:
                            value[values[0]] = values[1][:8]

            else:
                value_end_index = attr.index('}', key_end_index)
                tmpVal = attr[key_end_index + 2:value_end_index]
                vlist = tmpVal.split(' ')
                if(len(vlist) == 2):
                    value[vlist[0]] = vlist[1]

        elif 'rtprxstats' in attr or 'rtptxstats' in attr:
            line = attr[val_start_index + 1:attr.index('}',
                                                       val_start_index)]
            key, value = line.split()

        elif 'jabber_profile' in attr:
            l_dict = {}
            val_start_index = attr.index('{', 2)
            key_end_index = attr.index('}')
            key_start_index = attr.index('{')
            line = attr[val_start_index - 1 + 1:attr.rindex('}',
                                                            val_start_index)]
            key = attr[attr.rindex('{', 0, key_end_index) +
                       1:key_end_index]
            l_dict = json.loads(line)
            return {key: l_dict}

        else:
            value = attr[val_start_index + 1:attr.index('}',
                                                        val_start_index)]
            key = attr[attr.rindex('{', 0, key_end_index) +
                       1:key_end_index]

        return {key: value}

    def parse_getcalls(self, output):

        pat = re.compile(r'{\w+\s\w+\s\w+}')
        attribs = re.findall(pat, output)
        call_list = list()
        for attr in attribs:
            attr = attr.strip()
            value = attr[attr.index('{') + 1:attr.index('}')]
            arr = value.split(' ')
            if arr and len(arr) == 3:
                call_dict = {'call_ref': arr[0], 'line_ref': arr[1],
                             'state': arr[2],
                             'Ref': arr[0], 'Id': arr[0],
                             'Line': arr[1], 'CallState': arr[2]}
                # call = Call()
                # call._copy_from_dict(call_dict)
                call_list.append(call_dict)
        return call_list

    def parse_holdreversionreq_1(self, output):
        output = output.strip()
        temp = eval(output)
        return temp

    def parse_get_streams(self, output):
        output = output.strip()
        pat = re.compile(r'{[\w+\s]*\w+\s*}')
        attribs = re.findall(pat, output)
        streams_list = []
        for attr in attribs:
            attr = attr.strip()
            value = attr[attr.index('{') + 1:attr.index('}')]
            arr = value.split(' ')
            if arr and len(arr) == 6:
                stream_dict = {'stream_ref': arr[0], 'call_ref': arr[1],
                               'type': arr[2], 'direction': arr[3],
                               'state': arr[4], 'mifctype': arr[5],
                               'StrmID': arr[0], 'CallId': arr[1],
                               'Type': arr[2]
                               }
                # stream = Stream()
                # stream._copy_from_dict(stream_dict)
                streams_list.append(stream_dict)
        return streams_list

    def parse_get_confid_list(self, output):
        output = output.strip()
        # print 'parse_get_confid_list ', output
        # pat = re.compile(r'{[\w+\s]*\w+}')
        pat = re.compile(r'{[\w0-9\s]*\w}')
        attribs = re.findall(pat, output)
        # print 'attibs ', attribs
        streams_list = []
        for attr in attribs:
            attr = attr.strip()
            value = attr[attr.index('{') + 1:attr.index('}')]
            arr = value.split(' ')
            # print "[%s]" % arr
            if arr:
                stream_dict = {'confid': arr[0], 'status': arr[1]
                               }

                streams_list.append(stream_dict)
        return streams_list

    def parse_get_lines(self, output):
        output = output.strip()
        pat = re.compile(r'{[\w\s.\\[\]+:@-]*}')
        attribs = re.findall(pat, output)
        attribs[0] = attribs[0].replace('\\', '')
        line_list = []
        for attr in attribs:
            attr = attr.strip()
            value = attr[attr.index('{') + 1:attr.index('}')]
            arr = value.split(' ')
            if arr and len(arr) == 2:
                line_dict = {'line_num': arr[0], 'full_address': arr[1]}
                # line = Line()
                # line._copy_from_dict(line_dict)
                line_list.append(line_dict)
        return line_list

    def parse_get_uris(self, output):
        uris = {}
        ret = {}
        uriInfo = {}
        try:
            pat = re.compile('\{\d+\}')
            output = ''.join(pat.split(output))
        except Exception:
            return ret
        if output:
            output = output.strip()
            lines = output.split('}}}')
            lines = filter(None, lines)
            for line in lines:
                uris = {}
                line_start_index = line.index('{')
                line_end_index = line.index('{', line_start_index + 1)
                uris_start_index = line_end_index
                uris_end_index = len(line)
                lindex = line[line_start_index + 1:line_end_index - 1]
                uriValue = line[uris_start_index:uris_end_index]
                pat = re.compile(r'{[0-9]\s{[\w+.:@]*}\s{[\w\s]*')
                lUris = re.findall(pat, uriValue)
                for u in lUris:
                    uriInfo = {}
                    uri_start_index = u.index('{')
                    uri_end_index = u.index('{', uri_start_index + 1)
                    uIndex = u[uri_start_index + 1:uri_end_index - 1]
                    uInfo = u[uri_end_index:len(u)]
                    pat = re.compile(r'[\w+.:@]*[\w\s]*')
                    uInfos = re.findall(pat, uInfo)
                    uInfos.pop(uInfos.index(' '))
                    uInfos = filter(None, uInfos)
                    uriInfo['uri'] = uInfos[0]
                    uriInfo['primary'] = False
                    if len(uInfos) == 2 and uInfos[1] != ' ':
                        uriInfo['primary'] = True
                    uris[uIndex] = uriInfo
                OrderedDict(sorted(uris.items(), key=lambda t: t[0]))
                ret[lindex] = uris
                OrderedDict(sorted(ret.items(), key=lambda t: t[0]))
        return ret

    def detailed_parse_char_by_char(self, msg):
        ret_dict = dict()
        l_index = msg.find('{')
        if l_index == -1:
            return
        char_index = 0
        send_line = ''
        while char_index < len(msg):
            r_index = msg.find('}', char_index)
            if r_index == -1 or char_index >= len(msg):
                return
            char_index = r_index + 1
            attr = msg[l_index:r_index + 1]
            send_line = attr
            ret_val = dict()
            if send_line.count('{') == send_line.count('}'):
                if '{attribute {{' in send_line:
                    val_index = send_line.find('{', 2)
                    val_end_index = send_line.rfind('}', 0, len(send_line))
                    ret_val['attribute'] = send_line[val_index:val_end_index]
                elif '{{holdreversionreq} {' in send_line:
                    index = send_line.find('{', 2)
                    end_index = send_line.rfind('}', 0, len(send_line))
                    if len(send_line[index:end_index]) > 10:
                        ret_val['holdreversionreq'] = (
                            self.parse_holdreversionreq_1
                            (send_line[index:end_index]))
                    else:
                        ret_val = (self.
                                   parse_single_line_to_key_value_pair
                                   (send_line))
                else:
                    ret_val = (self.
                               parse_single_line_to_key_value_pair(send_line))
                l_index = msg.find('{', char_index)
                send_line = ''
                for k in ret_val:
                    key = k
                    value = ret_val[k]
                if key:
                    ret_dict[key] = value
                pass
            else:
                continue
        return ret_dict

    def jsonify_string(self, json_string):
        if json_string:
            decoded_val = json.loads(json_string,
                                     object_pairs_hook=common_utils.
                                     CamelotOrderedDict)
            if 'JSON_LIST' in json_string:
                return decoded_val['JSON_LIST']
            return decoded_val

    def parse_cmstats(self, msg):
        cmstats_part_1 = msg
        cmstats_part_2 = None
        ret = {}

        if '{timestamp' in msg:
            timestamp_index = msg.index('{timestamp')
            cmstats_part_1 = msg[:timestamp_index]
            cmstats_part_2 = msg[timestamp_index:]
            cmstats_part_2 = cmstats_part_2.strip()

        ret = self.complex_parse(cmstats_part_1)
        for key in ret:
            ret[key] = int(ret[key])
        ret['timestamps'] = []
        if cmstats_part_2:
            pat = re.compile(
                r'''
                ^
                {(timestamp)\s{
                (?P<registration_event>.+)}\s
                (?P<ip_addr>.+)\s
                (?P<date>.+)\s
                (?P<time>.*)}
                $
                ''', re.I | re.VERBOSE)

            while cmstats_part_2:
                if ' {timestamp ' in cmstats_part_2:
                    idx = cmstats_part_2.index(' {timestamp ')
                    parse_str = cmstats_part_2[:idx]
                    cmstats_part_2 = cmstats_part_2[idx:]
                    cmstats_part_2 = cmstats_part_2.strip()
                else:
                    parse_str = cmstats_part_2
                    cmstats_part_2 = None

                time_dict = pat.match(parse_str)
                if time_dict:
                    ret['timestamps'].append(time_dict.groupdict())

        return ret
