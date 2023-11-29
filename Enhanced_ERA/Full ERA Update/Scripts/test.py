# # Summaries
# # Imports and Data
import pandas as pd
from Helpers import get_sheet_data,write_df_to_sheet


data = get_sheet_data("All_Scraped_Data_Cleaned_Full","Wildflower")
data.drop(["index"],axis=1)

#Unique values top level
full_df = None

for col in data:
    df = data[col].value_counts().reset_index()
    df.columns = [df.columns[1],"Count"]
    if full_df is not None:
        full_df = pd.concat([full_df,df],axis=1)
    else:
        full_df = df
full_df.to_csv("test1.csv")

#Unique values bottom level on relevant columns ("Brown, Blue","Brown, Black" --> ["Brown","Blue","Black"])
def get_unique_values(df, column_name):
    unique_values = []
    for cell_value in df[column_name]:
        if isinstance(cell_value,float):
            continue   
        values = ",".join(str(cell_value).split("|")).split(",")
        for value in values:
            if value not in unique_values:
                unique_values.append(value)
    return unique_values


_ = {}
for col in data.columns:
    _[col] = get_unique_values(data,col)

max_length = 0
for key in _:
    if len(_[key]) > max_length:
        max_length = len(_[key])

for key in _:
    number_of_pads = max_length - len(_[key])
    _[key] += [""]*number_of_pads

df = pd.DataFrame(_)
for col in df:
    df[col] = df[col].apply(lambda x: x.strip().title() if not isinstance(x,float) else x).drop_duplicates()

df.to_csv("test2.csv")