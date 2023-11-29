**Main Scripts**

Each script scrapes one of the following resources: 

* Ernst Seeds: https://www.ernstseed.com/
* Izel Plants: https://www.izelplants.com/
* Mid Atlantic Natives: https://midatlanticnatives.com/
* Petals from the Past: https://petalsfromthepast.com/
* Plant More Natives: https://www.plantmorenatives.com/
* Toad Shade: https://www.toadshade.com/

<br>
<br>
<br>

The general procedure in each \<Directory\>.py script is: 

1. Read in the original ERA data from Google sheets in order to get the names for each plant to search on

2. Use [requests](https://docs.python-requests.org/en/latest/) + [BeatifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) (if static web content) to open and grab content from the directory web page or [Selenium](https://www.selenium.dev/documentation/) (if dynamic web content) to traverse the web page and store content

3. Store full inventory and then determine matches in the ERA. 

4. For each match, store the Name, Root URL and Direct Url in a DataFrame

4. Once we've iterated through each plant, we write the DataFrame to a Google sheet 


<br>
<br>
<br>



**Clean and Join**

*join_CSVs.py* creates a long DataFrame of availability and writes it to google sheets. one plant one store. 

*oneline_agg.py* creates a wide DataFrame of availability and writes it to google sheets. one plant many stores. 



