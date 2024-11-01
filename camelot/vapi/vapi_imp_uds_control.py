import camelot
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger

log = camlogger.getLogger(__name__)


class CamelotIMPUdsControl(v.CamelotVapiUtils):

    '''Camelot im, presence and uds commands
    '''

    def imp_query_response(self, query_id=None, clear=False):
        '''Shows the xmpp query status and response details
        for the provided query_id. The query_id being provided here
        should be the one returned by the xmpp/im roster, chat and presence
        commands. By default once the response is returned the Camelot
        cleares the response clear is set to False.

        :parameter query_id: Mandatory Parameter. Takes the queryid returned by
         any of xmpp roster commands
        :parameter clear: Optional parameter. Defaults to True.
         If set to Fase then Camelot will not clear the response
         otherwise by defaults Camelot clears the response on returning
         to the user.
        :parameter queryid: for backward compatibility of tngpi users
        :parameter noclear: for backward compatibility of tngpi users

        :returns: Upon success, A dictionary of field:value pairs with
         the following fields.\n
          * status:This field takes success/failure depend on
          the query reponse received
          * command:This field will show the command which was
          invoked for this queryid.
          * contact:This field will show the JID of the buddy for
          which the query was made
          * starttime:This field shows the time the query was generated
          * failure reason:This field shows the reason for the failure
          if error response was received
          * xml stanza:This field shows the xml stanza for the error
          responses received.

        >>> ep1.imp_query_response('4063652144', 'False')
        {'status':'success', 'command': 'removebuddy',
        'contact': 'jabberep1500001@camelot.test',
        'starttime': '2014-07-24T18:04:09',
        'failure reason': '', 'xml stanza':'' }
        '''

        if not query_id:
            camelot.CamelotError("invalid query id")
        msg = '{} {}'.format(camelot.IMP_QUERY_RESPONSE, query_id)
        if clear is True:
            msg = '{} {}'.format(msg, 'clear')
        else:
            msg = '{} {}'.format(msg, 'noclear')
        return self._query_camelot(camelot.IMP_QUERY_RESPONSE, msg)

    def clear_xmpp_im_response(self, queryid):
        '''
        Clears the imp query response for the provided queryid.
        If thequery_id is not provided then the camelot clears
        all responses for xmpp roster management commands like
        add_buddy, remove_buddy, remove_buddy etc. If the provided
        queryid doesn't have the buffered the response then the
        command returns 0.

        :parameter query_id: Optional parameter. Takes the queryid for
         which the response should be cleared in Camelot
        :parameter queryid: This is used for backward compatibility of tngpi

        :returns: 1 on success 0 on failure.

        >>> ep1.imp_clear_response('172539688')
        1
        '''
        msg = camelot.IMP_CLEAR_RESPONSE

        if queryid:
            msg = '{} {}'.format(msg, queryid)

        return self._query_camelot(camelot.IMP_CLEAR_RESPONSE, msg)

    def imp_clear_response(self, query_id):
        '''
        Clears the imp query response for the provided queryid.
        If thequery_id is not provided then the camelot clears
        all responses for xmpp roster management commands like
        add_buddy, remove_buddy, remove_buddy etc. If the provided
        queryid doesn't have the buffered the response then the
        command returns 0.

        :parameter query_id: Optional parameter. Takes the queryid for
         which the response should be cleared in Camelot
        :parameter queryid: This is used for backward compatibility of tngpi

        :returns: 1 on success 0 on failure.

        >>> ep1.imp_clear_response('172539688')
        1
        '''
        msg = camelot.IMP_CLEAR_RESPONSE

        if query_id:
            msg = '{} {}'.format(msg, query_id)

        return self._query_camelot(camelot.IMP_CLEAR_RESPONSE, msg)

    def send_xmpp_im(self, jabber_id, msg):
        ''' TNGPI COMMAND
        '''
        if not jabber_id:
            camelot.CamelotError("invalid buddy's jid")
        if not msg:
            camelot.CamelotError("empty message")

        msg = '{} {}^{}^'.format(camelot.SEND_IM, jabber_id, msg)

        return self._query_camelot(camelot.SEND_IM, msg)

    def send_im(self, jid, msg):
        '''
        Sends the message to the buddy whose jabber id is mentioned. Both jid
        and msg are mandatory fields. The query id which is returned by this
        command can be used by get_im_query_response command to know the
        details of the sent message and the contact to whom it was sent.User
        can call this API on receiving the station event 'imquerycompleted'
        from Camelot.

        :parameter jid: buddy's jid
        :parameter msg:  message to be sent.

        :returns: success case returns query id.
         if jid is not given then error returned is a message saying
         "must specify buddy jid"
         if  msg is not given then error returned is a message saying
         "must specify message"
         if invalid jid is mentioned then it returns 0

        >>> ep1.send_im('jabberep1401001@camelot.test','hello')
        4051806944
        >>> ep1.send_im()
        must specify contact user
        >>> ep1.send_im('jabberep1401001@camelot.test')
        must specify message
        '''

        if not jid:
            camelot.CamelotError("invalid buddy's jid")
        if not msg:
            camelot.CamelotError("empty message")

        msg = '{} {}^{}^'.format(camelot.SEND_IM, jid, msg)

        return self._query_camelot(camelot.SEND_IM, msg)

    def im_query_response(self, query_id, clear=True):
        '''
        This command is invoked with the query id returned from IM/XMPP
        operations like sending a chat message using send_im, to
        know the information about the sent message.

        :parameter query_id: Id returned by send_im command.
        :parameter clear: default value is True, Camelot clears the response
         after returning information about the response received.
         However, if clear option is set to False the response is not cleared
         in camelot.

        :returns: returns the dictionary with field:value pair with the
         following fileds:\n
         * status - If IM/XMPP operation like sending a chat message
           using send_im got a type=error in the response, status will
           be set to 'failure'. If successful, status will be set to 'success'.
         * state - This is the state of the last IM/XMPP operations
           done, like sending a chat message using send_im.
           This state is being received in XMPP chat event message from
           XMPP/IMP server. The possible chat states are -
           "composing, displayed, delivered, invalid, error".
         * command - This field shows the command which was invoked
           for this queryid.
         * contact - This field shows the JID of the buddy for which
           the query was made.
         * message - This field shows the message which was sent using
           IM/XMPP commands like sending a chat message using send_im.
         * starttime - This field shows the time the query was generated.

        >>> a_query_id = ep1.send_im('jabberep1600002@camelot.test','hello')
         '4051371016'
        >>> ep1.im_query_response('4051371016')
        {'command': 'sendim',
         'contact': 'jabberep1600002@camelot.test',
         'message': 'hello',
         'sent time': '2016-10-17T14:40:13.409',
         'state': 'delivered',
         'status': 'success'}

        >>> a_query_id = ep1.send_im('abc@camelot.test','hello')
         '182615876'
        >>> ep1.im_query_response('182615876')
        {'command': 'sendim',
         'contact': 'abc@camelot.test',
         'message': 'hello',
         'sent time': '2016-10-17T14:40:27.993',
         'state': 'error',
         'status': 'failure'}
        '''
        if query_id is None:
            camelot.CamelotError("invalid query id")
        msg = '{} {}'.format(camelot.IM_QUERY_RESPONSE, query_id)
        if clear is True:
            msg = '{} {}'.format(msg, 'clear')
        else:
            msg = '{} {}'.format(msg, 'noclear')
        return self._query_camelot(camelot.IM_QUERY_RESPONSE, msg)

    def get_xmpp_im_response(self, jabber_id, clear=False):
        ''' TNGPI COMMAND '''
        if not jabber_id:
            camelot.CamelotError('invalid jid, provide valid jid')
        msg = '{} {}'.format(camelot.GET_IM_INFO, jabber_id)
        if clear:
            msg = '{} {}'.format(msg, 'clear')
        else:
            msg = '{} {}'.format(msg, 'noclear')
        return self._query_camelot(camelot.GET_IM_INFO, msg)

    def get_xmpp_im_info(self, jabber_id, clear=False):
        '''gets last sent and received message from  buddy whose jabber id is
         given.Also shows total number of messages sent and received

        :parameter jabber_id: The jabber id of buddy
        :parameter clear: If true the camelot clears the response
         for future retrieval purpose on returning to the user.
         By default Camelot does not clears the received response on
         returning to the user.This parameter lets the user to instruct
         the camelot to override the default behaviour

        :returns: If the -field argument is omitted, a list of {field  value}
        information is returned .If the -field option is specified, only the
        value for the specified field is returned

        >>> ep.get_xmpp_im_info(jabber_id)
        {{'last received im': 'hello 2',
         'last received im timestamp': '2015-04-02T19:09:29.290',
         'last sent im': 'hello',
         'last sent im timestamp': '2015-04-02T19:08:49:391',
         'total ims received': '1',
         'total ims sent': '1'}

        '''

        if not jabber_id:
            camelot.CamelotError('invalid jabber_id, provide valid jabber_id')
        msg = '{} {}'.format(camelot.GET_IM_INFO, jabber_id)
        if clear:
            msg = '{} {}'.format(msg, 'clear')
        else:
            msg = '{} {}'.format(msg, 'noclear')
        return self._query_camelot(camelot.GET_IM_INFO, msg)

    def get_im_info(self, jid, clear=False):
        '''
        Provides information about last message sent and received to and from
        buddy along with there time stamp.It also shows the total number of
        messages sent and received.

        :parameter jid: buddy's jid
        :parameter clear: defaults to False else if set to True the Camleot
         clears the response.

        :returns: returns the dictionary with field:value pair with the
         following fields:

            * last sent im: message sent
            * last sent im timestamp: time stamp of sent message
            * last received im: message recv
            * last received im timestamp: time stamp of received message
            * total ims sent: total messages sent
            * total ims received: total messages received
            * total error im responses received: total error responses received
            * last received error im resp: last error response received
            * last received error im resp timestamp: time stamp of last error
              response received

        >>> ep1.get_im_info('jabberep2100007@camelot.test')
        {'last received im timestamp': '0-00-00T00:00:00.00',
        'last sent im': 'testmail2', 'last sent im timestamp':
        '2016-09-16T11:44:14:678', 'total error im responses received': '1',
        'last received im': '', 'total ims received': '0',
        'total ims sent': '1',
        'last received error im resp': "<error type='cancel'><service-
        unavailable xmlns='urn:ietf:params:xml:ns:xmpp-stanzas'/></error>",
        'last received error im resp timestamp': '2016-09-16T11:44:14.735'}
        '''
        if not jid:
            camelot.CamelotError('invalid jid, provide valid jid')
        msg = '{} {}'.format(camelot.GET_IM_INFO, jid)
        if clear:
            msg = '{} {}'.format(msg, 'clear')
        else:
            msg = '{} {}'.format(msg, 'noclear')
        return self._query_camelot(camelot.GET_IM_INFO, msg)

    def im_clear_response(self, query_id):
        '''
        Clears the im query(send_im) response for the provided queryid.
        If thequery_id is not provided then the camelot clears
        all responses for xmpp roster management commands like
        add_buddy, remove_buddy, remove_buddy etc. If the provided
        queryid doesn't have the buffered the response then the
        command returns 0.

        :parameter query_id: Optional parameter. Takes the queryid for
         which the response should be cleared in Camelot

        >>> ep1.imclearresponse('172539688')
        1
        '''
        msg = camelot.IMP_CLEAR_RESPONSE
        if query_id is not None:
            msg = '{} {}'.format(msg, query_id)

        return self._query_camelot(camelot.IMP_CLEAR_RESPONSE, msg)

    def set_presence(self, show='', status=''):
        '''
        Modifies the show and status field values in the presence
        information of the endpoint.When the setpresence command is
        invoked the Camelot prepares the XMPP request and send the
        presence request to the xmpp server. On successfully sending
        the request to server the Camelot returns the query-id to the
        clients.. On recieving the response from server the Camelot
        generates the station event in the form
        "presenceinfo updated query-id". The clients are expected
        to wait for this event and on receiving this event they can call
        the command "presence_query_response" to get response.

        :parameter show: Optional parameter.It takes the value of the field
         show to be sent in the presence request. Values accepted for this
         field are: available, chat, away, dnd, xa, unavailable, probe, error
        :parameter status: Optional parameter. It takes the value of the
         field status to be sent in the presence request

        >>> ep1.set_presence('away', 'in lab')
        187118096
        >>> ep1.presence_query_response('187118096')
        {'result':'success', 'command': 'setpresence',
        'starttime':'2014-08-11T13:05:12',
        'show':'away}', 'status': 'in lab', 'priority': '127'}
        '''
        if show is None and status is None:
            camelot.CamelotError('show or status should be specified')
        msg = camelot.SET_PRESENCE
        if show is not None:
            msg = '{} {}'.format(msg, show)
        if status is not None:
            msg = '{} {}'.format(msg, status)
        return self._query_camelot(camelot.SET_PRESENCE, msg)

    def get_presence(self, jid=None):
        '''
        Shows the presence information of the endpoint
        or its buddies.

        :parameter jid: Optional parameter. If not mentioned it
         displayes the self presence. If jid mentioned, it takes
         the buddy name in the JID form as explained in xmpp
         RFC 6121. ex: jabberep@camelot.test

        :returns: Returns presence information as dictionary in key-value
         format. The keys are as follows:\n
         * show :  shows the current presence state of the endpoint.
         * status: shows the presence status of the end point.
         * priority: shows the priority of the endpoint.
         * phone status: shows the phone status of the endpoint.
         * im status: shows the im status of the end point.
         * subscription: shows the subscription state of the endpoint.

        >>> ep1.get_presence()
        {'show':'unavailable', 'status':'', 'priority':'-1',
        'phone status':'','im status':''}
        '''
        msg = camelot.GET_PRESENCE
        if jid is None:
            msg = '{} {}'.format(msg, 'null')
        else:
            msg = '{} {}'.format(msg, jid)

        return self._query_camelot(camelot.GET_PRESENCE, msg)

    def presence_query_response(self, query_id, clear=True):
        '''
        Displays the presence response corresponding to the query id
        mentioned. By default once the response is returned the
        Camelot cleares the response unless -noclear is mentioned
        in the command

        :parameter query_id: Mandatory Parameter. Takes the queryid
         returned by setpresence command
        :parameter clear: Defaults to True and clears the response
         on returning to the user. If set to False the Camelot preserves
         the response.

        :returns: returns the dictionary as key-value pair with the
         following keys:\n
             * result: shows whether success or failure.
             * command: shows the command which was invoked
               for this queryid.
             * starttime: This field shows the time the query
               was generated.
             * show: shows the current presence state of the endpoint.
             * status: shows the presence status of the end point.
             * priority: shows the priority of the endpoint.
             * phone status: shows the phone status of the endpoint.
             * im status: shows the im status of the end point.
             * failure reason: This field shows the reason for the
               failure if error response was received.
             * xml stanza: shows the xml stanza for the error responses
               received.

        >>> ep1.presence_query_response('187118096')
        {'result':'success', 'command':'setpresence',
        'starttime':'2014-08-11T13:05:12', 'show': 'away',
        'status':'in lab', 'priority':'127',  'phonestatus':
        'unavailable', 'imstatus':'available', 'failure reason':'',
        'xml stanza':''}
        '''
        if query_id is None:
            camelot.CamelotError("invalid query id")

        msg = '{} {}'.format(camelot.PRESENCE_QUERY_RESPONSE, query_id)
        if clear is True:
            msg = '{} {}'.format(msg, 'clear')
        else:
            msg = '{} {}'.format(msg, 'noclear')
        return self._query_camelot(
            camelot.PRESENCE_QUERY_RESPONSE, msg)

    def presence_clear_response(self, query_id):
        '''
        Clears the presence query(set_presence or get_presence)
        response for the provided queryid.If thequery_id is not
        provided then the camelot clears all responses for queries
        set_presence and get_presence. If the provided queryid
        doesn't have the buffered the response then the command
        returns 0.

        :parameter query_id: Optional parameter. Takes the queryid for
         which the response should be cleared in Camelot.

        :returns: 1 on sucess and 0 on failure.

        >>> ep1.presence_clear_response('172539688')
        1
        '''
        msg = camelot.PRESENCE_CLEAR_RESPONSE
        if query_id is not None:
            msg = '{} {}'.format(msg, query_id)

        return self._query_camelot(camelot.PRESENCE_CLEAR_RESPONSE, msg)

    def http_query_request(self, ip, port, url,
                           jsessionid='0', jsessionidsso='0', oauthtoken='0',
                           secure=True, showfinalresp=False, noautoref=False,
                           service='cucm', domain='null', protocol='https',
                           serviceport='0', servicefqdn='null', auth_type='0',
                           body=None, headers={}, method='GET', timeout=0):
        '''Forms the HTTP query request as per the argements provided and
        sends the request to the server ip and port.

        :parameter ip: ip address of the http server to which the
         requested to be sent.A resolvable FQDN can also be given.
         For the Collab Edge deployments this parameter can be optional.
         Camelot picks up automaticlly from the DNS reslution.
        :parameter port: port of the http server to be connected to.
         For the Collab Edge deployments this parameter can be optional.
         Camelot picks up automaticlly from the DNS reslution.
        :parameter url: This parameter forms the URL of the HTTP GET request.
         If the url has the query parameters then user  needs  to provide the
         query parameters as part of this arguement.
        :parameter jsessionid: if provided Camelot adds jsessionid to the
         Cookie header for the formed request.
        :parameter jsessionidsso: if provided Camelot adds jsessionidsso to the
         Cookie header for the formed request.
        :parameter secure: If this optinal parameter is provided Camelot do
         sends the formed HTTP get request on https secure connection.This
         paramter defaults to 1 always means always sends Http request on
         secure connection.
        :parameter oauthtoken: If provided Camleot adds Http Authorization
         header to the HTTP request and populates this header with this
         parameter value. Ex: Authorization: Bearer oauthtoken-value
        :parameter showfinalresp: When set to True the Camelot shows only the
         final response for that query, all intermediate responses will be
         consumed by Camelot internally but will not be shown to the user.
         By default Camelot will show all the responses to the client.
        :parameter noautoref: when set to True the Camelot doesn't refresh
         either SSO OAuth Token or SSO Session cookies automatically.By
         default Camelot will attempt to refresh SSO Oauth token and SSO
         Session cookies automatically.
        :parameter service: services for sso. cadidates are unity and cucm.
         defaults to cucm service.
        :parameter domain: Optional Parameter. If provided the command uses
         this value to calculate the encoded prefix for the url. If not
         provided then command takes the domain value from the endpoint
         configuration  sip.phone.domain.
        :parameter protocol: It defaults to "https". This parameter will be
         used, as one of the parameter, to calculate the EDGE prefix for the
         queries sent to any service node like cucm, ucxn etc through EDGE.
        :parameter servicefqdn: It takes the service node like cucm and unity
         host address in the resolvable FQDN format. If provided it means that
         the query is meant to send to provided service node through Collab
         Edge. This parameter will be used, as one of the parameter, to
         calculate the EDGE prefix for the HTTP request URL. Note: Camelot
         doesn't understand what is the provided service node rather it just
         uses the provided service fqdn.
        :parameter serviceport: Defaults to 8443. This parameter value will be
         considered only when the "servicefqdn" was configured. If provided
         it means that the query is meant to send to service nodes like to
         cucm and unity through Collab Edge. This parameter will be used, as
         one of the parameter, to calculate the EDGE prefix for the HTTP
         request URL.
        :parameter auth_type: This parameter is to indicate the authentication
         type to be used in Authorization header for the formed request.
         Possible values are 'Bearer','Digest' and 'Basic'.While handling
         subsequent authorization challenges also this auth type will be used.
         If no value is specified then Camelot will choose authentication
         type depending on various considerations. Please refer to the below
         link for more details on this.
         'https://wiki.cisco.com/display/CAMELOT/httpqueryreq'
        :parameter body: This parameter can be used to provide a body
         to be attached to html query request.Camelot will add corresponding
         Content-Length header. However tester needs to ensure correctness
         of the body provided.On absence of any value default is None.
        :parameter headers: This parameter is of dictionary type which
         takes a set of html header and value pairs from tester to be used
         in the html query request. On absence of any value by default it
         it will be an empty dictionary.For any header where the value can also
         come from other parameters of this API , value from this headers
         parameter always gets first precedence. For example, if 'Host' header
         is also included in the headers dictionary then Camelot will take the
         value from this dictionary parameter instead of taking the value from
         'Host'parameter if present.So testers need to be cautious about this.
        :parameter method: Tester can provide http method to be used for the
         html query request by using this optional parameter.On absence of
         any value by default 'GET' method will be used. Possible values for
         this parameters are 'GET','POST','DELETE','PATCH' etc.
        :parameter timeout: This parameter is to configure time in seconds
         to wait for a response from the server.On absence by default 10
         seconds will be used.


        :returns: query id on success

        >>> ep1.http_query_request('10.12.10.105', '8443',
                '/cucm-uds/users?name=USER1500001', secure=True,
                headers={'Cookie':'i18next=en-US;amlbcookie=01;',
                    'Forwarded':'for=192.0.2.60;'})
        32769
        '''
        config_request = camelot.HTTP_QUERY_REQ

        config_request = '{} {}'.format(config_request, ip)

        if not url:
            raise camelot.CamelotError('url is not specified')

        config_request = '{} {} {}'.format(config_request, port, url)

        if secure:
            config_request = '{} {}'.format(config_request, 'https')
        else:
            config_request = '{} {}'.format(config_request, 'http')

        config_request = '{} {} {} {}'.format(config_request, jsessionid,
                                              jsessionidsso, oauthtoken)
        if showfinalresp:
            config_request = '{} {}'.format(config_request, 'showfinalresp')
        else:
            config_request = '{} {}'.format(config_request, "0")
        if noautoref:
            config_request = '{} {}'.format(config_request, 'noautoref')
        else:
            config_request = '{} {}'.format(config_request, '0')
        if service == 'cucm':
            config_request = '{} {}'.format(config_request, 'cucm-uds')
        elif service == 'unity':
            config_request = '{} {}'.format(config_request, 'ucxn')

        config_request = '{} {} {} {} {} {}'.format(config_request, domain,
                                                    protocol, serviceport,
                                                    servicefqdn, auth_type)
        if body is None:
            config_request = '{} ^{}'.format(config_request, 'NULL')
        else:
            config_request = '{} ^{}'.format(config_request, body)

        if not isinstance(headers, dict):
            msgtext = 'set valid {header: value} dictionary for headers'
            raise camelot.CamelotError(msgtext)
        else:
            config_request = '{}^{}'.format(config_request, headers)
        if method:
            config_request = '{}^{}'.format(config_request, method)
        else:
            config_request = '{}^{}'.format(config_request, 'GET')
        if timeout:
            config_request = '{}^{}'.format(config_request, timeout)
        else:
            config_request = '{}^{}'.format(config_request, 10)

        log.debug("http_query_req arguments {}".format(config_request))
        return self._query_camelot(
            camelot.HTTP_QUERY_REQ, config_request)

    def http_query_response(self, query_id, no_clear=False, **kwargs):
        ''' Returns the http query reponse for the provided valid query id.

        :parameter query_id: The id of the HTTP request.
        :parameter no_clear: If provided the camelot retains the response
         for future retrieval purpose on returning to the user.
         By default Camelot clears the received response on returning to
         the user.This parameter lets the user to instruct the camelot to
         override the default behaviour.

        :returns: Returns http response on success. on failure returns the
         empty list.
         The following fields are returned in http response:\n
         * body : body of the received HTTP response alone.
         * statuscode : statuscode received in HTTP response.
         * redirqueryid : It holds the queryid to get the intermediate
           responses,if the submitted query using
           httpqueryreq has more than one response.
         * query : actual query made.
         * edgenode : Host address of the VCS-E node,if
           the query node was made on Collab Edge deployment
           otherwise it will be empty.
         * edgeport : Port of the VCS-E node used to send the
           query when submitted on Collab Edge deployment
           otherwise it will be empty.
         * servicenode :
               * For On-Premise it shows the server that the
                 query  was sent to.
               * For Collab Edge it shows the service node to
                 which the query was sent through VCS-E node.
         * serviceport : Defines the server port used for query.
               * For On-Premise it shows the server port to which
                 the query was sent.
               * For Collab Edge it shows the service node port to
                 which the query was sent through VCS-E node.
         * starttime : Query Time, in YYYY-MM-DDTHH:MM:SS format
         * tlscipher : TLS cipher value negotiated for the HTTPS
           connection.
         * camelot_reason : Error text describing various
           application based error scenario with resect to the
           query and it's response.
               * For Eg: if Camelot stops generating further request due to
                 repetitive 401 received then camelot_reason will be as below
                 as part of the query ID to which final 407 belongs.\n
               camelot_reason = repetitive 401, Camelot stopped handling\n

         Please refer to the below link for more details on this.
         'https://wiki.cisco.com/display/CAMELOT/httpqueryresponse'

        >>> ep1.http_query_response(32771)
         { 'query': '/cucm-uds/clusterUser?username=JABBEREP1200001',
           'servicenode': 'cam-feature12-pub','starttime':'2014-1-7T20:37:15',
           'redirqueryid':'','statuscode':'200',
           'camelot_reason': '','edgenode': '','edgeport': '',
           'serviceport': '8443','tlscipher': 'ECDHE-RSA-AES256-GCM-SHA384',
           'Cache-Control':'private','Expires': 'Thu, 01 Jan 1970 05:30:00 IST,
           'X-Frame-Options':'SAMEORIGIN','Content-Type':'application/xml',
           'Content-Length':'205','Date':Tue, 07 Jan 2014 15:07:15 GMT',
           'Server':''body':'<?xml version="1.0" encoding="UTF-8"
           standalone="yes"?><clusterUser version="10.5.0"
           uri="https://cam-feature12-pub:8443/cucm-uds/clusterUser?
           username=JABBEREP1200001"><result found="false"/></clusterUser>'}

        '''
        queryid = kwargs.get('queryid', None)
        if queryid:
            query_id = queryid
        if not query_id:
            camelot.CamelotError('Specify query id')
            return

        if no_clear:
            config_request = '{} {} {}'.format(
                camelot.HTTP_QUERY_RESPONSE, query_id, 'noclear')
        else:
            config_request = '{} {} {}'.format(
                camelot.HTTP_QUERY_RESPONSE, query_id, 'clear')

        return self._query_camelot(
            camelot.HTTP_QUERY_RESPONSE, config_request)

    def http_clear_response(self, query_id, **kwargs):
        '''Clears the http responses retained with camelot.

        :parameter query_id: The id of the HTTP request which was
            placed through httpqueryreq command.

        :returns: 1 on success 0 on failure.

        >>> ep.http_clear_response(queryid)
        1
        '''
        queryid = kwargs.get('queryid', None)
        if queryid:
            query_id = queryid
        if query_id:
            config_request = '{} {}'.format(camelot.HTTP_CLEAR_RESPONSE,
                                            query_id)
        else:
            config_request = (camelot.HTTP_CLEAR_RESPONSE)
        return self._query_camelot(camelot.HTTP_CLEAR_RESPONSE,
                                   config_request)

    def get_imp_info(self):
        '''Shows the login status of both IMP and XMPP login for
        an endpoint along with additional details of IMP and XMPP login

        :returns: contains the list of dictionaries with {field, value} pars.\n
         The following fields are supported:\n

         * imp login state :  Shows the login state of the IMP login.
           Possible values are: loggedout, loggingin and loggedin.
         * xmpp login state :  Shows the login state of the XMPP login.
           Possible values are: loggedout, loggingin and loggedin.
         * imp login type : The type of the imp login. The possible values are:
                * sso : When Camelot used  username/ SSO-oAuthkey
                        for the IM/P login.
                * uc-directory : when Camelot used username/password for
                                 the IM/P login.
         * failure reason : Shows the failure reason of IMP or XMPP login
         * cups server : shows the IMP server used for IMP and XMPP login.
         * cups port : shows the IMP server port used for IMP login
         * imp session key : shows the session key received after the
           successful login of IMP login.
         * vtg-token : Shows the vtg token received as part of SOAP
           get-onetime-password API.
         * buddy list refresh - status of buddy list refresh.
         Below are the possible values:\n
             * "" - initial value
             * pending - refresh is started
             * success - refresh is completed successfully
             * failed - refresh is failed
         * full_jid : the full jid received from xmpp server from bind
           response. The format of it would be user@domain/resource
         * jid : it is bare jid of full jid. The bare jid would contain
           username@domain
         * stream_management : displays status of stream management requests
            * status\n
              Below are the possible values:
                 * "" - initial value
                 * enabled - stream management enabled
                 * failed -  stream management disabled

         Please refer to the below link for more details on this.
         https://wiki.cisco.com/display/CAMELOT/IMP+and+XMPP
        >>> ep.get_imp_info()
         {
          'imp login state': 'loggedin',
          'xmpp login state': 'loggedin',
          'imp login type': 'sso',
          'failure reason': '',
          'active cup server': 'cam-cup-107.camelot.test',
          'active cup port': '8443',
          'primary cup server': 'cam-cup-107.camelot.test',
          'primary cup port': '8443',
          'backup1 cup server': 'cam-cup-131.camelot.test',
          'backup1 cup port': '8443',
          'backup2 cup server': '',
          'backup2 cup port': '',
          'imp session key': 'd49dfd0f-d4cf-4935-8857-56669644185f',
          'vtg-token': '',
          'buddy list refresh': '',
          'last login response timestamp': '2020-10-22::00:51:53:179',
          'imp cipher': 'ECDHE-RSA-AES256-GCM-SHA384',
          'xmpp cipher': 'ECDHE-ECDSA-AES256-GCM-SHA384',
          'full_jid': 'jabberep1200001@camelot.test/
           f9759a191aa6be451b5cd0ebc0a1148b73f1b64c',
          'jid': 'jabberep1200001@camelot.test',
          'stream management': {
          'status': 'enabled',
          },
          }
        '''
        return self._query_camelot(camelot.GET_IMP_INFO)

    def get_uds_info(self):
        '''returns the current UDS login information, like state,
        home node cluster, current UDS server, UDS server cache list.

        :returns: a variable sized list of dictionaries with {field value}
        pairs containing extended information about the uds login
        information.\n
            * state : current UDS Login state.
              Stable states are{} uds_login_complete/uds_appl_request_complete
              Error states are uds_centuds_disc_error/uds_home_cluster_node
              _disc_error uds_home_node_version_error/uds_get_uds
              servers_error uds_sso_login_error/uds_get_service_profile_error
              uds_device_discovery_error/uds_login_error
              uds_appl_request_error/uds_server_refresh_req_error
            * home-uds server :  Home node server host name
            * curr-uds server : Current UDS server picked for UDS requests.
            * version : Current UDS server version number
            * attempts : No of UDS login attempts
            * sucesses : No of UDS login successes
            * failures : No of UDS login failures
            * error code : HTTP response code for any UDS query request.
            * failure reason : Describes the failure reason for UDS
              login or any application UDS query request.
            * complete error response : Complete HTTP error response
              from network
            * uds servers cache : UDS servers cache list separated
              with space.
            * refresh interval : UDS server cache refresh interval
              selected/calculated after rand(). Units is minutes.
            * first login : Specifies current login flow attempted
              is a initial login flow/subsequent login flow.
            * uds server refresh : status of uds server list refresh.
              Below are the possible values:\n
             * "" - initial value
             * pending - refresh is started
             * success - refresh is completed successfully
             * failed - refresh is failed
            * uds query url status key_value pair : displays any UDS query
              download status. The possible key names are "version_query",
              "user_query", "devices_query", "max_devices_query",
              "em_loggedin_devices", "bulk_query", "remote_destination",
              "version_query_optional"
              For more information refer wiki
              https://wiki.cisco.com/display/CAMELOT/Jabber+Simulation#JabberSimulation-UDSlogin


         >>> ep.get_uds_info()
         >>> ep1.get_info()['state']
          'inservicepending'
         >>> ep1.get_uds_info()
         {
          'state': 'uds_login_complete',
          'first login': 'yes',
          'attempts': '1',
          'successes': '1',
          'failures': '0',
          'home-uds server': 'cam-ccm-118.camelot.test',
          'curr-uds server': 'cam-ccm-118.camelot.test',
          'version': '',
          'error code': '200',
          'failure reason': '',
          'complete error response': '',
          'uds servers cache': 'cam-ccm-118.camelot.test',
          'refresh interval': '3',
          'uds server refresh': '',
          'tlscipher': 'ECDHE-RSA-AES256-GCM-SHA384',
          'tlscurves': 'P-521:P-384:P-256:P-192',
          'devices_query': {
          'url': '/Y2FtZWxvdC50ZXN0L2/cucm-uds/user/JABBEREP1100001/devices',
          'camelot_reason': 'http edge server cam-vcse-154.camelot.test
           conn error:socket error: attempt to http failover',
          'inservice_impact': 'True',
          'response': {
          'response_code': '0',
          'response_phrase': 'connection error',
          'warning': '',
         },
         },
         }

         >>> ep1.get_info()['state']
          'inservicepending'
         >>> ep1.get_uds_info()
         {
          'state': 'uds_login_complete',
          'first login': 'yes',
          'attempts': '1',
          'successes': '1',
          'failures': '0',
          'home-uds server': 'cam-ccm-118.camelot.test',
          'curr-uds server': 'cam-ccm-118.camelot.test',
          'version': '',
          'error code': '200',
          'failure reason': '',
          'complete error response': '',
          'uds servers cache': 'cam-ccm-118.camelot.test',
          'refresh interval': '3',
          'uds server refresh': '',
          'tlscipher': 'ECDHE-RSA-AES256-GCM-SHA384',
          'tlscurves': 'P-521:P-384:P-256:P-192',
          'devices_query': {
          'url': '/Y2FtZWxvdC50ZXN0L2/cucm-uds/user/JABBEREP1100001/devices',
          'camelot_reason': '',
          'inservice_impact': 'True',
          'response': {
          'response_code': '200',
          'response_phrase': '',
          'warning': '',
         },
         },

         >>> ep1.get_info()['state']
          'inservicepending'

         >>> ep1.get_uds_info()
         {
          'state': 'uds_login_complete',
          'first login': 'yes',
          'attempts': '1',
          'successes': '1',
          'failures': '0',
          'home-uds server': 'cam-ccm-118.camelot.test',
          'curr-uds server': 'cam-ccm-118.camelot.test',
          'version': '',
          'error code': '200',
          'failure reason': '',
          'complete error response': '',
          'uds servers cache': 'cam-ccm-118.camelot.test',
          'refresh interval': '3',
          'uds server refresh': '',
          'tlscipher': 'ECDHE-RSA-AES256-GCM-SHA384',
          'tlscurves': 'P-521:P-384:P-256:P-192',
          'devices_query': {
          'url': '/Y2FtZWxvdC50ZXN0L2/cucm-uds/user/JABBEREP1100001/devices',
          'camelot_reason': '',
          'inservice_impact': 'True',
          'response': {
          'response_code': '200',
          'response_phrase': '',
          'warning': '',
         },
         },
          'version_query_optional': {
          'url': '/Y2FtZWxvdC50ZXN0L2/cucm-uds/version',
          'camelot_reason': '',
          'inservice_impact': 'False',
          'response': {
          'response_code': '200',
          'response_phrase': '',
          'warning': '',
         },
         },
          'batch_query': {
          'email': {
          'url': '/Y2FtZWxvdC50ZXN0L2/cucm-uds/private/users',
          'camelot_reason': 'Bad Request',
          'inservice_impact': 'False',
          'response': {
          'response_code': '400',
          'response_phrase': '400 Bad Request',
          'warning': '',
         },
         },
          'name': {
          'url': '/Y2FtZWxvdC50ZXN0L2/cucm-uds/private/users',
          'camelot_reason': 'edge server cam-vcse-152.camelot.test error:502
           Next Hop Connection Failed: list exhaust, waiting for next cycle',
          'inservice_impact': 'False',
          'response': {
          'response_code': '502',
          'response_phrase': '502 Next Hop Connection Failed',
          'warning': '',
         },
         },
         },
         }

         >>> ep1.get_info()['state']
          'inservice'

         >>> ep1.get_uds_info()
         {
          'state': 'uds_login_complete',
          'first login': 'yes',
          'attempts': '1',
          'successes': '1',
          'failures': '0',
          'home-uds server': 'cam-ccm-118.camelot.test',
          'curr-uds server': 'cam-ccm-118.camelot.test',
          'version': '',
          'error code': '200',
          'failure reason': '',
          'complete error response': '',
          'uds servers cache': 'cam-ccm-118.camelot.test
           cam-ccm-116.camelot.test cam-ccm-99.camelot.test
           cam-ccm-117.camelot.test',
          'refresh interval': '3',
          'uds server refresh': 'pending',
          'tlscipher': 'ECDHE-RSA-AES256-GCM-SHA384',
          'tlscurves': 'P-521:P-384:P-256:P-192',
          'get_edge_config': {
          'url': '/Y2FtZWxvdC50ZXN0/get_edge_config/',
          'camelot_reason': 'http edge server cam-vcse-154.camelot.test
           conn error:socket error: list exhaust, waiting for next cycle',
          'inservice_impact': 'False',
          'response': {
          'response_code': '0',
          'response_phrase': 'connection error',
          'warning': '',
         },
         },
          'devices_query': {
          'url': '/Y2FtZWxvdC50ZXN0L2/cucm-uds/user/JABBEREP1100001/devices',
          'camelot_reason': '',
          'inservice_impact': 'True',
          'response': {
          'response_code': '200',
          'response_phrase': '',
          'warning': '',
         },
         },
          'version_query_optional': {
          'url': '/Y2FtZWxvdC50ZXN0L2/cucm-uds/version',
          'camelot_reason': '',
          'inservice_impact': 'False',
          'response': {
          'response_code': '200',
          'response_phrase': '',
          'warning': '',
         },
         },
          'batch_query': {
          'email': {
          'url': '/Y2FtZWxvdC50ZXN0L2/cucm-uds/private/users',
          'camelot_reason': 'Bad Request',
          'inservice_impact': 'False',
          'response': {
          'response_code': '400',
          'response_phrase': '400 Bad Request',
          'warning': '',
         },
         },
          'name': {
          'url': '/Y2FtZWxvdC50ZXN0L2/cucm-uds/private/users',
          'camelot_reason': 'edge server cam-vcse-152.camelot.test error:502
           Next Hop Connection Failed: list exhaust, waiting for next cycle',
          'inservice_impact': 'False',
          'response': {
          'response_code': '502',
          'response_phrase': '502 Next Hop Connection Failed',
          'warning': '',
         },
         },
         },
         }
        '''
        return self._query_camelot(camelot.GET_UDS_INFO)

    def get_uds_user(self):
        '''
        returns uds user response as a json object(dictionary)

        :returns: Dictionary on success and None on failure

        >>> ep.get_uds_user()
        {user': {@uri': https://cam-ccm-57.camsso.test:844
        /cucm-uds/user/JABBEREP1200001',
        @version': 12.5.0',
        accountType': {#text': ldap', @useLdapAuth': true'},
        allowProvisionEMMaxLoginTime': false',
        callForwardAllDestination': {
        @appliesToAllExtensions': true',
        destination': None,
        sendToVoiceMailPilotNumber': false'},
        credentials': {@uri': https://cam-ccm-57.camsso.test:
        8443/cucm-uds/user/JABBEREP1200001/credentials'},
        department': None,
        devices': {@uri': https://cam-ccm-57.camsso.test:8443/
        cucm-uds/user/JABBEREP1200001/devices'},
        directoryUri': None,
        displayName': jabberep1200001',
        emMaxLoginTime': None,
        email': jabberep1200001@camsso.test',
        enableDoNotDisturb': {#text': false',
        @appliesToAllDevices': true'},
        extensions': {@uri': https://cam-ccm-57.camsso.test:8443/
        cucm-uds/user/JABBEREP1200001/extensions'},
        firstName': jabberep1200001',
        homeCluster': {#text': true',
        @enableCalendarPresence': false',
        @enableImAndPresence': true'},
        homeNumber': None,
        id': 5f66fe4a-cc50-41d2-137a-05978b2d45df',
        imAndPresence': {server': cam-cup-77.camsso.test'},
        lastName': jabberep1200001',
        manager': None,
        middleName': None,
        mobileConnect': false',
        mobileNumber': None,
        msUri': None,
        nickName': None,
        pager': None,
        phoneNumber': None,
        remoteDestinationLimit': 4',
        selfServiceId': None,
        serviceProfile': {uri': http://cam-ccm-8:6970/SPDefault.cnf.xml'},
        speedDials': {@uri': https://cam-ccm-8:8443/cucm-uds/
        user/JABBEREP1200001/speedDials'},
        subscribedServices': {@uri': https://cam-ccm-8:8443/
        cucm-uds/user/JABBEREP1200001/subscribedServices'},
        title': None,
        userLocale': {
        #text': English, United States',
        @appliesToAllDevices': true',
        @uri': https://cam-ccm-8:8443/cucm-uds/options/installedLocales',
        @value': ',
        },
        userName': JABBEREP1200001',
        }}
        '''
        return self._query_camelot(camelot.GET_UDS_USER)

    def close_xmpp_im(self, jabber_id):
        '''
        closes  im  sesion with the buddy whose jabber id is given

        :parameter jabber_id: The jabber id of the buddy

        :returns: True on success and False on failure

        >>> ep.close_xmpp_im(jabber_id)
        1
        '''
        log.debug('Entering method close_xmpp_im().')
        if not jabber_id:
            log.error('jabber id not specified')
            return
        return self._query_camelot(camelot.XMPP_CLOSE_IM, jabber_id)

    def sso_login(self, user_name='default', user_mode='user',
                  login_type='jabber', imp_login='implogin', jsession_id='no',
                  jsession_id_sso='no'):
        '''
        Invokes the SSO based login with configured sip.phone.sso
        paramters and/or argument values. It internaly invokes,
        the various UDS and IDP queries required to get SSO OAuth token.
        The queries involves, home node discovery, sso mode discovery,
        SAML request/response processing and OAuth token retrieval.

        :parameter user_name:  user_name used for home node discovery
         and IDP authentication
        :parameter user_mode: user_mode decides the argument name while forming
         the home node discovery query. Refer sip.phone.sso.
        :parameter login_type: type decides to invoke jabber bassed SSO login
         or browser based SSO login.  Refer sip.phone.ssso
        :parameter jsession_id:  jsession_id value retrieved in the
         previous successful login
        :parameter jsession_id_sso: jsession_id_sso of the previous
         successful login

        :returns: The current ssologin state, either loggingin or loggedout.

        >>> ep.sso_login('jabber1000', 'user', 'jabber')
        'loggingin'
         It invokes the jabber based sso login for the user jabber1000 by
         forming the home node discovery query with argument type as user_name.
         Note: If mode is email then argument type  is email. And jsessionid
         and jsession_id_sso are only applicable for browser based login.
        '''
        kwargs = {'user_name': user_name,
                  'user_mode': user_mode,
                  'login_type': login_type,
                  'imp_login': imp_login,
                  'jsession_id': jsession_id,
                  'jsession_id_sso': jsession_id_sso
                  }
        return self._query_camelot(camelot.SSO_LOGIN, None, **kwargs)

    def get_secure_uds_users_access_url_info(self):
        '''returns the configured secured UDS users access URL information
         received in device config xml file.

        :returns: A variable sized list of dictionaries with {field value}
        pairs containing URL server, port, url path etc., information.
            * secure_uds_users_access_url_parsed :  Url present status
                * True - Url tag is present
                * False- Url tag is not present
            * secure_uds_users_access_url :  Complete url
            * host_name : Url server host name
            * port : Url server port
            * url : Url service path
            * secure : Url is secured or not
                * True - Url is secured (https)
                * False- Url is non-secured (http)

        >>> ep.get_secure_uds_users_access_url_info()
        {'secure_uds_users_access_url_parsed' : 'True',
        'secure_uds_users_access_url' :
        'cam-feature4-pub:8443/cucm-uds/users',
        'host_name' : 'cam-feature4-pub.camelot.test',
        'port': 8443, 'url' : 'cucm-uds/users', 'secure' : 'True'
        }
        '''
        return self._query_camelot(camelot.
                                   GET_SECURE_UDS_USERS_ACCESS_URL_INFO)
