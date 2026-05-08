import pandas as pd
import time
from datetime import datetime
from pathlib import Path
import argparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_args():
    parser = argparse.ArgumentParser(description="Run EverwildeFarms scraper.")
    parser.add_argument("--debug", dest="debug", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--write-to-sheet", dest="write_to_sheet", action=argparse.BooleanOptionalAction, default=False)
    return parser.parse_args()


_ARGS = parse_args()
DEBUG = _ARGS.debug
WRITE_TO_SHEET = _ARGS.write_to_sheet
SCRIPT_NAME = "EverwildeFarms"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)
SCROLL_PAUSE_SECONDS = 2
MAX_IDLE_SCROLLS = 5

options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)

from Helpers import get_sheet_data,write_df_to_sheet



era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()
scientific_name_set = set(scientific_names)


matches_list = []
match_urls_list = []


home_page = "https://www.everwilde.com/Southeast-Wildflower-Seeds.html"

driver = webdriver.Chrome(options=options)
driver.get(home_page)

WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "ul li h2 a"))
)

# Scroll until product count stabilizes across several passes.
idle_scrolls = 0
last_count = 0
while idle_scrolls < MAX_IDLE_SCROLLS:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_SECONDS)
    current_count = len(driver.find_elements(By.CSS_SELECTOR, "ul li h2 a"))
    if current_count > last_count:
        last_count = current_count
        idle_scrolls = 0
    else:
        idle_scrolls += 1

link_elements = driver.find_elements(By.CSS_SELECTOR, "ul li h2 a")
links = []
names = []
skipped_items = 0
for link_element in link_elements:
    href = link_element.get_attribute("href")
    type_elements = link_element.find_elements(By.CSS_SELECTOR, "span.type")
    type_text = type_elements[0].text.strip() if type_elements else ""
    if not href or not type_text:
        skipped_items += 1
        continue
    links.append(href)
    names.append(type_text)

driver.close()

if DEBUG:
    print(f"[DEBUG] Parsed link elements={len(link_elements)}")
    print(f"[DEBUG] Parsed names={len(names)}, skipped={skipped_items}")
    print(f"[DEBUG] Sample names={names[:5]}")

for link,name in list(zip(links,names)):
    if name in scientific_name_set:
        match_urls_list.append(link)
        matches_list.append(name)


era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["Everwilde.com"]*(len(matches_list)),"URL": match_urls_list})
raw_df = pd.DataFrame({"Scientific Name": names, "URL": links})

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