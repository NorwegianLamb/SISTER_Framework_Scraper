''' 
Author: Flavio Gjoni
Description: Automated scraper for the SISTER framework, it gathers the PDF files for property successions and parse them
Version: 1.1x
'''

# Selenium LIBS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# Other LIBS
import requests
from bs4 import BeautifulSoup
import argparse
import time

# --------------------------------------------- GLOBAL --------------------------------------------------------------------------------------------------

# Headless chrome browser + OPTIONS() settings + base_url
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
base_url = "https://portalebanchedaticdl.visura.it"

# --------------------------------------------- LOGIN/LOGOUT FUNCTIONS --------------------------------------------------------------------------------------------------

# Login function (entry function in main())
def login(username, password):
    base_url_login = base_url + "/authenticateNuovoVisura.do?url=sito"
    driver.get(base_url_login)
    driver.maximize_window()
    
    # Find the login form elements and submit the login
    username_field = driver.find_element("name", "userName")
    password_field = driver.find_element("name", "password")
    login_button = driver.find_element("xpath", '//*[@id="testata"]/div/div[2]/div[1]/button')
    username_field.send_keys(str(username))
    password_field.send_keys(str(password))
    login_button.click()

    # Check if "Credenziali errate" is present on the page
    if "Credenziali errate" in driver.page_source:
        print("Invalid credentials!")
    else:
        logout() # change to FW_Login()


def logout():
    # Logging out
    time_to_wait = 2
    print(f"\nWaiting {time_to_wait} seconds for the logout to AVOID detection...")
    time.sleep(time_to_wait)
    driver.get(base_url + "/actionLogOutNuovoVisura.do?url=sito")

    # Close webdriver
    time.sleep(1)
    driver.quit()
    print("Logout and WebDriver closed, tschüß :)")

# --------------------------------------------- FW_LOGIN/LOGOUT FUNCTIONS ----------------------------------------------------------------------------------------

def FW_login():
    pass

def FW_logout():
    pass

# --------------------------------------------- QUERY_FIND/DOWNLOAD/ANALYZE FUNCTIONS -------------------------------------------------------------------------------

def queryFind():
    pass

def queryDownload():
    pass

def queryAnalyze():
    pass

# --------------------------------------------- ENTRY POINT --------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated scraper for the SISTER framework, it gathers the PDF files for property successions and parses them")
    parser.add_argument("-u", "--username", required=True, help="Username for login")
    parser.add_argument("-p", "--password", required=True, help="Password for login")
    args = parser.parse_args()
    login(args.username, args.password)

# -------------------------------------- USEFUL to keep ------------------------------------------------------------------------------------------------------

"""
try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "userName"))
        )
    finally:
        print("found")
"""