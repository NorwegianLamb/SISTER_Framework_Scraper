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

# -------------------------------------------------------------------------------------------------------------------------------

def getResponseInfo(response, getContent=True):
    print(f"Response headers: {response.headers}")
    if(getContent):
        print(f"Response content: {response.text}") # .content if binary data
    cookies_str = "\n".join([str(cookie) for cookie in session.cookies]) # this for sure has a better way to be done
    print(f"Cookies:\n{cookies_str}")


def setBaseCookies():
    response = session.get(base_url + "/homepageAreeTematicheAction.do")
    if response.status_code == 200:
        # getResponseInfo(response)
        pass
    else:
        print("volevi, es ist schwer digga :'c")



def login(username, password):
    # setting basic SESSION token
    setBaseCookies()
    # defining POST request data & sending it
    base_url_login = base_url + "/authenticateNuovoVisura.do"
    login_data = {
        'username': username,
        'password': password,
        'firstPage': '/homepageBancheDatiActionNuovoVisura.do'
    }
    login_response = session.post(base_url_login, data=login_data)
    if login_response.status_code == 200:
        getResponseInfo(login_response)
    else:
        print("volevi pt.2, es ist nicht einfach :'c")
    
    # temp
    logout()



def search_data(query):
    data = {}
    response = session.post(base_url, data=data)
    if response.status_code == 200:
       download_file()
    else:
        pass



def download_file(url):
    pass



def logout():
    print("\nWaiting 2 seconds for the logout to AVOID detection...")
    time.sleep(2)
    # defining GET request for logging out
    logout_url = base_url + "/actionLogOutNuovoVisura.do?url=sito"
    logout_response = session.get(logout_url)
    if logout_response.status_code == 200:
        getResponseInfo(logout_response, False)
    else:
        print("bro how can you be so bad T_T")
    # closing requests.Session()
    session.close()
    print("Logout and Sessions closed, goodbye :)")


# -------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    #'''
    parser = argparse.ArgumentParser(description="Automated scraper for the SISTER framework, it gathers the PDF files for property successions and parse them")
    parser.add_argument("-u", "--username", required=True, help="Username for login")
    parser.add_argument("-p", "--password", required=True, help="Password for login")
    args = parser.parse_args()
    #'''
    login(args.username, args.password)