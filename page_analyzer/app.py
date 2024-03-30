from flask import Flask, render_template, redirect, url_for
from flask import request, flash, get_flashed_messages
from page_analyzer.parser import normalized_url, url_parse, get_error
from page_analyzer import psql as db
from dotenv import load_dotenv
import os


load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route("/")
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    with db.get_connection(DATABASE_URL) as conn:
        urls = db.get_urls(conn)
    db.close_connection(conn)
    return render_template('urls/index.html', urls=urls)


@app.post('/urls')
def urls_post():
    url = request.form.get('url')
    validation_error = get_error(url)
    formatted_url = normalized_url(url)
    if validation_error:
        flash(*validation_error)
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html',
                               messages=messages,
                               value_url=url), 422
    with db.get_connection(DATABASE_URL) as conn:
        url_info = db.get_id(conn, formatted_url)
        if not url_info:
            url_id = db.new_url_id(conn, formatted_url)
            flash('Страница успешно добавлена', 'success')
        else:
            url_id = url_info.id
            flash('Страница уже существует', 'success')
    db.close_connection(conn)
    return redirect(url_for('get_url',
                            id=url_id))


@app.route('/urls/<int:id>')
def get_url(id):
    with db.get_connection(DATABASE_URL) as conn:
        checks = db.get_url_check(conn, id)
        url = db.get_url_by_id(conn, id)
        msgs = get_flashed_messages(with_categories=True)
    db.close_connection(conn)
    return render_template('urls/output.html',
                           msgs=msgs,
                           url=url,
                           checks=checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def get_url_checks(id):
    with db.get_connection(DATABASE_URL) as conn:
        url_info = db.get_url_by_id(conn, id)
        with db.get_connection(DATABASE_URL) as conn:
            check = url_parse(url_info.name)
            if check['status_code'] == 200:
                check['url_id'] = id
                db.insert_check(conn, check)
                flash('Страница успешно проверена', 'success')
            else:
                flash('Произошла ошибка при проверке', 'danger')
    db.close_connection(conn)
    return redirect(url_for('get_url', id=id))
