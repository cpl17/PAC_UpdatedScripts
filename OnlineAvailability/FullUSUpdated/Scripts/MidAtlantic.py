import pandas as pd
import requests
import html
from datetime import datetime
from pathlib import Path

DEBUG = True
WRITE_TO_SHEET = True
SCRIPT_NAME = "MidAtlantic"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

from Helpers import get_sheet_data,write_df_to_sheet



era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()
scientific_name_set = set(scientific_names)

matches_list = []
match_urls_list = []
all_names = []
all_links = []


BASE_API = "https://midatlanticnatives.com/wp-json/wp/v2"
CATEGORY_SLUG = "bare-root-native-plants"
PER_PAGE = 100

def get_category_id(slug: str) -> int:
    response = requests.get(
        f"{BASE_API}/product_cat",
        params={"slug": slug, "per_page": 100},
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()
    categories = response.json()
    if not categories:
        raise RuntimeError(f"Could not find product category slug '{slug}'")
    return categories[0]["id"]


def normalize_scientific_name(title_text: str) -> str:
    text = html.unescape((title_text or "").strip())
    # Most product titles are "Genus species, Common name ...".
    before_comma = text.split(",", 1)[0].strip()
    parts = before_comma.split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    return before_comma


category_id = get_category_id(CATEGORY_SLUG)
page_num = 1

while True:
    response = requests.get(
        f"{BASE_API}/product",
        params={"product_cat": category_id, "per_page": PER_PAGE, "page": page_num},
        headers=headers,
        timeout=60,
    )
    # WP REST returns 400 for out-of-range page.
    if response.status_code == 400:
        if DEBUG:
            print(f"[DEBUG] Page {page_num}: no more results (status 400), stopping.")
        break
    response.raise_for_status()
    products = response.json()
    if not products:
        if DEBUG:
            print(f"[DEBUG] Page {page_num}: empty product list, stopping.")
        break

    page_names = []
    page_links = []
    for p in products:
        title_text = p.get("title", {}).get("rendered", "")
        link = p.get("link", "")
        name = normalize_scientific_name(title_text)
        if not name or not link:
            continue
        page_names.append(name)
        page_links.append(link)
        all_names.append(name)
        all_links.append(link)
        if name in scientific_name_set:
            matches_list.append(name)
            match_urls_list.append(link)

    if DEBUG:
        print(f"[DEBUG] Page {page_num}: products={len(products)}, parsed={len(page_names)}")
        print(f"[DEBUG] Page {page_num}: sample names={page_names[:5]}")

    page_num += 1


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


    
