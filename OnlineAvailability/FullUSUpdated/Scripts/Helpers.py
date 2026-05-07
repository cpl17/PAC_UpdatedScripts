import pandas as pd


import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe

def get_sheet_data(GSHEET_NAME,TAB_NAME):
    gc = gspread.service_account(filename="service_account.json")
    sh = gc.open(GSHEET_NAME)
    worksheet = sh.worksheet(TAB_NAME)
    df = pd.DataFrame(worksheet.get_all_records())
    return df


def write_df_to_sheet(GSHEET_NAME,TAB_NAME,df):
    gc = gspread.service_account(filename="service_account.json")
    sh = gc.open(GSHEET_NAME)
    worksheet = sh.worksheet(TAB_NAME)
    set_with_dataframe(worksheet, df)




