import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import argparse

from Helpers import get_sheet_data,write_df_to_sheet

def parse_args():
    parser = argparse.ArgumentParser(description="Run WesternNative scraper.")
    parser.add_argument("--debug", dest="debug", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--write-to-sheet", dest="write_to_sheet", action=argparse.BooleanOptionalAction, default=False)
    return parser.parse_args()


_ARGS = parse_args()
DEBUG = _ARGS.debug
WRITE_TO_SHEET = _ARGS.write_to_sheet
SCRIPT_NAME = "WesternNative"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()
scientific_name_set = set(scientific_names)


matches_list = []
match_urls_list = []
all_names = []
all_urls = []


urls = [
    "https://www.westernnativeseed.com/wildflowers.html",
    "https://new.westernnativeseed.com/grasses/",
    "https://www.westernnativeseed.com/trees.html",
]


for url in urls:

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    product_cards = soup.select("li.product")
    links = []
    names = []
    for card in product_cards:
        link_el = card.select_one("a.woocommerce-LoopProduct-link")
        name_el = card.select_one("h2.woocommerce-loop-product__title")
        if not link_el or not name_el:
            continue
        href = (link_el.get("href") or "").strip()
        name = name_el.get_text(" ", strip=True)
        if not href or not name:
            continue
        links.append(href)
        names.append(name)

    all_names.extend(names)
    all_urls.extend(links)

    if DEBUG:
        print(f"[DEBUG] URL: {url}")
        print(f"[DEBUG] Parsed rows: {len(names)}")
        print(f"[DEBUG] Sample names: {names[:5]}")

    for link,name in list(zip(links,names)):
        if name in scientific_name_set:
            match_urls_list.append(link)
            matches_list.append(name)



era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["WesternNativeSeed.com"]*(len(matches_list)),"URL": match_urls_list})
raw_df = pd.DataFrame({"Scientific Name": all_names, "URL": all_urls})

if DEBUG:
    print(f"[DEBUG] Raw scraped rows: {len(raw_df)}")
    print(f"[DEBUG] Raw unique names: {raw_df['Scientific Name'].nunique()}")
    print(f"[DEBUG] Matched rows (pre-dedupe): {len(matches_df)}")
    print(f"[DEBUG] Matched unique names (pre-dedupe): {matches_df['Scientific Name'].nunique()}")
    print(f"[DEBUG] ERA unique scientific names: {era['Scientific Name'].nunique()}")

#Matches Df
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")

if DEBUG:
    print(f"[DEBUG] Final output rows (post-dedupe): {len(final)}")
    print(f"[DEBUG] Final unique USDA symbols: {final['USDA'].nunique(dropna=True)}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_raw_{timestamp}.csv", index=False)
    matches_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_matches_pre_dedupe_{timestamp}.csv", index=False)
    final.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_final_{timestamp}.csv", index=False)
    print(f"[DEBUG] Wrote debug CSV snapshots to {DEBUG_DIR}")

if WRITE_TO_SHEET:
    write_df_to_sheet("All_Online_Scraped_Data_Full","WesternNativeSeed",final)
    if DEBUG:
        print("[DEBUG] Wrote final dataframe to Google Sheet tab WesternNativeSeed")