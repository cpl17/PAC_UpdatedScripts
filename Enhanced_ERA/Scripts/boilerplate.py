
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from selenium.common.exceptions import TimeoutException,NoSuchElementException




options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)
ser = Service("C:\Program Files (x86)\chromedriver.exe")


driver = webdriver.Chrome(service=ser, options=options)
# wait = WebDriverWait(driver, 3)


base_url = 'https://www.google.com/search?q='
    
# wait.until(EC.presence_of_element_located(((By.ID,"characteristics"))))  


# #URL - Success
# q = 'site:https://www.eastpikeland.org "Native Plants"'
# url = base_url + q
# # url = "https://www.eastpikeland.org"


# #URL - Failure (0 results)


q = 'site:https://highlandtwp1853.org/about/ "Dark Sky"'
url = base_url + q

# #URL - Failure (Search string not found in title)

# url = 'site:https://easttown.org/ "Dark Sky"'



try:
    driver.get(url)
    wait = WebDriverWait(driver, 10)


except TimeoutException:

    print("Page didn't load")

#Identify the first element 
try:
    first_element = driver.find_element(by=By.TAG_NAME,value="h3")
    print(first_element.text)

except NoSuchElementException:
    print("No Results")


driver.quit()