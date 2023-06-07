from Google import Create_Service
from googleapiclient.http import MediaFileUpload,MediaIoBaseDownload
import pandas as pd
import io
import os 

CLIENT_SECRET_FILE = 'service_account.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)
# # print(dir(service))

# # #Upload files
# # folder_id = "1KZgUWT74O3ltPASUBAuVapotoEjbGMid"
# # file_names = ["Google.py","TEST.txt"]
# # mime_types = ['text/x-script.phyton','text/plain']

# # for file_name,mime_type in zip(file_names,mime_types):
# #     file_metadata = {
# #         'name': file_name,
# #         'parents':[folder_id]
# #     }

# #     media = MediaFileUpload(file_name,mimetype=mime_type)

# #     service.files().create(
# #         body = file_metadata,
# #         media_body = media,
# #         fields='id'
# #     ).execute()
# # #List all files 

# # folder_id = '1KZgUWT74O3ltPASUBAuVapotoEjbGMid'
# # query = f"parents = '{folder_id}'"

# # response = service.files().list(q=query).execute()
# # files = response.get('files')
# # nextPageToken = response.get('nextPageToken')

# # while nextPageToken:
# #     response = service.files().list(q=query,pageToken = nextPageToken).execute()
# #     files.extend(response.get('files'))
# #     nextPageToken=response.get('nextPageToken')


# # df = pd.DataFrame(files)
# # print(df)






# #Download all files in a directory 



# folder_id = '1KZgUWT74O3ltPASUBAuVapotoEjbGMid'
# query = f"parents = '{folder_id}' and trashed = false"

# response = service.files().list(q=query).execute()
# files = response.get('files')
# nextPageToken = response.get('nextPageToken')

# while nextPageToken:
#     response = service.files().list(q=query,pageToken = nextPageToken).execute()
#     files.extend(response.get('files'))
#     nextPageToken=response.get('nextPageToken')


# file_ids = [file['id'] for file in files]
# file_names = [file['name'] for file in files]

# for file_id,file_name in zip(file_ids, file_names):
#     request = service.files().get_media(fileId=file_id)

#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fd=fh,request=request)
#     done = False
    
#     while not done:
#         status,done = downloader.next_chunk()
    
#     fh.seek(0)

#     with open(os.path.join('TEST',file_name),'wb') as f:
#         f.write(fh.read())
#         f.close()



# import pandas as pd
# import gspread
# from gspread_dataframe import set_with_dataframe



# def get_sheet_data(GSHEET_NAME,TAB_NAME):
#     gc = gspread.service_account()
#     sh = gc.open(GSHEET_NAME)
#     worksheet = sh.worksheet(TAB_NAME)
#     df = pd.DataFrame(worksheet.get_all_records())
#     return df


# def write_df_to_sheet(GSHEET_NAME,TAB_NAME,df):
#     gc = gspread.service_account()
#     sh = gc.open(GSHEET_NAME)
#     worksheet = sh.worksheet(TAB_NAME)
#     set_with_dataframe(worksheet, df)



# #Uupdating File

# import requests

# accessToken = '###' # Please set your access token.
# updateFileId = '###' # Please set the file ID fot the text file on Google Drive.

# headers = {"Authorization": "Bearer " + accessToken}
# file = open("./Test.txt", "rb")
# r2 = requests.patch(
#     "https://www.googleapis.com/upload/drive/v3/files/" + updateFileId + "?uploadType=media",
#     headers=headers,
#     data=file,
# )



#Download a single file 

# file_id = '1awRsImZ2NotOeCNhTzk7kMT-GMpOllmEQxyVeTrU43c'
# export_mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

# request= service.files().export_media(fileId=file_id,mimeType=export_mime_type)
# file = io.BytesIO()

# downloader = MediaIoBaseDownload(file, request)
# done = False
# while done is False:
#     status, done = downloader.next_chunk()
#     print(F'Download {int(status.progress() * 100)}.')


# with file.write....

import gspread


# Authenticate and create the Sheets and Drive API clients
drive_service = Create_Service(CLIENT_SECRET_FILE,'drive','v3',SCOPES)

# ID of the Google Sheets document
spreadsheet_id = '1awRsImZ2NotOeCNhTzk7kMT-GMpOllmEQxyVeTrU43c'

# Path to save the downloaded Excel file
save_path = 'downloaded_file.xlsx'

# Export the Sheets document as an Excel file using the Drive API
request = drive_service.files().export_media(fileId=spreadsheet_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
response = request.execute()

# Save the response content as a file
with open(save_path, 'wb') as file:
    file.write(response)

print("File downloaded and saved as Excel successfully!")