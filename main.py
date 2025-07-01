# import packages
import math
import requests
from bs4 import BeautifulSoup

# helpers
from helper import get_latest_qfc

# open main window
qfc_site_resp = requests.get("https://eservices.qfc.qa/qfcpublicregister/publicregister.aspx")
if qfc_site_resp.status_code != 200:
    print("Cannot get page")
    raise Exception("Cannot get page")

# get latest qfc
latest_qfc_number = get_latest_qfc(qfc_site_resp)

start_from_qfc_number = input(f"Enter start from qfc number(default: {latest_qfc_number}) : ") or latest_qfc_number
print(start_from_qfc_number)

# pagination_bar_length = find pagibation length from page
# diff = latest_qfc_number - start_from _qfc_num
# target_page = math.ceil(diff/pagination_bar_len)

# while True:
    # pagination_bar_length = find pagibation length from page
    # page = set_page(target_page)
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
    # target_page += 1
    

