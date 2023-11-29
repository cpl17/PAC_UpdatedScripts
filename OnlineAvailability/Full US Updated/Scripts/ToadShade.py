import requests 
import pandas as pd

from Helpers import get_sheet_data,write_df_to_sheet



era = get_sheet_data("ERAFull","ERAFull")
common_names = era["Common Name"].to_list()
scientific_names = era["Scientific Name"].to_list()

matches_list = []
match_urls_list = []


#Get the list of all available plants by scientific name
response = requests.get("https://www.toadshade.com/SpeciesList.html")
table = pd.read_html(response.text)
availability = table[3].loc[:,1].str.lower().to_list()


#For each name in the db, check if its in the availability list
for scientific_name in scientific_names:

    if scientific_name.lower() in availability:


        namelist = scientific_name.split()
        namelist[0] = namelist[0].title()
        full_url = f"https://www.toadshade.com/{'-'.join(namelist)}.html"

        #Store matches
        match_urls_list.append(full_url)
        matches_list.append(scientific_name)
        


#Wrangle data
era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["ToadShade.com"]*(len(matches_list)),"URL":match_urls_list})
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")


write_df_to_sheet("All_Online_Scraped_Data_Full","ToadShade",final)

