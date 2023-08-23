import pandas as pd
import os
from Helpers import get_sheet_data,write_df_to_sheet
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload
import io

CLIENT_SECRET_FILE = 'service_account.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)

#Donload TextFiles into Temporary Folder
os.mkdir("Temp")

folder_id = '1a4LL-8AJA_i2Yy5jknFP49muSZLWIae6'
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
    request = service.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh,request=request)
    done = False
    
    while not done:
        status,done = downloader.next_chunk()
    
    fh.seek(0)

    with open(os.path.join('Temp',file_name),'wb') as f:
        f.write(fh.read())
        f.close()



# For each file -> read file into string,check common and scientific names for each plant against the string. Using a copy of the 
# source dataframe, remove all non-matched values,  and append to a list

#The source database
era_al = get_sheet_data("ERA","AL")
era_al = era_al[["Scientific Name","Common Name","USDA Symbol"]]
era_al_copy = era_al.copy()

for col in era_al:
    era_al[col] = era_al[col].str.lower()


count_dict = {}
list_of_dfs = []


for file in os.listdir("./Temp"):

    full_path = "./Temp/" + file

    with open(full_path,encoding='unicode_escape') as f:
        string = f.read().lower()
    
    df = era_al.copy()
    df["Match"] = 0

    com_names = df["Common Name"].to_list()
    scientific_names = df["Scientific Name"].to_list()


    #Check the string for the common name and scientific name. 
    # If there is a match, replace match with a 1
    for i,tup in enumerate(list(zip(com_names,scientific_names))):
        common_name = tup[0]
        scientific_name = tup[1]
        if ((common_name in string) | (scientific_name in string)):
            df.loc[i,"Match"] = 1
            print("match")

    #Create a nursery column
    nursery = file.split(".")[0]
    df["Nursery"] = nursery
    
    #Reduce the df to only where there is a match
    df = df[df.Match == 1]

    #Find the number of matches and append to the count dict
    count = df.Match.sum()
    count_dict.update({nursery:count})

    df.drop("Match",axis=1,inplace=True)
    list_of_dfs.append(df)

nursery_matches_source = pd.concat(list_of_dfs)

### Output: A long df with entries SYMBOL NURSERY URL. ###
# Note: URLS are the nursery urls NOT the urls used for the http requests. 
local_long = nursery_matches_source.copy()
nursery_info = get_sheet_data("Local_Catalog_URLS","AL")

mapping = nursery_info.set_index("Nursery").to_dict()["Nursery URL"] #Nursery to URL


local_long["URL"] = local_long["Nursery"].map(mapping)
local_long = local_long[["USDA Symbol","Nursery","URL"]]
local_long.columns = ["USDA Symbol","Source","URL"]
local_long["USDA Symbol"] = local_long["USDA Symbol"].str.upper()
write_df_to_sheet("LOCAL","AL",local_long)

### Output: Aggegrate along symbol to get SYMBOL URLS COUNT df ###
df = nursery_matches_source.copy()
df["URL"] = df["Nursery"].map(mapping)
df = df[["USDA Symbol","Nursery","URL"]]

f = lambda x: ', '.join(map(str, set(x)))
local_agg = df.groupby("USDA Symbol").agg({"URL":[f,len],"Nursery":f})
local_agg.reset_index(inplace=True)
local_agg.columns = ["USDA Symbol","URLS","COUNT","Source"]
local_agg["USDA Symbol"] = local_agg["USDA Symbol"].str.upper()
local_agg = pd.merge(local_agg,era_al_copy,on="USDA Symbol",how="left")
local_agg["Common Name"] = local_agg["Common Name"].str.title()
local_agg["String"] = [f"{row['Common Name']} ({row['Scientific Name']}): {row['Source']}" for _,row in local_agg.iterrows()]
write_df_to_sheet("LOCAL_AGG","AL",local_agg)

os.remove("Temp")



    



