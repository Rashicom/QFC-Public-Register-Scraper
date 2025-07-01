# import packages
import math
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# helpers
from helper import get_latest_qfc, get_pagination_bar, get_screen_documents_uris

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

diff = latest_qfc_number - start_from_qfc_number
if diff == 0:
    target_page = 1
else:
    target_page = math.ceil(diff/page_lenght)

# open page using selenium
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
qfc_page = driver.get("https://eservices.qfc.qa/qfcpublicregister/publicregister.aspx")
driver.maximize_window()
time.sleep(5)

uris = get_screen_documents_uris(driver, "driver")

# while True:
for i in range(2):
    print("Going to target page : ", target_page)
    # open target_page(qfc_page)

    # if page is None:
        # return
    # documents_count = get_doc_count(page)

    # for row in page.rows till documents_count:
        # continue if qfc number is top of defined qfc
        # if page.qfc_number > start_from_qfc_number:
            # continue
        # detail_iframe_url = get_url(row)
        # detail_page = get_detail_page(detail_iframe_url)

        # write information to csv

        # close detail_page
    target_page += 1
    

