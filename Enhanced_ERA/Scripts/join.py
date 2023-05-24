
import pandas as pd
import numpy as np
import gspread
from  Helpers import get_sheet_data,write_df_to_sheet


STATE = "AL"
CURRENT_VERSION_DATE = "12_21"

era_reduced = get_sheet_data("ERA", f"{STATE}_Reduced").set_index("Scientific Name")
era = get_sheet_data("ERA", f"{STATE}").set_index("Scientific Name")
era_cnp = get_sheet_data(f"CNP AL Database {CURRENT_VERSION_DATE}","ERA_AL")


#na's being written as "", replace as np.nan
for column in era_reduced.columns:
    era_reduced[column]= era_reduced[column].apply(lambda x: np.nan if x == "" else x)


print(era_reduced.head())



source_dict = era_reduced.to_dict()


print(era_reduced.isna().sum())
print("Total Missing: ",era_reduced.isna().sum().sum())

gc = gspread.service_account()
sh = gc.open("All_Scraped_Data_Cleaned")
worksheet_list = sh.worksheets()

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

    updated_df = pd.DataFrame(source_dict)
    
    print(f"After Updating: {str(df.columns.to_list())}" + " using " + worksheet.title)
    print("Total Missing: ",updated_df.isna().sum().sum())

    print(updated_df.isna().sum())

write_df_to_sheet("ERA_Updated_Data",f"{STATE}_Reduced",updated_df.reset_index())


era_cnp[updated_df.columns.to_list()] = updated_df.values
write_df_to_sheet("ERA_Updated_Data",f"{STATE}_CNP",era_cnp)














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

#     updated_df = pd.DataFrame(source_dict)
    
#     print(f"After Updating: {str(df.columns.to_list())}" + " using " + worksheet.title)
#     print("Total Missing: ",updated_df.isna().sum().sum())

#     print(updated_df.isna().sum())

# write_df_to_sheet("ERA_Updated_Data",f"{STATE}_Reduced",updated_df.reset_index())


# era_pa_cnp[updated_df.columns.to_list()] = updated_df.values
# write_df_to_sheet("ERA_Updated_Data",f"{STATE}_CNP",era_pa_cnp)


















