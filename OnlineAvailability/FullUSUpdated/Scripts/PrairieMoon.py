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
SCRIPT_NAME = "PrairieMoon"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)

DELAY = 2




era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()
scientific_name_set = set(scientific_names)

driver = webdriver.Chrome(options=options)


matches_list = []
match_urls_list = []
all_names = []
all_links = []

#Open Home Page, Get the number of pages
home_page = "https://www.prairiemoon.com/seeds/"
driver.get(home_page)
WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH,'//*[@id="category-listing-wrapper"]/div[3]/div/span/div/a[8]')))
num_pages = int(driver.find_element(By.XPATH,'//*[@id="category-listing-wrapper"]/div[3]/div/span/div/a[8]').text)

# for page_number in range(1,num_pages+1):
for page_number in range(1,3):

    if page_number != 1:

        page = f"https://www.prairiemoon.com/seeds/?page={page_number}"
        driver.get(page)
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR,"p.category-product-name a")))
        time.sleep(5)


    link_elements = driver.find_elements(By.CSS_SELECTOR,"p.category-product-name a")
    links = [link.get_attribute('href') for link in link_elements]
    all_links.extend(links)
    if DEBUG:
        print(f"[DEBUG] Page {page_number}: links={len(links)}")

    for link in link_elements:

        name_element = link.find_element(By.TAG_NAME,"span")
        name = name_element.text
        all_names.append(name)


        if name in scientific_name_set:
            if DEBUG:
                print(f"[DEBUG] Match on page {page_number}: {name}")
            matches_list.append(name)
            match_urls_list.append(link.get_attribute("href"))

    time.sleep(5)
    


driver.close()


era = era[["USDA Symbol","Scientific Name"]]

full_inventory_df = pd.DataFrame({"Scientific Name":all_names,"Root":["PrairieMoon.com"]*(len(all_names)),"URL":all_links})
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["PrairieMoon.com"]*(len(matches_list)),"URL":match_urls_list})

#Matches Df
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")

if DEBUG:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[DEBUG] Raw rows={len(full_inventory_df)}, matches pre-dedupe={len(matches_df)}, final rows={len(final)}")
    full_inventory_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_raw_{timestamp}.csv", index=False)
    matches_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_matches_pre_dedupe_{timestamp}.csv", index=False)
    final.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_final_{timestamp}.csv", index=False)
    print(f"[DEBUG] Wrote debug CSV snapshots to {DEBUG_DIR}")

if WRITE_TO_SHEET:
    write_df_to_sheet("All_Online_Scraped_Data_Full","PrairieMoon",final)

# #Full Inventory 
# final = pd.merge(full_inventory_df,era,on="Scientific Name",how="left")
# final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
# final = final[["USDA","Scientific Name","Root","URL"]]
# final = final.drop_duplicates(subset="Scientific Name",keep="first")
# write_df_to_sheet("All_Scraped_Data",f"PrairieMoon_FullInventory",final)

