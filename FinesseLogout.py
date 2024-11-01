import pymongo
import requests
import urllib3
from bs4 import BeautifulSoup as bs
import logging, datetime
from pathlib import Path



# Logging
logging.basicConfig(filename='logs/{0}.log'.format(Path('{0}'.format(__file__)).stem), level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

'''


'''


# Database class
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




class finesse():

    def __init__(self):
        try:
            # Server URL's - SSO is only need for the Origin / refer request header
            self.finnese_url = "https://fin125.dv.ccenterprisecloud.com"
            self.cuic_url = "https://uic125.dv.ccenterprisecloud.com"
            self.sso_url = 'https://sso.dv.ccenterprisecloud.com'
            self.db = fun_db()
        except:
            logging.error("Failed to build request and basic url -- How did you fail this bad?")
        return

    def update_adfs_token(self,user_info):
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.s = requests.session()
            print("user inf = {0}".format(user_info))
            user = user_info['username']
            password = user_info['pwd']
            dn = user_info['dn']
            logging.debug("username = {0},password = {1}, dn = {2}".format(user,password,dn))
            logging.debug("---------- Start update_adfs_token for {0}  ----------".format(user))
            sso_token_url_1 = '{0}:8445/desktop/sso/token?cc_username={1}&return_refresh_token=true'.format(self.finnese_url, user)
            logging.debug("First Request to Finesse - URL = {0}".format(sso_token_url_1))
            r1 = self.s.request("GET", "{0}".format(sso_token_url_1), verify=False)
            logging.debug("R1 response - code = {0}".format(r1.status_code))
            if r1.status_code == 200:
                for h in r1.headers:
                    logging.debug('R1 Headers {0} : {1}'.format(h, r1.headers[h]))
                logging.debug("TEST010100-0")
                r1soup = bs(r1.text, 'lxml')
                logging.debug("TEST010100-1")
                # This url provides the Redirect URL, this is used for the 2nd request URL and the Refer Header needed for the request
                logging.debug("WHAT?? -- = {0}".format(r1soup))
                r1_sso_redirect_url = r1soup.find(id='options').get("action")
                logging.debug("TEST010101")
                r1_refer_url = r1_sso_redirect_url.split("&client-request-id=")
                logging.debug("TEST010102")
                r1_refer_url = r1_refer_url[0]
                logging.debug("TEST010103")
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
                r2 = self.s.request('POST', r1_sso_redirect_url, headers=headers, data=payload)
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
                    r3 = self.s.request("POST", "{0}".format(r2_sso_redirect_url), data=r3_payload, headers=r3_headers,
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
                        r4 = self.s.request("POST", '{0}'.format(r4_relay_url), data=r4_payload, verify=False)
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
                                    self.db.update_user_sso_token(user,r4data['token'],"{0}".format(datetime.datetime.now()))
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
            logging.error("Failed to get token for {0}, nothing is going to work!!!!".format(user))
        return()

    def all_user_update_tokens(self):
        ''' Update all user tokens'''
        try:
            all_users = self.db.pull_users()
            for agents in all_users:
                logging.debug("Starting to pull new SSO Token for {0}".format(agents['username']))
                self.update_adfs_token(agents)
        except:
            logging.error("Failed to pull users to update tokens")
        return

    def login_agent_ready(self,user_info):
        try:
            url = "{0}:8445/finesse/api/User/{1}".format(self.finnese_url,user_info['dn'])
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
            r1 = s.request("PUT", "{0}".format(url), data=login_payload, headers=headers ,verify=False)
            logging.debug("R1 response - code = {0}".format(r1.status_code))
            if r1.status_code == 202:
                logging.debug('Agent {0} is logged in - lets go ready'.format(user_info['username']))
                r2 = s.request("PUT", "{0}".format(url), data=ready_payload, headers=headers, verify=False)
                logging.debug("R1 response - code = {0}".format(r2.status_code))
                if r2.status_code == 202:
                    logging.debug("Agent is in the ready state")
                    self.db.update_user_state(user_info['username'],'Ready')
                else:
                    logging.error(
                        "Failed to make {0} Ready, status_code {1}, body {2}".format(user_info['username'], r2.status_code,r2.text))
            else:
                logging.error("Failed to login {0}, status_code {1}, body {2}".format(user_info['username'],r1.status_code,r1.text))
        except:
            logging.error("Failed to login user")

    def logout_agent(self,user_info):
        try:
            url = "{0}:8445/finesse/api/User/{1}".format(self.finnese_url,user_info['dn'])
            token = str(user_info['token'])
            ### Don't forget the Content Type .. it will fail
            headers = {'Authorization': 'Bearer {0}'.format(token),
                       'Content-Type': 'application/xml'}
            notready_payload = '<User><state>NOT_READY</state><reasonCodeId>27</reasonCodeId></User>'.format(user_info['dn'])
            logout_payload = '<User><state>LOGOUT</state></User>'
            logging.debug(''' Change {0} to Not Ready'''.format(user_info['username']))
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            s = requests.session()
            logging.debug("URL = {0}".format(url))
            logging.debug("Headers = {0}".format(headers))
            logging.debug("payload = {0}".format(notready_payload))
            r1 = s.request("PUT", "{0}".format(url), data=notready_payload, headers=headers ,verify=False)
            logging.debug("R1 response - code = {0}".format(r1.status_code))
            if r1.status_code == 202:
                logging.debug('Agent {0} is now Not-Ready'.format(user_info['username']))
                r2 = s.request("PUT", "{0}".format(url), data=logout_payload, headers=headers, verify=False)
                logging.debug("R1 response - code = {0}".format(r2.status_code))
                if r2.status_code == 202:
                    logging.debug("Agent is now Logged out")
                    self.db.update_user_state(user_info['username'],'loggedout')
                else:
                    logging.error(
                        "Failed to make {0} Ready, status_code {1}, body {2}".format(user_info['username'], r2.status_code,r2.text))
            else:
                logging.error("Failed to login {0}, status_code {1}, body {2}".format(user_info['username'],r1.status_code,r1.text))
        except:
            logging.error("Failed to login user")



    def all_user_agent_login(self):
        ''' Update all user tokens'''
        try:
            all_users = self.db.pull_users()
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
            all_users = self.db.pull_users()
            logging.debug("------------------")
            logging.debug(" Start Logging out all users ")
            logging.debug("------------------")
            for agents in all_users:
                logging.debug("Starting Logout in {0}".format(agents['username']))
                self.logout_agent(agents)
        except:
            logging.error("Failed to pull users to LogOut Users")
        return


#######
if __name__ == "__main__":
    fin = finesse()
    # Update all tokens for users in DB
    fin.all_user_update_tokens()
    # Login all agents into the phones.. lets take calls. !! :)
    fin.all_user_agent_logout()