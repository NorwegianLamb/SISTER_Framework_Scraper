''' 
Author: Flavio Gjoni
Description: Automated scraper for the SISTER framework, it gathers the PDF files for property successions and parse them
Version: 1.0x
'''
import requests
from bs4 import BeautifulSoup
import argparse

# -------------------------------------------------------------------------------------------------------------------------------

base_url = "https://portalebanchedaticdl.visura.it/homepageAreeTematicheAction.do"
session = requests.Session()

# -------------------------------------------------------------------------------------------------------------------------------

def setBaseCookies():
    response = session.get(base_url)
    if response.status_code == 200:
        print(response)
    else:
        print('volevi')



def login(username, password):
    login_data = {
        'username': username,
        'password': password
    }
    response = session.post('', data=login_data)
    if response.status_code == 200:
        print(response)
    else:
        print("volevi pt.2")



def search_data(query):
    data = {}
    response = session.post(base_url, data=data)
    if response.status_code == 200:
       download_file()
    else:
        pass



def download_file(url):
    pass

# -------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Scraper")
    parser.add_argument("-u", "--username", required=True, help="Username for login")
    parser.add_argument("-p", "--password", required=True, help="Password for login")
    args = parser.parse_args()
    #login(args.username, args.password)
    setBaseCookies()