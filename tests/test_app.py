import pytest
from page_analyzer import app
from page_analyzer.psql_ import execute_sql_script


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            execute_sql_script()
        yield client
    with app.app_context():
        execute_sql_script()


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Анализатор страниц' in response.data.decode('utf-8')
    assert 'Сайты' in response.data.decode('utf-8')


@pytest.mark.parametrize("url, expected_message", [
    ('https://ru.hexlet.io/', 'Страница успешно добавлена'),
    ('wrong://url', None)
])
def test_url_submission(client, url, expected_message):
    response = client.post('/urls', data={'url': url})

    if expected_message:
        assert response.status_code == 302
        assert '/urls/1' in response.headers['Location']

        with client.session_transaction() as session:
            flash_messages = session['_flashes']
            assert flash_messages
            assert next(
                (i for i in flash_messages if expected_message in i[1]), None)
    else:
        assert response.status_code == 422


@pytest.mark.parametrize("url, expected_message", [
    ('https://ru.hexlet.io/', 'Страница успешно проверена'),
    ('https://wrongurlwrong.com', 'Произошла ошибка при проверке')
])
def test_check_url(client, url, expected_message):
    client.post('/urls', data={'url': url})
    response = client.post('/urls/1/checks')
    assert response.status_code == 302
    with client.session_transaction() as session:
        flash_messages = session['_flashes']
        assert flash_messages
        assert next(
            (i for i in flash_messages if expected_message in i[1]), None)
