from flask import Flask, render_template, redirect, url_for
from flask import request, flash, get_flashed_messages
from page_analyzer.parser import normalized_url, url_parse, url_validate
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
    conn = db.get_connection()
    urls = db.get_urls_fromdb(conn)
    db.close_connection(conn)
    return render_template('urls/index.html', urls=urls)


@app.post('/urls')
def urls_post():
    conn = db.get_connection()
    url = request.form.get('url')

    if not url:
        flash('URL обязателен', 'danger')
        msgs = get_flashed_messages(with_categories=True)
        return render_template('index.html', msgs=msgs), 422

    url = normalized_url(url)

    if not url_validate(url):
        flash('Некорректный URL', 'danger')
        msgs = get_flashed_messages(with_categories=True)
        return render_template('index.html', msgs=msgs), 422

    if id := db.get_id(url, conn):
        flash('Страница уже существует', 'info')
        return redirect(url_for('get_url', id=id))

    id = db.new_url_id(url, conn)
    db.close_connection(conn)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url', id=id))


@app.route('/urls/<int:id>')
def get_url(id):
    conn = db.get_connection()
    msgs = get_flashed_messages(with_categories=True)
    url = db.get_url_by_id(id, conn)
    checks = db.get_url_check(id, conn)
    db.close_connection(conn)

    return render_template('urls/output.html',
                           url=url, checks=checks, msgs=msgs)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def get_url_checks(id):
    conn = db.get_connection()
    url = db.get_url_by_id(id, conn)['name']
    try:
        page_data = url_parse(url)

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')

    else:
        db.insert_check(id, page_data, conn)
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('get_url', id=id))
    db.close_connection(conn)
    return redirect(url_for('get_url', id=id))
