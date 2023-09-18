import re
import os
from pdfminer.high_level import extract_text
from fractions import Fraction
from codicefiscale import codicefiscale


# Define regular expressions to match "Unità immobiliare" and "Intestati" sections.
unita_immobiliare_pattern = re.compile(r'Unità immobiliare n\.(\d+) Trasferita\n\nDati identificativi\n\n(.*?)\n\n', re.DOTALL)
intestati_pattern = re.compile(r'(\d+)\. (.*?)\n\nDiritto di: (.*?)\n', re.DOTALL)

def convert_fraction_to_float(fraction_str):
    try:
        return float(Fraction(fraction_str))
    except ValueError:
        return None

def extract_data_from_pdf(pdf_path):
    text = extract_text(pdf_path)

    # Extract "Unità immobiliare" data.
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

    # Extract "Intestati" data.
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

    return unita_immobiliare_data, intestati_data

# Example usage:
nota = "000004"
current_directory = os.getcwd()
download_directory = os.path.join(current_directory, 'data')
renamed_directory = os.path.join(download_directory, 'renamed')
file_path = os.path.join(renamed_directory, f'nota-{nota}.pdf')

unita_immobiliare_data, intestati_data = extract_data_from_pdf(file_path)

manualCheck_noCF = False
companyCF = False

for intestato_number, intestato_info in intestati_data.items():
    cf_value = intestato_info['Intestato Info']['CF']
    if not cf_value:
        manualCheck_noCF = True

for intestato_number, intestato_info in intestati_data.items():
    try:
        birthdate = codicefiscale.decode(cf_value)['birthdate']
        print(f"Intestato {intestato_number} CF: {cf_value}, Birthdate: {birthdate}")
    except ValueError:
        companyCF = True

if(manualCheck_noCF):
    print("MANUAL CHECK FILE")
elif(companyCF):
    print("-------------------------------------------------")
    max_share = 0
    chosen_intestato = None

    for intestato_number, intestato_info in intestati_data.items():
        share = intestato_info['Diritto di Proprieta']
        if share > max_share or share == max_share:
            max_share = share
            chosen_intestato = intestato_info

    # Print the chosen intestato
    if chosen_intestato:
        print("Chosen Intestato:")
        print(f"Nome: {chosen_intestato['Intestato Info']['nome']}")
        print(f"CF: {chosen_intestato['Intestato Info']['CF']}")
        print(f"Diritto di Proprieta: {max_share}")
    else:
        print("No intestato found with share and birthdate information.")
    print("-------------------------------------------------")
else:
    print("-------------------------------------------------")
    # Calculate the intestato with the highest share and oldest birthdate (if available)
    max_share = 0
    oldest_birthdate = None
    chosen_intestato = None

    for intestato_number, intestato_info in intestati_data.items():
        share = intestato_info['Diritto di Proprieta']
        if intestato_info['Intestato Info']['CF']:
            birthdate = codicefiscale.decode(intestato_info['Intestato Info']['CF'])['birthdate']
        else:
            birthdate = None
        
        if share > max_share or (share == max_share and birthdate and birthdate < oldest_birthdate):
            max_share = share
            oldest_birthdate = birthdate
            chosen_intestato = intestato_info

    # Print the chosen intestato
    if chosen_intestato:
        print("Chosen Intestato:")
        print(f"Nome: {chosen_intestato['Intestato Info']['nome']}")
        print(f"CF: {chosen_intestato['Intestato Info']['CF']}")
        if chosen_intestato['Intestato Info']['CF']:
            print(f"Birthdate: {oldest_birthdate}")
        print(f"Diritto di Proprieta: {max_share}")
    else:
        print("No intestato found with share and birthdate information.")
    print("-------------------------------------------------")