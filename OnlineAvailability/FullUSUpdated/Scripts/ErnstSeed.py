import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import argparse

from Helpers import get_sheet_data, write_df_to_sheet

def parse_args():
    parser = argparse.ArgumentParser(description="Run ErnstSeed scraper.")
    parser.add_argument("--debug", dest="debug", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--write-to-sheet", dest="write_to_sheet", action=argparse.BooleanOptionalAction, default=False)
    return parser.parse_args()


_ARGS = parse_args()
DEBUG = _ARGS.debug
WRITE_TO_SHEET = _ARGS.write_to_sheet
SCRIPT_NAME = "ErnstSeed"
_REPO_ROOT = Path(__file__).resolve().parents[1]
DEBUG_DIR = _REPO_ROOT / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

BASE_QUERY = "_product_type=individual-species"
PAGE1_URL = f"https://www.ernstseed.com/seed-finder-tool/?{BASE_QUERY}"


def listing_url(page_num: int) -> str:
    if page_num <= 1:
        return PAGE1_URL
    return f"https://www.ernstseed.com/seed-finder-tool/page/{page_num}/?{BASE_QUERY}"


def parse_max_page(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    anchor = soup.select_one(".e-load-more-anchor[data-max-page]")
    if anchor and anchor.get("data-max-page"):
        try:
            return max(1, int(anchor["data-max-page"]))
        except ValueError:
            pass
    return 27


def botanical_to_era_name(botanical_raw: str, scientific_name_set: set):
    """Map tile botanical text to an ERA Scientific Name (exact set membership)."""
    s = re.sub(r"\s+", " ", (botanical_raw or "").strip())
    if not s:
        return None
    candidates = [s]
    if "," in s:
        candidates.append(s.split(",", 1)[0].strip())
    for c in candidates:
        if c in scientific_name_set:
            return c
    return None


def scrape_page(html: str):
    soup = BeautifulSoup(html, "html.parser")
    tiles = soup.select('div[data-elementor-type="loop-item"].product')
    out = []
    skipped_items = 0
    for tile in tiles:
        link_el = tile.select_one('a[href*="/product/"]')
        name_el = tile.select_one("span.elementor-heading-title")
        if not link_el or not link_el.get("href") or not name_el:
            skipped_items += 1
            continue
        botanical_raw = name_el.get_text(strip=True)
        out.append((botanical_raw, link_el["href"].strip()))
    return out, skipped_items


era = get_sheet_data("ERAFull", "ERAFull")
era["Scientific Name"] = era["Scientific Name"].astype(str).str.strip()
scientific_name_set = set(era["Scientific Name"])

matches_list = []
match_urls_list = []
all_names = []
all_links = []

first = requests.get(PAGE1_URL, headers=headers, timeout=60)
first.raise_for_status()
max_page = parse_max_page(first.text)
if DEBUG:
    print(f"[DEBUG] Parsed max_page={max_page} from listing")

pages_to_fetch = list(range(1, max_page + 1))
html_by_page = {1: first.text}
for page_num in pages_to_fetch:
    if page_num == 1:
        html = html_by_page[1]
    else:
        url = listing_url(page_num)
        if DEBUG:
            print(f"[DEBUG] GET {url}")
        r = requests.get(url, headers=headers, timeout=60)
        r.raise_for_status()
        html = r.text

    pairs, skipped_items = scrape_page(html)
    if DEBUG:
        print(f"[DEBUG] Page {page_num}: tiles parsed={len(pairs)}, skipped={skipped_items}")

    for botanical_raw, href in pairs:
        all_links.append(href)
        all_names.append(botanical_raw)
        era_name = botanical_to_era_name(botanical_raw, scientific_name_set)
        if era_name is not None:
            matches_list.append(era_name)
            match_urls_list.append(href)


era = era[["USDA Symbol", "Scientific Name"]]
matches_df = pd.DataFrame(
    {"Scientific Name": matches_list, "Root": ["ErnstSeed.com"] * len(matches_list), "URL": match_urls_list}
)
raw_df = pd.DataFrame({"Scientific Name": all_names, "URL": all_links})

final = pd.merge(matches_df, era, on="Scientific Name", how="left")
final.rename({"USDA Symbol": "USDA"}, axis=1, inplace=True)
final = final[["USDA", "Scientific Name", "Root", "URL"]]
final = final.drop_duplicates(subset="Scientific Name", keep="first")

if DEBUG:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[DEBUG] Raw rows={len(raw_df)}, raw unique names={raw_df['Scientific Name'].nunique()}")
    print(f"[DEBUG] Matches pre-dedupe={len(matches_df)}, final rows={len(final)}")
    raw_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_raw_{timestamp}.csv", index=False)
    matches_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_matches_pre_dedupe_{timestamp}.csv", index=False)
    final.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_final_{timestamp}.csv", index=False)
    print(f"[DEBUG] Wrote debug CSV snapshots to {DEBUG_DIR}")

if WRITE_TO_SHEET:
    write_df_to_sheet("All_Online_Scraped_Data_Full", "ErnstSeed", final)

print("ErnstSeed scrape complete")
