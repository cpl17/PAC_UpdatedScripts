import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

from Helpers import get_sheet_data,write_df_to_sheet

DEBUG = True
WRITE_TO_SHEET = True
SCRIPT_NAME = "PlantMore"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}



era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()
scientific_name_set = set(scientific_names)

matches_list = []
match_urls_list = []
all_names = []
all_links = []

######### Scraping #########
base_page = "https://www.plantmorenatives.com/plants/"
page_number = 1
while True:
    page_url = f"{base_page}?page={page_number}"
    response = requests.get(page_url, headers=headers, timeout=60)
    if response.status_code == 404:
        if DEBUG:
            print(f"[DEBUG] Page {page_number}: 404 received, stopping.")
        break
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("ul.productGrid li.product article.card")
    if not cards:
        if DEBUG:
            print(f"[DEBUG] Page {page_number}: no product cards found, stopping.")
        break

    page_links = []
    page_names = []
    for card in cards:
        link_el = card.select_one("h3.card-title a[href]")
        raw_name = (card.get("data-name") or "").strip()
        if not link_el or not raw_name:
            continue
        link = link_el["href"].strip()
        name = raw_name.split("'")[0].split("(")[0].strip()
        if not link or not name:
            continue
        page_links.append(link)
        page_names.append(name)
        all_links.append(link)
        all_names.append(name)
        if name in scientific_name_set:
            if DEBUG:
                print(f"[DEBUG] Match on page {page_number}: {name}")
            matches_list.append(name)
            match_urls_list.append(link)

    if DEBUG:
        print(f"[DEBUG] Page {page_number}: links={len(page_links)}, names={len(page_names)}")
        print(f"[DEBUG] Page {page_number}: sample names={page_names[:5]}")

    page_number += 1



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

