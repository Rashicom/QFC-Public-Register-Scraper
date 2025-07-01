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
    a_list = content_id.find_all('a')
    result = [a.get_text(strip=True) for a in a_list if a.get_text(strip=True) not in {">", "<", "..."}]
    return result