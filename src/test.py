import re
import os
from pdfminer.high_level import extract_text

# REGEX to match "Unità immobiliare" and "Intestati" sections
unita_immobiliare_pattern = re.compile(r'Unità immobiliare n\.(\d+) Trasferita\n\nDati identificativi\n\n(.*?)\n\n', re.DOTALL)
intestati_pattern = re.compile(r'(\d+)\. (.*?)\n\nDiritto di: (.*?)\n', re.DOTALL)

def extract_data_from_pdf(pdf_path):
    text = extract_text(pdf_path)

    # extract "unità immobiliare"
    unita_immobiliare_matches = unita_immobiliare_pattern.findall(text)
    unita_immobiliare_data = []
    for match in unita_immobiliare_matches:
        unita_immobiliare_number = match[0]
        unita_immobiliare_info = match[1].strip()
        unita_immobiliare_data.append({
            'Unita Immobile Number': unita_immobiliare_number,
            'Info': unita_immobiliare_info # should I keep this?
        })

    # extract "intestati"
    intestati_matches = intestati_pattern.findall(text)
    intestati_data = {}
    for match in intestati_matches:
        intestato_number = match[0]
        intestato_info = match[1].strip() # should prob. choose better names
        diritto_di_proprieta = match[2].strip() # strip again to get only from x/y to the end of line (in case of special divisions)
        intestati_data[intestato_number] = {
            'Intestato Info': intestato_info,
            'Diritto di Proprieta': diritto_di_proprieta
        }

    return unita_immobiliare_data, intestati_data

nota = "000014"
current_directory = os.getcwd()
download_directory = os.path.join(current_directory, 'data')
renamed_directory = os.path.join(download_directory, 'renamed')
file_path = os.path.join(renamed_directory, f'nota-{nota}.pdf')

unita_immobiliare_data, intestati_data = extract_data_from_pdf(file_path)

# print the data
for unita_immobile in unita_immobiliare_data:
    print(f"Unità Immobile Number: {unita_immobile['Unita Immobile Number']}")
    print(f"Info: {unita_immobile['Info']}")
    print()

for intestato_number, intestato_info in intestati_data.items():
    print(f"Intestato Number: {intestato_number}")
    print(f"Intestato Info: {intestato_info['Intestato Info']}")
    print(f"Diritto di Proprieta: {intestato_info['Diritto di Proprieta']}")
    print()




"""
WHAT DO WE NEED FROM THAT FILE?

    -> UNITA' IMMOBILIARE N°<num>: <PARSE INFO> (CATASTO, FOGLIO, PARTICELLA, SUBALTERNO)
        -> THESE ARE GOING TO BE INSERTED IN "Ricerca per Immobili" + "intestati" 
            -> se IMMOBILE trovato è lo stesso dell'INTESTATO/I a fine PDF aggiungi, altrimenti inserisci "NO"
                -> SE RISULTATO = "NO" uscire dal file PDF (anche se solo 1 no? è possibile?) -> continuare il loop delle note
            -> SE IMMOBILE è lo stesso, ci salviamo "UBICAZIONE", "CLASSAMENTO", "CONSISTENZA" + "ALTRE UBICAZIONI, CONST.." + ...

    -> INTESTATI:
        -> n.1, n.2, ..., n.<num>
            -> SALVA NOME, CF, DIRITTO DI PROPRIETA' -> da qui capire chi ha il maggior diritto e filtri finali
"""