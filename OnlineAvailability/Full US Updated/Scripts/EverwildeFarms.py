import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)
ser = Service("C:\Program Files (x86)\chromedriver.exe")

from Helpers import get_sheet_data,write_df_to_sheet



era = get_sheet_data("ERAFull","ERAFull")
common_names = era["Common Name"].to_list()
scientific_names = era["Scientific Name"].to_list()

driver = webdriver.Chrome(service=ser, options=options)


matches_list = []
match_urls_list = []


home_page = "https://www.everwilde.com/Southeast-Wildflower-Seeds.html"

driver.get(home_page)


# #Scroll to the bottom of the page
last_height = driver.execute_script("return document.body.scrollHeight")

while True:

    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(3)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break

    else:
        last_height = new_height


link_elements = driver.find_elements(By.CSS_SELECTOR,"ul li h2 a")
names = [link_element.find_element(By.CLASS_NAME,"type").text for link_element in link_elements]

for link,name in list(zip(link_elements,names)):
    if name in scientific_names:
        match_urls_list.append(link.get_attribute("href"))
        matches_list.append(name)


era = era[["USDA Symbol","Scientific Name"]]
matches_df = pd.DataFrame({"Scientific Name":matches_list,"Root":["Everwilde.com"]*(len(matches_list)),"URL": match_urls_list})

#Matches Df
final = pd.merge(matches_df,era,on="Scientific Name",how="left")
final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)
final = final[["USDA","Scientific Name","Root","URL"]]
final = final.drop_duplicates(subset="Scientific Name",keep="first")
final.to_csv("Test.csv")
write_df_to_sheet("All_Online_Scraped_Data_Full","EverwildeFarms",final)