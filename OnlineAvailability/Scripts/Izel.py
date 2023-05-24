import pandas as pd
import time
import math

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

for STATE in ["PA","AL"]:

    era = get_sheet_data("ERA",STATE)
    common_names = era["Common Name"].to_list()
    scientific_names = era["Scientific Name"].to_list()

    driver = webdriver.Chrome(service=ser, options=options)


    matches_list = []
    match_urls_list = []
    all_names = []
    all_links = []

    #Get the number of pages - depends on the number of plants listed 
    home_page = "https://www.izelplants.com/all-plants/?product_list_limit=128"
    driver.get(home_page)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,'//*[@id="amasty-shopby-product-list"]/div[1]/div[1]/span')))

    num_plants_string = driver.find_element(By.XPATH,'//*[@id="amasty-shopby-product-list"]/div[1]/div[1]/span').text
    num_plants = int(num_plants_string.split(" ")[-1])
    num_pages = math.ceil(num_plants / 128)

    # for page_number in range(1,num_pages + 1):
    for page_number in range(1,3):

        if page_number != 1:

            page = f"https://www.izelplants.com/all-plants/?p={page_number}&product_list_limit=128"
            driver.get(page)
            WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR,"a.product-item-link")))
            time.sleep(5)


        link_elements = driver.find_elements(By.CSS_SELECTOR,"a.product-item-link")
        all_links += [link.get_attribute("href") for link in link_elements]

        for link in link_elements:

            # name_element = link.find_element(By.TAG_NAME,"span")
            name = link.text
            all_names.append(name)


            if name in scientific_names:
                print(name,page_number)
                matches_list.append(name)
                match_urls_list.append(link.get_attribute("href"))

        time.sleep(5)



    era = era[["USDA Symbol","Scientific Name"]]


    matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["IzelPlants.com"]*(len(matches_list)),"URL":match_urls_list})

    #Matches Df
    final = pd.merge(matches_df,era,on="Scientific Name",how="left")
    final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
    final = final[["USDA","Scientific Name","Root","URL"]]
    final = final.drop_duplicates(subset="Scientific Name",keep="first")
    write_df_to_sheet("All_Scraped_Data",f"Izel_{STATE}",final)

#Full Inventory 
full_inventory_df = pd.DataFrame({"Scientific Name":all_names,"Root":["IzelPlants.com"]*(len(all_names)),"URL":all_links})
final = pd.merge(full_inventory_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")
write_df_to_sheet("All_Scraped_Data",f"Izel_FullInventory",final)

    


