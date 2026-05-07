import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

from Helpers import get_sheet_data,write_df_to_sheet

DEBUG = True
WRITE_TO_SHEET = True
SCRIPT_NAME = "AmandasNursery"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()
scientific_name_set = set(scientific_names)


matches_list = []
match_urls_list = []
all_names = []
all_urls = []
skipped_items = 0

for num in range(1,5):
    
    url = f"https://www.amandasnativeplants.com/onlinestore?page={num}"


    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select('li[data-hook="product-list-grid-item"]')
    links = []
    names = []

    for item in items:
        anchor = item.select_one('a[data-hook="product-item-container"]')
        if not anchor or "href" not in getattr(anchor, "attrs", {}):
            anchor = item.select_one('a[href*="product-page"]')
        title_el = item.select_one('[data-hook="product-item-name"]')
        raw_title = ""
        if title_el:
            raw_title = title_el.get_text(strip=True)
        else:
            root = item.select_one('[data-hook="product-item-root"]')
            lbl = (root.get("aria-label") or "") if root else ""
            if lbl.endswith(" gallery"):
                lbl = lbl[: -len(" gallery")].strip()
            raw_title = lbl
            if not raw_title:
                legacy = item.select_one("div a div div div h3")
                if legacy:
                    raw_title = legacy.get_text(strip=True)

        if not anchor or "href" not in anchor.attrs or not raw_title:
            skipped_items += 1
            continue
        links.append(anchor["href"])
        names.append(raw_title.split(" - ")[0].strip())

    all_names.extend(names)
    all_urls.extend(links)

    if DEBUG:
        print(f"[DEBUG] Page {num}: raw items={len(items)}, parsed={len(names)}, skipped={skipped_items}")
        print(f"[DEBUG] Page {num}: sample names={names[:5]}")

    for link,name in list(zip(links,names)):
        if name in scientific_name_set:
            match_urls_list.append(link)
            matches_list.append(name)


era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["AmandasNativePlants.com"]*(len(matches_list)),"URL": match_urls_list})
raw_df = pd.DataFrame({"Scientific Name": all_names, "URL": all_urls})

#Matches Df
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")

if DEBUG:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[DEBUG] Total parsed rows={len(raw_df)}, unique parsed names={raw_df['Scientific Name'].nunique()}")
    print(f"[DEBUG] Matched rows before dedupe={len(matches_df)}, final rows={len(final)}")
    print(f"[DEBUG] Total skipped malformed items={skipped_items}")
    raw_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_raw_{timestamp}.csv", index=False)
    matches_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_matches_pre_dedupe_{timestamp}.csv", index=False)
    final.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_final_{timestamp}.csv", index=False)
    print(f"[DEBUG] Wrote debug CSV snapshots to {DEBUG_DIR}")

if WRITE_TO_SHEET:
    write_df_to_sheet("All_Online_Scraped_Data_Full","AmandasNursery",final)