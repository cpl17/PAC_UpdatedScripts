import pandas as pd
import time
from datetime import datetime
from pathlib import Path
import argparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import re

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

def clean_text(full_text):
        
    pattern = r'\((.*?)\)'
    match = re.search(pattern, full_text)


    # Checking if a match is found
    if match:
        return match.group(1)
    else:
        return 

era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()
scientific_name_set = set(scientific_names)



matches_list = []
match_urls_list = []
all_names_seen = []



for page_num in range(1,16):

    url = f"https://southernseedexchange.com/collections/flower-seeds?page={page_num}"

    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract links and names using CSS selectors (links not working)
    # all_links = [link['href'] for link in soup.select('a.product-link')]
    all_names = [clean_text(name.text) for name in soup.select('.product-block__title')]
    all_names_seen.extend([name for name in all_names if name])
    if DEBUG:
        print(f"[DEBUG] Page {page_num}: parsed names={len(all_names)}")

    # for link,name in list(zip(all_links,all_names)):
    #     if name in scientific_names:
    #         match_urls_list.append(link)
    #         matches_list.append(name)

    for name in all_names:
        if name in scientific_name_set:
            matches_list.append(name)



era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["SouthernSeedExchange.com"]*(len(matches_list)),"URL":["southernseedexchange.com/collections/flower-seeds"]*(len(matches_list))})
raw_df = pd.DataFrame({"Scientific Name": all_names_seen})

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
