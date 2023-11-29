import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

from Helpers import get_sheet_data,write_df_to_sheet


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

era = get_sheet_data("ERAFull","ERAFull")
common_names = era["Common Name"].to_list()
scientific_names = era["Scientific Name"].to_list()


matches_list = []
match_urls_list = []

for num in range(1,5):
    
    url = f"https://www.amandasnativeplants.com/onlinestore?page={num}"


    response = requests.get(url,headers=headers)
    soup = BeautifulSoup(response.text)
    items = soup.select('li[data-hook="product-list-grid-item"]')
    links = [link.select_one("div a")['href'] for link in items ]
    names = [link.select_one("div a div div div h3").text.split(" - ")[0] for link in items]

    print(names)

    for link,name in list(zip(links,names)):
        if name in scientific_names:
            match_urls_list.append(link)
            matches_list.append(name)


era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["AmandasNativePlants.com"]*(len(matches_list)),"URL": match_urls_list})

#Matches Df
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")
final.to_csv("Test.csv")
write_df_to_sheet("All_Online_Scraped_Data_Full","AmandasNursery",final)