
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from selenium.common.exceptions import TimeoutException

from Helpers import get_sheet_data,write_df_to_sheet

import winsound


options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)
ser = Service("C:\Program Files (x86)\chromedriver.exe")

STATE = "PA"

source_data = get_sheet_data("ERA",STATE)

#Search Results is a csv download from the site that has a symbol for each plant on the site
temp = get_sheet_data("SearchResults","SearchResults")
symbols_in_USDA = temp["Accepted Symbol"]
symbols = source_data["USDA Symbol"]
symbols_in_both = symbols[symbols.isin(symbols_in_USDA)]



# Scrape All
list_of_dfs = []
errors = []


driver = webdriver.Chrome(service=ser, options=options)
wait = WebDriverWait(driver, 3)

for symbol in symbols_in_both:

    

    
    print(symbol)

    
    driver.get(f"https://plants.usda.gov/home/plantProfile?symbol={symbol}")

    time.sleep(10)

    try:
        wait.until(EC.presence_of_element_located(((By.ID,"characteristics"))))  

    except TimeoutException:
        errors.append(symbol)
        continue



    charactersitics_div = driver.find_element(By.ID,"characteristics")
   
    source = charactersitics_div.get_attribute("innerHTML")

    
    try:
        table = pd.read_html(source)[0]
    
    except:
        errors.append(symbol)
        continue
  

    table.columns = ["Column","Value"]

    group_index = (table["Column"]==table["Value"])
    table = table[~group_index]

    table.set_index("Column",inplace=True)
    table = table.T
    table.index = [symbol]
    table.columns.names = [None]

    list_of_dfs.append(table)

    print(errors)




full_df = pd.concat(list_of_dfs).reset_index()
mapping = source_data[["USDA Symbol","Scientific Name"]].set_index("USDA Symbol").to_dict()
full_df["index"] = full_df['index'].map(mapping["Scientific Name"])

write_df_to_sheet("All_Scraped_Data_Original",f"USDAPlants_{STATE}",full_df)

winsound(400,10000)
