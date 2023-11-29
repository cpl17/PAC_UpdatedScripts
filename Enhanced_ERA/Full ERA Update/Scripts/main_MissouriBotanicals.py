import pandas as pd
import string
import winsound


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By

from Helpers import get_sheet_data,write_df_to_sheet


options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)
ser = Service("C:\Program Files (x86)\chromedriver.exe")



source_data = get_sheet_data("ERAFull","ERAFull")
scientific_names = source_data["Scientific Name"].to_list()

matches = []


driver = webdriver.Chrome(service=ser, options=options)

for letter in string.ascii_uppercase[1:]:
# for letter in ["A"]:

    print(letter)

    driver.get(f"https://www.missouribotanicalgarden.org/PlantFinder/PlantFinderListResults.aspx?letter={letter}")


    outer_div = driver.find_element(By.CLASS_NAME,"p2")
    
    link_elements = outer_div.find_elements(By.CSS_SELECTOR,"div div a")
    names = [el.text.split("'")[0] for el in link_elements]
    links = [el.get_attribute("href") for el in link_elements]
    
    all_name_link_pairs = list(set(list(zip(names,links))))
    all_name_link_pairs.sort()

    for pair in all_name_link_pairs:
        if pair[0] in scientific_names:
            matches.append(pair)

driver.close()



driver = webdriver.Chrome(service=ser, options=options)

all_plant_dicts = {}

for name,link in matches:
# for name,link in matches[:10]:

    print(name)
    driver.get(link)

    row_elements = driver.find_elements(By.CSS_SELECTOR,"div.column-right div.row")
    plant_dict = {name:{}}
    for el in row_elements[:-1]:
        column,value = el.text.split(":")
        plant_dict[name].update({column:value})
    all_plant_dicts.update(plant_dict)


full_df = pd.DataFrame(all_plant_dicts).T.reset_index()
write_df_to_sheet("All_Scraped_Data_Original_Full","MissouriBotanical",full_df)

winsound.Beep(400,5000)
