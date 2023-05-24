
# # Imports and Data
import pandas as pd
from bs4 import BeautifulSoup
import requests 
from requests.exceptions import TooManyRedirects
import winsound


import pandas as pd
import requests

from Helpers import get_sheet_data,write_df_to_sheet


STATE = "AL"
BASE_URL = "https://www.wildflower.org/plants/result.php?id_plant="
HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Chrome/87.0.4280.141"}

source_data = get_sheet_data("ERA",STATE)
names = source_data["Scientific Name"]


# Get the names of all the plants on the site 

url = "http://www.newmoonnursery.com/index.cfm/fuseaction/plants.main/alphaKey/ALL/index.htm"

response = requests.get(url = url, headers = HEADERS)
page = response.text 
soup = BeautifulSoup(page,features="lxml")

all_names_on_site = [element.text.strip("\n").strip() for element in soup.select("h3.plantListTitle")]


scientific_names_era = source_data["Scientific Name"].to_list()

scientific_names_url_formatted = []
scientific_names = []

# for name in scientific_names_era:
for name in scientific_names_era:


    if name in all_names_on_site:
        scientific_names_url_formatted.append("-".join(name.split()))
        scientific_names.append(name)       


#Scrape
all_plant_dicts = {}

for name,search_name in list(zip(scientific_names,scientific_names_url_formatted)):

    url = f"http://www.newmoonnursery.com/plant/{search_name}"

    print(url)

    try :
        response = requests.get(url = url, headers = HEADERS)
    except TooManyRedirects:
        continue
    
    page = response.text 
    soup = BeautifulSoup(page)

    plant_dict = {name:{}}

    selector = "div#plantAttributes div.attribute"
    for item in soup.select(selector=selector):
        column,value = item.text.strip("\n").split(": ")
        plant_dict[name][column] = value

    selector = "div.charBlock"
    blocks = soup.select(selector=selector)

    for block in blocks:
        column =  block.select("h4")[0].text
        value = ",".join([list_item.text for list_item in block.select("ul li")])
        plant_dict[name][column] = value

    all_plant_dicts.update(plant_dict)





full_df = pd.DataFrame(all_plant_dicts).T.reset_index()

write_df_to_sheet("All_Scraped_Data_Original",f"NewMoon_{STATE}",full_df)

winsound.Beep(400,10000)

