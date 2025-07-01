from bs4 import BeautifulSoup
import requests

# get latest qfc_number from content
def get_latest_qfc(qfc_site):
    soup = BeautifulSoup(qfc_site.content, 'html.parser')
    # this take the first class match
    content_div = soup.find('div', class_='qfc-informationResult')
    qfc_div = content_div.find('div', class_='qfc-number')
    spans = qfc_div.find_all('span')
    qfc_number = spans[1].get_text(strip=True)
    return qfc_number