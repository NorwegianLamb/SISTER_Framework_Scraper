''' 
Author: Flavio Gjoni
Description: Automated scraper for the SISTER framework, it gathers the PDF files for property successions and parse them
Version: 1.2x
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
import pandas as pd
import csv
from pdfminer.high_level import extract_text
from fractions import Fraction
from codicefiscale import codicefiscale
import requests
from bs4 import BeautifulSoup
import argparse
import time
import os
import glob
import shutil

# --------------------------------------------- GLOBAL --------------------------------------------------------------------------------------------------

custom_header = ['N. PROG.', 'Prog', 'Date validità', 
                    'Repertorio', 'Causale', 'In atti dal', 
                    'Descrizione', 'Da Sviluppare? SI/NO', 'Nominativo', 
                    'C.F.', 'Indirizzo Immobile', 'Altri Immobili']
df = pd.DataFrame(columns=custom_header)

# Select current dir
current_directory = os.getcwd()
download_directory = os.path.join(current_directory, 'data')
renamed_directory = os.path.join(download_directory, 'renamed')
csv_file = os.path.join(current_directory, 'output.csv')

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
                try:
                    undo_button = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/table/tbody/tr/td[2]/form/input'))
                    )
                finally:
                    pass
                # "indietro" after entering the "note" page
                # undo_button.click()
            else:
                print(f"Nota trovata: {n}")
                # --------------------------------------------------------------
                tableTest = driver.find_element(By.CSS_SELECTOR,"table.listaIsp")
                all_rows = tableTest.find_elements(By.CSS_SELECTOR,"tbody tr")
                # --------------------------------------------------------------
                queryInspect(len(all_rows))
                print("\n")
                try:
                    undo_button = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/table/tbody/tr/td[2]/form/input'))
                    )
                finally:
                    pass
            # "indietro" after entering the "note" page
            undo_button.click()
        n += 1



def queryInspect(len_rows):
    # save the INFO-table to start saving data for the CSV/EXCEL file
    try:
        note_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table/tbody[2]/tr'))
        )
    finally:
        pass
    for i in range(1, len_rows):
        tableTest = driver.find_element(By.CSS_SELECTOR,"table.listaIsp")
        all_rows = tableTest.find_elements(By.CSS_SELECTOR,"tbody tr")
        note_row = all_rows[i]
        td_headers = ["numero","prog","anno","datevalide","repertorio","causale","inattodal","descrizione"]
        td_info = {}
        for header in td_headers:
            td_element = note_row.find_element(By.CSS_SELECTOR, f'td[headers="{header}"]')
            td_info[header] = td_element.text
        if(len_rows > 2):
            analyzedNote = queryDownload((str(td_info["numero"])+"_"+str(i)), note_row)
        else:
            analyzedNote = queryDownload(td_info["numero"], note_row)
        check_immobili = []
        for unita_immobile in analyzedNote[0]:
            check_immobili.append([unita_immobile['Info']['Foglio'], unita_immobile['Info']['Particella'],unita_immobile['Info']['Subalterno']])

        info_immobile = []
        #---
        if(analyzedNote[4] == True):
            pass
            #here in case MANUAL CHECK (just add line to csv)
        elif(analyzedNote[3] == False): # persona_fisica
            try:
                persona_fisica = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="menu-left"]/li[1]/a'))
                )
            finally:
                persona_fisica.click()
            # click on radio_checkbox "Codice fiscale:"
            try:
                cf_radio = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset[1]/table[3]/tbody/tr[9]/td[1]/input'))
                )
            finally:
                cf_radio.click()
                cf_textbox = driver.find_element(By.NAME, 'cod_fisc_pf')
                cf_textbox.send_keys(str(analyzedNote[2]))
                cf_sendinput = driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/form/p/input[4]')
                cf_sendinput.click()
            # after clicking on check, inspect if CF/CI
            try:
                radio_check_cf = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table/tbody/tr[2]/td[1]/input'))
                )
            finally:
                radio_check_cf.click()
                immobili_submit = driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/form/table/tbody/tr/td[1]/input[1]')
                immobili_submit.click()
            # SIAMO NELLA LISTA DEGLI IMMOBILI DEL CF
            try:
                foglio_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table/tbody[1]/tr/th[5]'))
                )
            finally:
                data_dict = {}
                classes_to_extract = ['rigascura', 'rigachiara']

                # Initialize a variable to alternate between classes
                current_class_index = 0

                # Iterate through rows alternately based on class
                for _ in range(len(classes_to_extract)):
                    # Get the current class name
                    current_class = classes_to_extract[current_class_index]
                    
                    # Find rows with the current class name
                    rows = driver.find_elements(By.XPATH, f"//tr[@class='{current_class}']")
                    
                    # Initialize an empty list for the current class
                    class_data_list = []
                    
                    # Iterate through the rows and extract the desired <td> elements
                    for row in rows:
                        # Initialize a list for this row
                        row_data = []
                        ubif_data = []
                        # Find the <td> elements with the desired headers
                        headers_to_extract = ['fogliotipo', 'partnum', 'subanno']
                        for header in headers_to_extract:
                            td_element = row.find_element(By.XPATH, f"./td[@headers='{header}']")
                            row_data.append(int(td_element.text))
                        if(row_data in check_immobili):
                            ubif_headers = ['ubicazione', 'classamento', 'consis']
                            for header_u in ubif_headers:
                                ubif_element = row.find_element(By.XPATH, f"./td[@headers='{header_u}']")
                                ubif_data.append(ubif_element.text)
                            info_immobile.append(ubif_data)
                        else:
                            info_immobile.append(["UNITA' DIFFERENTE DALLA NOTA TROVATA"])
                            
                        # Append the row data to the class data list
                        class_data_list.append(row_data)
                    
                    # Add the class data list to the main dictionary
                    data_dict[current_class] = class_data_list
                    
                    # Toggle to the next class index (0 or 1)
                    current_class_index = 1 - current_class_index
            #-----------------------------------------------------------------------------------------------
            #-----------------------------------------------------------------------------------------------
            # --- BACK TO NOTE ----------
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
            try:
                input_nota = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table[2]/tbody/tr[1]/td[2]/input'))
                )
            finally:
                input_nota.clear()
                input_nota.send_keys(td_info["numero"])
                driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/form/input[1]').click()
            # CHECK if the NOTE exists:
            try:
                undo_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/table/tbody/tr/td[2]/form/input'))
                )
            finally:
                pass
            #-----------------------------------------------------------------------------------------------
            #-----------------------------------------------------------------------------------------------
        elif(analyzedNote[3] == True): # persona_giur
            try:
                persona_giuridica = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="menu-left"]/li[2]/a'))
                )
            finally:
                persona_giuridica.click()
            # click on radio_checkbox "Codice fiscale:"
            try:
                cf_radio = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset[1]/table/tbody/tr/td/table[5]/tbody/tr/td[1]/input'))
                )
            finally:
                cf_radio.click()
                cf_textbox = driver.find_element(By.NAME, 'cod_fisc')
                cf_textbox.send_keys(str(analyzedNote[2]))
                cf_sendinput = driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/form/input[5]')
                cf_sendinput.click()
            # after clicking on check, inspect if CF/CI
            try:
                radio_check_cf = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table/tbody[2]/tr/td[1]/input'))
                )
            finally:
                radio_check_cf.click()
                immobili_submit = driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/form/table/tbody/tr/td[1]/input[1]')
                immobili_submit.click()
            # SIAMO NELLA LISTA DEGLI IMMOBILI DEL CF
            try:
                foglio_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table/tbody[1]/tr/th[5]'))
                )
            finally:
                data_dict = {}
                classes_to_extract = ['rigascura', 'rigachiara']

                # Iterate through the classes and extract data
                for current_class in classes_to_extract:
                    try:
                        # Find rows with the current class name
                        rows = driver.find_elements(By.XPATH, f"//tr[@class='{current_class}']")
                        
                        # Initialize an empty list for the current class
                        class_data_list = []
                        
                        # Iterate through the rows and extract the desired <td> elements
                        for row in rows:
                            # Initialize a list for this row
                            row_data = []
                            ubif_data = []
                            # Find the <td> elements with the desired headers
                            headers_to_extract = ['fogliotipo', 'partnum', 'subanno']
                            for header in headers_to_extract:
                                td_element = row.find_element(By.XPATH, f"./td[@headers='{header}']")
                                row_data.append(int(td_element.text))
                            if(row_data in check_immobili):
                                ubif_headers = ['ubicazione', 'classamento', 'consis']
                                for header_u in ubif_headers:
                                    ubif_element = row.find_element(By.XPATH, f"./td[@headers='{header_u}']")
                                    ubif_data.append(ubif_element.text)
                                info_immobile.append(ubif_data)
                            else:
                                info_immobile.append(["UNITA' DIFFERENTE DALLA NOTA TROVATA"])
                                
                            # Append the row data to the class data list
                            class_data_list.append(row_data)
                        
                        # Add the class data list to the main dictionary
                        data_dict[current_class] = class_data_list
                    
                    except Exception as e:
                        # Handle cases where the class is not found (e.g., it doesn't exist)
                        print(f"Error processing '{current_class}' class: {str(e)}")
            #--------------------------------------------
            #--------------------------------------------
            # --- BACK TO NOTE ----------
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
            try:
                input_nota = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/fieldset/table[2]/tbody/tr[1]/td[2]/input'))
                )
            finally:
                input_nota.clear()
                input_nota.send_keys(td_info["numero"])
                driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/form/input[1]').click()
            # CHECK if the NOTE exists:
            try:
                undo_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/form/table/tbody/tr/td[2]/form/input'))
                )
            finally:
                pass
        #---
        #---
        #---
        saveCSV(td_info, analyzedNote[1], analyzedNote[2], info_immobile) # save to CSV


def queryDownload(nota, note_row):
    try:
        check_nota = WebDriverWait(note_row, 20).until(
            EC.presence_of_element_located((By.XPATH, './td[1]/input[1]'))
        )
    finally:
        check_nota.click()
    # request the document

    # LOOP FOR CASES LIKE NOTA°15, NOTA°19 -> multiple files

    visura_nota = driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/form/table/tbody/tr/td[1]/input')
    visura_nota.click()
    # wait for it to load and save it
    try:
        save_doc = WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="colonna1"]/div[2]/div[1]/table/tbody/tr[1]/td[1]/input'))
        )
    finally:
        if("ANCORA PRODOTTO CONSULTARE" in driver.page_source): # select case of document not ready
                return([[],
                        "MANUAL CHECK", # nome max
                        "MANUAL CHECK",
                        True])
        else:
            save_doc.click()
            if(awaitDownloadedFile()):
                renameLastDownload(nota)
                # EXIT DOWNLOAD SEC + analyze downloaded note
                back_to_notes = driver.find_element(By.XPATH, '//*[@id="colonna1"]/div[2]/div[1]/table/tbody/tr[2]/td/form/input[3]')
                back_to_notes.click()
                return queryAnalyze(nota)
        

def queryAnalyze(nota):
    # REGEX to match "Unità immobiliare" and "Intestati" sections -> literally my nightmare
    unita_immobiliare_pattern = re.compile(r'Unità immobiliare n\.(\d+) Trasferita\n\nDati identificativi\n\n(.*?)\n\n', re.DOTALL)
    intestati_pattern = re.compile(r'(\d+)\. (.*?)\n\nDiritto di: (.*?)\n', re.DOTALL)
    file_path = os.path.join(renamed_directory, f'nota-{nota}.pdf')

    def convert_fraction_to_float(fraction_str):
        try:
            return float(Fraction(fraction_str))
        except ValueError:
            return None

    # extract data and analyze it
    text = extract_text(file_path)
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
        # Extract "Diritto di Proprieta" information and convert to float
        diritto_di_proprieta_match = re.search(r'(\d+/\d+)', diritto_di_proprieta)
        diritto_di_proprieta_value = diritto_di_proprieta_match.group(1) if diritto_di_proprieta_match else ''
        diritto_di_proprieta_float = convert_fraction_to_float(diritto_di_proprieta_value)
        intestati_data[intestato_number] = {
            'Intestato Info': intestato_info_dict,
            'Diritto di Proprieta': diritto_di_proprieta_float
        }

    manualCheck_noCF = False
    companyCF = False
    for intestato_number, intestato_info in intestati_data.items():
        cf_value = intestato_info['Intestato Info']['CF']
        if not cf_value:
            manualCheck_noCF = True

    for intestato_number, intestato_info in intestati_data.items():
        try:
            birthdate = codicefiscale.decode(cf_value)['birthdate']
        except ValueError:
            companyCF = True

    if(manualCheck_noCF):
        print("MANUAL CHECK FILE")
        return [unita_immobiliare_data, # unità immobiliari
            "MANUAL CHECK", # nome max
            "MANUAL CHECK",
            companyCF,
            True] # CF/PI max
    elif(companyCF):
        max_share = 0
        chosen_intestato = ""
        for intestato_number, intestato_info in intestati_data.items():
            share = intestato_info['Diritto di Proprieta']
            if share > max_share or share == max_share:
                max_share = share
                chosen_intestato = intestato_info
    else:
        max_share = 0
        oldest_birthdate = ""
        chosen_intestato = ""

        for intestato_number, intestato_info in intestati_data.items():
            share = intestato_info['Diritto di Proprieta']
            if intestato_info['Intestato Info']['CF']:
                birthdate = codicefiscale.decode(intestato_info['Intestato Info']['CF'])['birthdate']
            else:
                birthdate = ""
            
            if share > max_share or (share == max_share and birthdate and birthdate < oldest_birthdate):
                max_share = share
                oldest_birthdate = birthdate
                chosen_intestato = intestato_info
    # ---- end of query
    return [unita_immobiliare_data, # unità immobiliari
            chosen_intestato['Intestato Info']['nome'], # nome max
            chosen_intestato['Intestato Info']['CF'],
            companyCF,
            False] # CF/PI max

def saveCSV(td_info, name, cf, info_immobile):
    data = {
        custom_header[0]: td_info['numero'],
        custom_header[1]: td_info['prog'],
        custom_header[2]: td_info['anno'],
        custom_header[3]: td_info['datevalide'],
        custom_header[4]: td_info['repertorio'],
        custom_header[5]: td_info['causale'],
        custom_header[6]: td_info['inattodal'],
        custom_header[7]: "SI",
        custom_header[8]: name,
        custom_header[9]: cf
    }

    if len(info_immobile) > 0:
        data[custom_header[10]] = info_immobile[0]
    else:
        data[custom_header[10]] = "???"

    if len(info_immobile) > 1:
        # Concatenate 'Altri Immobili' into a single string separated by '|'
        data[custom_header[11]] = '  |  '.join([',  '.join(sublist) for sublist in info_immobile[1:]])
    else:
        data[custom_header[11]] = ""

    df.loc[len(df)] = data
    # extra
    print(f"Link to PDF: (x)")


# --------------------------------------------- ENTRY POINT --------------------------------------------------------------------------------------------------

# ORGANIZE AND CLEAN

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated scraper for the SISTER framework, it gathers the PDF files for property successions and parses them")
    parser.add_argument("-u", "--username", required=True, help="Username for login")
    parser.add_argument("-p", "--password", required=True, help="Password for login")
    parser.add_argument("-n", "--numstart", required=True, help="beginning note number")
    parser.add_argument("-N", "--numend", required=True, help="ending note number")
    args = parser.parse_args()
    login(args.username, args.password)
    queryFind(args.numstart, args.numend)
    df.to_csv('output.csv', index=True)
    FW_logout()

# -----------------------------------------------------------------------------------------------------------------------------------------------------------