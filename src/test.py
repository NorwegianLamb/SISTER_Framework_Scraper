import os
current_directory = os.getcwd()
download_directory = os.path.join(current_directory, 'data')
# os.makedirs(download_directory, exist_ok=True)

print(download_directory)