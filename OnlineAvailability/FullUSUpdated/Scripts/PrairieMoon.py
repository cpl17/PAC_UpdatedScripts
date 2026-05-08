import pandas as pd
import time
from datetime import datetime
from pathlib import Path
import argparse
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


from Helpers import get_sheet_data,write_df_to_sheet

def parse_args():
    parser = argparse.ArgumentParser(description="Run PrairieMoon scraper.")
    parser.add_argument("--debug", dest="debug", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--write-to-sheet", dest="write_to_sheet", action=argparse.BooleanOptionalAction, default=False)
    return parser.parse_args()


_ARGS = parse_args()
DEBUG = _ARGS.debug
WRITE_TO_SHEET = _ARGS.write_to_sheet
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

base_page = "https://www.prairiemoon.com/seeds/"
MAX_PAGES = 300
RESULTS_PER_PAGE = 48
last_signature = None
repeat_signature_count = 0

for page_number in range(1, MAX_PAGES + 1):
    if page_number == 1:
        page_url = f"{base_page}#/?resultsPerPage={RESULTS_PER_PAGE}"
    else:
        page_url = f"{base_page}#/?page={page_number}&resultsPerPage={RESULTS_PER_PAGE}"

    driver.get(page_url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".g-product-card"))
    )
    time.sleep(1)

    cards = driver.find_elements(By.CSS_SELECTOR, ".g-product-card")
    page_names = []
    page_links = []
    skipped_items = 0
    for card in cards:
        link_elements = card.find_elements(By.CSS_SELECTOR, "a.g-product-card__link")
        name_elements = card.find_elements(By.CSS_SELECTOR, ".g-product-card__brand")
        if not link_elements or not name_elements:
            skipped_items += 1
            continue
        href = (link_elements[0].get_attribute("href") or "").strip()
        if href and href.startswith("/"):
            href = urljoin(base_page, href)
        name = name_elements[0].text.strip()
        if not href or not name:
            skipped_items += 1
            continue
        page_links.append(href)
        page_names.append(name)

    signature = tuple(page_links[:8])
    if not page_links:
        if DEBUG:
            print(f"[DEBUG] Page {page_number}: no cards parsed, stopping.")
        break
    if signature == last_signature:
        repeat_signature_count += 1
    else:
        repeat_signature_count = 0
    last_signature = signature
    # End only after repeated identical pages, avoids premature stop on transient load issues.
    if repeat_signature_count >= 2:
        if DEBUG:
            print(f"[DEBUG] Page {page_number}: repeated signature detected multiple times, stopping pagination.")
        break

    all_links.extend(page_links)
    all_names.extend(page_names)
    if DEBUG:
        print(f"[DEBUG] Page {page_number}: links={len(page_links)}, names={len(page_names)}, skipped={skipped_items}")
        print(f"[DEBUG] Page {page_number}: sample names={page_names[:5]}")

    for name, link in zip(page_names, page_links):
        if name in scientific_name_set:
            if DEBUG:
                print(f"[DEBUG] Match on page {page_number}: {name}")
            matches_list.append(name)
            match_urls_list.append(link)


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

