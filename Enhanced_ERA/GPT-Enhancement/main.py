import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os
import sys
import numpy as np


#Get Key
load_dotenv()
my_variable = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=my_variable)


#Read in ERA data
data = pd.read_csv("Updated_Reduced.csv")


# names = ["Ruellia humilis", "Phyllodoce caerulea", "Mentzelia tricuspis", "Cornus canadensis", "Pittosporum hawaiiense", "Chloracantha spinosa", "Carex atrofusca", "Galax urceolata", "Carex tuckermanii", "Betula pumila", "Poa alpina", "Persea palustris", "Adenophyllum porophylloides", "Echinocereus viridiflorus", "Ribes montigenum"]
# data = data[data["index"].isin(names)]

data.set_index("index",inplace=True)
data = data["Dryopteris cristata":]
names = data.index.to_list()

columns = data.columns.to_list()


###TEST###
# data.to_csv("Test_ERA.csv")

print(names[0],names[-1])
print(columns)

print(data.isna().sum().sum())

gpt_output = pd.DataFrame(index=names,columns=columns)

count = 0
for name in names:

    line = [name] + ([""]*len(columns))
   
  
    for i,column in enumerate(columns):

        if data.loc[name,column] is not np.nan:
            continue

        if column == "Sun Exposure":

            prompt = f""""What is the required sun exposure for the plant {name}? 
                Shade, Part Shade or Sun are the allowed unique responses.
                It's allowed to include multiple of them and do so by separating them with a comma. 

                Example 1: "Shade" 
                Example 2: "Part Shade, Sun"
                Example 3: "Shade, Part Shade, Sun"

                Only include the answer in your reponse. Your answer should be less than 20 characters long.
                
                If you do not know return "Missing".
                """

        elif column == "Soil Moisture":

            prompt = f"""What is the required soil moisture for the plant {name}?
                Dry, Moist, or Wet are the allowed unique responses. 
                It's allowed to include multiple of them. Do so by separating them with a comma.
                
                
                Example 1: "Moist"
                Example 2: "Dry,Moist"
                Example 3: "Wet"  

                Only include the answer in your response. Your answer should be less than 20 characters long.

                If you do not know return "Missing"
                """

        elif column == "Flowering Months":

            prompt = f"""What is the bloom period of the plant {name}?

                Include the first three letters of the first month, the first three letters of the second month and separate them using -.

                Example 1: "Apr-Jun"
                Example 2: "Mar-Aug" 
                Example 3: "Jun-Sep"

                Only include the answer in your response. Your answer should be less than 20 characters long.

                
                If you do not know or if the plant doesn't bloom return "Missing"
                """

        elif column == "Height (feet)":

            prompt = f"""What is the height of the plant {name}. Provide the value in feet. 
                If there is a decimal, round to 1 decimal. 
                If there is a range, separate the start and end using -. 

                Example 1: ".1-2"
                Example 2: ".2-.3
                Example 3: "5"
                Example 4: "50-60"

                Only include the answer in your response. Your answer should be less than 20 characters long.


                If you do not know return "Missing"
                """


        elif column == "Showy":

            prompt = f"""Is the plant with the scientific name {name} considered showy? A plant is showy if it has vibrant, striking, or conspicuous features.
                Respond with only Yes or No. 

                Example 1: "Yes"
                Example 2: "No" 

                Only include the answer in your response. 


                If you do not know return "Missing".
                """
                
        else:

            #'Flower Color'

            prompt = f"""What color is the plant with the scientific name {name}? Please output only the color. If there are multiple colors the plant can be described with,
                please use a comma to separate them. 
                
                Example 1: "Color". 
                Example 2: "First color, second color". 

                Only include the answer in your response. Your answer should be less than 20 characters long.
                
                If you do not know, respond with "Missing".
                """


        name = name.strip()


        #Get blurb using ChatGPT API

        response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
        {"role": "system", "content": "You are a helpful assistant who outputs information about plants. You will use the resources you have on plants to answer my questions."},
        {"role": "user", "content": prompt}
        ]
        )
        count +=1

        response = response.choices[0].message.content

        # gpt_output.at[name,column] = response
        line[i+1] = response
        try:
            print(name + "," + response)
        except UnicodeEncodeError:
            print("error")  

    with open("output.txt","a") as f:
        f.write(",".join(line) + "\n")

      
print(count)
gpt_output.to_csv("Test_GPT_Bottom.csv")

   










