import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set the path to the downloaded JSON file with your credentials
credentials_path = 'service_account.json'

# Set the directory ID of your Google Drive folder
drive_folder_id = '1S1h2lSrfGKKVQhFVqZKsmaO2pCAMmf91'

# Create a service object using the credentials
credentials = service_account.Credentials.from_service_account_file(
    credentials_path,
    scopes=['https://www.googleapis.com/auth/drive']
)
service = build('drive', 'v3', credentials=credentials)

def download_google_doc(doc_id, output_path):
    request = service.files().export_media(fileId=doc_id, mimeType='text/plain')
    media = request.execute()

    with open(output_path, 'wb') as f:
        f.write(media)

def process_drive_folder(folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)",
    ).execute()

    files = results.get('files', [])

    for file in files:
        doc_id = file['id']
        doc_name = file['name']

        # Set the output path for the text file
        output_path = f"{doc_name}.txt"

        # Download and save the content of the Google Doc
        download_google_doc(doc_id, output_path)

if __name__ == '__main__':
    process_drive_folder(drive_folder_id)