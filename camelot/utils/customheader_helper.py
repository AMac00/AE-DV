import logging
import camelot
from camelot.utils.rawendpoint_helper import (OutActionObject, InActionObject)

log = logging.getLogger('CustomHeaders')


class CustomHeadersObject(object):

    def __init__(self, camelotep, msgstr):
        self.ep = camelotep
        self.outmsgid = msgstr['outmsgid']
        self.inmsgid = msgstr['inmsgid']
        self.errortext = msgstr['error']

    def clear(self):

        '''
        This member function removes the customisation functionality added
        by sip_custom_headers(). Currently implemented for
        only outgoing messages and for any future enhancements in
        sip_custom_headers(), this function also needs enhancement.

        Input: Takes no input parameters.

        :returns: Upon success, True is returned. Orelse, returns False

        >>> Obj = ep1.sip_custom_headers(headers={'Subject':'SIP Call'},
        methods=['INVITE','BYE'],action='add', mode='request')

        >>> ep1.place_call(ep2line)
        ...  Verify custom changes in SIP messages ...

        >>> Obj.clear()
        True

        For more information please refer to camelot wiki page:\n
        https://wiki.cisco.com/display/CAMELOT/Simplified+SIP+Message+handling#SimplifiedSIPMessagehandling-SipCustomHeadersAPIimplementation
        '''

        if not self.ep:
            log.info("already cleared")
            return False

        # Read both msgid
        outmsgid = self.get_outmsgid()
        inmsgid = self.get_inmsgid()
        # if both are empty return True
        if not outmsgid and not inmsgid:
            log.info("both msgid are none")
            return False

        out_message = '{0}^{1}@'.format(
            outmsgid, inmsgid)

        reply_buff = self.ep._query_camelot(
            camelot.CLEAR_CUSTOM_HEADERS, out_message)
        if reply_buff is False:
            log.error("clear failed")

        self.ep = None
        self.outmsgid = None
        self.inmsgid = None
        self.errortext = None
        return reply_buff

    def get_outmsgid(self):
        if not self.outmsgid:
            return '-1'
        else:
            return self.outmsgid

    def get_inmsgid(self):
        if not self.inmsgid:
            return '-1'
        else:
            return self.inmsgid

    def get_errortext(self):
        return self.errortext
