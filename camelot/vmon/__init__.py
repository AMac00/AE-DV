from threading import RLock
import socket
import json

import camelot
from camelot.endpoint import CamelotEndpoint
from camelot.encoder import encoder
from camelot.vmon.vmon_connection import Connection
from camelot.vmon.vmon_instance import VmonInstance
from camelot import camlogger

connections = {}
_connections_lock = RLock()
_server_callbacks = {}

log = camlogger.getLogger(__name__)

vmoninstances = {}


class Vmon(object):

    '''Vmon instance representation, ip port and path are mandatory\n
    'from camelot import vmon' package
    '''
    def __init__(self, ip, port):
        self.vmonref = None
        self.vmonname = None
        self.vmonserv_ip = ip
        self.vmonserv_port = port

    def start(self):
        '''startmonitor Start monitoring calls

        :returns: nothing if successfull.
                  exception 'could not start monitor' is raised if failed.

        >>> vmonobj.start()
        '''
        server_conn = _get_vmon_connection(
            self.vmonserv_ip, self.vmonserv_port, self.vmonref)
        vmon_params = {
            'vmonref': self.vmonref,
        }
        response = server_conn.execute_vmon_command(
            camelot.START_MONITOR, vmon_params=vmon_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def stop(self):
        ''' stopmonitor Stops monitoring calls

        :returns: nothing if successfull.
                  exception 'monitor is not started/vmon instance is not valid'
                  is raised if failed.

        >>> vmonobj.stop()
        '''
        server_conn = _get_vmon_connection(
            self.vmonserv_ip, self.vmonserv_port, self.vmonref)
        vmon_params = {
            'vmonref': self.vmonref,
        }
        response = server_conn.execute_vmon_command(
            camelot.STOP_MONITOR, vmon_params=vmon_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def add_endpoint(self, endpoint, description):
        ''' add endpoint to the monitor(vmon server) queue for monitoring

        :parameter endpoint: endpoint object created
                             by camelot.create_new_endpoint()
        :parameter description: description of the phone

        :returns: nothing if successful,\n
                  else 'Invalid Endpoint/ endpoint already exists'
                  exception is raised

        >>> vmonobj.add_endpoint(ep,"phone 1")
        '''
        server_conn = _get_vmon_connection(
            self.vmonserv_ip, self.vmonserv_port, self.vmonref)
        epref = '{}:{}:{}'.format(
            endpoint.ip, endpoint.port, endpoint.ep_id)
        vmon_params = {
            'vmonref': self.vmonref,
            'epref': epref,
            'description': description,
        }
        response = server_conn.execute_vmon_command(
            camelot.ADD_TO_MONITOR, vmon_params=vmon_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def remove_endpoint(self, endpoint):
        ''' remove endpoint from the monitor server. Once removed,
        the endpoint will no longer be monitored

        :parameter endpoint: endpoint object created by create_new_endpoint()

        :returns: nothing if successful,\n
                  else 'Invalid Endpoint/endpoint not found' exception is
                  thrown if it fails.

        >>> vmonobj.remove_endpoint(ep)
        '''
        server_conn = _get_vmon_connection(
            self.vmonserv_ip, self.vmonserv_port, self.vmonref)
        epref = '{}:{}:{}'.format(
            endpoint.ip, endpoint.port, endpoint.ep_id)
        vmon_params = {
            'vmonref': self.vmonref,
            'epref': epref,
        }
        response = server_conn.execute_vmon_command(
            camelot.REMOVE_FROM_MONITOR, vmon_params=vmon_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def release(self):
        ''' releases monitor releases endpoints associated with the monitor.
        Does not delete monitor files or the monitor directory.

        :returns: nothing is successful, else 'No endpoints added
                  to be released' exception is thrown

        >>> vmonobj.release()
        '''
        server_conn = _get_vmon_connection(
            self.vmonserv_ip, self.vmonserv_port, self.vmonref)
        vmon_params = {
            'vmonref': self.vmonref,
        }
        response = server_conn.execute_vmon_command(
            camelot.RELEASE_MONITOR, vmon_params=vmon_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def set_monitor(self, mode=None, entries=None, events=None):
        ''' Set thresholds associated with a monitor

        :parameter entries: maximum number of entries per log file
                            by default 500
        :parameter mode: Specify which class of events to monitor:\n
                                * calls - call state events\n
                                * streams - streams events\n
                                * epstate - endpoint info events\n
                                * station - monitor specific station events\n
        :parameter events: Any of the supported (python) list of station events

        :returns: nothing if successful, else
                  'Invalid parameter/value passed' exception is thrown

        >>> vmonobj.set_monitor('calls', '1000')
        >>> vmonobj.set_monitor(
            'epstate', '1000', 'httpqueryresponse deletevvmresponse')
        '''
        server_conn = _get_vmon_connection(
            self.vmonserv_ip, self.vmonserv_port, self.vmonref)
        vmon_params = {
            'vmonref': self.vmonref,
        }
        if mode:
            vmon_params['mode'] = mode
            if events:
                vmon_params['events'] = events
        if entries:
            vmon_params['entries'] = entries
        response = server_conn.execute_vmon_command(
            camelot.SET_MONITOR, vmon_params=vmon_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def clear_monitor(self, mode=None, entries=None, events=None):
        ''' Clear user defined entries associated with a monitor

        :returns: nothing if successful, else
                  'Invalid parameter/value passed' exception is thrown

        >>> vmonobj.clear_monitor()
        '''
        server_conn = _get_vmon_connection(
            self.vmonserv_ip, self.vmonserv_port, self.vmonref)
        vmon_params = {
            'vmonref': self.vmonref,
        }
        if mode:
            vmon_params['mode'] = mode
            if events:
                vmon_params['events'] = events
        if entries:
            vmon_params['entries'] = entries
        response = server_conn.execute_vmon_command(
            camelot.CLEAR_MONITOR, vmon_params=vmon_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def get_info(self):
        '''Gets current information about a monitor. changes made using
        set_monitor() can be verified.

        :returns: dictionary of monitor information as shown below

        >>> vmonobj.get_info()
        {'current file': '1.txt',
         'entries per file': '500',
         'mode': 'calls',
         'monitor directory': '/tmp/vmon'}

        >>> vmonobj.get_info()
        {'current file': None,
         'entries per file': None,
         'mode': 'calls',
         'monitor directory': None}
        '''
        server_conn = _get_vmon_connection(
            self.vmonserv_ip, self.vmonserv_port, self.vmonref)
        vmon_params = {
            'vmonref': self.vmonref,
        }
        response = server_conn.execute_vmon_command(
            camelot.GET_MONITOR_INFO, vmon_params=vmon_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']

    def get_members(self):
        '''
        get the members from vmon server list.  It will return a
        list of endpoint references

        :returns: list of endpoint references added else returns an empty list

        >>> vmonobj.get_members()
        ['192.168.1.109:5000:00000004'. '192.168.1.109:5000:00000005',...]
        '''
        server_conn = _get_vmon_connection(
            self.vmonserv_ip, self.vmonserv_port, self.vmonref)
        vmon_params = {
            'vmonref': self.vmonref,
        }
        response = server_conn.execute_vmon_command(
            camelot.GET_MONITOR_MEMBERS, vmon_params=vmon_params)
        if not response['rc']:
            raise camelot.CamelotError(response['msg'])
        return response['msg']


def _get_vmon_connection(ip, port, vmonref=None):
    connection_key = '{}:{}'.format(ip, port)
    if vmonref and not vmoninstances.get(vmonref):
        raise camelot.CamelotError(
            "Invalid vmon instance {} at ({}, {})".format(vmonref, ip, port)
        )

    with _connections_lock:
        if not connections.get(connection_key, None):
            conn = Connection(ip, port)
            connections[connection_key] = conn

    server_conn = connections.get(connection_key, None)
    if not server_conn:
        raise camelot.CamelotError(
            "Unable to create Connection object to VMON server at ({}, {})"
            "".format(ip, port)
        )
    return server_conn


def create_new_monitor(ip, port, *args, **kwargs):
    '''Create a new vmon instance

    :parameter ip: ip of the vmon server
    :parameter port: port of the vmon server
    :parameter dirpath: directory path to store vmon data
                        specify another path or None
                        default is /tmp/vmon
    :parameter kwargs: optional parameter. It takes following keys:\n
                         * dirpath: directory path to store vmon data,
                           defaults to None
                         * vmoninstance:  key for which user can provide the
                           subsclass for
                           vmonInstance.On providing this key the Vmon server
                           instantiates this subclass
                           otherwise the VmonInstance will be instantiated.\n
                         * vmon_class: key for which user can provide subclass
                           for Vmon class.
                           On providing this key vmon client instantiates this
                           subclass otherwise
                           Vmon will be instantiated.\n

    :returns: vmon instance is created if successful. Else if not running\n
              'Plesae check ip/port or make sure vmonserver is running'
              exception is raised.

    >>> vmonobj = camelot.vmon.create_new_monitor('10.12.10.188',30101)
    <Vmon object at 0x1b53a10>

    >>> vmonobj = camelot.vmon.create_new_monitor(
    '10.12.10.188',30101,vmon_class=myvmon)
    <myvmon object at 0x1b53a10>

    >>> vmonobj = camelot.vmon.create_new_monitor(
    '10.12.10.188',30101,vmon_class=myvmon, vmoninstance=
    'myvmonclass.VmonInstanceUser1')
    <myvmon object at 0x1b53a10>
    '''
    vmon_class = kwargs.get('vmon_class', Vmon)
    vmonInstance_class = kwargs.get('vmoninstance', None)
    vmon_params = kwargs.get('vmon_params', {})

    if args:
        vmon_params['dirpath'] = args[0]
        # need to be checked

    if not issubclass(vmon_class, Vmon):
        raise camelot.CamelotError('vmon_class is not subclass of Vmon')

    if not ip:
        raise camelot.CamelotError('ip is not specified')
    if not port:
        raise camelot.CamelotError('port is not specified')

    IP = socket.gethostbyname(ip)
    server_conn = _get_vmon_connection(IP, port)
    response = server_conn.execute_vmon_command(camelot.NEW_MONITOR,
                                                vmonInstance_class,
                                                vmon_params=vmon_params)
    if response and not response['rc']:
        raise camelot.CamelotError('create vmon failed')
    newmonitor = vmon_class(ip, port)
    newmonitor.vmonref = response['msg']
    vmoninstances[newmonitor.vmonref] = newmonitor
    log.debug('created monitor {}: {}'.format(newmonitor.vmonref, newmonitor))
    return newmonitor


def delete_monitor(ip, port, vmonref):
    '''Delete requested vmon instance'

    :parameter ip: ip of the monitor server
    :parameter port: port of the monitor server

    :returns: vmon reference

    >>> camelot.vmon.delete_vmon('10.12.10.188', 30101)
    '''
    IP = socket.gethostbyname(ip)
    server_conn = _get_vmon_connection(IP, port)
    vmon_params = {
        'vmonref': vmonref,
    }
    response = server_conn.execute_vmon_command(camelot.DELETE_MONITOR,
                                                vmon_params=vmon_params)
    if response and not response['rc']:
        raise camelot.CamelotError(response['msg'])
    del vmoninstances[vmonref]
    return vmonref


def get_monitors():
    return vmoninstances.keys()


def stop_all():
    log.debug("Closing all VMON connections")
    with _connections_lock:
        for key, conn in connections.items():
            conn.close_event_channel()
        connections.clear()
