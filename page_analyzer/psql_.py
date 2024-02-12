import psycopg2
from datetime import date
import os
from dotenv import load_dotenv


load_dotenv()
ROOT = f'{os.path.dirname(__file__)}/..'
DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    try:
        env_variable = os.getenv('DATABASE_URL')
        connection = psycopg2.connect(env_variable)
        connection.autocommit = True
        return connection
    except Exception as e:
        print(f'Error connecting to database{e}')
        return None


def execute_sql_script():
    path = f'{ROOT}/database.sql'
    with open(path) as f:
        script = f.read()
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(script)


def get_urls_from_db():
    with connect() as connection:
        with connection.cursor() as cursor:
            query = """
            SELECT urls.id, urls.name, MAX(url_checks.created_at)
            AS max_created_at, url_checks.status_code
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id, urls.name, url_checks.status_code"""
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
            return list(data)


def insert_new_url(url: str) -> tuple | int:
    with connect() as connection:
        with connection.cursor() as cursor:
            check_query = 'SELECT id FROM urls WHERE name = %s;'
            cursor.execute(check_query, (url,))
            existing_id = cursor.fetchone()
            if existing_id:
                return existing_id[0], True
            insert_query = '''
            INSERT INTO urls (name, created_at)
            VALUES (%s, %s) RETURNING id;'''
            cursor.execute(insert_query, (url, date.today().isoformat()))
            return cursor.fetchone()[0]


def get_url_by_id(id_):
    with connect() as connection:
        with connection.cursor() as cursor:
            query = "SELECT * FROM urls WHERE id = %s;"
            cursor.execute(query, (id_,))
            url = cursor.fetchone()
            if url:
                column_names = [desc[0] for desc in cursor.description]
                return dict(zip(column_names, url))
            return None


def insert_new_check(url_id: int, status_code: int, seo_info: dict):
    insert_query = """
    INSERT INTO url_checks
    (url_id, status_code, h1, title, description, created_at)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                insert_query,
                (
                    url_id,
                    status_code,
                    seo_info.get('h1'),
                    seo_info.get('title'),
                    seo_info.get('description'),
                    date.today().isoformat()
                )
            )


def get_url_checks(id_):
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT JSONB_BUILD_OBJECT(
                        'id', id,
                        'url_id', url_id,
                        'status_code', status_code,
                        'h1', h1,
                        'title', title,
                        'description', description,
                        'created_at', created_at
                    ) AS url_check
                    FROM url_checks
                    WHERE url_id = %s;
                """, (id_,))

            results = cursor.fetchall()

            url_check_list = [result[0] for result in results]
            return reversed(url_check_list)
