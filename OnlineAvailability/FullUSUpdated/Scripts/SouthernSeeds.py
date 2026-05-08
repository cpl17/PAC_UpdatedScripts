import pandas as pd
from datetime import datetime
from pathlib import Path
import argparse
import requests
from bs4 import BeautifulSoup


from Helpers import get_sheet_data,write_df_to_sheet

def parse_args():
    parser = argparse.ArgumentParser(description="Run SouthernSeeds scraper.")
    parser.add_argument("--debug", dest="debug", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--write-to-sheet", dest="write_to_sheet", action=argparse.BooleanOptionalAction, default=False)
    return parser.parse_args()


_ARGS = parse_args()
DEBUG = _ARGS.debug
WRITE_TO_SHEET = _ARGS.write_to_sheet
SCRIPT_NAME = "SouthernSeeds"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

def extract_scientific_from_href(href: str, scientific_slug_to_name: dict):
    if not href:
        return None
    href_lower = href.lower()
    for slug, sci_name in scientific_slug_to_name.items():
        if slug in href_lower:
            return sci_name
    return None

era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()
scientific_name_set = set(scientific_names)
scientific_slug_to_name = {
    name.lower().replace(" ", "-"): name
    for name in scientific_name_set
}



matches_list = []
match_urls_list = []
all_names_seen = []
all_links_seen = []



for page_num in range(1,50):

    url = f"https://southernseedexchange.com/collections/flower-seeds?page={page_num}"

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    product_cards = soup.select(".product-block[data-product-id]")
    if not product_cards:
        if DEBUG:
            print(f"[DEBUG] Page {page_num}: no product cards found, stopping pagination.")
        break

    page_matches = 0
    page_raw = 0
    for card in product_cards:
        link_el = card.select_one("a.product-link[href*='/products/']")
        title_el = card.select_one(".product-block__title")
        if not link_el:
            continue
        href = link_el.get("href", "").strip()
        if not href:
            continue
        if href.startswith("/"):
            href = f"https://southernseedexchange.com{href}"
        page_raw += 1
        all_links_seen.append(href)
        if title_el:
            all_names_seen.append(title_el.get_text(" ", strip=True))

        scientific_name = extract_scientific_from_href(href, scientific_slug_to_name)
        if scientific_name and scientific_name in scientific_name_set:
            matches_list.append(scientific_name)
            match_urls_list.append(href)
            page_matches += 1

    if DEBUG:
        print(f"[DEBUG] Page {page_num}: parsed products={page_raw}, page matches={page_matches}")



era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["SouthernSeedExchange.com"]*(len(matches_list)),"URL":match_urls_list})
raw_df = pd.DataFrame({"Listing Title": all_names_seen, "URL": all_links_seen})

#Matches Df
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")

if DEBUG:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[DEBUG] Raw names={len(raw_df)}, matches pre-dedupe={len(matches_df)}, final rows={len(final)}")
    raw_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_raw_{timestamp}.csv", index=False)
    matches_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_matches_pre_dedupe_{timestamp}.csv", index=False)
    final.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_final_{timestamp}.csv", index=False)
    print(f"[DEBUG] Wrote debug CSV snapshots to {DEBUG_DIR}")

if WRITE_TO_SHEET:
    write_df_to_sheet("All_Online_Scraped_Data_Full","SouthernSeedExchange",final)
