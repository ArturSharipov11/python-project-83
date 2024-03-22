import os
import psycopg2
import psycopg2.extras
from datetime import date
from dotenv import load_dotenv


load_dotenv()
ROOT = f'{os.path.dirname(__file__)}/..'
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def close_connection(connection):
    connection.close()


def execute_sql_script(conn):
    path = f'{ROOT}/database.sql'
    with open(path) as f:
        script = f.read()
    with conn.cursor() as cursor:
        cursor.execute(script)



def get_urls_fromdb(conn):
    with conn.cursor() as cursor:
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


def new_url_id(url: str, conn) -> tuple | int:
    with conn.cursor() as cursor:
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


def get_url_by_id(id, conn):
    with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        cursor.execute("SELECT * FROM urls WHERE id=%s", (id,))
        result = cursor.fetchone()
        print(result)
        return result


def insert_check(url_id: int, status_code: int, seo_info: dict, conn):
    insert_query = """
    INSERT INTO url_checks
    (url_id, status_code, h1, title, description, created_at)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    with conn.cursor() as cursor:
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


def get_url_checks(id_, conn):
    with conn.cursor() as cursor:
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
