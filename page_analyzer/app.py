from flask import Flask,render_template, redirect, url_for
from flask import request,flash, get_flashed_messages
from validators import url as valid
from page_analyzer.parser import normalize_url
from page_analyzer import psql_ as db
from dotenv import load_dotenv
import os


if "SECRET_KEY" not in os.environ:
    load_dotenv()


ROOT = f'{os.path.dirname(__file__)}/..'
db.execute_sql_script(f'{ROOT}/database.sql')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route("/")
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    messages = get_flashed_messages(with_categories=True)
    urls = db.get_urls_from_db()
    return render_template(
        'urls/index.html',
        messages=messages,
        urls=urls
    )


@app.post('/urls')
def urls_post():
    data = request.form['url']
    if not valid(data):
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            url=data
        ), 422
    normal_url = normalize_url(data)
    id_ = db.insert_new_url(normal_url)
    if isinstance(id_, tuple):
        flash('Страница уже существует', 'info')
        id_ = id_[0]
    else:
        flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url', id=id_))


@app.get('/urls/<id>')
def url(id):
    url = db.get_url_by_id(id)
    return render_template(
        'urls/output.html',
        url=url
    )


@app.post('/urls/<id>/checks')
def url_checks(id):
    db.insert_new_check(id)
    return redirect(url_for('url', id=id))


if __name__ == '__main__':
    app.run(debug=True, port=5001)