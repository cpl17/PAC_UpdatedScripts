import requests 
import pandas as pd
from datetime import datetime
from pathlib import Path
import argparse
from bs4 import BeautifulSoup

from Helpers import get_sheet_data,write_df_to_sheet

def parse_args():
    parser = argparse.ArgumentParser(description="Run ToadShade scraper.")
    parser.add_argument("--debug", dest="debug", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--write-to-sheet", dest="write_to_sheet", action=argparse.BooleanOptionalAction, default=False)
    return parser.parse_args()


_ARGS = parse_args()
DEBUG = _ARGS.debug
WRITE_TO_SHEET = _ARGS.write_to_sheet
SCRIPT_NAME = "ToadShade"
DEBUG_DIR = Path(__file__).resolve().parents[1] / "DebugOutput" / SCRIPT_NAME
DEBUG_DIR.mkdir(parents=True, exist_ok=True)


era = get_sheet_data("ERAFull","ERAFull")
scientific_names = era["Scientific Name"].to_list()

matches_list = []
match_urls_list = []


def normalize_scientific_name(name: str):
    name = (name or "").strip()
    parts = name.split()
    if len(parts) < 2:
        return None
    return f"{parts[0]} {parts[1]}"


# Get the list of all available plants by scientific name from species table rows.
response = requests.get("https://www.toadshade.com/SpeciesList.html", timeout=60)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

availability = set()
href_by_name = {}
for row in soup.select("tr"):
    i_tags = row.select("td i")
    if not i_tags:
        continue
    # The first italicized token pair is the scientific binomial.
    first_i_text = i_tags[0].get_text(" ", strip=True)
    sci_name = normalize_scientific_name(first_i_text)
    if not sci_name:
        continue
    availability.add(sci_name.lower())
    link_el = row.select_one("td a[href$='.html']")
    if link_el and link_el.get("href"):
        href = link_el.get("href").strip()
        if href.startswith("http"):
            href_by_name[sci_name] = href
        else:
            href_by_name[sci_name] = f"https://www.toadshade.com/{href}"

if DEBUG:
    print(f"[DEBUG] Availability rows={len(availability)}")


#For each name in the db, check if its in the availability list
for scientific_name in scientific_names:

    if scientific_name.lower() in availability:


        full_url = href_by_name.get(scientific_name)
        if not full_url:
            namelist = scientific_name.split()
            namelist[0] = namelist[0].title()
            full_url = f"https://www.toadshade.com/{'-'.join(namelist)}.html"

        #Store matches
        match_urls_list.append(full_url)
        matches_list.append(scientific_name)
        


#Wrangle data
era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["ToadShade.com"]*(len(matches_list)),"URL":match_urls_list})
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")


if DEBUG:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[DEBUG] Matches pre-dedupe={len(matches_df)}, final rows={len(final)}")
    matches_df.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_matches_pre_dedupe_{timestamp}.csv", index=False)
    final.to_csv(DEBUG_DIR / f"{SCRIPT_NAME}_final_{timestamp}.csv", index=False)
    print(f"[DEBUG] Wrote debug CSV snapshots to {DEBUG_DIR}")

if WRITE_TO_SHEET:
    write_df_to_sheet("All_Online_Scraped_Data_Full","ToadShade",final)

