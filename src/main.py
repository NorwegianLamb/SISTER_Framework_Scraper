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
from selenium.webdriver.support.select import Select
# Other LIBS
import re
from pdfminer.high_level import extract_text
import requests
from bs4 import BeautifulSoup
import argparse
import time
import os
import glob
import shutil

# --------------------------------------------- GLOBAL --------------------------------------------------------------------------------------------------

# Select current dir
current_directory = os.getcwd()
download_directory = os.path.join(current_directory, 'data')
renamed_directory = os.path.join(download_directory, 'renamed')

# Headless chrome browser + OPTIONS() settings + base_url
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("prefs", {
  "download.default_directory": f"{download_directory}"
})
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
base_url = "https://portalebanchedaticdl.visura.it"

# --------------------------------------------- HELPER FUNCTIONS --------------------------------------------------------------------------------------------------

def awaitDownloadedFile():
    file_downloaded = False
    max_wait_time = 60
    start_time = time.time()
    while not file_downloaded and time.time() - start_time < max_wait_time:
        # Check if the file exists in the download directory
        all_files = glob.glob(os.path.join(download_directory, '*'))
        if any(f.endswith('.crdownload') for f in all_files):
            # .crdownload file exists, indicating the download is in progress
            time.sleep(1)
        elif any(f.endswith('.pdf') for f in all_files):
            # .pdf file exists, indicating the download is complete
            file_downloaded = True
        else:
            time.sleep(1)
    return file_downloaded

def renameLastDownload(nota):
    pdf_files = [f for f in glob.glob(os.path.join(download_directory, '*.pdf'))]
    pdf_file = pdf_files[0]
    new_filename = f"nota-{nota}.pdf"
    new_file_path = os.path.join(download_directory, new_filename)
    os.rename(pdf_file, new_file_path)

    renamed_file_path = os.path.join(renamed_directory, new_filename)
    shutil.move(new_file_path, renamed_file_path)

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
        FW_login()
        #logout()


def logout():
    driver.switch_to.default_content()
    while("Logout" not in driver.page_source):
        print("mh..")
        time.sleep(1)

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
    # Entering the framework ----------------------------------------------------------------------------------------------------
    try:
        open_FW = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="prodotti"]/div/article/form/div[1]/div[2]/table[2]/tbody/tr/td[2]/a[2]'))
        )
    finally:
        open_FW.click()

    # Accepting requests ----------------------------------------------------------------------------------------------------
    var = True
    while(var):
        if("IDENTITA' FEDERATA" in driver.page_source):
            var = False
        else:
            time.sleep(1)
    
    driver.get('https://portalebanchedatij.visura.it/Visure/SceltaServizio.do?tipo=/T/TM/VCVC_')
    
    try:
        selezione_ufficio_provinciale = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table/tbody/tr/td[2]/select'))
        )
    finally:
        select_element = Select(selezione_ufficio_provinciale)
        select_element.select_by_value('MILANO Territorio-MI')
        applica_button = driver.find_element("xpath", '//*[@id="colonna1"]/div[2]/form/input')
        applica_button.click()
    
    # Getting into "NOTE" Section ----------------------------------------------------------------------------------------------------
    var = True
    while(var):
        if("Ufficio provinciale di: MILANO Territorio" in driver.page_source):
            var = False
        else:
            time.sleep(1)
    driver.get('https://portalebanchedatij.visura.it/Visure/SceltaLink.do?lista=NOTA&codUfficio=MI')

    # Inserting NOTE info ----------------------------------------------------------------------------------------------------
    try:
        selezione_comune = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table[1]/tbody/tr[2]/td[2]/select'))
        )
    finally:
        select_element_2 = Select(selezione_comune)
        select_element_2.select_by_value('F205#MILANO#0#0')
        anno_input = driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table[2]/tbody/tr[2]/td[4]/input')
        anno_input.send_keys('2023')
        scegli_tipologia = driver.find_element("xpath", '//*[@id="colonna1"]/div[2]/form/fieldset/table[3]/tbody/tr/td[1]/input')
        scegli_tipologia.click()

    try:
        selezione_voltura = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table[3]/tbody/tr/td[3]/select'))
        )
    finally:
        select_element_3 = Select(selezione_voltura)
        select_element_3.select_by_value('01')
        

