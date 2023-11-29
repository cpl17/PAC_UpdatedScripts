**Overview**

The code in this directory is a method of double-checking the data present in the RPC. Text files of the nurseries' availability are manually gathered and stored in a Google Drive. 

**Find Matches**

The procedures of *getmatches_alltext.py* are as follows:

1. Determine the ids and file names of each text file using the Google API

2. Download and write each file to a dummy directory

3. For each source (textfile), for each plant, check if plant name in text. The output for each
   source is a dataframe with columns [["Scientific Name","Common Name","USDA Symbol","Nursery"]]

4. All the long dataframes are concatenated and written to "LOCAL" in google sheets

4. Then, a one plant many nurseries wide dataframe is created and written to "LOCAL_AGG" in google sheets