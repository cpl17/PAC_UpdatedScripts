import pandas as pd
import os
from Helpers import get_sheet_data,write_df_to_sheet
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload
import io

def download_google_doc(doc_id, output_path):
    request = service.files().export_media(fileId=doc_id, mimeType='text/plain')
    media = request.execute()
    output_path = "Temp/" + output_path
    with open(output_path, 'wb') as f:
        f.write(media)

CLIENT_SECRET_FILE = 'service_account.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)

#Donload TextFiles into Temporary Folder
if "Temp" not in os.listdir():
    os.mkdir("Temp")

folder_id = '1S1h2lSrfGKKVQhFVqZKsmaO2pCAMmf91'
query = f"parents = '{folder_id}' and trashed = false"

response = service.files().list(q=query).execute()
files = response.get('files')
nextPageToken = response.get('nextPageToken')

while nextPageToken:
    response = service.files().list(q=query,pageToken = nextPageToken).execute()
    files.extend(response.get('files'))
    nextPageToken=response.get('nextPageToken')


file_ids = [file['id'] for file in files]
file_names = [file['name'] for file in files]

for file_id,file_name in zip(file_ids, file_names):    
    print(file_name)
    # request = service.files().get_media(fileId=file_id)

    # fh = io.BytesIO()
    # downloader = MediaIoBaseDownload(fd=fh,request=request)
    # done = False
    
    # while not done:
    #     status,done = downloader.next_chunk()
    
    # fh.seek(0)
    download_google_doc(file_id,file_name)










    



