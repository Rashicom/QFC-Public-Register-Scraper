# import packages
import math
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# helpers
from helper import get_latest_qfc, get_pagination_bar, get_screen_documents_uris, next_page, next_target_page

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
print("page len", page_lenght)

start_from_qfc_number_str = input(f"Enter start from qfc number(default: {latest_qfc_number_str}) : ") or latest_qfc_number_str
start_from_qfc_number = int(start_from_qfc_number_str)

pagination_bar = get_pagination_bar(qfc_site_resp)
pagination_bar_lenght = len(pagination_bar) + 1 # adding 1 because current page number is not in the list


# open page using selenium
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
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

# iterate through pages
# while True:
for i in range(1):
    # open target_page(qfc_page)
    if i > 0:
        driver = next_page(driver)
    if driver is None:
        raise Exception("Completed")
    
    uris = get_screen_documents_uris(driver, "driver")
    print(">>>>>>>>>>>> :", uris)

    # documents_count = get_doc_count(page)

    # for row in page.rows till documents_count:
        # continue if qfc number is top of defined qfc
        # if page.qfc_number > start_from_qfc_number:
            # continue
        # detail_iframe_url = get_url(row)
        # detail_page = get_detail_page(detail_iframe_url)

        # write information to csv

        # close detail_page

