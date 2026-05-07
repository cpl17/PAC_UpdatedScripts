import pandas as pd
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

DEBUG = True
WRITE_TO_SHEET = True
SCRIPT_NAME = "MidAtlantic"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)

from Helpers import get_sheet_data,write_df_to_sheet



era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()
scientific_name_set = set(scientific_names)

driver = webdriver.Chrome(options=options)


matches_list = []
match_urls_list = []
all_names = []


home_page = "https://midatlanticnatives.com/product-category/bare-root-native-plants/"

driver.get(home_page)


#Scroll to the bottom of the page
last_height = driver.execute_script("return document.body.scrollHeight")

while True:

    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(7)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break

    else:
        last_height = new_height


#Find link elements for each plant, use a cleaned version of the link text (Full inventory text)
#to create a list of all the plants on the page. 
link_elements = driver.find_elements(By.CSS_SELECTOR,"div h2 a")
all_links = [link.get_attribute("href") for link in link_elements]

all_names_text = [element.text for element in link_elements]
all_names = [" ".join(x.split(" ")[:2]).strip(",") for x in all_names_text]
if DEBUG:
    print(f"[DEBUG] Parsed links={len(all_links)}")
    print(f"[DEBUG] Sample parsed names={all_names[:5]}")


#Find Matches. All relevant links have a child italize tag that holds the name 
for link in link_elements:
    try:
        name = " ".join((link.text).split(" ")[:2]).strip(",")

    except:
        continue

    if name in scientific_name_set:
        matches_list.append(name)
        match_urls_list.append(link.get_attribute("href"))



driver.close()


era = era[["USDA Symbol","Scientific Name"]]
full_inventory_df = pd.DataFrame({"Scientific Name":all_names,"Root":["MidAtlanticNatives.com"]*(len(all_names)),"URL":all_links})
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["MidAtlanticNatives.com"]*(len(matches_list)),"URL":match_urls_list})

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
    write_df_to_sheet("All_Online_Scraped_Data_Full",f"MidAtlantic",final)

# #Full Inventory 
# final = pd.merge(full_inventory_df,era,on="Scientific Name",how="left")
# final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
# final = final[["USDA","Scientific Name","Root","URL"]]
# final = final.drop_duplicates(subset="Scientific Name",keep="first")
# write_df_to_sheet("All_Scraped_Data",f"MidAtlantic_FullInventory",final)


    
