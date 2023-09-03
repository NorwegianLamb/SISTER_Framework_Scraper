import re #regex
import os
from pdfminer.high_level import extract_pages, extract_text

nota = "000004"

current_directory = os.getcwd()
download_directory = os.path.join(current_directory, 'data')
renamed_directory = os.path.join(download_directory, 'renamed')
file_path = os.path.join(renamed_directory, f'nota-{nota}.pdf')

# from what I see here we will have to REGEX the 'unità immobiliare n.{regex express}' and loop them to save them
# we should do the same with the 'intestati -> {num}. [text]'

text = extract_text(file_path)

#here comes my nightmare: regex
pattern = re.compile(r"Unità immobiliare")
matches = pattern.findall(text)
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


print(matches)

# currently not needed an IMAGE extractor, only text is sufficient, maybe parse the images in the PDF so we can delete useless info?