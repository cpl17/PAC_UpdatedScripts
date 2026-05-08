import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import argparse

from Helpers import get_sheet_data, write_df_to_sheet

def parse_args():
    parser = argparse.ArgumentParser(description="Run Izel scraper.")
    parser.add_argument("--debug", dest="debug", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--write-to-sheet", dest="write_to_sheet", action=argparse.BooleanOptionalAction, default=False)
    return parser.parse_args()


_ARGS = parse_args()
DEBUG = _ARGS.debug
WRITE_TO_SHEET = _ARGS.write_to_sheet
SCRIPT_NAME = "Izel"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

era = get_sheet_data("ERAFull", "ERAFull")
era["Scientific Name"] = era["Scientific Name"].astype(str).str.strip()
scientific_name_set = set(era["Scientific Name"])

matches_list = []
match_urls_list = []
all_names = []
all_links = []

page_number = 1
while True:
    page_url = f"https://www.izelplants.com/all-plants/?p={page_number}&product_list_limit=128"
    response = requests.get(page_url, headers=headers, timeout=60)

    if response.status_code == 404:
        if DEBUG:
            print(f"[DEBUG] Page {page_number}: received 404, stopping pagination.")
        break

    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    link_elements = soup.select("a.product-item-link")

    if not link_elements:
        if DEBUG:
            print(f"[DEBUG] Page {page_number}: no product links found, stopping.")
        break

    page_names = []
    page_links = []
    for link in link_elements:
        href = link.get("href")
        name = link.get_text(strip=True)
        if not href or not name:
            continue
        page_links.append(href)
        page_names.append(name)

    if DEBUG:
        print(f"[DEBUG] Page {page_number}: found {len(page_links)} product links")

    for name, href in zip(page_names, page_links):
        all_names.append(name)
        all_links.append(href)
        if name in scientific_name_set:
            if DEBUG:
                print(f"[DEBUG] Match on page {page_number}: {name}")
            matches_list.append(name)
            match_urls_list.append(href)

    page_number += 1

era = era[["USDA Symbol", "Scientific Name"]]
matches_df = pd.DataFrame(
    {"Scientific Name": matches_list, "Root": ["IzelPlants.com"] * len(matches_list), "URL": match_urls_list}
)
raw_df = pd.DataFrame({"Scientific Name": all_names, "URL": all_links})

final = pd.merge(matches_df, era, on="Scientific Name", how="left")
final.rename({"USDA Symbol": "USDA"}, axis=1, inplace=True)
final = final[["USDA", "Scientific Name", "Root", "URL"]]
final = final.drop_duplicates(subset="Scientific Name", keep="first")

if DEBUG:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[DEBUG] Raw rows={len(raw_df)}, matches pre-dedupe={len(matches_df)}, final rows={len(final)}")
    raw_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_raw_{timestamp}.csv", index=False)
    matches_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_matches_pre_dedupe_{timestamp}.csv", index=False)
    final.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_final_{timestamp}.csv", index=False)
    print(f"[DEBUG] Wrote debug CSV snapshots to {DEBUG_DIR}")

if WRITE_TO_SHEET:
    if len(final) == 0:
        print("[DEBUG] Skipping sheet write: final dataframe is empty.")
    else:
        try:
            write_df_to_sheet("All_Online_Scraped_Data_Full", "IzelPlants", final)
        except Exception as exc:
            print(f"[DEBUG] Sheet write failed for tab 'IzelPlants': {exc}")

#Full Inventory 
# full_inventory_df = pd.DataFrame({"Scientific Name":all_names,"Root":["IzelPlants.com"]*(len(all_names)),"URL":all_links})
# final = pd.merge(full_inventory_df,era,on="Scientific Name",how="left")
# final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
# final = final[["USDA","Scientific Name","Root","URL"]]
# final = final.drop_duplicates(subset="Scientific Name",keep="first")
# write_df_to_sheet("All_Online_Scraped_Data_Full",f"Izel_FullInventory",final)

    


