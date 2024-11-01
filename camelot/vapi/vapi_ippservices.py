import camelot
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger

log = camlogger.getLogger(__name__)


class CamelotIPPServices(v.CamelotVapiUtils):
    '''CamelotIPPServices representation
    '''

    def __init__(self):
        pass

    def get_ipps_multimedia(self, ipps_ref=None):
        '''Return the multi-media uris on the content type received
           in the refer. This is handled for out-of-dialog refers.

        :parameter ipps_ref: is an optional parameter.  If provided,
                 return will only include the information for the
                 CiscoIPPhoneExecute object referenced by ipps_ref.
                 If None, then all objects are returned.

        :returns: List of Dictionaries as below.
                If no CiscoIPPhoneExecute objects have been received,
                empty list [] will be returned.\n
                * ipps_ref - internal reference
                * receive_time - timestamp of when REFER request is
                  received by the endpoint.
                * session_id - Session-ID header value received in the REFER
                  request. If header is not present, value will be empty
                  string.
                * receive_xml - the complete CiscoIPPhoneExecute element
                  received in the REFER request
                * notify_status - status of the request
                    * pending - request received, but processing in
                      camelot not complete and NOTIFY result
                      not sent.
                    * complete - request processed and NOTIFY sent.
                    * error - an internal camelot error occurred.
                      Check logs.  Information in the response
                      may not be accurate or complete.
                * notify_time - timestamp of when Camelot sent the
                  NOTIFY request containing the CiscoIPPhoneResponse object
                * notify_xml - the complete CiscoIPPhoneResponse xml
                  object sent in the NOTIFY message.

        >>> ep1.get_ipps_multimedia()
            [{
             'ipps_ref': '0xc1a3ce4',
             'receive_time': '2016-12-12T17:09:18.24-05:00',
             'session_id': '462828ed004050008000aabbccdd1111;
                            remote=00000000000000000000000000000000',
             'receive_xml': '<CiscoIPPhoneExecute>
              <ExecuteItem URL="RTPMTx:232.218.118.3:30958"/>
              <ExecuteItem URL="RTPMTx:Play:DtZipZip"/>
            </CiscoIPPhoneExecute>
            ',
             'notify_status': 'completed',
             'notify_time': '2016-12-12T17:09:18.24-05:00',
             'notify_xml': '<CiscoIPPhoneResponse>
             <ResponseItem URL="RTPMTx:232.218.118.3:30958" Data=
             "Success" Status="0" />
             <ResponseItem URL="RTPMTx:Play:DtZipZip" Data=
             "Success" Status="0" />
            </CiscoIPPhoneResponse>',
            },
             {
             'ipps_ref': '0xc1a3d3c',
             'receive_time': '2016-12-12T17:10:06.831-05:00',
             'session_id': '462828ed004050008000aabbccdd1111;
                            remote=00000000000000000000000000000000',
             'receive_xml': '<CiscoIPPhoneExecute>
              <ExecuteItem URL="RTPMTx:Stop"/>
            </CiscoIPPhoneExecute>',
             'notify_status': 'completed',
             'notify_time': '2016-12-12T17:10:06.831-05:00',
             'notify_xml': '<CiscoIPPhoneResponse>
             <ResponseItem URL="RTPMTx:Stop" Data="Invalid
              associatedsessionid" Status="7" />
            </CiscoIPPhoneResponse>',
            }]

        >>> ep1.get_ipps_multimedia('0xc1a3ce4')
            [{
             'ipps_ref': '0xc1a3ce4',
             'receive_time': '2016-12-12T17:09:18.24-05:00',
             'session_id': '462828ed004050008000aabbccdd1111;
                            remote=00000000000000000000000000000000',
             'receive_xml': '<CiscoIPPhoneExecute>
              <ExecuteItem URL="RTPMTx:232.218.118.3:30958"/>
              <ExecuteItem URL="RTPMTx:Play:DtZipZip"/>
            </CiscoIPPhoneExecute>
            ',
             'notify_status': 'completed',
             'notify_time': '2016-12-12T17:09:18.24-05:00',
             'notify_xml': '<CiscoIPPhoneResponse>
             <ResponseItem URL="RTPMTx:232.218.118.3:30958" Data=
             "Success" Status="0" />
             <ResponseItem URL="RTPMTx:Play:DtZipZip" Data=
             "Success" Status="0" />
            </CiscoIPPhoneResponse>',
            }]

        >>> ep1.get_ipps_multimedia()
            []
        '''
        return self._query_camelot(camelot.GET_IPPS_MULTIMEDIA, ipps_ref)

    def get_ipps_rtpstream(self):
        '''This API will return information about the current state of
        the RTP streaming commands (RTPRx, RTPTx, RTPMRx, and RTPMTx)
        received by the endpoint.  Only if a stream that is successfully
        started or stopped will be shown here.  After RTP streaming ends,
        the information will still be available to the just completed stream
        until the next stream starts. Information for completed stream will
        be retained through an outofservice/inservice cycle and will only be
        lost if the endpoint is uninitialized or released. If an error
        occurred prior to starting the stream, the command will show nothing
        of value.

        :returns: List of Dictionaries containing information about the
            current status of RTP streaming.
            If no CiscoIPPhoneExecute objects have been received,
            empty list [] will be returned.\n
            * status - current status or state of the stream.
                * tx - actively transmitting.
                * rx - actively receiving.
                * idle - no streaming currently in progress.
            * direction - tx or rx.
            * steam_type - multicast or unicast.
            * ipaddress - IP address being used. IPv4 or IPv6.
            * port - port used.
            * volume - volume used.  If no volume was provided
            with the ExecuteItem object, then the value will be "".
            * path - value provided for the XSI Audio Path Control.
            If no value was received then this will be set to None.
            Obviously this value has no practical use for camelot,
            but is being reported if it was received in the URI.
            * start - start time of the media transmission or reception.
            * stop - time media transmission or reception ended.

        >>> ep1.get_ipps_rtpstream()
        [   {"status":"idle",
              "direction":"tx",
              "stream_type":"multicast",
              "ipaddress":"232.218.118.3",
              "port":"30958",
              "volume":"",
              "path":"",
              "start":"2017-01-24T18:37:56.943-05:30",
              "stop":"2017-01-24T18:38:53.861-05:30"}
        ]

        >>> ep1.get_ipps_rtpstream()
        [   {"status":"idle",
              "direction":"tx",
              "stream_type":"multicast",
              "ipaddress":"232.218.118.3",
              "port":"30958",
              "volume":"",
              "path":"",
              "start":"2017-01-24T18:37:56.943-05:30",
              "stop":"2017-01-24T18:38:53.861-05:30"},
            {"status":"tx",
              "direction":"tx",
              "stream_type":"multicast",
              "ipaddress":"232.218.118.3",
              "port":"30958",
              "volume":"",
              "path":"",
              "start":"2017-01-24T18:37:56.943-05:30",
              "stop":""}
        ]

        >>> ep1.get_ipps_rtpstream()
        [   {"status":"",
              "direction":"",
              "stream_type":"",
              "ipaddress":"",
              "port":"",
              "volume":"",
              "path":"",
              "start":"",
              "stop":""}
        ]
        '''
        return self._query_camelot(camelot.GET_IPPS_RTP_STREAM)
