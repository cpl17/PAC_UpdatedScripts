import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By

from Helpers import get_sheet_data,write_df_to_sheet

import winsound


import os
print(os.getcwd())
options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)
ser = Service("C:\Program Files (x86)\chromedriver.exe")



DELAY = 2

driver = webdriver.Chrome(service=ser, options=options)

#Metadata and Source Data
era = get_sheet_data("ERAFull","ERAFull")
common_names = era["Common Name"].to_list()
scientific_names = era["Scientific Name"].to_list()

#Lists to fill with Names of Matches and URLs
matches_list = []
match_urls_list = []

#Gets overwritten (intended)
all_names = []
all_links = []

#Open Species Page (Contains all Seeds on the site)
home_page = "https://www.ernstseed.com/seed-finder-tool/?_product_type=individual-species"
driver.get(home_page)

# for page_num in range(1,46):
for page_num in range(1,3):

    print(page_num)
    time.sleep(5)

    if page_num != 1:

        driver.get(f"https://www.ernstseed.com/seed-finder-tool/?_product_type=individual-species&_paged={page_num}")
        time.sleep(3)

    #Get Link Elements - Anchor tags that contain the direct link and the name of the plant
    link_elements = driver.find_elements(By.CSS_SELECTOR,"a.woocommerce-LoopProduct-link")
    links = [link.get_attribute("href") for link in link_elements]
    all_links.extend(links)


    #Get the names
    name_elements = driver.find_elements(By.CSS_SELECTOR,"p.botanical-name")
    names = [name.text for name in name_elements]
    all_names.extend(names)


    assert len(link_elements) == len(name_elements)


    for name, link in list(zip(names,links)):
        if name in scientific_names:
            matches_list.append(name)
            match_urls_list.append(link)



driver.close()



era= era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["ErnstSeed.com"]*(len(matches_list)),"URL":match_urls_list})

#Matches Df
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")
write_df_to_sheet("All_Online_Scraped_Data_Full","ErnstSeed",final)


#Full Inventory 


# full_inventory_df = pd.DataFrame({"Scientific Name":all_names,"Root":["ErnstSeed.com"]*(len(all_names)),"URL":all_links})

# final = pd.merge(full_inventory_df,era,on="Scientific Name",how="left")
# final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
# final = final[["USDA","Scientific Name","Root","URL"]]
# final = final.drop_duplicates(subset="Scientific Name",keep="first")

# write_df_to_sheet("All_Scraped_Data",f"ErnstSeed_FullInventory",final)

winsound.Beep(400,10000)




