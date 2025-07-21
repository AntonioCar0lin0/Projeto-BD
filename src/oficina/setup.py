from .db import Database

# Faz a criação do database a partir das querys existentes
class SetupDatabase:
    def __init__(self):
        self.db = Database()

    def criar_tabelas(self):
        comandos = [
            """CREATE TABLE IF NOT EXISTS solicitante (
                id_solicitante SERIAL PRIMARY KEY
            );""",
            """CREATE TABLE IF NOT EXISTS cliente (
                id_cliente SERIAL PRIMARY KEY,
                email VARCHAR(100) NOT NULL,
                telefone VARCHAR(15) NOT NULL,
                endereco VARCHAR(255),
                id_solicitante INTEGER UNIQUE REFERENCES solicitante(id_solicitante)
            );""",
            """CREATE TABLE IF NOT EXISTS pessoa_fisica (
                id_cliente INTEGER PRIMARY KEY REFERENCES cliente(id_cliente),
                cpf CHAR(11) UNIQUE NOT NULL,
                nome VARCHAR(100),
                data_nascimento DATE
            );""",
            """CREATE TABLE IF NOT EXISTS pessoa_juridica (
                id_cliente INTEGER PRIMARY KEY REFERENCES cliente(id_cliente),
                cnpj CHAR(14) UNIQUE NOT NULL,
                razao_social VARCHAR(255)
            );""",
            """CREATE TABLE IF NOT EXISTS mecanico (
                matricula_mec SERIAL PRIMARY KEY,
                nome VARCHAR(100),
                telefone VARCHAR(15),
                especialidade VARCHAR(100),
                tipo_mecanico VARCHAR(20),
                id_solicitante INTEGER REFERENCES solicitante(id_solicitante)
            );""",
            """CREATE TABLE IF NOT EXISTS efetivo (
                id_mecanico INTEGER PRIMARY KEY REFERENCES mecanico(matricula_mec),
                salario NUMERIC(10,2),
                registro_clt VARCHAR(50)
            );""",
            """CREATE TABLE IF NOT EXISTS freelancer (
                id_mecanico INTEGER PRIMARY KEY REFERENCES mecanico(matricula_mec),
                hora_servico NUMERIC(10,2)
            );""",
            """CREATE TABLE IF NOT EXISTS veiculo (
                veiculo_id SERIAL PRIMARY KEY,
                marca VARCHAR(50),
                cor VARCHAR(30),
                modelo VARCHAR(50),
                ano INTEGER,
                id_cliente INTEGER REFERENCES cliente(id_cliente)
            );""",
            """CREATE TABLE IF NOT EXISTS carro (
                veiculo_id INTEGER PRIMARY KEY REFERENCES veiculo(veiculo_id),
                numero_portas INTEGER,
                tipo_combustivel VARCHAR(30),
                capacidade_passageiros INTEGER
            );""",
            """CREATE TABLE IF NOT EXISTS moto (
                veiculo_id INTEGER PRIMARY KEY REFERENCES veiculo(veiculo_id),
                cilindrada INTEGER,
                tipo_moto VARCHAR(50)
            );""",
            """CREATE TABLE IF NOT EXISTS ordem_servico (
                id_os SERIAL PRIMARY KEY,
                descricao TEXT,
                data_abertura DATE,
                status VARCHAR(20),
                id_solicitante INTEGER REFERENCES solicitante(id_solicitante)
            );""",
            """CREATE TABLE IF NOT EXISTS servico (
                id_servico SERIAL PRIMARY KEY,
                tempo_estimado INTEGER,
                valor_padrao NUMERIC(10, 2),
                cod_os INTEGER REFERENCES ordem_servico(id_os)
            );""",
            """CREATE TABLE IF NOT EXISTS execucao_servico (
                id_execucao SERIAL PRIMARY KEY,
                id_os INTEGER REFERENCES ordem_servico(id_os),
                id_mecanico INTEGER REFERENCES mecanico(matricula_mec),
                id_servico INTEGER REFERENCES servico(id_servico),
                tempo_gasto INTERVAL
            );""",
            """CREATE TABLE IF NOT EXISTS peca (
                cod_peca SERIAL PRIMARY KEY,
                nome_peca VARCHAR(100),
                qt_estoque INTEGER,
                valor_uni NUMERIC(10,2)
            );""",
            """CREATE TABLE IF NOT EXISTS utiliza_peca (
                id_os INTEGER REFERENCES ordem_servico(id_os),
                id_peca INTEGER REFERENCES peca(cod_peca),
                quantidade INTEGER NOT NULL,
                PRIMARY KEY (id_os, id_peca)
            );"""
        ]

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                for comando in comandos:
                    cursor.execute(comando)
                conn.commit()
                print(" Tabelas criadas com sucesso.")
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
