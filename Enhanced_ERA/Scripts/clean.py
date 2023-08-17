import pandas as pd
import numpy as np
import re
import time 

from Helpers import get_sheet_data,write_df_to_sheet

STATE = "AL"

era_unique = get_sheet_data("UniqueValues",f"ERA_{STATE}") ###TODO: CHARNGE THIS to not test once other tasks are comleted 
source_data = get_sheet_data("ERA",STATE)



##################Gardenia##############
RESOURCE = "Gardenia"

data = get_sheet_data("All_Scraped_Data_Original",f"{RESOURCE}_{STATE}")

relevant_columns = ["index","Exposure","Height","Characteristics"]
data= data[relevant_columns]


# Clean Height
def determine_height(x):

    if isinstance(x,float):
        return x 
    
    if x == "":
        return np.nan


    x = x.split(" (")[0].replace("'","") 
    
    if '"' in x:
        #Range list looks like ['6"', "1'"]
        range_list = x.split(" – ")
        bottom,top = range_list[0],range_list[1]
        
        if '"' in bottom:
            range_list[0] = str(round(int(range_list[0].replace('"','')) / 12,1))
        if '"' in top:
            range_list[1] = str(round(int(range_list[1].replace('"','')) / 12,1)) 

        return "–".join(range_list)
    
    else:

        return x.replace(" to ","–")

data["Height (feet)"] = data.Height.apply(determine_height)

#Clean Showy
def is_showy(x):
    if isinstance(x,float):
        return x
    else:
        return "Yes" if "Showy" in x else "No"

data["Showy"] = data.Characteristics.apply(is_showy)

#Clean Exposure
def clean_exposure(cell_value):
    if isinstance(cell_value,float):
        return cell_value

    x = cell_value.split(",")
    for i,val in enumerate(x):
        if val == " Partial Sun":
            x[i] = " Partial Shade"
    return ",".join(x)       

data["Sun Exposure"] = data["Exposure"].apply(clean_exposure)


data.drop(["Exposure","Height","Characteristics"],axis=1,inplace=True)
write_df_to_sheet("All_Scraped_Data_Cleaned",f"{RESOURCE}_{STATE}",data)

time.sleep(15)


#####################Missouri Botantical################
RESOURCE = "MissouriBotanical"


data = get_sheet_data("All_Scraped_Data_Original",f"{RESOURCE}_{STATE}")
relevant_columns = ["index","Sun","Flower","Bloom Time","Height","Bloom Description","Water"]
data= data[relevant_columns]


#Height -> Height (feet)
def determine_height(cell_value):
    x = cell_value.split(" to ")
    f = lambda y: str(round(float(y.strip()),1)) if "." in y else y.strip()
    x = list(map(f,x))
    return "–".join(x)


data["Height (feet)"] = data["Height"].str.replace("feet","").str.replace(".00","")
data["Height (feet)"] = data["Height (feet)"].apply(determine_height)


# Bloom Time -> Flowering Months
def clean_bloom(cell_value):
    x = cell_value.split("to")
    x = list(map(lambda y : (y.strip())[:3],x))
    return "–".join(x)


data["Flowering Months"] = data["Bloom Time"].apply(clean_bloom)


# Flower -> Showy
def determine_showy(cell_value):
    #If showy, its first in comma separated string
    if isinstance(cell_value,float):
        return cell_value
    x = cell_value.split(",")[0]
    x = x.strip()
    if x == "Showy":
        return "Yes"
    else:
        return "No" 


data["Showy"] = data["Flower"].apply(determine_showy)

#Bloom Description -> Flower Color

source_colors = era_unique["Flower Color"].dropna()


def determine_color(cell_value):
    if isinstance(cell_value,float):
        return cell_value
    
    x = cell_value.replace("ish","")

    for color in source_colors:
        if color == x:
            return color
    for color in source_colors:
        if color in x:
            return color


data["Flower Color"] = data["Bloom Description"].apply(determine_color)


# Sun -> Sun Exposure


def clean_exposure(cell_value):
    if isinstance(cell_value,float):
        return cell_value

    x = cell_value.split("–")
    for i,val in enumerate(x):
        if val.lower().strip() == "full sun":
            x[i] = "Sun"
        if val.lower().strip() == "full shade":
            x[i] = "Shade" 
        if val.lower().strip() == "part shade":
            x[i] = "Part Shade"       
        
    return ",".join(x)       


data["Sun Exposure"] = data["Sun"].apply(clean_exposure)


# Water -> Soil Moisture


def get_soilmoisture(cell_value):
    if isinstance(cell_value,float):
        return cell_value
    x = cell_value.strip().title()
    if x == "Dry To Medium":
        return "Moist"
    elif x in ["Wet","Dry"]:
        return x
    else:
        return np.nan


