from asterisk.ami import SimpleAction, AMIClient, EventListener
import logging.handlers, time
import subprocess, math
import sys
from pymongo import MongoClient
import time


__file__ = 'loadgen_{0}.log'.format(time.strftime("%m-%d-%Y"))
logging.basicConfig(filename='/var/AgentEmulator/logs/{0}'.format(__file__), level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

# logging.basicConfig( level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     datefmt='%d-%b-%y %H:%M:%S')


logging.debug("-------Start new LoadGen Run--------")


def event_listener(event, **kwargs):
    if "DialStatus" in event.keys():
        logging.debug("DialStatus = {0} for {1}".format(event['DialStatus'],event['Channel']))

class AllEventListener(EventListener):
    def on_event(event,**kwargs):
        logging.debug('Event',event)

def callback_response(response):
    logging.debug(response)


def asterisk_login():
    try:
        logging.debug("Error happened, lets try to login back in")
        ast_client = AMIClient(address='10.38.243.35',port=5038)
        ast_client.login(username='user',secret='mysecret')
        logging.debug("Loggined in again")
    except:
        logging.error("Error logging backin again.")
    return


def asteris_call():
    try:
        ## Connect to mongodb
        if col.count_documents({'loadgen_id': 0}) == 0:
            logging.debug("Didn't find the record in DB, this will fail without it")
        else:
            calls = col.find_one({'loadgen_id': 0},{"__id": 0})
            if int(calls['status']) == 0:
                logging.debug("LoadGen status is stopped (0)= {0}".format(calls))
                db_client.close()
                return
            else:
                logging.debug("LoadGen is in running {0}, lets place some calls".format(calls['status']))
    except:
        logging.error("Error connecting to MongoDB")
        return
    if int(calls['status']) >= 0:
        try:
            action = SimpleAction(
                'Originate',
                Channel='SIP/lab/{0}'.format('{0}'.format(calls['dn'])),
                Exten='lab',
                Priority=1,
                Context='{0}'.format(calls['context']),
                CallerID='"Load Test" <{0}>'.format(calls['clid'])
            )
            cpmsleeptimer = int(round(60 / int(calls['cpm'])))
            currentcallcount = 0
            logging.debug("The sleep timer is {0} seconds per call".format(cpmsleeptimer))
            while currentcallcount <= int(calls['cpm']):
                logging.debug("Placing {0} call".format(currentcallcount))
                call = ast_client.send_action(action,callback=callback_response)
                #logging.debug(call)
                time.sleep(cpmsleeptimer)
                currentcallcount = currentcallcount + 1
        except:
            logging.error("Error running call for this minute")
            # asterisk_login()
        return


if __name__ == '__main__':
    try:
        ## Asterisk client connection
        ast_client = AMIClient(address='10.38.243.35',port=5038)
        ast_client.login(username='user',secret='mysecret')
        ast_client.add_event_listener(event_listener)
        ast_client.add_event_listener(AllEventListener())
        logging.debug("Connected to Asterisk box")
    except:
        logging.error("Error connecting to Asterisk box")
    try:
        db_client = MongoClient('127.0.0.1', 27017)
        db = db_client['aedb']
        col = db['loadgen']
    except:
        logging.error("Error connecting to MongoDB")
    i = 0
    try:
        while i <= 1:
            asteris_call()
    except:
        logging.error("Error running asteris_call function")