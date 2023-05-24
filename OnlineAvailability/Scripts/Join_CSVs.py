import pandas as pd
from Helpers import get_sheet_data,write_df_to_sheet
import gspread
import time

#Availability

gc = gspread.service_account()
sh = gc.open("All_Online_Scraped_Data")
worksheet_list = sh.worksheets()

for STATE in ["AL","PA"]:
    
    full_df = None

    for worksheet in worksheet_list:

        if STATE not in worksheet.title:
            continue

        df = get_sheet_data("All_Online_Scraped_Data",worksheet.title)
        df = df.drop_duplicates(subset="Scientific Name",keep="first")

        if full_df is None:
            full_df = df
        
        else:

            full_df = pd.concat([full_df,df])


    full_df.rename({"USDA Symbol":"USDA","URL":"Web"},axis=1,inplace=True)
    full_df = full_df[["USDA","Scientific Name","Root","Web"]]

    write_df_to_sheet("ONLINE",STATE,full_df)

    time.sleep(30)

















      
    



    