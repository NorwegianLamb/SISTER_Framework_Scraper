''' 
Author: Flavio Gjoni
Description: Automated scraper for the SISTER framework, it gathers the PDF files for property successions and parse them
Version: 1.0x
'''
import requests
from bs4 import BeautifulSoup
import argparse
import time

# -------------------------------------------------------------------------------------------------------------------------------

base_url = "https://portalebanchedaticdl.visura.it"
session = requests.Session()
session.debug = True # Comment in PROD

# CHECKER_FUNCS -------------------------------------------------------------------------------------------------------------------------------


def getResponseInfo(response, getContent=False):
    print(f"Response headers: {response.headers}")
    cookies_str = "\n".join([str(cookie) for cookie in session.cookies]) # this for sure has a better way to be done
    print(f"Cookies:\n{cookies_str}")
    if(getContent):
        print(f"Content:\n{response.text}")



def setBaseCookies():
    response = session.get(base_url + "/homepageAreeTematicheAction.do")
    if response.status_code == 200:
        # getResponseInfo(response)
        pass
    else:
        print("volevi, es ist schwer digga :'c")



def temp_LogoutButtonPresent(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    logout_button = soup.find('input', {'type': 'button', 'value': 'Logout', 'onclick': "location.href='/actionLogOutNuovoVisura.do?url=sito'"})
    print(logout_button is not None)


# LOGIN/LOGOUT -------------------------------------------------------------------------------------------------------------------------------


def login(username, password):
    # setting basic SESSION token
    setBaseCookies()
    # defining POST request data
    base_url_login = base_url + "/authenticateNuovoVisura.do?url=sito"
    login_data = {
        'userName': username,
        'password': password,
        'firstPage': '/homepageBancheDatiActionNuovoVisura.do'
    }
    # sending LOGIN POST request
    login_response = session.post(base_url_login, data=login_data)
    if login_response.status_code == 200:
        if "Credenziali errate" in login_response.text:
            print("Invalid credentials!")
            #print("Request:")
            #print(login_response.request.headers)
            #print(login_response.request.body)
        else:
            # getResponseInfo(login_response, True)
            temp_LogoutButtonPresent(login_response.text)
            logout()
    else:
        print("volevi pt.2, es ist nicht einfach :'c")



def logout():
    print("\nWaiting 2 seconds for the logout to AVOID detection...")
    time.sleep(2)
    # defining GET request for logging out
    logout_url = base_url + "/actionLogOutNuovoVisura.do?url=sito"
    logout_response = session.get(logout_url)
    if logout_response.status_code == 200:
        # getResponseInfo(logout_response, True)
        pass
    else:
        print("bro how can you be so bad T_T")
    # closing requests.Session()
    session.close()
    print("Logout and Sessions closed, goodbye :)")


# LOGIN_QUERY/PARSER_FW -------------------------------------------------------------------------------------------------------------------------------




# QUERY/PARSER -------------------------------------------------------------------------------------------------------------------------------


def searchData(query):
    data = {}
    response = session.post(base_url, data=data)
    if response.status_code == 200:
       downloadFile()
    else:
        pass



def downloadFile(url):
    pass


# ENTRY_POINT -------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    #'''
    parser = argparse.ArgumentParser(description="Automated scraper for the SISTER framework, it gathers the PDF files for property successions and parse them")
    parser.add_argument("-u", "--username", required=True, help="Username for login")
    parser.add_argument("-p", "--password", required=True, help="Password for login")
    args = parser.parse_args()
    #'''
    login(args.username, args.password)