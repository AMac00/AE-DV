import requests
from requests.auth import HTTPBasicAuth
import urllib3, logging, ssl
from bs4 import BeautifulSoup as bs
import time


'''
    Logs into ADFS

'''
Working = 0
if Working == 1 :
    uri = "https://fin125.dv.ccenterprisecloud.com"
    cuic = "https://uic125.dv.ccenterprisecloud.com"
    sso_test = "{0}/sso/test".format(uri)
    # sso_fetch_token = '{0}/sso/token'.format(uri)
    user = 'riles'
    password = 'Emu!830r'
    dn = '1005550071'
    #  https://www.cisco.com/c/en/us/support/docs/contact-center/finesse/215626-finesse-thirdparty-client-integration-wi.html
    # https://fin125.dv.ccenterprisecloud.com:8445/desktop/sso/token?cc_username=riles&return_refresh_token=true
    # https://fin125.dv.ccenterprisecloud.com:8445/desktop/sso/token?cc_username=riles
    # Refresh URL  https://fin125.dv.ccenterprisecloud.com:8445/desktop/sso/token?cc_username=riles&refresh-token=<refresh-token-value>
    sso_refersh_token = ':8445/desktop/sso/token?cc_username={0}&return_refresh_token=true'.format(user)
    sso_new_token = ':8445/desktop/sso/token?cc_username={0}'.format(user)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    s = requests.session()

    '''  LOGING FOR THE FIRST TIME'''
    # Get Original Finesse IDS redirect
    print("-----------")
    print("First Request to Finesse")
    r1 = s.request("GET","{0}{1}".format(uri,sso_new_token), verify=False)
    print("R1 response")
    if r1.status_code == 200:
        # Print Headers
        print("Headers")
        for k in r1.headers:
            print("R1 headers {0} : {1}".format(k,r1.headers[k]))
        print("Payload")
        # Pars for ReferHeader
        # refer_header = r.headers['Referer']
        # print("Refer Header = {0}".format(refer_header))
        # Parse response for Tokens
        r1soup = bs(r1.text, 'lxml')
        # Get URL Token
        action_url = r1soup.find(id='options').get("action")
        print('{0}'.format(action_url))
        # Parse URL Token Refer header
        refer_url= action_url.split("&client-request-id=")
        refer_url= refer_url[0]
        print("refer url = {0}".format(refer_url))
        headers = {'Referer': refer_url}
        # Post Auth Requtest
        payload = {'UserName': user, 'Password': password, 'AuthMethod': 'FormsAuthentication'}
        print("------------------------------------")
        print('Working on R2')
        print("R2 URL = {0}".format(action_url))
        print("Send UserName - Password ")
        r2 = s.request('POST',action_url,headers=headers,data=payload)
        print("R2 response")
        print("Auth Post Code = {0}".format(r2.status_code))
        print("Auth Post Body = {0}".format(r2.text))
        print("Auth Post Headers")
        for h in r2.headers:
            print("R2 Headers {0} = {1}".format(h,r2.headers[h]))
        if r2.status_code == 200:
            # Parse out the SAML Respone value
            r2soup = bs(r2.text, 'lxml')
            print("{0}".format(r2soup))
            r2action = r2soup.find('form').get('action')
            # r2SAMLREsponse = r2soup.find('input').get('value')
            r2SAMLResponse = r2soup.find('input',{'name':"SAMLResponse"}).get('value')
            r2RelayState = r2soup.find('input',{'name':'RelayState'}).get('value')
            print("r2 action url = {0}".format(r2action))
            print("r2 SAMLRespone = {0}".format(r2SAMLResponse))
            print("r2 r2RelayState = {0}".format(r2RelayState))
            '''
            Now we start sending thing back to Finesse 
            '''
            print("------------------------------------")
            print('Working on R3')
            print("R3 URL = {0}".format(r2action))
            payload = {'SAMLResponse': r2SAMLResponse, 'RelayState': r2RelayState}
            headers= {'origin': 'https://sso.dv.ccenterprisecloud.com', 'referer':'https://sso.dv.ccenterprisecloud.com'}
            r3 = s.request("POST","{0}".format(r2action), data=payload,verify=False)
            print("R3 response")
            print("Auth Post Code = {0}".format(r3.status_code))
            if r3.status_code == 200:
                print("Auth Post Body = {0}".format(r3.text))
                print("Auth Post Headers")
                for h in r3.headers:
                    print("R3 Headers {0} = {1}".format(h,r3.headers[h]))
                # Parse out the SAML Respone value
                r3soup = bs(r3.text, 'lxml')
                print("{0}".format(r3soup))
                r3uniqueId = r3soup.find('input', {'name': "uniqueId"}).get('value')
                print("r3 SAMLRespone = {0}".format(r3uniqueId))
                #Capture Return Cookie
                #s.cookies = r3.headers['Set-Cookie']
                '''
                After you have the finesse Cookie, you can do your
        
                '''
                print("------------------------------------")
                print('Working on R4')
                print("Print R4 Cookies = {0}".format(s.cookies))
                #### The /ids/relay 300 contains a  location header that has the finessee SSo Auth Location for the token request... Thats the next step to get the token
                relay_url = '{0}:8553/ids/relay'.format(cuic)
                payload4 = {'uniqueId': r3uniqueId}
                print(" URL = {0}".format(relay_url))
                r4 = s.request("POST", '{0}'.format(relay_url),data=payload4, verify=False)
                print("R4 response")
                print("Auth Post Code = {0}".format(r4.status_code))
                print("Auth Post Body = {0}".format(r4.text))
                print("Auth Post Headers")
                for h in r4.headers:
                    print("{0} = {1}".format(h, r4.headers[h]))


