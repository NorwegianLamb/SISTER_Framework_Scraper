import os, glob

current_directory = os.getcwd()
download_directory = os.path.join(current_directory, 'data')

def renameLastDownload(nota):
    all_files = glob.glob(os.path.join(download_directory, '*'))
    sorted_files = sorted(all_files, key=os.path.getmtime, reverse=True)
    latest_file = sorted_files[0]
    new_filename = f"Nota{str(nota)}.pdf"
    new_file_path = os.path.join(download_directory, new_filename)
    os.rename(latest_file, new_file_path)

header = ["prova"]
print(f"aa='{header[0]}'")