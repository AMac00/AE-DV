import pymongo
import logging, time
import camelot
from pathlib import Path

# Logging
logging.basicConfig(filename='logs/{0}.log'.format(Path('{0}'.format(__file__)).stem), level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


# Database class1
class fun_db():

    def __init__(self):
        try:
            self.client = pymongo.MongoClient('localhost',27017)
            self.db = self.client['aedb']
            self.col_agents = self.db['agents']
        except:
            logging.error("Failed to connect to MongoDB")
        return

    def pull_phones(self):
        try:
            self.phones = self.col_agents.find({},{'phonemac':1,"_id": False})
            return(self.phones)
        except:
            logging.error("Failed to pull phone mac addresses from Database")
            return

class telephony():

    def __init__(self):
        try:
            self.camelotserver = "10.38.243.32"
            self.ccmserver = "10.38.243.17"
            self.camgroup1 = 5000
            self.camgroup2 = 5001
            self.camgroup3 = 5002
            self.camgroup4 = 5003
            self.serv = camelot.create_camelot_server(self.camelotserver, self.camgroup1)
        except:
            logging.error("Failed to to load telephony class")
        return

    ''' Used for parsing Streams'''

    def get_stream_ref(self,ep, direction, type, callref):
        ep.release_streams()
        streams = ep.get_streams()
        for stream in streams:
            if (stream['CallId'] == callref and stream['Direction'] == direction and stream['Type'] == type):
                return stream['StrmID']

    ''' Used for Event Callback'''

    def event_callbacks(self,event):
        logging.debug("Received Event : %s" % event)
        logging.debug("Received Event Type : %s" % event.event_type)
        logging.debug("Received Event Sub_type: %s" % event.event_sub_type)
        logging.debug("Received Event Message: %s" % event.message)
        return ()


    def register_phone(self,ephonemac):
        try:
            logging.debug("Lets get {0} registered - Started".format(ephonemac))
            # Create Phone Endpoint
            ep = self.serv.create_new_endpoint('sipx', ephonemac)
            # Build Additional Phone elements
            ep.config('sip.phone.ip', self.camelotserver)
            ep.config('sip.phone.httpip', self.ccmserver)
            ep.config('sip.phone.modelnumber', '684')
            ep.config('sip.protocol.reguseragenthdr', 'Cisco-CP8851/11.5.1')
            # Start call back for events at device level
            ep.register_event_callback(self.event_callbacks)
            __return__ = ep.start_info_events()
            logging.debug("Start info events = {0}".format(__return__))
            __return__ = ep.start_station_events()
            logging.debug("Start Station events = {0}".format(__return__))
            # Try to register device
            ep.set_client_data(ephonemac)
            ep.init()
            ep.inservice()
            # We need to wait for the phone to register
            i = 5
            while i >= 0 and "inservice" not in ep.get_info()['state']:
                logging.debug("ep1 state -> {0}".format(ep.get_info()['state']))
                time.sleep(3)
                i = i - 1
            ret = self.serv.get_endpoint(ephonemac)
            logging.debug("Return from Ret = {0}".format(ret))
            return(ep)
        except:
            logging.error("Failed to register {0}".format(ephonemac))
            return()


# Build Classes
db_class = fun_db()
cam = telephony()
phone_mac = db_class.pull_phones()
for phones in phone_mac:
    logging.debug("Found {0} Phone Mac, lets get it registered".format(phones['phonemac']))
    ephone = cam.register_phone(phones['phonemac'])
