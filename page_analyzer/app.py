from flask import Flask, render_template, redirect, url_for
from flask import request, flash, get_flashed_messages
from validators import url as valid
from page_analyzer.parser import normalized_url, get_html_text, get_seo_info
from page_analyzer import psql as db
from dotenv import load_dotenv
import os
import requests


load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')



@app.route("/")
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    messages = get_flashed_messages(with_categories=True)
    conn = db.get_connection()
    urls = db.get_urls_fromdb(conn)
    db.close_connection(conn)
    return render_template(
        'urls/index.html',
        messages=messages,
        urls=urls
    )


@app.post('/urls')
def urls_post():
    url = request.form['url']
    conn = db.get_connection()
    if not valid(url):
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            url=url
        ), 422
    normal_url = normalized_url(url)
    id = db.new_url_id(normal_url, conn)
    if isinstance(id, tuple):
        flash('Страница уже существует', 'info')
        id = id[0]
    else:
        flash('Страница успешно добавлена', 'success')
    db.close_connection(conn)
    return redirect(url_for('get_url', id=id))


@app.route('/urls/<int:id>')
def get_url(id):
    conn = db.get_connection()
    messages = get_flashed_messages(with_categories=True)
    url = db.get_url_by_id(id, conn)
    checks = db.get_url_checks(id, conn)
    conn.commit()
    db.close_connection(conn)
    return render_template(
        'urls/output.html',
        url=url,
        checks=checks,
        messages=messages
    )


@app.post('/urls/<id>/checks')
def get_url_checks(id):
    conn = db.get_connection()
    url = db.get_url_by_id(id, conn)
    url_name = url.get('name')
    try:
        response = requests.get(url_name)
        response.raise_for_status()

        text = get_html_text(url_name)
        seo_info = get_seo_info(text)

        db.insert_check(id, response.status_code, seo_info)

        flash('Страница успешно проверена', 'success')
    except (
        requests.RequestException, requests.Timeout,
        requests.ConnectionError, requests.TooManyRedirects,
        requests.HTTPError
    ):
        flash('Произошла ошибка при проверке', 'danger')
    
    finally:
        db.close_connection(conn)
        return redirect(url_for('get_url', id=id))
