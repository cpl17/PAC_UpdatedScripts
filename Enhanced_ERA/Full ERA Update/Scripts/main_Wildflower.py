import pandas as pd
from bs4 import BeautifulSoup
import requests 
import re
import numpy as np
from collections import defaultdict
import winsound

from Helpers import get_sheet_data,write_df_to_sheet


BASE_URL = "https://www.wildflower.org/plants/result.php?id_plant="
HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Chrome/87.0.4280.141"
}



#Removes the html tags from the subheader strings picked up by the regex
def clean_subheader_values(string):
    string = str(string).replace("</strong>","").replace("<br/>","")
    new_string = ",".join(string.split(" , ")) #Remove spacing with csv's
    return new_string

#Source Data

source_data = get_sheet_data("ERAFull","ERAFull")



# The pages are organized into sections/headers ("Bloom Infrormtion"), with subheaders ("Bloom Time") and their values ("April-Aug") 
# The subheader values are in <strong> tags. The subheader values are between <strong> and <br/> tags. 
# The output will be a df with rows for each plant and each column corresponding to a subheader within the relevant sections. 


list_of_relevant_sections = ["Plant Characteristics", "Bloom Information", "Growing Conditions", "Benefit","Propagation"]

labeled_plant_dicts = {} #{symbol:{subheader:value}} i.e. ACMI:{Bloom Time: "April",...}
list_of_unique_subheaders = [] #["Bloom Time",....]



for symbol in source_data["USDA Symbol"]:
# for symbol in source_data["USDA Symbol"]:

    print(symbol)

    full_url = BASE_URL + symbol
    response = requests.get(url = full_url, headers = HEADERS)
    soup = BeautifulSoup(response.text,features='lxml')


    all_sections = soup.find_all('div',class_="section")


    named_section_dict = {} #{Plant Characteristics: soup object of all child objects in the section div}
    num_sections = 0

    #Find the relevant sections. If none are relevant, move to next symbol
    for section in all_sections:
        try:
            section_name = section.select_one('h4').text
        except AttributeError: #Symbol Not in DB
            continue

        if section_name in list_of_relevant_sections:
            num_sections += 1
            named_section_dict[section_name] = section
        
    #Symbol in DB but no relevant information
    if num_sections == 0:
        continue


    list_of_section_subheaders = []

    #For each section, identify the subheaders in strong tags
    for section in named_section_dict.keys():
        for subheader in  named_section_dict[section].select('strong'):
            subheader = subheader.text.replace(":","")
            if subheader not in list_of_unique_subheaders:
                list_of_unique_subheaders.append(subheader)
            list_of_section_subheaders.append(subheader)

    list_of_section_values = []

    #For each section identify the subheader values between a strong and br tag. Remove the text between anchor tags if they exist
    for section in named_section_dict.keys():

        string = str(named_section_dict[section])
        string = string.replace("<i>","").replace("</i>","")
        full_section_cleaned = re.sub("</a>","",re.sub("<a.*?>","",string)).replace("\n"," ")

        for val in re.findall("<\/strong>.*?<br\/>",full_section_cleaned):
            list_of_section_values.append(clean_subheader_values(val))
    
    plant_dict = {}
    for head, val in list(zip(list_of_section_subheaders,list_of_section_values)):
        plant_dict[head] = val
        
    
    labeled_plant_dicts.update({symbol:plant_dict})


#If a plant does not have a subheader in the dict, add missing subheader:nan key value pair to its dict
for symbol,plant_dict in labeled_plant_dicts.items():
    for subheader in list_of_unique_subheaders:
        if subheader not in plant_dict.keys():
            plant_dict.update({subheader:np.nan})


#Create a dict of {subheader: [value for plant 1, value for plant 2, ... ], subheader2: [value for plant 1, ...],...}
#Every plant has dict with an equal number of key:value pairs, all ordered correctly, so this works 
dd = defaultdict(list)

for d in labeled_plant_dicts.values(): # you can list as many input dicts as you want here
    for key, value in d.items():
        dd[key].append(value)

index = labeled_plant_dicts.keys()
full_df = pd.DataFrame(dd,index=index).reset_index()
print(full_df)

mapping = source_data[["USDA Symbol","Scientific Name"]].set_index("USDA Symbol")
full_df = full_df.set_index(("index")).join(mapping,how="left").reset_index()
print(full_df)
# full_df["Color"].replace('Not Applicable', np.nan)
full_df = full_df[~(full_df["Scientific Name"].isna())]

write_df_to_sheet("All_Scraped_Data_Original_Full",f"Wildflower",full_df)

winsound.Beep(400,10000)