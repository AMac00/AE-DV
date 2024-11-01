import pymongo
import requests
import urllib3
from bs4 import BeautifulSoup as bs
import logging, datetime, time
from pathlib import Path
import datetime as datetime
import random



# Logging
today = datetime.datetime.now()
__file__ = 'finessehangup_{0}.log'.format(time.strftime("%m-%d-%Y"))
logging.basicConfig(filename='/var/AgentEmulator/logs/{0}'.format(__file__), level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

'''
Moved all the function into this one.. Really just to consolidate .. might need to look at device logins 


'''


class finesse():

    def __init__(self):
        try:
            # Server URL's - SSO is only need for the Origin / refer request header
            self.finnese_url = "https://fin125.dv.ccenterprisecloud.com"
            self.cuic_url = "https://uic125.dv.ccenterprisecloud.com"
            self.sso_url = 'https://sso.dv.ccenterprisecloud.com'
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.db = self.db_connection()
        except:
            logging.error("Failed to build request and basic url -- How did you fail this bad?")
        return

    def db_connection(self):
        try:
            self.client = pymongo.MongoClient('localhost',27017)
            self.db = self.client['aedb']
            self.col_agents = self.db['agents']
            return(self.col_agents)
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

    def pull_users(self):
        try:
            self.users = self.col_agents.find({},{"_id": False})
            return(self.users)
        except:
            logging.error("Failed to pull phone mac addresses from Database")
            return

    def update_user_state(self,user,agent_state):
        try:
            self.col_agents.find_one_and_update({"username": '{0}'.format(user)}, {
            "$set": {'agent_state': '{0}'.format(agent_state)}})
        except:
            logging.error("Failed to update {0} agent state".format(user))
        return

    def update_user_sso_token(self,user,token,token_date):
        try:
            record = self.col_agents.find_one({'username': '{0}'.format(user)})
            logging.debug("Found {0} lets update with a new token".format(record))
            self.col_agents.find_one_and_update({"username":'{0}'.format(user)},{"$set": {'token': '{0}'.format(token), 'token_date': '{0}'.format(token_date)}})
        except:
            logging.error("Failed to update user with new token {0}".format(user))
        return

    def update_adfs_token(self, user_info):
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            s = requests.session()
            print("user inf = {0}".format(user_info))
            user = user_info['username']
            password = user_info['pwd']
            dn = user_info['dn']
            logging.debug("username = {0},password = {1}, dn = {2}".format(user, password, dn))
            logging.debug("---------- Start update_adfs_token for {0}  ----------".format(user))
            sso_token_url_1 = '{0}:8445/desktop/sso/token?cc_username={1}&return_refresh_token=true'.format(
                self.finnese_url, user)
            logging.debug("First Request to Finesse - URL = {0}".format(sso_token_url_1))
            r1 = s.request("GET", "{0}".format(sso_token_url_1), verify=False)
            logging.debug("R1 response - code = {0}".format(r1.status_code))
            if r1.status_code == 200:
                for h in r1.headers:
                    logging.debug('R1 Headers {0} : {1}'.format(h, r1.headers[h]))
                r1soup = bs(r1.text, 'lxml')
                # This url provides the Redirect URL, this is used for the 2nd request URL and the Refer Header needed for the request
                logging.debug("WHAT?? -- = {0}".format(r1soup))
                r1_sso_redirect_url = r1soup.find(id='options').get("action")
                r1_refer_url = r1_sso_redirect_url.split("&client-request-id=")
                r1_refer_url = r1_refer_url[0]
                logging.debug("Found SSO Redirect URL = {0}".format(r1_sso_redirect_url))
                logging.debug("Found SSO Redirect used for the Referer header = {0}".format(r1_refer_url))
                logging.debug("-----------")
                logging.debug("Start working on 2nd Request")
                # Adding Refer Header
                headers = {'Referer': r1_refer_url}
                # Add the username password to  the 2nd request
                payload = {'UserName': user, 'Password': password, 'AuthMethod': 'FormsAuthentication'}
                logging.debug("Second Request to SSO - URL = {0}".format(r1_sso_redirect_url))
                logging.debug("Body = {0}".format(payload))
                logging.debug('Headers = {0}'.format(headers))
                r2 = s.request('POST', r1_sso_redirect_url, headers=headers, data=payload)
                logging.debug("R2 response - code = {0}".format(r2.status_code))
                if r2.status_code == 200:
                    for h in r2.headers:
                        logging.debug('R2 Headers {0} : {1}'.format(h, r2.headers[h]))
                    r2soup = bs(r2.text, 'lxml')
                    # Action URl needed for the CUIC /ids/saml/response?metaAlias=/sp"
                    r2_sso_redirect_url = r2soup.find('form').get('action')
                    # r2SAMLREsponse = r2soup.find('input').get('value')
                    r2SAMLResponse = r2soup.find('input', {'name': "SAMLResponse"}).get('value')
                    r2RelayState = r2soup.find('input', {'name': 'RelayState'}).get('value')
                    logging.debug("Found CUIC /ids/saml URL ={0}".format(r2_sso_redirect_url))
                    logging.debug("Found RelayState = {0} SAMLResponse {1}".format(r2RelayState, r2SAMLResponse))
                    logging.debug("-----------")
                    logging.debug("Start working on 3nd Request")
                    # Adding Origin and Refere Header needed for Finesse Request
                    r3_headers = {'origin': '{0}'.format(self.sso_url), 'referer': '{0}'.format(self.sso_url)}
                    # Adding Payload for SamlResponse and Relay trust status
                    r3_payload = {'SAMLResponse': r2SAMLResponse, 'RelayState': r2RelayState}
                    logging.debug("Third Request to SSO - URL = {0}".format(r2_sso_redirect_url))
                    logging.debug("Body = {0}".format(r3_payload))
                    logging.debug('Headers = {0}'.format(r3_headers))
                    r3 = s.request("POST", "{0}".format(r2_sso_redirect_url), data=r3_payload,
                                        headers=r3_headers,
                                        verify=False)
                    logging.debug("R3 response - code = {0}".format(r3.status_code))
                    if r3.status_code == 200:
                        for h in r3.headers:
                            logging.debug('R3 Headers {0} : {1}'.format(h, r3.headers[h]))
                        r3soup = bs(r3.text, 'lxml')
                        r3uniqueId = r3soup.find('input', {'name': "uniqueId"}).get('value')
                        logging.debug("R3 UniqueID = {0}".format(r3uniqueId))
                        logging.debug("-----------")
                        logging.debug("Start working on 4nd Request")
                        # Set the CUIC Relay URL = This response provides the tokens needed to login an agent
                        r4_relay_url = '{0}:8553/ids/relay'.format(self.cuic_url)
                        # The UniqueID provides relay authentication for the token
                        r4_payload = {'uniqueId': r3uniqueId}
                        logging.debug("Fourth Request to SSO - URL = {0}".format(r4_relay_url))
                        logging.debug("Body = {0}".format(r4_payload))
                        r4 = s.request("POST", '{0}'.format(r4_relay_url), data=r4_payload, verify=False)
                        logging.debug("R4 response - code = {0}".format(r4.status_code))
                        if r4.status_code == 200:
                            for h in r4.headers:
                                logging.debug('R2 Headers {0} : {1}'.format(h, r4.headers[h]))
                            r4data = r4.json()
                            for data in r4data:
                                logging.debug("r4 data {0} = {1}".format(data, r4data[data]))
                            if "token" in r4data.keys():
                                logging.debug("Found Token {0}".format(r4data['token']))
                                ''' 
                                Add or Update the user in the Database
                                '''
                                try:
                                    self.update_user_sso_token(user, r4data['token'],
                                                                  "{0}".format(datetime.datetime.now()))
                                except:
                                    logging.error("Failed to update token for {0}".format(user))
                        else:
                            logging.error("Failed R4 for {0}".format(user))
                    else:
                        logging.error("Failed R3 for {0}".format(user))
                else:
                    logging.error("Failed R2 for {0}".format(user))
            else:
                logging.error("Failed R1 to get redirect finesse url for {0}".format(user))
        except:
            logging.error("Failed to get token for {0}, nothing is going to work!!!!".format(user_info['username']))
        return ()

    def all_user_update_tokens(self):
        ''' Update all user tokens'''
        try:
            all_users = self.pull_users()
            for agents in all_users:
                logging.debug("Starting to pull new SSO Token for {0}".format(agents['username']))
                self.update_adfs_token(agents)
        except:
            logging.error("Failed to pull users to update tokens")
        return

    def login_agent_ready(self, user_info):
        try:
            url = "{0}:8445/finesse/api/User/{1}".format(self.finnese_url, user_info['dn'])
            token = str(user_info['token'])
            ### Don't forget the Content Type .. it will fail
            headers = {'Authorization': 'Bearer {0}'.format(token),
                       'Content-Type': 'application/xml'}
            login_payload = '<User><state>LOGIN</state><extension>{0}</extension></User>'.format(user_info['dn'])
            ready_payload = '<User><state>READY</state><reasonCodeId>2</reasonCodeId></User>'
            logging.debug(''' Trying to login {0} to finesse'''.format(user_info['username']))
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            s = requests.session()
            logging.debug("URL = {0}".format(url))
            logging.debug("Headers = {0}".format(headers))
            logging.debug("payload = {0}".format(login_payload))
            r1 = s.request("PUT", "{0}".format(url), data=login_payload, headers=headers, verify=False)
            logging.debug("R1 response - code = {0}".format(r1.status_code))
            if r1.status_code == 202:
                logging.debug('Agent {0} is logged in - lets go ready'.format(user_info['username']))
                r2 = s.request("PUT", "{0}".format(url), data=ready_payload, headers=headers, verify=False)
                logging.debug("R1 response - code = {0}".format(r2.status_code))
                if r2.status_code == 202:
                    logging.debug("Agent is in the ready state")
                    self.update_user_state(user_info['username'], 'Ready')
                else:
                    logging.error(
                        "Failed to make {0} Ready, status_code {1}, body {2}".format(user_info['username'],
                                                                                     r2.status_code, r2.text))
            else:
                logging.error(
                    "Failed to login {0}, status_code {1}, body {2}".format(user_info['username'], r1.status_code,
                                                                            r1.text))
        except:
            logging.error("Failed to login user")

    def logout_agent(self, user_info):
        try:
            url = "{0}:8445/finesse/api/User/{1}".format(self.finnese_url, user_info['dn'])
            token = str(user_info['token'])
            ### Don't forget the Content Type .. it will fail
            headers = {'Authorization': 'Bearer {0}'.format(token),
                       'Content-Type': 'application/xml'}
            notready_payload = '<User><state>NOT_READY</state><reasonCodeId>27</reasonCodeId></User>'.format(
                user_info['dn'])
            logout_payload = '<User><state>LOGOUT</state></User>'
            logging.debug(''' Change {0} to Not Ready'''.format(user_info['username']))
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            s = requests.session()
            logging.debug("URL = {0}".format(url))
            logging.debug("Headers = {0}".format(headers))
            logging.debug("payload = {0}".format(notready_payload))
            r1 = s.request("PUT", "{0}".format(url), data=notready_payload, headers=headers, verify=False)
            logging.debug("R1 response - code = {0}".format(r1.status_code))
            if r1.status_code == 202:
                logging.debug('Agent {0} is now Not-Ready'.format(user_info['username']))
                r2 = s.request("PUT", "{0}".format(url), data=logout_payload, headers=headers, verify=False)
                logging.debug("R1 response - code = {0}".format(r2.status_code))
                if r2.status_code == 202:
                    logging.debug("Agent is now Logged out")
                    self.update_user_state(user_info['username'], 'loggedout')
                else:
                    logging.error(
                        "Failed to make {0} Ready, status_code {1}, body {2}".format(user_info['username'],
                                                                                     r2.status_code, r2.text))
            else:
                logging.error(
                    "Failed to login {0}, status_code {1}, body {2}".format(user_info['username'], r1.status_code,
                                                                            r1.text))
        except:
            logging.error("Failed to login user")

    def all_user_agent_login(self):
        ''' Update all user tokens'''
        try:
            all_users = self.pull_users()
            logging.debug("------------------")
            logging.debug(" Start Logging in all users ")
            logging.debug("------------------")
            for agents in all_users:
                logging.debug("Starting Logging in {0}".format(agents['username']))
                self.login_agent_ready(agents)
        except:
            logging.error("Failed to pull users to Login Users")
        return

    def all_user_agent_logout(self):
        ''' Update all user tokens'''
        try:
            all_users = self.pull_users()
            logging.debug("------------------")
            logging.debug(" Start Logging out all users ")
            logging.debug("------------------")
            for agents in all_users:
                logging.debug("Starting Logout in {0}".format(agents['username']))
                self.logout_agent(agents)
        except:
            logging.error("Failed to pull users to LogOut Users")
        return

    def validate_and_hangup(self,user_info,call_length_timer):
        #Check if there are any active dialogs'
        try:
                    s = requests.session()
                    url = "{0}:8445/finesse/api/User/{1}/Dialogs".format(self.finnese_url,user_info['dn'])
                    headers = {'Authorization': 'Bearer {0}'.format(user_info['token']),
                               'Content-Type': 'application/xml'}
                    logging.debug("URL = {0}".format(url))
                    logging.debug("Headers = {0}".format(headers))
                    r1 = s.request("GET", "{0}".format(url), headers=headers ,verify=False)
                    logging.debug("R1 response - code = {0}".format(r1.status_code))
                    if r1.status_code == 200 or r1.status_code == 202:
                        logging.debug("Received Ok, but we need to check for actual dialog")
                        r1soup = bs(r1.text, 'lxml')
                        # Lets check to see if we have a dialog
                        if r1soup.find('dialog'):
                            diaglog = r1soup.find('dialog')
                            dialog_id = diaglog.find('id').text
                            logging.debug("Found diaglog ID {0}".format(dialog_id))
                            # We have a dialog, lets check if this is a new call or an old call
                            # IF this is a new call, lets create the timers
                            logging.debug("TEST -- {0}".format(user_info))
                            now = datetime.datetime.now()
                            if "calltime" not in user_info.keys():
                               logging.debug("(NewCall) calltime in database - lets start it")
                               call_time = now.strftime('%Y-%m-%d %H:%M:%S')
                               self.col_agents.find_one_and_update({"dn": '{0}'.format(user_info['dn'])}, {"$set": {'calltime': '{0}'.format(call_time)}})
                            # This is not a new call, lets check the timer and hand up if needed.
                            if "calltime" in user_info.keys():
                                logging.debug("(OLDCall) Found calltime in database - lets check length")
                                start_call_time = datetime.datetime.strptime(user_info['calltime'],'%Y-%m-%d %H:%M:%S')
                                drop_call_time = start_call_time + datetime.timedelta(seconds=int(call_length_timer))
                                current_call_time = now
                                # Lets check if the current call is longer then the allowed timer. If so Drop the Call
                                if current_call_time > drop_call_time:
                                    logging.debug("Current call exceeds {0} total allowed call time, time to drop it. {1} > {2}".format(call_length_timer,datetime.datetime.now(),drop_call_time))
                                    r2_payload = '<Dialog><targetMediaAddress>{0}</targetMediaAddress><requestedAction>DROP</requestedAction></Dialog>'.format(user_info['dn'])
                                    r2_url = "{0}:8445/finesse/api/Dialog/{1}".format(self.finnese_url,dialog_id)
                                    r2 = s.request("PUT", '{0}'.format(r2_url), data=r2_payload, headers=headers, verify=False)
                                    if r2.status_code == 200 or r2.status_code == 202:
                                        logging.debug("Confirmed Drop Call")
                                        # Clear the call in DB only after received Drop call success
                                        self.col_agents.find_one_and_update({"username": '{0}'.format(user_info['username'])},{"$unset": {'calltime': 1}})
                                else:
                                    logging.debug("There is a current call but under {0} second timer,  {1} > {2}".format(call_length_timer,datetime.datetime.now(),drop_call_time))
                        else:
                            logging.debug("Received {0} OK, but did not contain a dialog for {1}".format(r1.status_code,user_info['dn']))
                            # Lets make sure we scrub the dialog timers
                            self.col_agents.find_one_and_update({"username": '{0}'.format(user_info['username'])}, {"$unset": {'calltime': 1}})
                    elif r1.status_code == 401:
                        logging.error("{0} is returning {1}, lets update the tokens".format(user_info['username'],r1.status_code))
                        self.all_user_update_tokens()
                    else:
                        logging.error("{0} received a {1} on the dialog request.  Something is broken".format(user_info['username'],r1.status_code))

        except:
            logging.error("There was an error in validate_and_hangup for {0}".format(user_info['username']))

        return

    def agent_monitor(self):
        # We are dropping calls ever X second timer 30 sec
        #aht_timer = 30
        aht_timer = random.randint(180,300)
        logging.info("The current agent talk time ( AHT ) is {0}".format(aht_timer))
        _db_ = self.db_connection()
        try:
            i = 0
            '''
            # 1 hour run time, 3600 seconds / 20 second sleep (30 second calls) = 180 (I use 170 so any delay in processing is baked into the total workflow)
            run_hours = 1
            run_timer = 170 * run_hours
            # 2 Hours = 340
            # 4 Hours = 680
            #  8 Hours = 1360
            # 24 Hours = 4320
            # This while is for a timed run, the new way is to run it non-stop as a service, lets hope the phones are avaialble... Bahhhaaaaa
            # while i <= run_timer:
            '''
            while i <= 1:
                logging.debug("Timer cycle = {0}".format(i))
                agents = _db_.find({}, {"_id": False})
                for agent in agents:
                    logging.debug("{0} is now up".format(agent['username']))
                    self.validate_and_hangup(agent,aht_timer)
                time.sleep(20)
                # i = i + 1 // OLD logic for non service rungs
        except:
            logging.error("There was an error in the main function and its all  going to break down.")
        return





#######
if __name__ == "__main__":
        fin = finesse()
        fin.agent_monitor()

