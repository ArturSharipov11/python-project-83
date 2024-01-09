import psycopg2
from datetime import date
import os


def connect():
    try:
        env_variable = os.getenv('DATABASE_URL')
        connection = psycopg2.connect(env_variable)
        connection.autocommit = True
        return connection
    except Exception as e:
        print(f'Error connecting to database{e}')
        return None


def execute_sql_script(filepath):
    with open(filepath) as f:
        script = f.read()
    with connect() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(script)
            except Exception as e:
                print(e)


def get_urls_from_db():
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM urls")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
            return list(reversed(data))


def insert_new_url(url: str) -> tuple | int:
    with connect() as connection:
        with connection.cursor() as cursor:
            check_query = 'SELECT id FROM urls WHERE name = %s'
            cursor.execute(check_query, (url,))
            existing_id = cursor.fetchone()
            if existing_id:
                return existing_id[0], True
            insert_query = '''
            INSERT INTO urls
            (name, created_at) VALUES (%s, %s) 
            RETURNING id
            '''
            cursor.execute(insert_query, (url, date.today().isoformat()))
            return cursor.fetchone()[0]


def get_url_by_id(id_):
    with connect() as connection:
        with connection.cursor() as cursor:
            query = "SELECT * FROM urls WHERE id = %s"
            cursor.execute(query, (id_,))
            url = cursor.fetchone()
            if url:
                column_names = [desc[0] for desc in cursor.description]
                return dict(zip(column_names, url))
            return None