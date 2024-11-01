'''
Created on 11-Sep-2013

@author: smaturi
'''


class CamelotServerResponse(object):

    def __init__(self):
        self.ack = None
        self.epAddress = None
        self.msgLength = None
        self.message = None
        self.connectionId = None


class BcgServerResponse(object):

    def __init__(self):
        self.bcg = None
        self.bcgServerIp = None
        self.bcgServerPort = None
        self.bcgInstanceId = None


class VmonServerResponse(object):

    def __init__(self):
        self.vmon = None
        self.vmonServerIp = None
        self.vmonServerPort = None
        self.vmonInstanceId = None
