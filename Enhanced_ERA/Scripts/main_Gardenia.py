import pandas as pd
import numpy as np
import time
import winsound


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from Helpers import get_sheet_data,write_df_to_sheet

options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)
ser = Service("C:\Program Files (x86)\chromedriver.exe")



STATE = "AL"

source_data = get_sheet_data("ERA",STATE)
names = source_data["Scientific Name"].apply(lambda x: "-".join(x.split(" ")))


full_df = None
dfs = []
list_of_unique_columns = []


driver = webdriver.Chrome(service=ser, options=options)

for name in names:


    driver.get(f"https://www.gardenia.net/plant/{name}")
    source = driver.page_source

    #Some pages don't exist but still return 200
    try:
        tables = pd.read_html(source)
    except ValueError:
        continue

    #The table is 2xm, first column are the plant characteristics names, the second are the values
    print(name)

    plant_df = tables[0].set_index(0).T
    plant_df.index = [name.replace("-"," ")]


    dfs.append(plant_df)


    for column in plant_df.columns:
        if column not in list_of_unique_columns:
            list_of_unique_columns.append(column)

    time.sleep(1)

print("here")

driver.close()



for df in dfs:
    #This is done by default when join in pd.concat()
    for name in list(set(list_of_unique_columns).difference(df.columns)):
        df[name] = np.NaN
        df.reindex(list_of_unique_columns,axis=1)

full_df = pd.concat(dfs).reset_index()


write_df_to_sheet("All_Scraped_Data_Original",f"Gardenia_{STATE}",full_df)

winsound.Beep(440,10000)

