from .db import Database
from psycopg2 import Error

# Define um método para ser reutilizadob nos outros códigos
class BaseCRUD:
    def __init__(self):
        self.db = Database()

    def execute_query(self, query, params=None, fetch=True):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetch and cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()
                    return {'columns': columns, 'data': results}
                elif not fetch:
                    conn.commit()
                    return cursor.rowcount
        except Error as e:
            print(f"Erro ao executar query: {e}")
            return None
