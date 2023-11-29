# # Imports and Data
import pandas as pd
from Helpers import get_sheet_data,write_df_to_sheet



source_data = get_sheet_data("ERAFull","ERAFull")


resource_column_pairs = [
    ("Gardenia",["Plant Type","Exposure","Height","Characteristics","Attracts"]),
    ("MissouriBotanical",["Sun", "Water","Flower","Fruit","Attracts","Bloom Time","Type","Height","Bloom Description"]),
    ("NCSU",["Life Cycle","Plant Type","Attracts","Dimensions","Flower Value To Gardener","Light"]),
    ("USDAPlants",["Height, Mature (feet)","Flower Color"]),
    ("Wildflower",["Bloom Time","Bloom Color","Soil Moisture","Duration","Habit","Light Requirement","Larval Host"]),
    ("NewMoon",["Height","Bloom Color","Exposure","Flowering Months","Soil Moisture Preference"])

]




for resource,columns in resource_column_pairs:


    # # Summaries
    data = get_sheet_data("All_Scraped_Data_Original_Full",f"{resource}")
    data.drop("index",axis=1,inplace=True)
    if "common name" in data.columns:
        data.drop("common name",axis=1,inplace=True)
    print(data.columns)


    #Unique values top level
    full_df = None

    for col in data:
        df = data[col].value_counts().reset_index()
        df.columns = [df.columns[1],"Count"]
        if full_df is not None:
            full_df = pd.concat([full_df,df],axis=1)
        else:
            full_df = df
    print(f"{resource}_TopLevel")
    write_df_to_sheet("UniqueValues_Full",f"{resource}_TopLevel",full_df)


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
    for col in data[columns]:
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

    write_df_to_sheet("UniqueValues_Full",f"{resource}",df)