def FW_logout():
    # Logging out
    time_to_wait = 2
    print(f"\nWaiting {time_to_wait} seconds to close the FW to AVOID detection...")
    time.sleep(time_to_wait)

    driver.get('https://portalebanchedatij.visura.it/framesetAgenziaTerritorioIF.htm')
    var = True
    while(var):
        if("IDENTITA' FEDERATA" in driver.page_source):
            var = False
        else:
            time.sleep(1)

    print("Switching to 1 of 2 Frames -> Barretta")
    driver.switch_to.frame(driver.find_element(By.NAME, "BARRETTA"))
    time.sleep(2)
    print("Switching to 2 of 2 Frames -> mainFrameVISURA")
    driver.switch_to.frame(driver.find_element(By.NAME, "mainFrameVISURA"))
    time.sleep(2)
    print("Exiting the FW...")
    driver.execute_script("vai('chiudi')")
    logout()

# --------------------------------------------- QUERY_FIND/DOWNLOAD/ANALYZE FUNCTIONS -------------------------------------------------------------------------------

def queryFind(n, N):
    n = int(n)
    N = int(N)
    time_to_sleep = 1
    while(n <= N):
        time.sleep(time_to_sleep)
        try:
            input_nota = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table[2]/tbody/tr[1]/td[2]/input'))
            )
        finally:
            input_nota.clear()
            input_nota.send_keys(n)
            driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/form/input[1]').click()
        # CHECK if the NOTE exists:
        try:
            undo_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/table/tbody/tr/td[2]/form/input'))
            )
        finally:
            if("NESSUNA CORRISPONDENZA TROVATA" in driver.page_source):
                pass
            else:
                print(f"Nota trovata: {n}")
                print("-----------------------------------------------------------------------------")
                queryInspect()
                print("-----------------------------------------------------------------------------\n")
                try:
                    undo_button = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/table/tbody/tr/td[2]/form/input'))
                    )
                finally:
                    pass
            undo_button.click()
        n += 1

def queryInspect():
    # save the INFO-table to start saving data for the CSV/EXCEL file
    try:
        note_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table/tbody[2]/tr'))
        )
    finally:
        td_headers = ["tipo","numero","prog","anno","datevalide","repertorio","causale","inattodal","descrizione"]
        for header in td_headers:
            td_element = driver.find_element(By.CSS_SELECTOR, f'td[headers="{header}"]')
            print(f"{header}: {td_element.text}")
        # download and rename the doc
        queryDownload(driver.find_element(By.CSS_SELECTOR, f'td[headers="numero"]').text)
        # queryDownload() could return all the ANALYZED info in the PDF file and add them to td_headers for loop text -> FULL LINE EXCEL
        # + HYPERLINK TO FILE after downloaded, so it would make sense to do it in this order: INSPECT-DOWNLOAD-ANALYZE-PARSE (need to write this func)-back here -> save excel


def queryDownload(nota):
    try:
        check_nota = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table/tbody[2]/tr/td[1]/input[1]'))
        )
    finally:
        check_nota.click()
    # request the document

    # LOOP FOR CASES LIKE NOTA°15, NOTA°19 -> multiple files

    visura_nota = driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/form/table/tbody/tr/td[1]/input')
    visura_nota.click()
    # wait for it to load and save it
    try:
        save_doc = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/div[1]/table/tbody/tr[1]/td[1]/input'))
        )
    finally:
        save_doc.click()
        if(awaitDownloadedFile()):
            renameLastDownload(nota)
            #queryAnalyze(nota)

    # Exit DOC_DOWNLOAD_SECTION
    back_to_notes = driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/div[1]/table/tbody/tr[2]/td/form/input[3]')
    back_to_notes.click()
    

