import os
import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

class Database:
    def __init__(self):
        self.params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', 5432),
            'database': os.getenv('DB_NAME', 'projeto_bd'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
        }
        if not self.params['password']:
            raise ValueError("DB_PASSWORD não encontrada no .env")

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(**self.params)
        try:
            yield conn
        finally:
            conn.close()
