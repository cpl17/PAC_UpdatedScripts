import requests 
import pandas as pd
from datetime import datetime
from pathlib import Path
import argparse

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


#Get the list of all available plants by scientific name
response = requests.get("https://www.toadshade.com/SpeciesList.html")
table = pd.read_html(response.text)
availability = table[3].loc[:,1].str.lower().to_list()
if DEBUG:
    print(f"[DEBUG] Availability rows={len(availability)}")


#For each name in the db, check if its in the availability list
for scientific_name in scientific_names:

    if scientific_name.lower() in availability:


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

