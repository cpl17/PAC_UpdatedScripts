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


for STATE in  ["PA","AL"]:

    era = get_sheet_data("ERA",STATE)
    common_names = era["Common Name"].to_list()
    scientific_names = era["Scientific Name"].to_list()

    driver = webdriver.Chrome(service=ser, options=options)


    matches_list = []
    match_urls_list = []
    all_names = []
    all_links = []

    # for page_number in range(1,28):
    for page_number in range(1,6):
        if page_number == 1:

            home_page = "https://petalsfromthepast.com/product-category/plants/"
            driver.get(home_page)
            WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR,"h2.woocommerce-loop-product__title")))
            time.sleep(2)
        
        else:

            page = f"https://petalsfromthepast.com/product-category/plants/page/{page_number}/"
            driver.get(page)
            WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR,"p.woocommerce-result-count"))) #there is a random blank page (8), have to use "Showing ... results" text
            time.sleep(2)


        link_elements = driver.find_elements(By.CSS_SELECTOR,"li a.woocommerce-loop-product__link")
        links = [link_element.get_attribute("href") for link_element in link_elements]
        all_links += links

        name_elements = driver.find_elements(By.CSS_SELECTOR,"h2.woocommerce-loop-product__title")
        names = [name_element.text for name_element in name_elements]
        all_names += names

        page_list = list(zip(links,names))

        for link_name_tuple in page_list:

            #Source name "Amsonia tabernaemontana" is found in name on webpage as "Amsonia tabernaemontana – ‘Bluestar"
            for name in scientific_names:
                if name in link_name_tuple[1]:
                    matches_list.append(name)
                    match_urls_list.append(link_name_tuple[0])
                    print(name,link_name_tuple[1])
                    break
            
            for i,name in enumerate(common_names):
                if name in link_name_tuple[1]:
                    matches_list.append(scientific_names[i]) #Need a consistent column to match on, if common name found, store match my it's corresponding scientific name
                    match_urls_list.append(link_name_tuple[0])
                    print(name,link_name_tuple[1])
                    break
            

            

        time.sleep(5)

        print(page_number,"\n")

    driver.close()



    era = era[["USDA Symbol","Scientific Name"]]

    
    matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["PetalsFromthePast.com"]*(len(matches_list)),"URL":match_urls_list})

    #Matches Df
    final = pd.merge(matches_df,era,on="Scientific Name",how="left")
    final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
    final = final[["USDA","Scientific Name","Root","URL"]]
    final = final.drop_duplicates(subset="Scientific Name",keep="first")
    write_df_to_sheet("All_Scraped_Data",f"PetalsFromthePast_{STATE}",final)

#Full Inventory 
full_inventory_df = pd.DataFrame({"Scientific Name":all_names,"Root":["PetalsFromthePast.com"]*(len(all_names)),"URL":all_links})
final = pd.merge(full_inventory_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")
write_df_to_sheet("All_Scraped_Data",f"PetalsFromthePast_FullInventory",final)