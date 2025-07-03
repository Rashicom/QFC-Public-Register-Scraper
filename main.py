# import packages
import math
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# helpers
from helper import get_latest_qfc, get_pagination_bar, get_screen_documents_uris, next_page, next_target_page, get_page_company_details, flatten_company_data, write_company_list_to_csv

# open main window
qfc_site_resp = requests.get("https://eservices.qfc.qa/qfcpublicregister/publicregister.aspx")
if qfc_site_resp.status_code != 200:
    print("Cannot get page")
    raise Exception("Cannot get page")

# get latest qfc
latest_qfc_number_str = get_latest_qfc(qfc_site_resp)
latest_qfc_number = int(latest_qfc_number_str)

# get screen doc length
page_lenght = len(get_screen_documents_uris(qfc_site_resp))

start_from_qfc_number_str = input(f"Enter start from qfc number(default: {latest_qfc_number_str}) : ") or latest_qfc_number_str
start_from_qfc_number = int(start_from_qfc_number_str)

pagination_bar = get_pagination_bar(qfc_site_resp)
pagination_bar_lenght = len(pagination_bar) + 1 # adding 1 because current page number is not in the list


# open page using selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
qfc_page = driver.get("https://eservices.qfc.qa/qfcpublicregister/publicregister.aspx")
driver.maximize_window()
time.sleep(5)

# navigate to the target page
diff = latest_qfc_number - start_from_qfc_number
if diff != 0:
    # we have to go the target page, it should be > 1
    # if diff is 0 then target page is 1(this page) not need to go to target
    target_page = math.ceil(diff/page_lenght)
    print(f"Going to target page :{target_page}")
    driver = next_target_page(driver,target_page)
else:
    target_page = 1

page_limit = int(input(f"How many page do you want to scrap from page no : {target_page}"))

# iterate through pages
# while True:
for i in range(page_limit):
    # open target_page(qfc_page)
    if i > 0:
        driver = next_page(driver)
    if driver is None:
        raise Exception("Completed")
    
    # read all company details of this page
    print(f"Scraping page : {i+1}")
    data = get_page_company_details(driver)
    print(data)

    # write batch data to csv
    print("Data Writing to csv")
    write_company_list_to_csv(data)
    print("Data write Complete")


    # write this page details to csv
    # each page contains about 30 records
    # update each buld record to csv
        

    # for row in page.rows till documents_count:
        # continue if qfc number is top of defined qfc
        # if page.qfc_number > start_from_qfc_number:
            # continue
        # detail_iframe_url = get_url(row)
        # detail_page = get_detail_page(detail_iframe_url)

        # write information to csv

        # close detail_page