'''
    Logs into ADFS and login IN/OUT an agent 
'''
testcase1 = 0
if testcase1 == 1:
    # Server URL's - SSO is only need for the Origin / refer request header
    fin = "https://fin125.dv.ccenterprisecloud.com"
    cuic = "https://uic125.dv.ccenterprisecloud.com"
    sso = 'https://sso.dv.ccenterprisecloud.com'
    # User Information
    user = 'riles'
    password = 'Emu!830r'
    dn = '1005550071'
    #Useful URL's
    #  https://www.cisco.com/c/en/us/support/docs/contact-center/finesse/215626-finesse-thirdparty-client-integration-wi.html
    # https://fin125.dv.ccenterprisecloud.com:8445/desktop/sso/token?cc_username=riles&return_refresh_token=true
    # https://fin125.dv.ccenterprisecloud.com:8445/desktop/sso/token?cc_username=riles
    # Refresh URL  https://fin125.dv.ccenterprisecloud.com:8445/desktop/sso/token?cc_username=riles&refresh-token=<refresh-token-value>
    #sso_refersh_token = ':8445/desktop/sso/token?cc_username={0}&return_refresh_token=true'.format(user)
    #sso_new_token = ':8445/desktop/sso/token?cc_username={0}'.format(user)
    # Set Basic Requests Template
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    s = requests.session()
    # Finesse SSO URL ( First Request)
    print("-----------")
    sso_token_url_1 = '{0}:8445/desktop/sso/token?cc_username={1}&return_refresh_token=true'.format(fin,user)
    print("First Request to Finesse - URL = {0}".format(sso_token_url_1))
    r1 = s.request("GET","{0}".format(sso_token_url_1), verify=False)
    print("R1 response - code = {0}".format(r1.status_code))
    if r1.status_code == 200:
        for h in r1.headers:
            print('R1 Headers {0} : {1}'.format(h,r1.headers[h]))
        r1soup = bs(r1.text, 'lxml')
        # This url provides the Redirect URL, this is used for the 2nd request URL and the Refer Header needed for the request
        r1_sso_redirect_url = r1soup.find(id='options').get("action")
        r1_refer_url= r1_sso_redirect_url.split("&client-request-id=")
        r1_refer_url= r1_refer_url[0]
        print("Found SSO Redirect URL = {0}".format(r1_sso_redirect_url))
        print("Found SSO Redirect used for the Referer header = {0}".format(r1_refer_url))
        print("-----------")
        print("Start working on 2nd Request")
        # Adding Refer Header
        headers = {'Referer': r1_refer_url}
        # Add the username password to  the 2nd request
        payload = {'UserName': user, 'Password': password, 'AuthMethod': 'FormsAuthentication'}
        print("Second Request to SSO - URL = {0}".format(r1_sso_redirect_url))
        print("Body = {0}".format(payload))
        print('Headers = {0}'.format(headers))
        r2 = s.request('POST',r1_sso_redirect_url,headers=headers,data=payload)
        print("R2 response - code = {0}".format(r2.status_code))
        if r2.status_code == 200:
            for h in r2.headers:
                print('R2 Headers {0} : {1}'.format(h, r2.headers[h]))
            r2soup = bs(r2.text, 'lxml')
            # Action URl needed for the CUIC /ids/saml/response?metaAlias=/sp"
            r2_sso_redirect_url = r2soup.find('form').get('action')
            # r2SAMLREsponse = r2soup.find('input').get('value')
            r2SAMLResponse = r2soup.find('input',{'name':"SAMLResponse"}).get('value')
            r2RelayState = r2soup.find('input',{'name':'RelayState'}).get('value')
            print("Found CUIC /ids/saml URL ={0}".format(r2_sso_redirect_url))
            print("Found RelayState = {0} SAMLResponse {1}".format(r2RelayState,r2SAMLResponse))
            print("-----------")
            print("Start working on 3nd Request")
            # Adding Origin and Refere Header needed for Finesse Request
            r3_headers= {'origin': '{0}'.format(sso), 'referer':'{0}'.format(sso)}
            # Adding Payload for SamlResponse and Relay trust status
            r3_payload = {'SAMLResponse': r2SAMLResponse, 'RelayState': r2RelayState}
            print("Third Request to SSO - URL = {0}".format(r2_sso_redirect_url))
            print("Body = {0}".format(r3_payload))
            print('Headers = {0}'.format(r3_headers))
            r3 = s.request("POST","{0}".format(r2_sso_redirect_url), data=r3_payload,headers=r3_headers,verify=False)
            print("R3 response - code = {0}".format(r3.status_code))
            if r3.status_code == 200:
                for h in r3.headers:
                    print('R3 Headers {0} : {1}'.format(h, r3.headers[h]))
                r3soup = bs(r3.text, 'lxml')
                r3uniqueId = r3soup.find('input', {'name': "uniqueId"}).get('value')
                print("R3 UniqueID = {0}".format(r3uniqueId))
                print("-----------")
                print("Start working on 4nd Request")
                # Set the CUIC Relay URL = This response provides the tokens needed to login an agent
                r4_relay_url = '{0}:8553/ids/relay'.format(cuic)
                # The UniqueID provides relay authentication for the token
                r4_payload = {'uniqueId': r3uniqueId}
                print("Fourth Request to SSO - URL = {0}".format(r4_relay_url))
                print("Body = {0}".format(r4_payload))
                r4 = s.request("POST", '{0}'.format(r4_relay_url), data=r4_payload, verify=False)
                print("R4 response - code = {0}".format(r4.status_code))
                if r4.status_code == 200:
                    for h in r4.headers:
                        print('R2 Headers {0} : {1}'.format(h, r4.headers[h]))
                    r4data = r4.json()
                    for data in r4data:
                        print("r4 data {0} = {1}".format(data,r4data[data]))
                    if "token" in r4data.keys():
                        print("Found Token {0}".format(r4data['token']))
                        print("Lets login {0} Agent".format(user))
                        url_model = '{0}:8445/finesse/api/User/{1}'.format(fin,dn)
                        headers = {"Authorization":"Bearer {0}".format(r4data['token']),
                                   'Content-Type': 'application/xml'
                                   }
                        payload = '<User><state>LOGIN</state><extension>{0}</extension></User>'.format(dn)
                        print("Agent Login")
                        print("Agent Login URL = {0}".format(url_model))
                        print("Agent Login Header = {0}".format(headers))
                        print("Agent payload  = {0}".format(payload))
                        r5 = s.request('PUT', url_model, headers=headers, data=payload, verify=False)
                        print("R5 response - code = {0}".format(r5.status_code))
                        if r5.status_code == 202:
                            print("Agent-Login Successful")
                            payload = '<User><state>READY</state><reasonCodeId>2</reasonCodeId></User>'
                            print("Lets go Ready")
                            r6 = s.request('PUT', url_model, headers=headers, data=payload, verify=False)
                            print("R6 response - code = {0}".format(r6.status_code))
                            if r6.status_code == 202:
                                print("Well looks like we are ready to take calls.. Thats pretty neat")
                                time.sleep(30)
                                print("Ok thats enough work, lets take a Break")
                                payload = '<User><state>NOT_READY</state><reasonCodeId>27</reasonCodeId></User>'
                                r7 = s.request('PUT', url_model, headers=headers, data=payload, verify=False)
                                print("R7 response - code = {0}".format(r7.status_code))
                                if r7.status_code == 202:
                                    time.sleep(10)
                                    payload = '<User><state>LOGOUT</state></User>'
                                    print("Ok that enough break, lets log out")
                                    r8 = s.request('PUT', url_model, headers=headers, data=payload, verify=False)
                                    print("R8 response - code = {0}".format(r8.status_code))
                                    if r8.status_code == 202:
                                        print("Loggout out successfully")
                        else:
                            print("Oh no something went wrong..")


