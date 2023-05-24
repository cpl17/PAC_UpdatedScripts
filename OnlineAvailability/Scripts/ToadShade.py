import requests 
import pandas as pd

from Helpers import get_sheet_data,write_df_to_sheet

for STATE in ["AL","PA"]:

    era = get_sheet_data("ERA",STATE)
    common_names = era["Common Name"].to_list()
    scientific_names = era["Scientific Name"].to_list()

    matches_list = []
    match_urls_list = []

    # for name in scientific_names[:15]:
    for name in scientific_names[:15]:
        test_url = f"https://www.toadshade.com/{'-'.join(name.split())}.html"
        response = requests.get(test_url)
        status_code = response.status_code
        if status_code == 200:
            matches_list.append(name)
            match_urls_list.append(response.url)
            print(name,len(matches_list))
        


    era = era[["USDA Symbol","Scientific Name"]]
    matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["ToadShade.com"]*(len(matches_list)),"URL":match_urls_list})
    final = pd.merge(matches_df,era,on="Scientific Name",how="left")
    final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
    final = final[["USDA","Scientific Name","Root","URL"]]
    final = final.drop_duplicates(subset="Scientific Name",keep="first")


    write_df_to_sheet("All_Scraped_Data",f"ToadShade_{STATE}",final)

