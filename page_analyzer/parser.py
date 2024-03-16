from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


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


def get_seo_info(text: str) -> dict:
    soup = BeautifulSoup(text, 'html.parser')

    h1 = soup.find('h1')
    h1_text = h1.text if h1 else ''

    title = soup.find('title')
    title_text = title.text if title else ''

    meta_tag = soup.find('meta', {'name': 'description'})
    meta_description = meta_tag.get('content') if meta_tag else ''

    return {
        'h1': h1_text,
        'title': title_text,
        'description': meta_description
    }
