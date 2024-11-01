import camelot
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger

log = camlogger.getLogger(__name__)


class CamelotCTIFeature(v.CamelotVapiUtils):
    '''Camelot CTI operation'''

    def __init__(self):
        pass

    def cti_get_response(self, req_id, no_clear=False):
        '''Get the information about Response of any CTI request

        :parameter req_id: Request ID generated to send request which response
                          you want to check.
        :parameter no_clear: If the value is false clears the response info,
                             default value is false.

        :returns: Upon success, A dictionary fieled:value pairs.
            otherwise throws an exception.\n
            current fields are supported:\n
            1.'request' - Request to which current Response belongs. It
            is represented in the form of dictionary which will change
            depending upon the request but there are some common fields
            mentioned below:\n
                * "command" denotes the Camelot API for which this
                  response belongs to.
                * "qbe_request" denotes string representation of sent
                  QBE request.
                * "send_time" denotes the time when the request was sent
                  from Camelot to CTI Manager.
                * apart from these, there will be some more parameter(s)
                  denoting the arguments of the sent request which will vary
                  depending upon the request.
            2.'response' - It shows the response details, which is parsed from
            the response received from CTI manager, in the form of the
            dictionary which includes the following fields:\n
                * "description" denotes reason for failure which is parsed from
                  the received failure response, for successful response it
                  will be "None"(as description will not be part of received
                  successful response).
                * "received_time" shows the time the Camelot has received the
                  response.
                * "pdu_number" shows PDU number received in the response.
                * "result" shows the result received in response in the
                  hexadecimal format.
                  if the result is successful it will be "0x0000" otherwise a
                  non zero hexadecimal number corresponding to an error.
                * "pdu_string" shows the string representation of PDU number
                  received in Qbe response.
            Possible exceptions are:\n
            1."Invalid Arguments"\n
            * This will come if you have not passed valid number of
            arguments.\n
            2."provided request id is invalid"\n
            * This will come if request Id passed didn't get any
              response yet or if you are checking the response of a
              request at-least second time and first time you didn't
              enable no_clear parameter so it's been removed.

        >>> csfd.place_call('7763')
        '0aef0000'
        >>> csfd.cti_send_dtmf('0aef0000' , '345#' , '2')
        '4312'
        >>> csfd.cti_get_response('4312' , True)
        {u'request': {u'dtmf_digits': u'432*#',
        u'qbe_request': u'QBE_CALL_PLAY_DTMF_REQUEST',
        u'command': u'send_cti_dtmf',
        u'play_rate': u'0',
        u'send_time': u'2017-08-17T11:35:32.962-05:30'},
        u'response': {u'description': u'None',
        u'received_time': u'2017-08-17T11:35:32.972-05:30',
        u'pdu_number': u'69',
        u'result': u'0x0000',
        u'pdu_string': u'QBE_CALL_PLAY_DTMF_RESPONSE'}}

        '''
        kwargs = {}
        no_clr = ''
        if no_clear:
            no_clr = 'NOCLEAR'
        kwargs = {'no_clear': no_clr,
                  'req_id': req_id}
        ret = self._query_camelot(camelot.CTI_GET_RESPONSE_STATUS,
                                  **kwargs)

        return ret

    def cti_send_dtmf(self, call_ref, dtmf_digits='', play_rate='0'):
        '''
        This function is applicable only for CSFD endpoint to send DTMF
        digits from a given call reference.

        :parameter call_ref: valid call reference.
        :parameter dtmf_digits: DTMF digits to send. Valid digits are:
                   0 - 9, A - D, * and # .
        :parameter play_rate: Frequency at which CUCM will play the DTMF
                   digits.

        :return: In successful case return request ID of request,
                 generated to send DTMF otherwise exceptions.\n
                 Possible exceptions are-\n
                 1.'Invalid call reference':\n
                 * This will come when call reference passed is not valid.
                 2.'DTMF digits should not be empty':\n
                 * This will come if you haven't passed any DTMF digits.
        :Note: To check the response use cti_get_reponse().\n
               Please refer:
               https://wiki.cisco.com/display/CAMELOT/Send+DTMF+digits
               It will contain some more parameters in request apart from
               common ones, which are mentioned below:\n
               1.'dtmf_digits' denotes the DTMF digits sent through
               cti_send_dtmf API.\n
               2.'play_rate' denotes play rate at which DTMF digits are being
               played.


        >>> csfd.place_call('7792')
        '0xf1706408'
        >>> csfd.cti_send_dtmf('0xf1706408' , '324#')
        '885431'

        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            raise camelot.CamelotError('Invalid call reference')
        if not dtmf_digits:
            raise camelot.CamelotError('DTMF digits should not be empty')

        return self._query_camelot(camelot.CTI_SEND_DTMF,
                                   call_ref, dtmf_digits, play_rate)

    def cti_clear_response(self, req_id=None):
        '''
        This function is applicable only for CSFD endpoint to clear response,
        if no request id is provided then it will delete all responses for that
        endpoint otherwise clears the response retrieved for provided request
        id .

        :parameter req_id: It is an optional parameter it's a request id
                   for which user wants to delete the response.

        :return: In successful case it deletes response(s) and returns'True'
                 else throws an exception.\n
                 Possible exceptions are:\n
                 1."provided request id is invalid"\n
                 * This will come if request Id passed does not have any
                 response(either been deleted or not generated by camelot).

        >>> csfd.cti_send_dtmf('0aef0000' , '345#' , '2')
        '4312'
        >>> csfd.cti_clear_response('4312')
        'True'

        '''
        return self._query_camelot(camelot.CTI_CLEAR_RESPONSE, req_id)
