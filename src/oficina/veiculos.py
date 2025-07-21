from .base import BaseCRUD

# Faz os inserts e listagem dos veículos associados aos clientes
class VeiculoCRUD(BaseCRUD):
    def inserir_carro(self, marca, cor, modelo, ano, id_cliente, numero_portas, tipo_combustivel, capacidade_passageiros):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO veiculo (marca, cor, modelo, ano, id_cliente) VALUES (%s, %s, %s, %s, %s) RETURNING veiculo_id;",
                    (marca, cor, modelo, ano, id_cliente)
                )
                veiculo_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO carro (veiculo_id, numero_portas, tipo_combustivel, capacidade_passageiros) VALUES (%s, %s, %s, %s);",
                    (veiculo_id, numero_portas, tipo_combustivel, capacidade_passageiros)
                )
                conn.commit()
                return veiculo_id
        except Exception as e:
            print(f"Erro ao inserir carro: {e}")
            return None

    def inserir_moto(self, marca, cor, modelo, ano, id_cliente, cilindrada, tipo_moto):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO veiculo (marca, cor, modelo, ano, id_cliente) VALUES (%s, %s, %s, %s, %s) RETURNING veiculo_id;",
                    (marca, cor, modelo, ano, id_cliente)
                )
                veiculo_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO moto (veiculo_id, cilindrada, tipo_moto) VALUES (%s, %s, %s);",
                    (veiculo_id, cilindrada, tipo_moto)
                )
                conn.commit()
                return veiculo_id
        except Exception as e:
            print(f"Erro ao inserir moto: {e}")
            return None

    def listar_veiculos_cliente(self, id_cliente):
        query = """
        SELECT 
            v.veiculo_id, v.marca, v.cor, v.modelo, v.ano,
            CASE WHEN c.veiculo_id IS NOT NULL THEN 'Carro' ELSE 'Moto' END as tipo_veiculo,
            COALESCE(
                CONCAT(c.numero_portas, ' portas, ', c.tipo_combustivel, ', ', c.capacidade_passageiros, ' passageiros'),
                CONCAT(m.cilindrada, 'cc, ', m.tipo_moto)
            ) as detalhes
        FROM veiculo v
        LEFT JOIN carro c ON v.veiculo_id = c.veiculo_id
        LEFT JOIN moto m ON v.veiculo_id = m.veiculo_id
        WHERE v.id_cliente = %s
        ORDER BY v.veiculo_id;
        """
        return self.execute_query(query, (id_cliente,))
