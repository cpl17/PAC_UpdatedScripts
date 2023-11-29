import pandas as pd
import os
from Helpers import get_sheet_data,write_df_to_sheet
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload
import io





# For each file -> read file into string,check common and scientific names for each plant against the string. Using a copy of the 
# source dataframe, remove all non-matched values,  and append to a list

#The source database
era_al = get_sheet_data("ERAFull","ERAFull")
era_al = era_al[["Scientific Name","Common Name","USDA Symbol"]]
era_al_copy = era_al.copy()

for col in era_al:
    era_al[col] = era_al[col].str.lower()


count_dict = {}
list_of_dfs = []


for file in os.listdir("./Temp"):

    print(file)

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
nursery_info = get_sheet_data("Full_CNP_Database","LOCAL_MAP")

mapping = nursery_info.set_index("SOURCE").to_dict()["URL"] #Nursery to URL


local_long["URL"] = local_long["Nursery"].map(mapping)
local_long = local_long[["USDA Symbol","Nursery","URL"]]
local_long.columns = ["USDA Symbol","Source","URL"]
local_long["USDA Symbol"] = local_long["USDA Symbol"].str.upper()
local_long.to_csv("LOCAL.csv")
write_df_to_sheet("LOCAL_Full","LOCAL_Full",local_long)

### Output: Aggegrate along symbol to get SYMBOL URLS COUNT df ###
df = nursery_matches_source.copy()
df["URL"] = df["Nursery"].map(mapping)
df = df[["USDA Symbol","Nursery","URL"]]

f = lambda x: ', '.join(map(str, set(x)))
local_agg = df.groupby("USDA Symbol").agg({"URL":[f,len],"Nursery":f})
local_agg.reset_index(inplace=True)
local_agg.columns = ["USDA Symbol","URLS","COUNT","Source"]
local_agg["Source"] = local_agg["Source"].apply(lambda x: ", ".join(sorted(x.split(", "))).strip())
local_agg["URLS"] = local_agg["Source"].apply(lambda x: ", ".join([mapping[y.strip()] for y in x.split(",")]))



local_agg["USDA Symbol"] = local_agg["USDA Symbol"].str.upper()
local_agg = pd.merge(local_agg,era_al_copy,on="USDA Symbol",how="left")
local_agg["Common Name"] = local_agg["Common Name"].str.title()
local_agg["String"] = [f"{row['Common Name']} ({row['Scientific Name']}): {row['Source']}" for _,row in local_agg.iterrows()]
local_agg.to_csv("LOCAL_AGG.csv")
write_df_to_sheet("LOCAL_AGG_Full","LOCAL_AGG_Full",local_agg)




    



