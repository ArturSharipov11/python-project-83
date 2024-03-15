import os
from flask import Flask
import pytest
from dotenv import load_dotenv
import page_analyzer


load_dotenv()
URL = 'http://localhost:8000'
DATABASE_URL = os.getenv('DATABASE_URL')
TESTING_URL = 'https://docs.djangoproject.com'



@pytest.fixture()
def app():
    app = page_analyzer.app
    app.config.update({
        "ENV": 'testing',
        "TESTING": True,
    })
    yield app


@pytest.fixture()
def client(app: Flask):
    return app.test_client()


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
