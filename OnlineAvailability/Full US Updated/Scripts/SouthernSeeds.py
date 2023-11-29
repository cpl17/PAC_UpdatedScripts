import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import re

import requests
from bs4 import BeautifulSoup


from Helpers import get_sheet_data,write_df_to_sheet

def clean_text(full_text):
        
    pattern = r'\((.*?)\)'
    match = re.search(pattern, full_text)


    # Checking if a match is found
    if match:
        return match.group(1)
    else:
        return 

era = get_sheet_data("ERAFull","ERAFull")
common_names = era["Common Name"].to_list()
scientific_names = era["Scientific Name"].to_list()
scientific_names_string = era["Scientific Name"].to_list()



matches_list = []
match_urls_list = []



for page_num in range(1,16):

    url = f"https://southernseedexchange.com/collections/flower-seeds?page={page_num}"

    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract links and names using CSS selectors (links not working)
    # all_links = [link['href'] for link in soup.select('a.product-link')]
    all_names = [clean_text(name.text) for name in soup.select('.product-block__title')]

    # for link,name in list(zip(all_links,all_names)):
    #     if name in scientific_names:
    #         match_urls_list.append(link)
    #         matches_list.append(name)

    for name in all_names:
        if name in scientific_names:
            matches_list.append(name)



era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["SouthernSeedExchange.com"]*(len(matches_list)),"URL":["southernseedexchange.com/collections/flower-seeds"]*(len(matches_list))})

#Matches Df
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")
write_df_to_sheet("All_Online_Scraped_Data_Full","SouthernSeedExchange",final)
