import pandas as pd
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from Helpers import get_sheet_data,write_df_to_sheet

DEBUG = True
WRITE_TO_SHEET = True
SCRIPT_NAME = "PlantMore"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)

DELAY = 2


# #Function that waits until the correct page is selected
# def wait_until_page_load(page_index):

#     if int(driver.find_element(By.CLASS_NAME,"wsite-selected").text) != (page_index +2):
#         time.sleep(5)
#         wait_until_page_load(page_index)



era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()
scientific_name_set = set(scientific_names)

matches_list = []
match_urls_list = []
all_names = []
all_links = []


######### Scraping #########

driver = webdriver.Chrome(options=options)

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
    if DEBUG:
        print(f"[DEBUG] Page index {page_index}: links={len(links)}, names={len(names)}")

    assert len(names) == len(links)

    
    for name,link in list(zip(names,links)):


        if name in scientific_name_set:
            if DEBUG:
                print(f"[DEBUG] Match on page index {page_index}: {name}")
            matches_list.append(name)
            match_urls_list.append(link)

    


driver.close()



era = era[["USDA Symbol","Scientific Name"]]


matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["PlantMoreNatives.com"]*(len(matches_list)),"URL":match_urls_list})
raw_df = pd.DataFrame({"Scientific Name":all_names,"URL":all_links})

#Matches Df
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")

if DEBUG:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[DEBUG] Raw rows={len(raw_df)}, matches pre-dedupe={len(matches_df)}, final rows={len(final)}")
    raw_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_raw_{timestamp}.csv", index=False)
    matches_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_matches_pre_dedupe_{timestamp}.csv", index=False)
    final.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_final_{timestamp}.csv", index=False)
    print(f"[DEBUG] Wrote debug CSV snapshots to {DEBUG_DIR}")

if WRITE_TO_SHEET:
    write_df_to_sheet("All_Online_Scraped_Data","PlantMoreNatives",final)

#Full Inventory 
# full_inventory_df = pd.DataFrame({"Scientific Name":all_names,"Root":["PlantMoreNatives.com"]*(len(all_names)),"URL":all_links})
# final = pd.merge(full_inventory_df,era,on="Scientific Name",how="left")
# final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
# final = final[["USDA","Scientific Name","Root","URL"]]
# final = final.drop_duplicates(subset="Scientific Name",keep="first")
# write_df_to_sheet("All_Scraped_Data","PlantMoreNatives_FullInventory",final)