def queryAnalyze(nota):
    # REGEX to match "Unità immobiliare" and "Intestati" sections -> literally my nightmare
    unita_immobiliare_pattern = re.compile(r'Unità immobiliare n\.(\d+) Trasferita\n\nDati identificativi\n\n(.*?)\n\n', re.DOTALL)
    intestati_pattern = re.compile(r'(\d+)\. (.*?)\n\nDiritto di: (.*?)\n', re.DOTALL)
    file_path = os.path.join(renamed_directory, f'nota-{nota}.pdf')

    # extract data and analyze it
    text = extract_text(file_path)
    unita_immobiliare_matches = unita_immobiliare_pattern.findall(text)
    unita_immobiliare_data = []
    # extract "unità immobiliare"
    unita_immobiliare_matches = unita_immobiliare_pattern.findall(text)
    unita_immobiliare_data = []
    for match in unita_immobiliare_matches:
        unita_immobiliare_number = match[0]
        unita_immobiliare_info = match[1].strip()
        # Extract additional information using regex
        unita_immobiliare_info_dict = {
            'Catasto': re.search(r'Catasto (.*?) -', unita_immobiliare_info).group(1).strip(),
            'Foglio': int(re.search(r'Foglio (\d+)', unita_immobiliare_info).group(1)),
            'Particella': int(re.search(r'Particella (\d+)', unita_immobiliare_info).group(1)),
            'Subalterno': int(re.search(r'Subalterno (\d+)', unita_immobiliare_info).group(1))
        }
        unita_immobiliare_data.append({
            'Unita Immobile Number': unita_immobiliare_number,
            'Info': unita_immobiliare_info_dict
        })
    # extract "intestati" -> this whole section could be taken after getting foglio,particella,sub
    intestati_matches = intestati_pattern.findall(text)
    intestati_data = {}
    for match in intestati_matches:
        intestato_number = match[0]
        intestato_info = match[1].strip()
        diritto_di_proprieta = match[2].strip()
        # Extract additional information from "Intestato Info"
        intestato_info_match = re.search(r'^([^()]+)', intestato_info)
        cf_match = re.search(r'\(CF (.*?)\)', intestato_info)
        intestato_info_dict = {
            'nome': intestato_info_match.group(1).strip() if intestato_info_match else '',
            'CF': cf_match.group(1).strip() if cf_match else ''
        }
        intestati_data[intestato_number] = {
            'Intestato Info': intestato_info_dict,
            'Diritto di Proprieta': diritto_di_proprieta
        }

    # ---- end of query

def printExcel():
    # da fare:
    """
    1) estrarre gli intestati e metterli in un [1,2,3,...]
        -> clean file extraction
        -> think for cases like words with accents and so on
        -> filter extra data
    2) prendere l'intestatario con più quote (filter)
        -> create func to filter the quotes
        -> how to display in case m/f? (in case twins -> write it UPPERCASE so manual double check)
        -> double check both FISICO and GIURIDICO   
    3) loop per ogni immobile e if(intestato[immobile] in [intestati]) 
        -> what if there is an immobile that belongs to other ppl from the intestati and not the one with the highest quotes?
        -> what if intestati/immobili don't match?
        -> dioporco
    4) se immobile/i all'intestatario -> tutte le info necessarie dell'immobile
    """

    # prima parte excel, preso dopo aver scritto la nota e cliccato su "cerca nota"
    print(f"N. PROG: (numero nota)")
    print(f"Prog: (x)")
    print(f"Anno: (x)")
    print(f"Date validità: (x)")
    print(f"Repertorio: (x)")
    print(f"Causale: (x)")
    print(f"In atti dal: (x)")
    print(f"Descrizione: (x)")
    print(f"?? Da sviluppare SI/NO ??")
    # download -> check immobili su "immobile" -> intestati -> (FILTER FUNC. (highest quotes -> m/f (idk how to do this) -> oldest))
    print(f"Nome e cognome: (filtered x)")
    print(f"Codice fiscale: (filtered x)")
    print(f"IN CASE of not same INTESTATARIO: No (in another column)")
    # loop all of its IMMOBILI and search them on "Immobili" to gather next info
    print(f"Ubicazione: (x)")
    print(f"Classamento/Consistenza: (x)")
    print(f"Altre ubicazioni: (x)")

    # extra
    print(f"Link to PDF: (x)")

def filterIntestati():
    pass

# --------------------------------------------- ENTRY POINT --------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated scraper for the SISTER framework, it gathers the PDF files for property successions and parses them")
    parser.add_argument("-u", "--username", required=True, help="Username for login")
    parser.add_argument("-p", "--password", required=True, help="Password for login")
    parser.add_argument("-n", "--numstart", required=True, help="beginning note number")
    parser.add_argument("-N", "--numend", required=True, help="ending note number")
    args = parser.parse_args()
    login(args.username, args.password)
    queryFind(args.numstart, args.numend)
    FW_logout()

# -------------------------------------- USEFUL to keep ------------------------------------------------------------------------------------------------------

"""
try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "userName"))
        )
    finally:
        print("found")
"""