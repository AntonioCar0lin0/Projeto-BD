from .base import BaseCRUD

# CRUD de mecânicos seja efetivo ou freelancer
class MecanicoCRUD(BaseCRUD):
    def inserir_efetivo(self, nome, telefone, especialidade, salario, registro_clt):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO solicitante DEFAULT VALUES RETURNING id_solicitante;")
                id_solicitante = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO mecanico (nome, telefone, especialidade, tipo_mecanico, id_solicitante) VALUES (%s, %s, %s, 'efetivo', %s) RETURNING matricula_mec;",
                    (nome, telefone, especialidade, id_solicitante)
                )
                matricula = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO efetivo (id_mecanico, salario, registro_clt) VALUES (%s, %s, %s);",
                    (matricula, salario, registro_clt)
                )
                conn.commit()
                print(f"Mecanico efetivo '{nome}' inserido com sucesso!")
                return matricula
        except Exception as e:
            print(f"Erro ao inserir efetivo: {e}")
            return None

    def inserir_freelancer(self, nome, telefone, especialidade, hora_servico):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO solicitante DEFAULT VALUES RETURNING id_solicitante;")
                id_solicitante = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO mecanico (nome, telefone, especialidade, tipo_mecanico, id_solicitante) VALUES (%s, %s, %s, 'freelancer', %s) RETURNING matricula_mec;",
                    (nome, telefone, especialidade, id_solicitante)
                )
                matricula = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO freelancer (id_mecanico, hora_servico) VALUES (%s, %s);",
                    (matricula, hora_servico)
                )
                conn.commit()
                print(f"Mecanico freelancer '{nome}' inserido com sucesso!")
                return matricula
        except Exception as e:
            print(f"Erro ao inserir freelancer: {e}")
            return None

    def listar_mecanicos(self):
        query = """
        SELECT 
            m.matricula_mec, m.nome, m.telefone, m.especialidade, m.tipo_mecanico,
            COALESCE(e.salario, f.hora_servico) as valor, e.registro_clt
        FROM mecanico m
        LEFT JOIN efetivo e ON m.matricula_mec = e.id_mecanico
        LEFT JOIN freelancer f ON m.matricula_mec = f.id_mecanico
        ORDER BY m.matricula_mec;
        """
        return self.execute_query(query)
