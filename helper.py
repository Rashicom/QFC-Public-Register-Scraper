from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

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
        spans = qfc_div.find_all('span')
        if a_tag.get('href') != "#":
            documents.append({
                "href": a_tag.get('href'),
                "qfc_number": spans[1].get_text(strip=True)
            })

    return documents
    

def get_pagination_bar(qfc_site):
    soup = BeautifulSoup(qfc_site.content, 'html.parser')
    content_id = soup.find('span', id='PrCompanyPager')
    a_list = content_id.find_all('a')
    result = [a.get_text(strip=True) for a in a_list if a.get_text(strip=True) not in {">", "<", "..."}]
    return result


def next_page(driver, timeout=20):
    pager = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "PrCompanyPager"))
    )

    # Get current HTML of pager to detect page change later
    old_pager_html = pager.get_attribute('innerHTML')

    # Find all <a> elements inside the pager
    links = pager.find_elements(By.TAG_NAME, 'a')
    links[-1].click()
    time.sleep(2)
    # Wait until the pager's HTML changes (indicating new page is loaded)
    WebDriverWait(driver, timeout).until(
        lambda d: d.find_element(By.ID, "PrCompanyPager").get_attribute('innerHTML') != old_pager_html
    )
    return driver

def next_target_page(driver, target_page, timeout=10):
    # press next page button till target_page
    for i in range(target_page-1):
        print(f"next page : {i+1}")
        driver = next_page(driver)
    return driver


def get_register_details(company_page):
    soup = BeautifulSoup(company_page.page_source, 'html.parser')
    
    # 1. Company Name
    company_name = soup.find('span', id='lblFirmArabicName').text.strip()
    company_name = soup.find('span', id='lblFirmTitle').text.strip()

    # 2. QFC Number
    qfc_number = soup.find('span', id='lblFirmNo')
    qfc_number = qfc_number.text.strip() if qfc_number else ''

    # 3. Details of Registration
    registration_info = {}
    registration_section = soup.select_one('.innerpage-details-registration .registration-title:contains("details of registration")')
    if registration_section:
        reg_items = registration_section.find_next('div', class_='registration-info').find_all('div', class_='registration-item')
        for item in reg_items:
            spans = item.find_all('span')
            if len(spans) == 2:
                key = spans[0].text.strip()
                value = spans[1].text.strip()
                registration_info[key] = value

     # 4. Details of Licence
    licence_info = {}
    licence_section = soup.select_one('.innerpage-details-registration .registration-title:contains("details of licence")')
    if licence_section:
        lic_items = licence_section.find_next('div', class_='registration-info').find_all('div', class_='registration-item')
        for item in lic_items:
            spans = item.find_all('span')
            if len(spans) == 2:
                key = spans[0].text.strip()
                value = spans[1].text.strip()
                licence_info[key] = value
    
    return {
        'company_name': company_name,
        'qfc_number': qfc_number,
        'registration_info': registration_info,
        'licence_info': licence_info
    }

def get_page_company_details(driver):
    wait = WebDriverWait(driver, 10)
    pager = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "public-register"))
    )

    qfc_links = driver.find_elements(By.CSS_SELECTOR, "div.qfc-informationResult div.qfc-number a")
    result = []
    
    for i, link in enumerate(qfc_links):
        href = link.get_attribute("href")
        qfcnum = link.text.strip()
        print(f"object :{i}, {qfcnum}")
        if "#" in href:
            continue
        full_url = href if href.startswith("http") else f"https://eservices.qfc.qa/qfcpublicregister/{href}"

        # Open new tab via JS
        driver.execute_script("window.open(arguments[0]);", full_url)

        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])

        # Wait for content to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # fetch data
        scrapped_data = get_register_details(driver)
        result.append(scrapped_data)

        # Close the tab
        driver.close()

        # Switch back to main tab
        driver.switch_to.window(driver.window_handles[0])

    return result


def flatten_company_data(company_data):
    flattened = {
        'Company Name': company_data['company_name'],
        'QFC Number': company_data['qfc_number'],
    }

    # Flatten registration info
    for key, value in company_data.get('registration_info', {}).items():
        flattened[f"Reg - {key}"] = value

    # Flatten licence info
    for key, value in company_data.get('licence_info', {}).items():
        flattened[f"Lic - {key}"] = value

    return flattened


import csv
import os

def flatten_company_data(company_data):
    flattened = {
        'Company Name': company_data['company_name'],
        'QFC Number': company_data['qfc_number'],
    }

    for key, value in company_data.get('registration_info', {}).items():
        flattened[f"Reg - {key}"] = value

    for key, value in company_data.get('licence_info', {}).items():
        flattened[f"Lic - {key}"] = value

    return flattened


import csv
import os

def write_company_list_to_csv(data_list, filename='qfc_companies.csv'):
    flattened_data = [flatten_company_data(item) for item in data_list]

    if not flattened_data:
        print("⚠️ No data to write.")
        return

    # Preserve field order while detecting new fields
    fieldnames = []
    all_fields_set = set()
    for item in flattened_data:
        for key in item.keys():
            if key not in all_fields_set:
                fieldnames.append(key)
                all_fields_set.add(key)

    file_exists = os.path.exists(filename)
    file_has_data = os.path.getsize(filename) > 0 if file_exists else False

    existing_data = []
    existing_fieldnames = []

    if file_has_data:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_fieldnames = reader.fieldnames or []
            existing_data = list(reader)

        # Combine fieldnames: keep existing order, append new fields
        combined_fieldnames = existing_fieldnames.copy()
        for field in fieldnames:
            if field not in combined_fieldnames:
                combined_fieldnames.append(field)
    else:
        combined_fieldnames = fieldnames

    # Combine old + new data
    all_data = existing_data + flattened_data

    # Write (or rewrite) full CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=combined_fieldnames)
        writer.writeheader()
        for row in all_data:
            writer.writerow({key: row.get(key, '') for key in combined_fieldnames})

    print(f"✅ CSV updated: {filename} (rows written: {len(all_data)})")

