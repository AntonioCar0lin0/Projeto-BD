from .base import BaseCRUD

# Realiza o cadastro de peças e controle de estoque
class PecaCRUD(BaseCRUD):
    def inserir_peca(self, nome_peca, qt_estoque, valor_uni):
        query = "INSERT INTO peca (nome_peca, qt_estoque, valor_uni) VALUES (%s, %s, %s) RETURNING cod_peca;"
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (nome_peca, qt_estoque, valor_uni))
                cod_peca = cursor.fetchone()[0]
                conn.commit()
                print(f"Peca '{nome_peca}' inserida com sucesso!")
                return cod_peca
        except Exception as e:
            print(f"Erro ao inserir peca: {e}")
            return None

    def listar_estoque(self, estoque_baixo=None):
        query = "SELECT cod_peca, nome_peca, qt_estoque, valor_uni FROM peca"
        params = None
        if estoque_baixo:
            query += " WHERE qt_estoque <= %s"
            params = (estoque_baixo,)
        query += " ORDER BY nome_peca;"
        return self.execute_query(query, params)

    def atualizar_estoque(self, cod_peca, nova_quantidade):
        query = "UPDATE peca SET qt_estoque = %s WHERE cod_peca = %s;"
        result = self.execute_query(query, (nova_quantidade, cod_peca), fetch=False)
        if result:
            print(f"Estoque da peca {cod_peca} atualizado para {nova_quantidade}")
        return result