data["Soil Moisture"] = data["Water"].apply(get_soilmoisture)



data.drop(["Height","Bloom Time","Flower","Sun","Bloom Description","Water"],axis=1,inplace=True)
write_df_to_sheet("All_Scraped_Data_Cleaned",f"{RESOURCE}_{STATE}",data)


time.sleep(15)


##############NCSU##############




RESOURCE = "NCSU"
data = get_sheet_data("All_Scraped_Data_Original",f"{RESOURCE}_{STATE}")
relevant_columns = ["index","Dimensions","Flower Value To Gardener","Light"]
data= data[relevant_columns]


# ## Dimensions -> Height (feet)
def determine_height(cell_value):
    if isinstance(cell_value,float):
        return cell_value
    if cell_value == "":
        return cell_value

    x = cell_value.split("|")[0]

    x = x.replace("Height:","").replace("- ","")

    x = x.split(".")

    min_feet,max_feet = int(x[0].strip().replace(" ft","")),int(x[2].strip().replace(" ft",""))
    min_inches,max_inches = int(x[1].strip().replace(" in","")), int(x[3].strip().replace(" in",""))

    range_min = str(round((((min_feet*12) + min_inches) / 12),1))
    range_max = str(round((((max_feet*12) + max_inches) / 12),1))
    
    #Removing extra sig fig
    if ("0." not in range_min) | ("0.0"in range_min):
        range_min = range_min.replace(".0","")
    if ("0." not in range_max) | ("0.0"in range_max):
        range_max = range_max.replace(".0","")
    
    return "–".join([range_min,range_max])


data["Height (feet)"] = data["Dimensions"].apply(determine_height)


# ## Flower Value -> Showy
def determine_showy(cell_value):
    if isinstance(cell_value,float):
        return cell_value
    
    x = cell_value.split("|")

    if "Showy" in x:
        return "Yes"
    else:
        return "No"



data["Showy"] = data["Flower Value To Gardener"].apply(determine_showy)


# ## Light -> Sun Exposure
def clean_exposure(cell_value):
    if isinstance(cell_value,float):
        return cell_value

    x = cell_value.split(" (")[0].strip().title()

    if x == "Full Sun":
        return "Sun"

    if x == "Partial Shade":
        return "Part Shade"
    
    if x == "Deep Shade":
        return "Shade"
    
    else:
        return np.nan
    
        


data["Sun Exposure"] = data["Light"].apply(clean_exposure)
data.drop(["Dimensions","Flower Value To Gardener","Light"],axis=1,inplace=True)

write_df_to_sheet("All_Scraped_Data_Cleaned",f"{RESOURCE}_{STATE}",data)


time.sleep(15)


########### New Moon #############

RESOURCE = "NewMoon"



data = get_sheet_data("All_Scraped_Data_Original",f"{RESOURCE}_{STATE}")
relevant_columns = ["index","Height","Bloom Color","Exposure","Flowering Months","Soil Moisture Preference"]
data= data[relevant_columns]




# # Height -> Height (feet)


def determine_height(cell_value):

    if isinstance(cell_value,float):
        return cell_value
    
    x = cell_value.split()

    measurement = x[1]
    if measurement.lower() in ["in","inches"]:
        f = lambda x : str(round(int(x)/ 12,1))
        range_list = x[0].split("-")
        if len(range_list) == 1:
            return str(round(int(x[0])/ 12,1))
        else:
            range_list = list(map(f,range_list))
            return "-".join(range_list)
    
    elif measurement.lower() in ["feet","ft"]:

        return cell_value.replace(measurement,"").strip()

    


data["Height (feet)"] = data["Height"].apply(determine_height)

# # Bloom Color -> Flowering Color


def determine_color(cell_value):
    if isinstance(cell_value,float):
        return cell_value

    x = [x.strip() for x in re.split(',|-', cell_value)]
    if len(x) == 2:
        return "–".join(x)
    elif len(x) > 2:
        return ",".join(x)
    else:
        return x[0]



data["Flower Color"] = data["Bloom Color"].apply(determine_color)

# # Flowering Months


def determine_flowering_months(cell_value):
    if isinstance(cell_value,float):
        return cell_value
    x = cell_value.split(",")
    
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    def sort_months(month_list):
        sorted_months = []
        for month in months:
            if month in month_list:
                sorted_months.append(month)
        return sorted_months

    x_sorted = sort_months(x)
    first_month,last_month = (x_sorted[0])[:3],(x_sorted[-1])[:3]

    return "-".join([first_month,last_month])    


data["Flowering Months"] = data["Flowering Months"].apply(determine_flowering_months)

# # Soil Moisture Preferences -> Soil Moisture

