import pandas as pd
import numpy as np
import gspread


from  Helpers import get_sheet_data,write_df_to_sheet

def number_to_excel_column(num):
    """
    Converts a number to an Excel column name.
    """
    if num <= 0:
        raise ValueError("Number must be greater than 0.")

    column_name = ""
    while num > 0:
        remainder = (num - 1) % 26
        column_name = chr(65 + remainder) + column_name
        num = (num - 1) // 26

    return column_name


STATE = "AL"
CURRENT_VERSION_DATE = "12_21"

era_reduced = get_sheet_data("ERA", f"{STATE}_Reduced").set_index("Scientific Name") #ERA - Only contains to be updated columns
era = get_sheet_data("ERA", f"{STATE}").set_index("Scientific Name") #Full Original ERA
era_cnp = get_sheet_data(f"CNP AL Database {CURRENT_VERSION_DATE}","ERA_AL") #Enhanced ERA 


#na's being written as "", replace as np.nan
for column in era_reduced.columns:
    era_reduced[column]= era_reduced[column].apply(lambda x: np.nan if x == "" else x)


print(era_reduced.head())



source_dict = era_reduced.to_dict()


print(era_reduced.isna().sum())
print("Total Missing: ",era_reduced.isna().sum().sum())

#Grab the Google Sheet with the scraped data from each source
gc = gspread.service_account()
sh = gc.open("All_Scraped_Data_Cleaned")
worksheet_list = sh.worksheets()


#Iteratively update ERA Reduced 
#For each column, for each plant if missing in era and present in worksheet -> update value. Else, continue
for worksheet in worksheet_list:

    if STATE not in worksheet.title:
        continue

    print(worksheet.title)

    df = get_sheet_data("All_Scraped_Data_Cleaned",worksheet.title)
    df.set_index("index",inplace=True)

    df_dict = df.to_dict()

    for col in df.columns:

        for name in era_reduced.index:

            if source_dict[col][name] is np.nan:
                if (name in df.index) and (df_dict[col][name] is not np.nan):
                
                    source_dict[col][name] = df_dict[col][name]

    era_reduced_updated = pd.DataFrame(source_dict)

    for col in era_reduced_updated.columns:
        era_reduced_updated[col] = era_reduced_updated[col].replace({" – ","–"})
    
    print(f"After Updating: {str(df.columns.to_list())}" + " using " + worksheet.title)
    print("Total Missing: ",era_reduced_updated.isna().sum().sum()) #Innacurate for Wildflower for some reason

    print(era_reduced_updated.isna().sum())

#Write updated data 
write_df_to_sheet("ERA_Updated_Data",f"{STATE}_Reduced",era_reduced_updated.reset_index())

################

number_of_rows = era_reduced_updated.shape[0] + 1

list_of_excel_headers = [number_to_excel_column(num_index) for num_index in [era_cnp.columns.get_loc(col) + 1 for col in era_reduced_updated.columns]]

gc = gspread.service_account()
sh = gc.open("CNP AL Database 12_21")
worksheet = sh.worksheet("ERA_AL")

era_reduced_updated = era_reduced_updated.fillna("") #To solve: Out of range float values are not JSON compliant
print(era_reduced_updated.head())
for header,column in zip(list_of_excel_headers,era_reduced_updated.columns):
    new_data = [column]
    new_data.extend(era_reduced_updated[column].to_list())
    worksheet.update(f"{header}1:{header + str(number_of_rows)}", [[cell_value] for cell_value in new_data])



#TODO: Determine correct workflow for this  



# STATE = "PA"

# era_pa_reduced = get_sheet_data("CNP SOURCE 5_22", "ERA_PA").set_index("Scientific Name")[era_reduced.columns]
# era_pa = get_sheet_data("CNP SOURCE 5_22", "ERA_PA").set_index("Scientific Name")[era.columns]
# era_pa_cnp = get_sheet_data("CNP SOURCE 5_22", "ERA_PA").set_index("Scientific Name")

# #na's being written as "", replace as np.nan
# for column in era_pa_reduced.columns:
#     era_pa_reduced[column]= era_pa_reduced[column].apply(lambda x: np.nan if x == "" else x)


# print(era_pa_reduced.head())



# source_dict = era_pa_reduced.to_dict()


# print(era_pa_reduced.isna().sum())
# print("Total Missing: ",era_pa_reduced.isna().sum().sum())

# gc = gspread.service_account()
# sh = gc.open("All_Scraped_Data_Cleaned")
# worksheet_list = sh.worksheets()

# for worksheet in worksheet_list:

    

#     if STATE not in worksheet.title:
#         continue

#     print(worksheet.title)

#     df = get_sheet_data("All_Scraped_Data_Cleaned",worksheet.title)
#     df.set_index("index",inplace=True)


#     df_dict = df.to_dict()

#     for col in df.columns:

#         for name in era_pa_reduced.index:

#             if source_dict[col][name] is np.nan:
#                 if (name in df.index) and (df_dict[col][name] is not np.nan):
                
#                     source_dict[col][name] = df_dict[col][name]

#     era_reduced_updated = pd.DataFrame(source_dict)
    
#     print(f"After Updating: {str(df.columns.to_list())}" + " using " + worksheet.title)
#     print("Total Missing: ",era_reduced_updated.isna().sum().sum())

#     print(era_reduced_updated.isna().sum())

# write_df_to_sheet("ERA_Updated_Data",f"{STATE}_Reduced",era_reduced_updated.reset_index())


# era_pa_cnp[era_reduced_updated.columns.to_list()] = era_reduced_updated.values
# write_df_to_sheet("ERA_Updated_Data",f"{STATE}_CNP",era_pa_cnp)


















