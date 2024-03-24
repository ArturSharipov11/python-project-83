from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from validators import url as valid


def normalized_url(url: str) -> str:
    parsed = urlparse(url)
    return f'{parsed.scheme}://{parsed.hostname}'


def get_html_text(url: str) -> str | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        return None


def url_parse(url):

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


def url_validate(url):
    if len(url) < 255 and valid(url):
        return True
