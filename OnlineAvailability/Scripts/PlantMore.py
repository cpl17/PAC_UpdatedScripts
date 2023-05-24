import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from Helpers import get_sheet_data,write_df_to_sheet

options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)
ser = Service("C:\Program Files (x86)\chromedriver.exe")

DELAY = 2


# #Function that waits until the correct page is selected
# def wait_until_page_load(page_index):

#     if int(driver.find_element(By.CLASS_NAME,"wsite-selected").text) != (page_index +2):
#         time.sleep(5)
#         wait_until_page_load(page_index)

for STATE  in ["AL","PA"]:

    era = get_sheet_data("ERA",STATE)
    common_names = era["Common Name"].to_list()
    scientific_names = era["Scientific Name"].to_list()

    matches_list = []
    match_urls_list = []
    all_names = []
    all_links = []


    ######### Scraping #########

    driver = webdriver.Chrome(service=ser, options=options)

    home_page = "https://www.plantmorenatives.com/store/c26/native_perennial_plant_store#/"

    driver.get(home_page)

    #Wait for pop-up and close. It does not return 
    time.sleep(10)
    pop_up = driver.find_element(By.XPATH,"//*[@id='leadform-popup-close-576d6d25-a6a2-40cb-ab77-1205e75d2f2e']")
    pop_up.click()



    xpaths_for_pages = ["first page"] + [f"//*[@id='wsite-com-category-product-group-pagelist']/a[{page_number}]" for page_number in range(3,8)]
    for page_index,path in enumerate(xpaths_for_pages):

        if path != "first page":

            page_element = driver.find_element(By.XPATH,path)
            page_element.click()

            time.sleep(5)

            # wait_until_page_load(page_index)

        #Get all the links and plant names on the page
        link_elements = driver.find_elements(By.CLASS_NAME,"wsite-com-category-product-link")
        links = [link.get_attribute("href") for link in link_elements]
        all_links.extend(links)
        
        name_elements = driver.find_elements(By.CLASS_NAME,"wsite-com-link-text")
        names_full_text = [name.text for name in name_elements]
        names = [x.split("'")[0].split("(")[0].strip("\n").rstrip() for x in names_full_text]
        all_names.extend(names)

        assert len(names) == len(links)

        
        for name,link in list(zip(names,links)):


            if name in scientific_names:
                print(name,page_index)
                matches_list.append(name)
                match_urls_list.append(link)

        


    driver.close()



    era = era[["USDA Symbol","Scientific Name"]]


    matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["PlantMoreNatives.com"]*(len(matches_list)),"URL":match_urls_list})

    #Matches Df
    final = pd.merge(matches_df,era,on="Scientific Name",how="left")
    final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
    final = final[["USDA","Scientific Name","Root","URL"]]
    final = final.drop_duplicates(subset="Scientific Name",keep="first")
    write_df_to_sheet("All_Scraped_Data",f"PlantMoreNatives_{STATE}",final)

#Full Inventory 
full_inventory_df = pd.DataFrame({"Scientific Name":all_names,"Root":["PlantMoreNatives.com"]*(len(all_names)),"URL":all_links})
final = pd.merge(full_inventory_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")
write_df_to_sheet("All_Scraped_Data","PlantMoreNatives_FullInventory",final)

