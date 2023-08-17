**Main Scripts**

Each script scrapes one of the following resources: 

* Gardenia: https://www.gardenia.net/guide/learn-how-to-grow-and-care-for-your-gardenia
* Missouri Botanical Garden: https://www.missouribotanicalgarden.org/
* NC State Plant Extension Office: https://plants.ces.ncsu.edu/
* New Moon Nursery: http://www.newmoonnursery.com/Plant-List
* USDA Plants: https://plants.usda.gov/home
* Lady Bird Johnson Wildflower Center: https://www.wildflower.org/plants-main


The *Google.py* and *Helpers.py* contain functions for reading/writing from Google sheets and documents. 

The general procedure in each *main_\<resource\>* file is: 

1. Read in the original ERA data from Google sheets in order to get the names for each plant to search on

2. Use [requests](https://docs.python-requests.org/en/latest/) + [BeatifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) (if static web content) to open and grab content from the plant web page or [Selenium](https://www.selenium.dev/documentation/) (if dynamic web content) to traverse the web page and store content

3. Run code tailored to each web page that grabs the relevant information for each plant and stores it in some data structure

4. Once we've iterated through each plant, we write it to a Google sheet 

The output is unique to each web page but includes data on height, color, sun exposure and other characteristics. 


**Data Quality Assurance**

The *get_unique_values* script produces unique values for each column of data for each resource at two levels of granularity. 

The top-level contains unique entries i.e. ("Sun,Part Shade" "Sun" "Shade,Sun" )
The lower level separates each entry along commas and produces unqiue entries among that data set ("Sun" "Part Shade" "Shade")

This output was used to tailor the cleaning scripts and get an overview how to approach transforming the formatting to fit the ERA format. 

**Clean and Join**





