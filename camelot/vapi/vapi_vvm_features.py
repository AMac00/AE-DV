import camelot
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger

log = camlogger.getLogger(__name__)


class CamelotVVMFeatures(v.CamelotVapiUtils):

    '''Camelot vvm feature representation
    '''
    def show_vvm_ids(self, read_type='all'):
        '''show all visual voice mail ids

        :parameter read_type:
            * all -  show all voice mail ids.(by default)
            * read - show all read voice mail ids.
            * unread - shown all unread voice mail ids.

        :returns: returns list of voice mails

        >>> ep.show_vvm_ids('all')
        {0:5290c788-b861-47e7-857f-2f3312acba6b,
        0:9fcb7287-ad1c-419b-9143-37371ed81642}
        '''
        read_types = ['all', 'read', 'unread']
        if read_type not in read_types:
            raise camelot.CamelotError('Invalid read_type')
        return self._query_camelot(camelot.SHOW_VVM_IDS, read_type)

    def show_vvm_info(self, msgid):
        '''It returns the information about the voice mail id such as
         msgtype, size, duration, read status, callernumber etc

        :parameter msgid: voice mail message id for which info has to be shown.

        :returns: It returns the information about the voice mail id such
         as msgtype, size, duration, read status, callernumber etc

        >>> ep.show_vvm_info('0:5290c788-b861-47e7-857f-2f3312acba6b')
        {'contenttype': 'audio/wav', 'read': 'false',
         'msgid': '0:17321b33-c7e4-409d-9e22-0f3965ebcf74',
         'priority': 'Normal', 'downloadstatus': '200',
         'msgtype': 'Voice', 'arrivaltime': '2015-04-20T13:10:14',
         'duration': '5620', 'attachmenturl': '/vmrest/messages/0:17321b33
         -c7e4-409d-9e22-0f3965ebcf74/attachments/0', 'unityserver': 'cam-
         unity-2.camelot.test', 'callernumber': '1000002', 'size': '62240',
         'subject':'Message from daaa6201 daaa6201', 'from' :'123456',
         'to' : '432222', 'callername' : 'daaa6201 daaa6201',
         'localarrivaltime' : '1444826075', 'priority' : 'Normal',
         'sensitivity' : 'Normal', 'imapuid' : '4','fromsub':'true',
         'fromvmintsub' : 'false','filtertype' : 'VoiceAndReceipts'}
        '''
        if not msgid:
            raise camelot.CamelotError('msgid not given')
        return self._query_camelot(camelot.SHOW_VVM_INFO, msgid)

    def fetch_vvm(self, msgid):
        '''Camelot will send this query to the unity connection server whose
         ip and port is set before invoking in-service. As a result of this
         voice mail is downloaded and discarded on the Camelot.

        :parameter msgid: msgid is the message id of the message to be
         downloaded from Unity Connection.

        :returns: query id on success and on failure 0 .

        >>> ep.fetch_vvm('0:5290c788-b861-47e7-857f-2f3312acba6b')
         33425
        '''
        if not msgid:
            raise camelot.CamelotError('msgid not given')
        return self._query_camelot(camelot.FETCH_VVM, msgid)

    def vvm_query_response(self, query_id, no_clear=False):
        ''' Returns the http query reponse for the provided valid query id.

        :parameter query_id: The id of the vvm request.
        :parameter no_clear: If provided the camelot retains the response
         for future retrieval purpose on returning to the user.
         By default Camelot clears the received response on returning to
         the user.This parameter lets the user to instruct the camelot to
         override the default behaviour.

        :returns: Returns vvm response on success. on failure returns the
         empty list.

        >>> ep1.vvm_query_response(32771)
         { 'query': '/cucm-uds/clusterUser?username=JABBEREP1200001',
           'servicenode': 'cam-feature12-pub','starttime':'2014-1-7T20:37:15',
           'redirqueryid':'','statuscode':'200',
           'Cache-Control':'private','Expires': 'Thu, 01 Jan 1970 05:30:00 IST,
           'X-Frame-Options':'SAMEORIGIN','Content-Type':'application/xml',
           'Content-Length':'205','Date':Tue, 07 Jan 2014 15:07:15 GMT',
           'Server':''body':'<?xml version="1.0" encoding="UTF-8"
           standalone="yes"?><clusterUser version="10.5.0"
           uri="https://cam-feature12-pub:8443/cucm-uds/clusterUser?
           username=JABBEREP1200001"><result found="false"/></clusterUser>'}

        '''
        if not query_id:
            camelot.CamelotError('Specify query id')
            return

        if no_clear:
            config_request = '{} {} {}'.format(
                camelot.VVM_QUERY_RESPONSE, query_id, 'noclear')
        else:
            config_request = '{} {} {}'.format(
                camelot.VVM_QUERY_RESPONSE, query_id, 'clear')

        return self._query_camelot(
            camelot.VVM_QUERY_RESPONSE, config_request)

    def send_vvm(self):
        '''Camelot sends /SendMessage query to the unity connection
         server whose ip and port is set before invoking in-service.
         It shall be invoked after /Record.

        :returns: 1 on success and on failure 0 is returned

        >>> ep.send_vvm()
         1
        '''
        return self._query_camelot(camelot.SEND_VVM)

    def record_vvm(self, record_mode='', record_time=10):
        '''Camelot sends /Record query to the unity server
         whose ip and port is set before invoking in-service.
         It shall be invoked after VMWS login is successful and
         reverse trap call is connected.

        :parameter record_mode: mode of recording. possible values are :
         1.RecordModeOverwrite (default value) 2.RecordModeAppend
        :parameter record_time: recording time in seconds.
         Default value is 10 secs.

        :returns: 1 on success and on failure 0 is returned

        >>> ep.record_vvm(record_time=10)
         1
        '''
        if not record_mode:
            record_mode = '0'
        kwargs = {'record_mode': record_mode,
                  'record_time': record_time
                  }
        return self._query_camelot(camelot.RECORD_VVM, **kwargs)

    def run_conversation(self, conversation='', prop_id_num=0,
                         prop_info=''):
        '''Camelot sends /runConversation query to the unity server
        whose ip and port is set before invoking in-service.
        It shall be invoked after VMWS login is successful and
        reverse trap call is connected.

        :parameter conversation: type of the conversation.
         conversation values would be fetched using
         get_supported_conversations_info command.
        :parameter prop_id_num: number of property ids.
         It is defined for future use.
        :parameter prop_info: property id information.
         It is defined for future use.

        :returns: 1 on success and on failure 0 is returned

        >>> ep.run_conversation(conversation='TUIRedirect')
         1
        '''
        kwargs = {'conversation': conversation,
                  'prop_id_num': prop_id_num,
                  'prop_info': prop_info,
                  }
        return self._query_camelot(camelot.RUN_CONVERSATION, **kwargs)

    def add_recipient(self, called_number='', called_name=''):
        '''Camelot sends /SearchRecipient query to the unity server
         whose ip and port is set before invoking in-service.
         It shall be invoked after VMWS login is successful.
         User can enter either called_number of called_name.
         if both are entered called_name will be considered.

        :parameter called_number: terminating party dn
        :parameter called_name:  terminating party name

        :returns: 1 on success and on failure 0 is returned

        >>> ep.add_recipient(called_number=6201)
         1
        '''
        if not called_number:
            called_number = '0'
        if not called_name:
            called_name = '0'
        kwargs = {'called_number': called_number,
                  'called_name': called_name
                  }
        return self._query_camelot(camelot.ADD_RECIPIENT_VVM, **kwargs)

    def play_vvm(self, msgid, time=None, blob=None, startpos=None):
        '''Camelot will send this query to the unity connection server whose
         ip and port is set before invoking in-service. As a result of this
         voice mail is downloaded and discarded on the Camelot.

        :parameter msgid: message id to be played
        :parameter time:  duration for which the visual voice
         mail has to be played. If time is not specified it plays for the
         entire duration of the message. (time is in milliseconds)
         Note: This field is not applicable to sipx endpoints.
        :parameter blob:  blob is the hex-dump string of the wave file
         which is to be compared, after a fresh download of the voice mail
         is done. Note: This field is not applicable to sipx endpoints.
        :parameter startpos:  position in the play request for desired
         start. startpos is referenced in milliseconds.
         For playing at the very beginning of a play request,
         user would set startpos to 0.
         For requesting to play in the middle of a 30 second message,
         user would set startpos to 15000.
         Note: This field will be applicable only to sipx endpoints.

        :returns: for jabber : query id on success and on failure 0 .
         for sipx : 1 on success and on failure 0 is returned

        >>> ep.play_vvm('0:5290c788-b861-47e7-857f-2f3312acba6b',time=5000)
         33425
        '''
        kwargs = {'time': time,
                  'blob': blob,
                  'startpos': startpos
                  }
        if not msgid:
            raise camelot.CamelotError('msgid not given')
        return self._query_camelot(camelot.PLAY_VVM, msgid, **kwargs)

    def vvm_clear_response(self, query_id):
        '''If no queryid is given this command clears all responses
        for the endpoint. If a queryid is given specific query response
        is cleared.

        :parameter query_id: The id of the HTTP request which was
         placed through play_vvm, fetch_vvm, delete_vvm command.

        :returns: 1 on success 0 on failure.

        >>> ep.vvm_clear_response(1222)
        1
        '''
        if query_id:
            config_request = '{} {}'.format(camelot.VVM_CLEAR_RESPONSE,
                                            query_id)
        else:
            config_request = (camelot.VVM_CLEAR_RESPONSE)
        return self._query_camelot(camelot.VVM_CLEAR_RESPONSE,
                                   config_request)

    def delete_vvm(self, msgid=None):
        '''send voice mail to the deleted folder

        :parameter msgid: msgid is the message id of the message to be
         deleted from Unity Connection.

        :returns: for jabber : query id on success and on failure 0 .
         for sipx endpoint :  1 on success and on failure 0 is returned

        >>> ep.delete_vvm('0:5290c788-b861-47e7-857f-2f3312acba6b')
         33425
        '''
        return self._query_camelot(camelot.DELETE_VVM, msgid)
