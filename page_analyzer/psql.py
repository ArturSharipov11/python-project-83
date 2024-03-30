import psycopg2.extras
import psycopg2
from contextlib import contextmanager
from datetime import datetime


@contextmanager
def get_connection(db_url):
    try:
        connection = psycopg2.connect(db_url)
        yield connection
    except Exception:
        if connection:
            connection.rollback()
        raise
    else:
        if connection:
            connection.commit()


def close_connection(connection):
    if connection:
        connection.close()


def get_id(conn, url):
    with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as curs:
        curs.execute('''SELECT id, name, created_at
                     FROM urls
                     WHERE name=%s;''', (url,))
        url_info = curs.fetchone()
        if url_info is not None:
            return url_info


def get_url_by_id(conn, id):
    with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as curs:
        curs.execute('''SELECT id, name, created_at
                     FROM urls
                     WHERE id=%s;''', (id,))
        return curs.fetchone()


def new_url_id(conn, url):
    with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as curs:
        curs.execute('''INSERT INTO urls (name, created_at)
                     VALUES (%s, %s) RETURNING id;''', (url,
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return curs.fetchone().id


def get_url_check(conn, id):
    with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as curs:
        curs.execute('''SELECT id, status_code, h1,
                     title, description, created_at
                     FROM url_checks
                     WHERE url_id=%s
                     ORDER BY id DESC;''', (id,))
        return curs.fetchall()


def get_urls(conn):
    with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as curs:
        curs.execute('SELECT id, name FROM urls ORDER BY id DESC;')
        urls = curs.fetchall()
        curs.execute('''SELECT url_id, created_at, status_code
                     FROM url_checks
                     ORDER BY created_at DESC;''')
        url_checks = curs.fetchall()
        if url_checks:
            result = []
            for url in urls:
                len_result = len(result)
                for check in url_checks:
                    if url.id == check.url_id:
                        result.append(url._asdict() | check._asdict())
                        break
                if len(result) == len_result:
                    result.append(url._asdict())
            return result
        return urls


def insert_check(conn, check):
    with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as curs:
        curs.execute('''INSERT INTO url_checks (url_id, status_code,
                     h1, title, description, created_at)
                     VALUES (%s, %s, %s, %s, %s, %s);''',
                     (check['url_id'],
                      check['status'],
                      check['head'],
                      check['title'],
                      check['description'],
                      datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
