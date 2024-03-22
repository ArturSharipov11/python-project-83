import os
from dotenv import load_dotenv


load_dotenv()
ROOT = f'{os.path.dirname(__file__)}/..'
DATABASE_URL = os.getenv('DATABASE_URL')


def execute_sql_script(conn):
    path = f'{ROOT}/database.sql'
    with open(path) as f:
        script = f.read()
    with conn.cursor() as cursor:
        cursor.execute(script)