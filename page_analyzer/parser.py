from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from validators import url as valid


def normalized_url(url):
    url = urlparse(url)
    return f'{url.scheme.lower()}://{url.netloc.lower()}'


def url_validate(url):
    if len(url) < 255 and valid(url):
        return True


def get_seo_info(url: str) -> dict:

    page_data = {}

    r = requests.get(url)
    r.raise_for_status()

    page_data['status_code'] = r.status_code
    soup = BeautifulSoup(r.text, 'html.parser')
    page_data['title'] = soup.select_one('title')
    page_data['h1'] = soup.select_one('h1')
    page_data['description'] = soup.select_one('meta[name="description"]')

    if page_data['status_code'] != 200:
        raise requests.exceptions.RequestException

    return page_data
