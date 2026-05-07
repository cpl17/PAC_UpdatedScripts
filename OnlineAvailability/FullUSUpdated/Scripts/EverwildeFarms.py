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
SCRIPT_NAME = "EverwildeFarms"
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


home_page = "https://www.everwilde.com/Southeast-Wildflower-Seeds.html"

driver.get(home_page)


# #Scroll to the bottom of the page
last_height = driver.execute_script("return document.body.scrollHeight")

while True:

    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(3)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break

    else:
        last_height = new_height


link_elements = driver.find_elements(By.CSS_SELECTOR,"ul li h2 a")
names = [link_element.find_element(By.CLASS_NAME,"type").text for link_element in link_elements]

if DEBUG:
    print(f"[DEBUG] Parsed link elements={len(link_elements)}")
    print(f"[DEBUG] Sample names={names[:5]}")

for link,name in list(zip(link_elements,names)):
    if name in scientific_name_set:
        match_urls_list.append(link.get_attribute("href"))
        matches_list.append(name)


era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["Everwilde.com"]*(len(matches_list)),"URL": match_urls_list})
raw_df = pd.DataFrame({"Scientific Name": names, "URL": [link.get_attribute("href") for link in link_elements]})

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
    write_df_to_sheet("All_Online_Scraped_Data_Full","EverwildeFarms",final)