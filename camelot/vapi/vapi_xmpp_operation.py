import camelot
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger

log = camlogger.getLogger(__name__)


class CamelotXMPPOperations(v.CamelotVapiUtils):

    '''Camelot vvm feature representation
    '''
    def add_group(self, name):
        '''
        Adds a new group. If the provided group name already exsits
        then this command will fail. Currently when this command is
        invoked Camelot do creates and maintains the group locally,
        as well as pushes it to the server as private storage/group.

        :parameter name: Name of the group

        :returns: on success 1 will be returned otherwise
         CamelotError: 0 exception.

        >>> ep1.addgroup('cisco-camelot-team')
        1
        '''
        if not name:
            camelot.CamelotError("invalid group name, it is empty")
        group = name.replace(" ", "___")
        return self._query_camelot(camelot.ADD_GROUP, group)

    def remove_group(self, name):
        '''
        removes the group, if exists, from the local storage of Camelot.
        If the provided group name doesn't exists then this command will
        fail. Once the group is removed then all the contacts which belong
        to this group will be disassociated from this group along with
        local storage and from IMP server. If no contacts are associated
        with the group ,Camelot sends the request to IMP server to remove
        this private group along with removing it from local storage.
        Use imp_query_response command to get the status of the returned
        queryid.

        :parameter name: Name of the group

        :returns: on success queryid will be returned otherwise
         CamelotError: 0 exception.

        >>> ep1.remove_group('monkey')
        4063652144
        '''

        if not name:
            camelot.CamelotError("invalid group name, it is empty")
        group = name.replace(" ", "___")
        return self._query_camelot(camelot.REMOVE_GROUP, group)

    def remove_all_buddies(self):
        '''
        Removes the entire roster(buddy list ) of the user.
        The groups will not be removed.

        :returns: on success queryid will be returned otherwise
         CamelotError: 0 exception.

        >>> ep1.remove_all_buddies()
        1
        '''
        return self._query_camelot(camelot.REMOVE_ALL_BUDDIES)

    def show_groups(self):
        ''' shows the groups created for this user.

        :returns: shows the groups of the user.

        >>> ep1.show_groups()
        ['group1', 'group2']
        '''
        log.debug('in method show groups')
        return self._query_camelot(camelot.SHOW_GROUPS)

    def get_buddies_by_group(self, group_name):
        '''shows the buddies belongs to the provided group.

        :parameter: Mandatory parameter. Name of the group

        :returns: the buddies in the list format, empty list if nobody exists

        >>> ep1.get_buddies_by_group('friends')
        [jabberep1300001@camelot.test, jabberep1300002@camelot.test]
        '''
        log.debug("in method get_buddies_by_group")
        if not group_name:
            camelot.CamelotError("group name is None")
        return self._query_camelot(camelot.GET_BUDDIES_BY_GROUP, group_name)

    def add_buddy(self, buddy_jid, display_name=None, groups=None):
        '''
        adds a buddy to the user's roster list if buddy is not already
        present in roster list
        else it throws CamelotError exception. On successfully
        sending the request to server the Camelot returns the
        query-id to the clients otherwise it returns the 0.
        On recieving the response from server the Camelot generates
        the station event in the form "impquerycompleted status query-id jid".
        The clients are expected to wait for this event and on receiving this
        event they can call the command "imp_query_response" to get response.

        :parameter buddy_jid: This is mandatory parameter and takes the buddy
         name in the JID form as explained in xmpp RFC 6121.
         ex: jabberep@camelot.test
        :parameter display_name:  This is optional parameter. It takes the
         display name of the buddy.
        :parameter groups:  This is optional parameter.This parameter takes
         the groups to which the buddy will be part of.More than one group must
         be seperated by comma(,). The group names provided here must have
         been created already using "addgroup" command.

        :returns:  on success the quesryid will be returned otherwise
         CamelotError: 0 exception.

        >>> ep1.add_buddy('jabberep1300001@camelot.test', 'ep1300001',
         "team,friends"]
        4063316224
        >>> ep1.imp_query_response('4063316224')
        {'status': 'success', 'command':'addbuddy',
        'contact':'jabberep1300001@camelot.test',
        'starttime': '2014-07-24T18:04:09', 'failure reason':'',
        'xml stanza':'' }

        '''
        if not buddy_jid:
            camelot.CamelotError("buddy_jid is empty, provide the buddy jid")

        msg = '{}^'.format(buddy_jid)
        if not display_name:
            display_name = '0'
        msg += '{}^'.format(display_name)
        if not groups:
            groups = '0'
        msg += '{}'.format(groups)

        return self._query_camelot(camelot.ADD_BUDDY, msg)

    def remove_buddy(self, jid):
        '''
        Removes the buddy from the user's roster(buddy list).

        :parameter jid: This is mandatory parameter and takes the buddy
         name in the JID form as explained in xmpp RFC 6121.
         ex: jabberep@camelot.test

        :returns: on success queryid will be returned otherwise
         CamelotError: 0 exception is returned.

        >>> ep1.get_buddy_list()
        ['jabberep@camelot.test']
        >>> ep1.remove_buddy('jabberep@camelot.test')
        '4043253308'
        >>> ep1.get_buddy_list()
        []
        '''
        log.debug("in the method remove_buddy with jid")
        if not jid:
            camelot.CamelotError("buddy_jid is empty, provide the buddy jid")
        return self._query_camelot(camelot.REMOVE_BUDDY, jid)

    def get_buddy_list(self, uniqueid='jid'):
        '''Returns the list of buddies for the mentioned end point on the basis
        of the unique id mentioned.

        :parameter uniqueid: Unique id. Can take the following values \n
            * jid
            * username
            * emailid
            * phonenumber

        :returns: list of buddy's jid, for more information
         on buddy like mobilenumber, firstname etc can be found
         using get_user_info api.

        >>> ep1.get_buddy_list()
        ['regep3200003@camelot.test']
        '''
        return self._query_camelot(camelot.GET_BUDDY_LIST, uniqueid)

    def add_buddy_to_group(self, jid, groups):
        '''
        Add the buddy from the user's roster(buddy list) to groups.
        if buddy is not part of roster list it will throw
        CamelotError exception.

        :parameter jid: This is mandatory parameter and takes the buddy
         name in the JID form as explained in xmpp RFC 6121.
         ex: jabberep@camelot.test
        :parameter groups:  This is mandatory parameter.This parameter takes
         the groups to which the buddy will be part of.More than one group must
         be seperated by comma(,). The group names provided here must have
         been created already using "addgroup" command.

        :returns: on success queryid will be returned otherwise
         CamelotError: 0 exception is returned.

        :note: To add a buddy to a group, buddy should be in roaster list.

        >>> ep1.add_buddy_to_group('jabberep@camelot.test',
            'group1, group2')
        '4043253308'
        '''
        log.debug("in the method remove_buddy with jid")
        if not jid or not groups:
            log.error("arguments passed are none")
        msg = '{}^{}'.format(jid, groups)
        return self._query_camelot(camelot.ADD_BUDDY_TO_GROUPS, msg)

    def move_buddy_to_groups(self, jid, from_groups, to_groups):
        '''
        Moves a buddy from one or more groups to other groups.

        :parameter jid: This is mandatory parameter and takes the buddy
         name in the JID form as explained in xmpp RFC 6121.
         ex: jabberep@camelot.test
        :parameter from_group: This parameter takes the groups to which the
         buddy already belongs to. More than one group must
         be seperated by comma(,). The group names provided here must have
         been created already using "addgroup" command.
        :parameter to_group: This parameter takes the groups to which the
         buddy needs to move to. More than one group must
         be seperated by comma(,). The group names provided here must have
         been created already using "addgroup" command.

        :returns: on success queryid will be returned otherwise
         CamelotError: 0 exception is returned.

        >>> ep1.move_buddy_to_groups('jabberep@camelot.test',
            'group1, group2', 'group3, group4')
        '4043253308'
        '''
        log.debug("in the method remove_buddy with jid")
        if not jid or not from_groups or not to_groups:
            log.error("arguments passed are none")
        msg = '{}^{}^{}'.format(jid, from_groups, to_groups)
        return self._query_camelot(camelot.MOVE_BUDDY_TO_GROUPS, msg)

    def remove_buddy_from_groups(self, jid, groups):
        '''
        removes a buddy from the provided groups.

        :parameter jid: This is mandatory parameter and takes the buddy
         name in the JID form as explained in xmpp RFC 6121.
         ex: jabberep@camelot.test
        :parameter groups:  This is mandatory parameter.This parameter takes
         the groups to which the buddy will be part of.More than one group must
         be seperated by comma(,). The group names provided here must have
         been created already using "addgroup" command.

        :returns: on success queryid will be returned otherwise
         CamelotError: 0 exception is returned.

        >>> ep1.remove_buddy_from_groups('jabberep@camelot.test',
            'group1, group2', 'group3, group4')
        '4043253308'
        '''
        log.debug("in the method remove_buddy with jid")
        if not jid or not groups:
            log.error("arguments passed are none")
        msg = '{}^{}'.format(jid, groups)
        return self._query_camelot(camelot.REMOVE_BUDDY_FROM_GROUPS, msg)
