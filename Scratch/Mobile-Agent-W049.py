import pymongo
import requests
import urllib3
from bs4 import BeautifulSoup as bs
import logging, datetime
from pathlib import Path
import time

# Logging
__file__ = 'finesselogin_{0}.log'.format(time.strftime("%m-%d-%Y"))
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    handlers=[
                        logging.FileHandler(filename='/var/agentemulator/logs/{0}'.format(__file__)),
                        logging.StreamHandler()
                    ])


class finesse():

    def __init__(self):
        try:
            # Server URL's - SSO is only need for the Origin / refer request header
            self.finnese_url = "https://den01wx049fin01.wx049.webexcce.com"
            self.cuic_url = "https://den01wx049uic01.wx049.webexcce.com"
            self.sso_url = 'https://sso.wx049.webexcce.com/'
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.db = self.db_connection()
        except:
            logging.error("Failed to build request and basic url -- How did you fail this bad?")
        return

    def db_connection(self):
        try:
            self.client = pymongo.MongoClient('localhost', 2727,
                                              username="lvuser",
                                              authSource='admin',
                                              password='password@123')
            self.db = self.client['aedb']
            self.col_agents = self.db['agents']
            logging.info("Connected to local database using aedb and agents collections")
            return (self.col_agents)
        except:
            logging.error("Failed to connect to MongoDB")
        return

    def db_pull_users(self):
        try:
            logging.debug("Trying to pull all users")
            self.users = self.col_agents.find({}, {"_id": False})
            return (self.users)
        except:
            logging.error("Failed to pull phone mac addresses from Database")
            return

    def db_update_user_state(self, user, agent_state):
        try:
            self.col_agents.find_one_and_update({"username": '{0}'.format(user)}, {
                "$set": {'agent_state': '{0}'.format(agent_state)}})
        except:
            logging.error("Failed to update {0} agent state".format(user))
        return

    def db_update_user_sso_token(self, user, token, token_date):
        try:
            record = self.col_agents.find_one({'username': '{0}'.format(user)})
            logging.debug("Found {0} lets update with a new token".format(record))
            self.col_agents.find_one_and_update({"username": '{0}'.format(user)}, {
                "$set": {'token': '{0}'.format(token), 'token_date': '{0}'.format(token_date)}})
        except:
            logging.error("Failed to update user with new token {0}".format(user))
        return

    def update_adfs_token(self, user_info):
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            s = requests.session()
            logging.info("user inf = {0}".format(user_info))
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

                # logging.debug("WHAT?? -- = {0}".format(r1soup))
                ### Need to select local IDP or Federated IDP -- What a Pain.
                r1_sso_redirect_url = r1soup.find(id='hrd').get("action")
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
                logging.debug("Second Request to SSO - URL = {0}{1}".format(self.sso_url, r1_sso_redirect_url))
                logging.debug("Body = {0}".format(payload))
                logging.debug('Headers = {0}'.format(headers))
                '''
                For customer that have federations to multiple IDP's, you need to attach the Provides ID.
                If you only have the single IDP then you don't need to supply the Provide ID.
                #r2 = s.request('POST', "{0}{1}".format(self.sso_url, r1_sso_redirect_url), headers=headers,data=payload)
                '''
                ###  Added IDP name to support federations
                r2 = s.request('POST', "{0}{1}{2}".format(self.sso_url, r1_sso_redirect_url,
                                                          "&RedirectToIdentityProvider=AD+AUTHORITY"), headers=headers,
                               data=payload)
                logging.debug("R2 response - code = {0}".format(r2.status_code))
                if r2.status_code == 200:
                    for h in r2.headers:
                        logging.debug('R2 Headers {0} : {1}'.format(h, r2.headers[h]))
                    r2soup = bs(r2.text, 'lxml')
                    logging.debug("R2 Body -- = {0}".format(r2soup))
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
                                    self.db_update_user_sso_token(user, r4data['token'],
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
            logging.debug("Start {0}".format("all_user_update_tokens"))
            all_users = self.db_pull_users()
            for agents in all_users:
                logging.debug("Starting to pull new SSO Token for {0}".format(agents['username']))
                self.update_adfs_token(agents)
        except:
            logging.error("Failed to pull users to update tokens")
        return

    def login_agent_ready(self, user_info):
        try:
            logging.debug("Start Login_Agent_Ready Process")
            url = "{0}:8445/finesse/api/User/{1}".format(self.finnese_url, user_info['agentid'])
            token = str(user_info['token'])
            ### Don't forget the Content Type .. it will fail
            headers = {'Authorization': 'Bearer {0}'.format(token),
                       'Content-Type': 'application/xml'}
            logging.debug("Start Login_Agent_Ready Process for {0}".format(user_info['agentid']))
            '''
            Login Body for Phone Login
            login_payload = '<User><state>LOGIN</state><extension>{0}</extension></User>'.format(user_info['dn'])
            Login Body for Mobile Agent - Call by Call 
            login_payload = '<User><state>LOGIN</state><extension>{0}</extension><mobileAgent><mode>NAILED_CONNECTION</mode><dialNumber>4085551234</dialNumber></mobileAgent></User>'.format(user_info['dn'])
            Login Body for Mobile Agent - Nailed Up
            login_payload = '<User><state>LOGIN</state><extension>{0}</extension><mobileAgent><mode>CALL_BY_CALL</mode><dialNumber>4085551234</dialNumber></mobileAgent></User>'.format(user_info['dn'])
            '''
            # Mobile Agent Login
            login_payload = '<User><state>LOGIN</state><extension>{0}</extension><mobileAgent><mode>NAILED_CONNECTION</mode><dialNumber>{1}</dialNumber></mobileAgent></User>'.format(
                user_info['dn'], user_info['madn'])
            # ready_payload = '<User><state>READY</state><reasonCodeId>2</reasonCodeId></User>'
            ready_payload = '<User><state>READY</state></User>'
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
                logging.debug("Agent login response body = {0}".format(r1.text))
                logging.debug("Now lets put the user in ready")
                r2 = s.request("PUT", "{0}".format(url), data=ready_payload, headers=headers, verify=False)
                logging.debug("R1 response - code = {0}".format(r2.status_code))
                if r2.status_code == 202:
                    logging.debug("Agent is in the ready state")
                    self.db_update_user_state(user_info['username'], 'Ready')
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

    def set_agent_to_ready(self, user_info):
        try:
            logging.debug("Start Login_Agent_Ready Process")
            url = "{0}:8445/finesse/api/User/{1}".format(self.finnese_url, user_info['agentid'])
            token = str(user_info['token'])
            ### Don't forget the Content Type .. it will fail
            headers = {'Authorization': 'Bearer {0}'.format(token),
                       'Content-Type': 'application/xml'}
            ready_payload = '<User><state>READY</state></User>'
            logging.debug(''' Trying to Set {0} To Ready'''.format(user_info['username']))
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            s = requests.session()
            logging.debug("URL = {0}".format(url))
            logging.debug("Headers = {0}".format(headers))
            logging.debug("payload = {0}".format(login_payload))
            r1 = s.request("PUT", "{0}".format(url), data=login_payload, headers=headers, verify=False)
            logging.debug("R1 response - code = {0}".format(r1.status_code))
            if r1.status_code == 202:
                self.db_update_user_state(user_info['username'], 'Ready')
                logging.debug('Agent {0} is Ready'.format(user_info['username']))
        except:
            logging.error("Error with the set_agent_to_ready function. ")
        return

    def logout_agent(self, user_info):
        try:
            # Logout Reason Codes
            '''
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/55</uri>
              <id>55</id>
              <category>LOGOUT</category>
              <code>222</code>
              <label>End of Shift</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/37</uri>
              <id>37</id>
              <category>LOGOUT</category>
              <code>223</code>
              <label>Lunch</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            </ReasonCodes>
            ---------------------------
            Not Ready Codes 
            <ReasonCodes category="NOT_READY">
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/29</uri>
              <id>29</id>
              <category>NOT_READY</category>
              <code>201</code>
              <label>Prep Time</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/31</uri>
              <id>31</id>
              <category>NOT_READY</category>
              <code>202</code>
              <label>Break</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/32</uri>
              <id>32</id>
              <category>NOT_READY</category>
              <code>203</code>
              <label>Coaching</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/34</uri>
              <id>34</id>
              <category>NOT_READY</category>
              <code>204</code>
              <label>Lunch</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/40</uri>
              <id>40</id>
              <category>NOT_READY</category>
              <code>205</code>
              <label>Unscheduled</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/41</uri>
              <id>41</id>
              <category>NOT_READY</category>
              <code>206</code>
              <label>Training</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/42</uri>
              <id>42</id>
              <category>NOT_READY</category>
              <code>207</code>
              <label>Meeting</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/43</uri>
              <id>43</id>
              <category>NOT_READY</category>
              <code>208</code>
              <label>Floor Support</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/44</uri>
              <id>44</id>
              <category>NOT_READY</category>
              <code>209</code>
              <label>System Down</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/45</uri>
              <id>45</id>
              <category>NOT_READY</category>
              <code>210</code>
              <label>Projects</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            <ReasonCode>
              <uri>/finesse/api/ReasonCode/46</uri>
              <id>46</id>
              <category>NOT_READY</category>
              <code>211</code>
              <label>Logout</label>
              <forAll>true</forAll>
              <systemCode>false</systemCode>
            </ReasonCode>
            </ReasonCodes>



            '''

            # ### Get the Reason codes list
            # token = str(user_info['token'])
            # ### Don't forget the Content Type .. it will fail
            # headers = {'Authorization': 'Bearer {0}'.format(token),
            #            'Content-Type': 'application/xml'}
            # url = "{0}:8445/finesse/api/User/{1}/ReasonCodes?category=ALL".format(self.finnese_url, user_info['agentid'])
            # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            # s = requests.session()
            # r1 = s.request("GET", "{0}".format(url), headers=headers, verify=False)
            # logging.debug("Reason Code Query response code = {0}".format(r1.status_code))
            # logging.debug("Reason Code Query body = {0}".format(r1.text))
            url = "{0}:8445/finesse/api/User/{1}".format(self.finnese_url, user_info['agentid'])
            token = str(user_info['token'])
            ### Don't forget the Content Type .. it will fail
            headers = {'Authorization': 'Bearer {0}'.format(token),
                       'Content-Type': 'application/xml'}
            notready_payload = '<User><state>NOT_READY</state><reasonCodeId>46</reasonCodeId></User>'.format(
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
                logging.debug("R2 response - code = {0}".format(r2.status_code))
                if r2.status_code == 202:
                    logging.debug("Agent is now Logged out")
                    self.db_update_user_state(user_info['username'], 'loggedout')
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
            all_users = self.db_pull_users()
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
            all_users = self.db_pull_users()
            logging.debug("------------------")
            logging.debug(" Start Logging out all users ")
            logging.debug("------------------")
            for agents in all_users:
                logging.debug("Starting Logout in {0}".format(agents['username']))
                self.logout_agent(agents)
        except:
            logging.error("Failed to pull users to LogOut Users")
        return

    def validate_and_transfer(self, user_info, call_length_timer):
        # Check if there are any active dialogs' and if a call if over X lenght Transfer
        try:
            s = requests.session()
            # Test Get User
            # url = "{0}:8445/finesse/api/User/{1}".format(self.finnese_url,user_info['agentid'])
            # headers = {'Authorization': 'Bearer {0}'.format(user_info['token']),
            #            'Content-Type': 'application/xml',
            #            'Referer': 'https://den01wx049fin01.wx049.webexcce.com:8445/desktop/logon.html?locale=en_US&isSSO=true'}
            # r1 = s.request("GET", "{0}".format(url), headers=headers ,verify=False)
            # logging.debug("R1 Response code = {0}".format(r1.status_code))
            # logging.debug("R1 Response text = {0}".format(r1.text))
            url = "{0}:8445/finesse/api/User/{1}/Dialogs".format(self.finnese_url, user_info['agentid'])
            headers = {'Authorization': 'Bearer {0}'.format(user_info['token']),
                       'Content-Type': 'application/xml'}
            logging.debug("URL = {0}".format(url))
            logging.debug("Headers = {0}".format(headers))
            r1 = s.request("GET", "{0}".format(url), headers=headers, verify=False)
            logging.debug("R1 response - code = {0}".format(r1.status_code))
            if r1.status_code == 200 or r1.status_code == 202:
                logging.debug("Received Ok, but we need to check for actual dialog")
                r1soup = bs(r1.text, 'lxml')
                # Lets check to see if we have a dialog
                logging.debug("Returned dialog - Lets look at the body {0}".format(r1soup))
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
                        self.col_agents.find_one_and_update({"dn": '{0}'.format(user_info['dn'])},
                                                            {"$set": {'calltime': '{0}'.format(call_time)}})
                    # This is not a new call, lets check the timer and hand up if needed.
                    if "calltime" in user_info.keys():
                        logging.debug("(OLDCall) Found calltime in database - lets check length")
                        start_call_time = datetime.datetime.strptime(user_info['calltime'], '%Y-%m-%d %H:%M:%S')
                        transfer_call_timer = start_call_time + datetime.timedelta(seconds=int(call_length_timer))
                        # drop_call_time = start_call_time + datetime.timedelta(seconds=int(call_length_timer))
                        current_call_time = now
                        # Lets check if the current call is longer then the allowed timer. If so transfer the call
                        if current_call_time > transfer_call_timer:
                            logging.debug(
                                "Current call exceeds {0} total allowed call time, time to transfer it. {1} > {2}".format(
                                    call_length_timer, datetime.datetime.now(), transfer_call_timer))
                            # Drop dialog
                            # r2_payload = '<Dialog><targetMediaAddress>{0}</targetMediaAddress><requestedAction>DROP</requestedAction></Dialog>'.format(user_info['dn'])
                            # Transfer Diaglog
                            r2_payload = '<Dialog><requestedAction>TRANSFER_SST</requestedAction><toAddress>{0}</toAddress><targetMediaAddress>{1}</targetMediaAddress></Dialog>'.format(
                                "8314082", user_info['dn'])
                            r2_url = "{0}:8445/finesse/api/Dialog/{1}".format(self.finnese_url, dialog_id)
                            r2 = s.request("PUT", '{0}'.format(r2_url), data=r2_payload, headers=headers, verify=False)
                            if r2.status_code == 200 or r2.status_code == 202:
                                logging.debug("Confirmed Transfered Call")
                                # Clear the call in DB only after received Drop call success
                                self.col_agents.find_one_and_update({"username": '{0}'.format(user_info['username'])},
                                                                    {"$unset": {'calltime': 1}})
                        else:
                            logging.debug("There is a current call but under {0} second timer,  {1} > {2}".format(
                                call_length_timer, datetime.datetime.now(), transfer_call_timer))
                else:
                    logging.debug(
                        "Received {0} OK, but did not contain a dialog for {1}".format(r1.status_code, user_info['dn']))
                    # Lets make sure we scrub the dialog timers
                    self.col_agents.find_one_and_update({"username": '{0}'.format(user_info['username'])},
                                                        {"$unset": {'calltime': 1}})
            elif r1.status_code == 401:
                logging.error(
                    "{0} is returning {1}, lets update the tokens".format(user_info['username'], r1.status_code))
                self.all_user_update_tokens()
            else:
                logging.error(
                    "{0} received a {1} on the dialog request.  Something is broken".format(user_info['username'],
                                                                                            r1.status_code))
        except:
            logging.error("There was an error in validate_and_transfer for {0}".format(user_info['username']))

        return

    def agent_workflow(self):
        '''
            0. Get ADF Token for each user
            1. Login Mobile Agent
            2. Set Ready State
            3. Answer Call
            4. Listen to call for ~30 seconds
            5. Transfer the Call back to Queue via CTI RP
            6. Go Ready for next call.
        '''
        # Agent Handle time is used to provide talk time before the transfer to another queue
        aht_timer = 30
        # logging.info("The current Testing run timer is {1} minutes long"(run_timer/60))
        try:
            i = 0
            run_cycles = 4800
            # Get or Update SSO token for each user
            try:
                self.all_user_update_tokens()
            except:
                logging.error("Error running the all_user_update_tokens function - Something really wrong happened.")
            # # Sign in Agent
            try:
                self.all_user_agent_login()
            except:
                logging.error("Error running the all_user_agent_login function - Something really wrong happened.")
            # Run  Agent Interaction Workflows
            try:
                # 1 hour run time, 3600 seconds / 20 second sleep (30 second calls) = 180 (I use 170 so any delay in processing is baked into the total workflow)
                while i <= run_cycles:
                    logging.debug("Timer cycle = {0}".format(i))
                    agents = self.col_agents.find({}, {"_id": False})
                    for agent in agents:
                        logging.debug("{0} is now up".format(agent['username']))
                        self.validate_and_transfer(agent, aht_timer)
                    time.sleep(10)
                    i = i + 1
            except:
                logging.error("Master Error in the agent_workflow.")
        # Logging out All Agents
        #  try:
        #      log_out_agent = 1
        #      if log_out_agent >= 0:
        #          logging.debug("Logging out all agents")
        #          self.all_user_agent_logout()
        #  except:
        #      logging.error("Agent Logout function did NOT work.")
        #      logging.error("Agent Logout function did NOT work.")
        except:
            logging.error("Master agent_workflow function did NOT work.")
        return


if __name__ == "__main__":
    # Test connection and validate basic script functions
    fin = finesse()
    # login Users
    fin.agent_workflow()

