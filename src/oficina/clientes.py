from .base import BaseCRUD

# Métodos para inserir, buscar e listar clientes pessoa física e jurídica
class ClienteCRUD(BaseCRUD):
    def inserir_cliente_pf(self, nome, cpf, data_nascimento, email, telefone, endereco):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO solicitante DEFAULT VALUES RETURNING id_solicitante;")
                id_solicitante = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO cliente (email, telefone, endereco, id_solicitante) VALUES (%s, %s, %s, %s) RETURNING id_cliente;",
                    (email, telefone, endereco, id_solicitante)
                )
                id_cliente = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO pessoa_fisica (id_cliente, cpf, nome, data_nascimento) VALUES (%s, %s, %s, %s);",
                    (id_cliente, cpf, nome, data_nascimento)
                )
                conn.commit()
                print(f"Cliente PF '{nome}' inserido com sucesso! ID: {id_cliente}")
                return id_cliente
        except Exception as e:
            print(f"Erro ao inserir cliente PF: {e}")
            return None

    def inserir_cliente_pj(self, razao_social, cnpj, email, telefone, endereco):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO solicitante DEFAULT VALUES RETURNING id_solicitante;")
                id_solicitante = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO cliente (email, telefone, endereco, id_solicitante) VALUES (%s, %s, %s, %s) RETURNING id_cliente;",
                    (email, telefone, endereco, id_solicitante)
                )
                id_cliente = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO pessoa_juridica (id_cliente, cnpj, razao_social) VALUES (%s, %s, %s);",
                    (id_cliente, cnpj, razao_social)
                )
                conn.commit()
                print(f"Cliente PJ '{razao_social}' inserido com sucesso! ID: {id_cliente}")
                return id_cliente
        except Exception as e:
            print(f"Erro ao inserir cliente PJ: {e}")
            return None

    def listar_clientes(self):
        query = """
        SELECT 
            c.id_cliente, c.email, c.telefone, c.endereco,
            COALESCE(pf.nome, pj.razao_social) as nome_razao,
            CASE WHEN pf.id_cliente IS NOT NULL THEN 'PF' ELSE 'PJ' END as tipo,
            COALESCE(pf.cpf, pj.cnpj) as documento
        FROM cliente c
        LEFT JOIN pessoa_fisica pf ON c.id_cliente = pf.id_cliente
        LEFT JOIN pessoa_juridica pj ON c.id_cliente = pj.id_cliente
        ORDER BY c.id_cliente;
        """
        return self.execute_query(query)

    def buscar_cliente_por_id(self, id_cliente):
        query = """
        SELECT 
            c.id_cliente, c.email, c.telefone, c.endereco,
            COALESCE(pf.nome, pj.razao_social) as nome_razao,
            CASE WHEN pf.id_cliente IS NOT NULL THEN 'PF' ELSE 'PJ' END as tipo,
            COALESCE(pf.cpf, pj.cnpj) as documento,
            pf.data_nascimento
        FROM cliente c
        LEFT JOIN pessoa_fisica pf ON c.id_cliente = pf.id_cliente
        LEFT JOIN pessoa_juridica pj ON c.id_cliente = pj.id_cliente
        WHERE c.id_cliente = %s;
        """
        return self.execute_query(query, (id_cliente,))
