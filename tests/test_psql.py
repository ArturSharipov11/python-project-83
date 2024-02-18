import pytest
import os
from page_analyzer import psql_ as db
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


@pytest.mark.parametrize("db_url, expected_result", [
    (DATABASE_URL, True),
    (None, ValueError),
])
def test_connect(db_url, expected_result):
    if expected_result == ValueError:
        with pytest.raises(ValueError):
            db.connect(db_url)
    else:
        connection = db.connect(db_url)
        assert connection is not None


def test_insert_url():
    db.execute_sql_script()
    url = "https://example.com"
    inserted_id = db.insert_new_url(url)
    assert isinstance(inserted_id, int)
    existed_id = db.insert_new_url(url)
    assert isinstance(existed_id, tuple)
    assert existed_id[0] == 1


def test_get_urls_from_db():
    db.execute_sql_script()
    empty_urls = db.get_urls_from_db()
    assert empty_urls == []
    db.insert_new_url("https://example.com")
    urls = db.get_urls_from_db()
    assert len(urls) == 1


def test_insert_and_get_url_check():
    db.execute_sql_script()
    url_id = db.insert_new_url("https://example.com")
    status_code = 200
    seo_info = {
        'h1': 'Example',
        'title': 'Example Page',
        'description': 'An example page'
    }
    db.insert_new_check(url_id, status_code, seo_info)
    url_checks = list(db.get_url_checks(url_id))
    assert url_checks[0]['description'] == seo_info.get('description')
    assert url_checks[0]['h1'] == seo_info.get('h1')
    assert url_checks[0]['title'] == seo_info.get('title')
