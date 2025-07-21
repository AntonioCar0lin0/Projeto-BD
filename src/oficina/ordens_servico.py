from .base import BaseCRUD
from datetime import date

# Faz a criação, listagem e atualização das ordens de serviço
class OrdemServicoCRUD(BaseCRUD):
    def criar_ordem_servico(self, descricao, id_solicitante, data_abertura=None, status='Aberta'):
        if data_abertura is None:
            data_abertura = date.today()
        query = """
        INSERT INTO ordem_servico (descricao, data_abertura, status, id_solicitante) 
        VALUES (%s, %s, %s, %s) RETURNING id_os;
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (descricao, data_abertura, status, id_solicitante))
                id_os = cursor.fetchone()[0]
                conn.commit()
                print(f"Ordem de serviço criada com sucesso! ID: {id_os}")
                return id_os
        except Exception as e:
            print(f"Erro ao criar OS: {e}")
            return None

    def listar_ordens_servico(self, status=None):
        query = """
        SELECT 
            os.id_os, os.descricao, os.data_abertura, os.status,
            COALESCE(pf.nome, pj.razao_social) as solicitante
        FROM ordem_servico os
        JOIN solicitante s ON os.id_solicitante = s.id_solicitante
        LEFT JOIN cliente c ON s.id_solicitante = c.id_solicitante
        LEFT JOIN pessoa_fisica pf ON c.id_cliente = pf.id_cliente
        LEFT JOIN pessoa_juridica pj ON c.id_cliente = pj.id_cliente
        """
        params = None
        if status:
            query += " WHERE os.status = %s"
            params = (status,)
        query += " ORDER BY os.id_os DESC;"
        return self.execute_query(query, params)

    def atualizar_status_os(self, id_os, novo_status):
        query = "UPDATE ordem_servico SET status = %s WHERE id_os = %s;"
        result = self.execute_query(query, (novo_status, id_os), fetch=False)
        if result:
            print(f"Status da OS {id_os} atualizado para '{novo_status}'")
        return result
