import psycopg
import os
from contextlib import contextmanager

class Table:
    DB_NAME = "foreverdm"

    @staticmethod
    @contextmanager
    def cursor():
        conn = psycopg.connect(f"""\
            dbname={Table.DB_NAME} \
            user={os.getenv('POSTGRES_USER')} \
            password={os.getenv('POSTGRES_PASSWORD')} \
            host={os.getenv('DB_ADDRESS')} \
            port={os.getenv('DB_PORT')} \
        """)
        try:
            yield conn.cursor()
        finally:
            conn.commit()
            conn.close()