def determine_moisture(cell_value):
    if isinstance(cell_value,float):
        return cell_value

    x = [x.strip() for x in re.split('to|,|/', cell_value)]
    new_list = []
    for val in x:
        if (val in ["Wet","Dry","Moist"]) & (val not in new_list):
            new_list.append(val)

    if len(new_list) == 0:
        return np.nan
    elif len(new_list) == 1:
        return new_list[0]
    elif len(new_list) == 3:
        return "Wet, Moist, Dry"
    elif sorted(new_list) == ["Dry","Moist"]:
        return "Moist, Dry"
    elif sorted(new_list) == ["Moist","Wet"]:
        return "Wet, Moist"  
    else:
        return np.nan 
    
    


data["Soil Moisture"] = data["Soil Moisture Preference"].apply(determine_moisture)


# # Exposure -> Sun Exposure

def determine_exposure(cell_value):
    if isinstance(cell_value,float):
        return cell_value

    x = [x.strip() for x in re.split('to|,|/', cell_value)]
    new_list = [np.nan]*3
    for val in x:
        if val in ["Full Sun","Sun"]:
            new_list[0] = "Sun"
        elif val in ["Partial Shade","Light Shade"]:
            new_list[1] = "Partial Shade"
        elif val == "Shade":
            new_list[2] = "Shade"
    return ",".join(pd.Series(new_list).dropna().to_list())
            


data["Sun Exposure"] = data["Exposure"].apply(determine_exposure)


data.drop(["Height","Bloom Color","Exposure","Soil Moisture Preference"],axis=1,inplace=True)
write_df_to_sheet("All_Scraped_Data_Cleaned",f"{RESOURCE}_{STATE}",data)

time.sleep(15)


##### USDA Plants  #############
RESOURCE = "USDAPlants"



data = get_sheet_data("All_Scraped_Data_Original",f"{RESOURCE}_{STATE}")
relevant_columns = ["index","Height, Mature (feet)","Flower Color"] #TODO:Change index
data= data[relevant_columns]



# # Cleaning


# ## Height -> Height (feet)


def determine_height(cell_value):
    if isinstance(cell_value,float):
        return cell_value

    if ((".0" in cell_value) | ("0.0" in cell_value)):
        return str(int(float(cell_value)))
    
    else:
        return cell_value
    



data["Height (feet)"] = data["Height, Mature (feet)"].astype("str").apply(determine_height)
data["Height (feet)"] = data["Height (feet)"].astype(str)


# Note: Flower Color and Height are formatted correctly

data.drop("Height, Mature (feet)",axis=1,inplace=True)
data.columns = ["index","Flower Color","Height (feet)"]


write_df_to_sheet("All_Scraped_Data_Cleaned",f"{RESOURCE}_{STATE}",data)



time.sleep(15)


################# Wildflower ############### 






RESOURCE = "Wildflower"



data = get_sheet_data("All_Scraped_Data_Original",f"{RESOURCE}_{STATE}")
relevant_columns = ["index","Bloom Time","Bloom Color", "Soil Moisture","Light Requirement","Size Notes"]
data= data[relevant_columns]


# Height 

def determine_height(cell_value):
    if isinstance(cell_value,float):
        return cell_value

    try:
        first_digit = re.findall(r'\d+',cell_value)[0]
    except IndexError:
        return np.nan

    if "feet" in cell_value.lower():
        return str(first_digit)
    if '"' in cell_value:
        return str(round(int(first_digit) / 12,1))
    if "inches" in cell_value:
        return str(round(int(first_digit) / 12,1)) 
    

# data["Height (feet)"] = data["Size Class"].apply(lambda x: x.split()[0].strip().replace(" ft.","").replace("-","–") if not isinstance(x,float) else x)
data["Height (feet)"] = data["Size Notes"].apply(determine_height)

# ## Bloom Time -> Flowering Months


def det_bloom(cell_value):
    if isinstance(cell_value,float):
        return cell_value
    
    x = cell_value.split(",")

    if len(x) == 1:
        return x[0]
    else:
        return "–".join([x[0],x[-1]])


data["Flowering Months"] = data["Bloom Time"].apply(det_bloom)


# ## Bloom Color -> Flower Color


def det_color(cell_value):
    if isinstance(cell_value,float):
        return cell_value
    
    x = cell_value.split(",")

    if len(x) == 1:
        return x[0].strip()
    else:
        return "–".join(x[:2]).strip()


data["Flower Color"] = data["Bloom Color"].apply(det_color)


# ## Soil Moisture


data["Soil Moisture"] = data["Soil Moisture"].str.strip()


# ## Light Requirement


data.rename({"Light Requirement":"Sun Exposure"},axis=1,inplace=True)


# Lookup Scientific Name

data.drop(["Bloom Time","Bloom Color","Size Notes"],axis=1,inplace=True)


write_df_to_sheet("All_Scraped_Data_Cleaned",f"{RESOURCE}_{STATE}",data)










