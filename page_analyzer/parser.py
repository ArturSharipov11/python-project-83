from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from validators import url as valid
import validators


def normalized_url(url):
    url_parse = urlparse(url)
    format_url = f'{url_parse.scheme}://{url_parse.netloc}'
    return format_url


def get_html_text(url: str) -> str | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        return None


def url_parse(url):

    result = {'status_code': None,
              'head': None,
              'title': None,
              'description': None}
    try:
        request = requests.get(url)
        get_status = request.status_code
        soup = BeautifulSoup(request.content, 'html5lib')
        result['status_code'] = get_status
        result['head'] = soup.h1.string if soup.h1 else None
        result['title'] = soup.title.string if soup.title else None
        for link in soup.find_all('meta'):
            if link.get('name') == 'description':
                result['description'] = link.get('content')
                break
    except requests.exceptions.ConnectionError:
        pass

    return result


def url_validate(url):
    if len(url) < 255 and valid(url):
        return True


def get_error(url):
    error = []
    if not url:
        error = ['URL обязателен', 'danger']
    elif len(url) > 255:
        error = ['URL больше 255 символов', 'danger']
    elif not validators.url(url):
        error = ['Некорректный URL', 'danger']
    return error
