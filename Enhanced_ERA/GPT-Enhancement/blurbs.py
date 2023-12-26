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
data = pd.read_csv("./Data/Blurbs.csv")[983:]
print(data.head())


names = data["Scientific Name"]
blurbs = data["Blurb"]


count = 984

for name,blurb in list(zip(names,blurbs)):

    print(name,count)

    if blurb != "Missing":
        #Write response to file
        with open("blurbs_2.txt","a") as f:
            f.write(name + " ##### " + blurb + "\n")
        count +=1
        continue


    prompt = f""""Describe the native plant "{name}" in 50 words for a home gardener with interesting attributes such as ideal conditions, primary pollinators that it attracts, unique uses for the plant, significant wildlife value, and physical attributes. 
    Do not provide details native status. 
    Omit subject (plant name) in response. 
    Do not use technical botany terminology. 
    Answer the question with only completely true statements, and if you're unsure of the answer, say 'Sorry, I don't know'"""

    #Get blurb using ChatGPT API

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
        {"role": "system", "content": "You are a helpful assistant who outputs information about plants. You will use the resources you have on plants to answer my questions."},
        {"role": "user", "content": prompt}
        ]
    )
    

    response = response.choices[0].message.content

    #Write response to file
    with open("blurbs_2.txt","a") as f:
        f.write(name + " ##### " + response + "\n")

    count+=1



      


   










