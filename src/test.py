import re #regex
import os
from pdfminer.high_level import extract_pages, extract_text

nota = "000004"

current_directory = os.getcwd()
download_directory = os.path.join(current_directory, 'data')
renamed_directory = os.path.join(download_directory, 'renamed')
file_path = os.path.join(renamed_directory, f'nota-{nota}.pdf')

for page_layout in extract_pages(file_path):
    for element in page_layout:
        print(element)