import pandas as pd
from Helpers import get_sheet_data,write_df_to_sheet




#Note: The inexplicable USDA back and forth is to keep with the naming conventions for each sheet
#Likely does not matter
data = get_sheet_data("ONLINE_Full","ONLINE_Full")
data.rename({"USDA":"USDA Symbol"},axis=1,inplace=True)

metadata = get_sheet_data("ERAFull","ERAFull")


f = lambda x: ', '.join(map(str, set(x)))
online_agg = data.groupby("USDA Symbol").agg({"Root":[f,len],"Web":f})

online_agg.reset_index(inplace=True)
online_agg.columns = ["USDA Symbol","Root","Count","Web"]

metadata = metadata[["USDA Symbol","Scientific Name","Common Name"]]
metadata.columns = ["USDA Symbol","Scientific Name","Common Name"]

final = online_agg.merge(metadata,on="USDA Symbol",how="left")
# final["Common Name"] = final["Common Name"].str.title()
final["String"] = [f"{row['Common Name']} ({row['Scientific Name']}): {row['Root']}" for _,row in final.iterrows()]

final.rename({"USDA Symbol":"USDA"},axis=1,inplace=True)

write_df_to_sheet("ONLINE_AGG_Full","ONLINE_AGG_Full",final)