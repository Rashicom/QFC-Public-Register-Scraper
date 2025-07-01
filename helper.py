from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# get latest qfc_number from content
def get_latest_qfc(qfc_site):
    soup = BeautifulSoup(qfc_site.content, 'html.parser')
    # this take the first class match
    content_div = soup.find('div', class_='qfc-informationResult')
    qfc_div = content_div.find('div', class_='qfc-number')
    spans = qfc_div.find_all('span')
    qfc_number = spans[1].get_text(strip=True)
    return qfc_number

def get_screen_documents_uris(qfc_site=None, origin="request"):
    if origin == "request":
        soup = BeautifulSoup(qfc_site.content, 'html.parser')
    else:
        soup = BeautifulSoup(qfc_site.page_source, 'html.parser')
    # this take the first class match
    content_divs = soup.find_all('div', class_='qfc-informationResult')
    documents = []
    for i,cont in enumerate(content_divs):
        qfc_div = cont.find('div', class_='qfc-number')
        a_tag = qfc_div.find_all('a')[-1]
        if a_tag.get('href') != "#":
            documents.append(a_tag.get('href'))

    return documents
    

def get_pagination_bar(qfc_site):
    soup = BeautifulSoup(qfc_site.content, 'html.parser')
    content_id = soup.find('span', id='PrCompanyPager')
    print(content_id.prettify())
    a_list = content_id.find_all('a')
    result = [a.get_text(strip=True) for a in a_list if a.get_text(strip=True) not in {">", "<", "..."}]
    return result


def next_page(driver, timeout=10):
    pager = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "PrCompanyPager"))
    )

    # Get current HTML of pager to detect page change later
    old_pager_html = pager.get_attribute('innerHTML')

    # Find all <a> elements inside the pager
    links = pager.find_elements(By.TAG_NAME, 'a')
    links[-1].click()

    # Wait until the pager's HTML changes (indicating new page is loaded)
    WebDriverWait(driver, timeout).until(
        lambda d: d.find_element(By.ID, "PrCompanyPager").get_attribute('innerHTML') != old_pager_html
    )
    return driver

def next_target_page(driver, target_page, timeout=10):
    # press next page button till target_page
    for i in range(target_page-1):
        print("next page")
        driver = next_page(driver)
    return driver