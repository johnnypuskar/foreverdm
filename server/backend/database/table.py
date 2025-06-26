import psycopg
import os
from contextlib import contextmanager

class Table:
    DB_NAME = "foreverdm"

    def __init__(self):
        self._conn = Table._new_connection()
        self._cursor = self._conn.cursor()
        print("INSTANCE CURSOR", self._cursor)
    
    def commit(self, close = True):
        self._conn.commit()
        if close:
            self.close()
    
    def close(self):
        self._conn.close()

    @staticmethod
    def _new_connection():
        return psycopg.connect(f"""\
            dbname={Table.DB_NAME} \
            user={os.getenv('POSTGRES_USER')} \
            password={os.getenv('POSTGRES_PASSWORD')} \
            host={os.getenv('DB_ADDRESS')} \
            port={os.getenv('DB_PORT')} \
        """)

    @staticmethod
    @contextmanager
    def cursor():
        print("CALLED THE STATIC CURSOR METHOD")
        conn = Table._new_connection()
        try:
            yield conn.cursor()
        finally:
            conn.commit()
            conn.close()