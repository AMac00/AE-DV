from threading import RLock
import socket
import json

import camelot
from camelot.endpoint import CamelotEndpoint
from camelot.encoder import encoder
from camelot.bcg.bcg_connection import Connection
from camelot.bcg.bcg_instance import BcgInstance
from camelot import camlogger

connections = {}
_connections_lock = RLock()
_server_callbacks = {}

log = camlogger.getLogger(__name__)

bcginstances = {}


class Bcg(object):
    '''BCG instance representation
    '''
    def __init__(self, ip, port):
        self.bcgref = None  # This should mirror the instance ref
        self.bcgname = None
        self.bcgserv_ip = ip
        self.bcgserv_port = port

    def start(self):
        '''Start the bcg server to schedule calls

        >>> bcgobj.start()
        '''
        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        bcg_params = {
            'bcgref': self.bcgref,
        }
        response = server_conn.execute_bcg_command(
            camelot.START_BCG, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def stop(self):
        ''' Stop the bcg server to schedule calls

        >>> bcgobj.stop()
        '''
        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        bcg_params = {
            'bcgref': self.bcgref,
        }
        response = server_conn.execute_bcg_command(
            camelot.STOP_BCG, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def add_endpoint(self, endpoint, autocmd_type='call'):
        ''' add endpoint to the bcg queue

        :parameter endpoint: endpoint object created
                             by camelot.create_new_endpoint()
        :parameter type: operation type. Possible values:\n
                         * call - invoke placecall from BCG
                         * script - invoke placescript from BCG
                         * camelot_api - invoke any camelot API.The API
                           should be specified using "set_camelot_api" method
                           in BCG level.

        >>> bcgobj.add_endpoint(ep)
        '''
        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        epref = '{}:{}:{}'.format(
            endpoint.ip, endpoint.port, endpoint.ep_id)
        bcg_params = {
            'bcgref': self.bcgref,
            'epref': epref,
            'autocmd_type': autocmd_type,
            'ep_type': endpoint.ep_type,
        }
        response = server_conn.execute_bcg_command(
            camelot.ADD_TO_BCG, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def set_camelot_api(self, endpoint, api_name, api_args={}):
        '''It is used for specifying a particular camelot API which
        will be invoked by BCG according to configured rate.\n

        :parameter endpoint: endpoint object created
                             by camelot.create_new_endpoint()
        :parameter api_name: name of the API to be invoked
        :parameter api_args: valid arguments of the API in dictionary
                            format.

        >>> bcgobj.set_camelot_api(ep, 'http_query_request',
                {'ip':'10.12.10.74', 'port':'8443',
                 'url':'/cucm-uds/clusterUser?username=JABBEREP1300000',
                 'secure':True})

        Note: Before calling this method we must invoke BCG command
        "add_endpoint" which should have "camelot_api" as second parm.
        For example:

        >>> bcgobj.add_endpoint(ep, 'camelot_api')

        '''

        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        epref = '{}:{}:{}'.format(
            endpoint.ip, endpoint.port, endpoint.ep_id)
        bcg_params = {
            'bcgref': self.bcgref,
            'epref': epref,
            'cmd': api_name,
            'args': api_args
        }
        response = server_conn.execute_bcg_command(
            camelot.SET_CAMELOT_API, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def remove_endpoint(self, endpoint):
        ''' remove endpoint from the bcg queue

        :parameters endpoint: endpoint object created by create_new_endpoint()

        >>> bcgobj.remove_endpoint(ep)
        '''
        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        epref = '{}:{}:{}'.format(
            endpoint.ip, endpoint.port, endpoint.ep_id)
        bcg_params = {
            'bcgref': self.bcgref,
            'epref': epref,
        }
        response = server_conn.execute_bcg_command(
            camelot.REMOVE_FROM_BCG, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def set_name(self, name):
        ''' set the name to the bcg instance

        :parameter name: name of the bcg

        >>> bcgobj.set_name()
        '''
        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        self.bcgname = name
        bcg_params = {
            'bcgref': self.bcgref,
            'name': self.bcgname,
        }
        response = server_conn.execute_bcg_command(
            camelot.SET_BCG, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def set_rate_sample_period(self, sampleperiod):
        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        bcg_params = {
            'bcgref': self.bcgref,
            'sampleperiod': sampleperiod
        }
        response = server_conn.execute_bcg_command(
            camelot.SET_BCG, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def get_name(self):
        '''get the name of bcg instance

        :returns: name of the bcg

        >>> bcgobj.get_name()
        'bcg1'
        '''

        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        bcg_params = {
            'bcgref': self.bcgref,
        }
        response = server_conn.execute_bcg_command(
            camelot.GET_BCG_NAME, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def get_info(self):
        '''get the bcg information

        :returns: dictionary of bcg information as shown below \n

        >>> bcgobj.get_info()
        {'endpoints queued': '199', 'state': 'running',
        'actual rate': '4.94', 'set rate': '5.0'}
        '''

        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        bcg_params = {
            'bcgref': self.bcgref,
        }
        response = server_conn.execute_bcg_command(
            camelot.GET_BCG_INFO, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def get_stats(self):
        '''get the bcg statistics information

        :returns: dictionary of bcg statistics shown below \n

        >>> bcgobj.get_stats()
        {'aborted endpoint': '', 'aborted reason': '',
        'attempts': '92', 'aborts': '0'}
        '''
        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        bcg_params = {
            'bcgref': self.bcgref,
        }
        response = server_conn.execute_bcg_command(
            camelot.GET_BCG_STATS, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def get_members(self):
        '''
        get the members from bcg server list.  It will return a
        list of endpoint references

        returns: list of endpoint references added

        >>> bcgobj.get_members()
        ['192.168.1.109:5000:00000004'. '192.168.1.109:5000:00000005',...]
        '''
        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        bcg_params = {
            'bcgref': self.bcgref,
        }
        response = server_conn.execute_bcg_command(
            camelot.GET_BCG_MEMBERS, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def get_state(self):
        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        bcg_params = {
            'bcgref': self.bcgref,
        }
        response = server_conn.execute_bcg_command(
            camelot.GET_BCG_STATE, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def set_rate(self, rate):
        ''' set the bcg cps rate

        :parameter rate:  calls per second rate

        >>> bcgobj.set_rate(2.0)

        '''
        server_conn = _get_bcg_connection(
            self.bcgserv_ip, self.bcgserv_port, self.bcgref
        )
        bcg_params = {
            'bcgref': self.bcgref,
            'bcgrate': rate,
        }
        response = server_conn.execute_bcg_command(
            camelot.SET_BCG, bcg_params=bcg_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']


def _get_bcg_connection(ip, port, bcgref=None):
    connection_key = '{}:{}'.format(ip, port)
    if bcgref and not bcginstances.get(bcgref):
        raise camelot.CamelotError(
            "Invalid bcg instance {} at ({}, {})".format(bcgref, ip, port)
        )

    with _connections_lock:
        if not connections.get(connection_key, None):
            conn = Connection(ip, port)
            connections[connection_key] = conn

    server_conn = connections.get(connection_key, None)
    if not server_conn:
        raise camelot.CamelotError(
            "Unable to create Connection object to BCG server at ({}, {})"
            "".format(ip, port)
        )
    return server_conn


def create_new_bcg(ip, port, *args, **kwargs):
    '''Create a new bcg instance'

    :parameter ip: ip of the bcg server
    :parameter port: port of the bcg server

    :returns: bcg reference

    >>> bcgobj = camelot.bcg.create_new_bcg('10.12.10.188',30101)
    '''
    bcg_class = kwargs.get('bcg_class', Bcg)
    bcgInstance_class = kwargs.get('bcginstance', None)
    bcg_params = kwargs.get('bcg_params', {})

    if not issubclass(bcg_class, Bcg):
        raise CamelotError('bcg_class not subclass of Bcg')

    if not ip:
        raise camelot.CamelotError('ip is not specified')
    if not port:
        raise camelot.CamelotError('port is not specified')

    IP = socket.gethostbyname(ip)
    server_conn = _get_bcg_connection(IP, port)
    response = server_conn.execute_bcg_command(camelot.NEW_BCG,
                                               bcgInstance_class,
                                               bcg_params=bcg_params)
    if response and not response['rc']:
        raise camelot.CamelotError('create bcg failed')
    newbcg = bcg_class(ip, port)
    newbcg.bcgref = response['msg']
    bcginstances[newbcg.bcgref] = newbcg
    log.debug('created bcg {}: {}'.format(newbcg.bcgref, newbcg))
    return newbcg


def delete_bcg(ip, port, bcgref):
    '''Delete requested bcg instance'

    :parameter ip: ip of the bcg server
    :parameter port: port of the bcg server

    :returns: bcg reference

    >>> camelot.bcg.delete_bcg('10.12.10.188', 30101)
    '''
    IP = socket.gethostbyname(ip)
    server_conn = _get_bcg_connection(IP, port)
    bcg_params = {
        'bcgref': bcgref,
    }
    response = server_conn.execute_bcg_command(camelot.DELETE_BCG,
                                               bcg_params=bcg_params)
    if response and not response['rc']:
        raise camelot.CamelotError(response['msg'])
    del bcginstances[bcgref]
    return bcgref


def get_bcgs():
    return bcginstances.keys()


def stop_all():
    log.debug("Closing all BCG connections")
    with _connections_lock:
        for key, conn in connections.items():
            conn.close_event_channel()
        connections.clear()
