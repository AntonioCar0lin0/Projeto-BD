import psycopg2
from psycopg2 import sql, Error
from contextlib import contextmanager
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

class OficinaDatabase:
    def __init__(self):
        """
        Gerenciador de banco de dados para sistema de oficina mecânica
        Configurações são carregadas do arquivo .env
        """
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'projeto_bd'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'port': int(os.getenv('DB_PORT', 5432))
        }
        
        # Verifica se a senha foi fornecida
        if not self.connection_params['password']:
            raise ValueError("DB_PASSWORD não encontrada no arquivo .env")
    
    @contextmanager
    def get_connection(self):
        """Context manager para gerenciar conexões de forma segura"""
        connection = None
        try:
            connection = psycopg2.connect(**self.connection_params)
            yield connection
        except Error as e:
            print(f"Erro ao conectar com o banco: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def test_connection(self):
        """Testa a conexão com o banco de dados"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"Conexão bem-sucedida! Versão PostgreSQL: {version[0]}")
                return True
        except Error as e:
            print(f"Erro na conexão: {e}")
            return False
    
    def execute_query(self, query, params=None, fetch=True):
        """Executa uma query no banco de dados"""
        try:
            with self.get_connection() as conn:
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

    # MÉTODOS PARA CLIENTES
    
    def inserir_cliente_pf(self, nome, cpf, data_nascimento, email, telefone, endereco):
        """Insere um cliente pessoa física"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Inserir solicitante
                cursor.execute("INSERT INTO solicitante DEFAULT VALUES RETURNING id_solicitante;")
                id_solicitante = cursor.fetchone()[0]
                
                # Inserir cliente
                cursor.execute("""
                    INSERT INTO cliente (email, telefone, endereco, id_solicitante) 
                    VALUES (%s, %s, %s, %s) RETURNING id_cliente;
                """, (email, telefone, endereco, id_solicitante))
                id_cliente = cursor.fetchone()[0]
                
                # Inserir pessoa física
                cursor.execute("""
                    INSERT INTO pessoa_fisica (id_cliente, cpf, nome, data_nascimento) 
                    VALUES (%s, %s, %s, %s);
                """, (id_cliente, cpf, nome, data_nascimento))
                
                conn.commit()
                print(f"Cliente PF '{nome}' inserido com sucesso! ID: {id_cliente}")
                return id_cliente
                
        except Error as e:
            print(f"Erro ao inserir cliente PF: {e}")
            return None
    
    def inserir_cliente_pj(self, razao_social, cnpj, email, telefone, endereco):
        """Insere um cliente pessoa jurídica"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Inserir solicitante
                cursor.execute("INSERT INTO solicitante DEFAULT VALUES RETURNING id_solicitante;")
                id_solicitante = cursor.fetchone()[0]
                
                # Inserir cliente
                cursor.execute("""
                    INSERT INTO cliente (email, telefone, endereco, id_solicitante) 
                    VALUES (%s, %s, %s, %s) RETURNING id_cliente;
                """, (email, telefone, endereco, id_solicitante))
                id_cliente = cursor.fetchone()[0]
                
                # Inserir pessoa jurídica
                cursor.execute("""
                    INSERT INTO pessoa_juridica (id_cliente, cnpj, razao_social) 
                    VALUES (%s, %s, %s);
                """, (id_cliente, cnpj, razao_social))
                
                conn.commit()
                print(f"Cliente PJ '{razao_social}' inserido com sucesso! ID: {id_cliente}")
                return id_cliente
                
        except Error as e:
            print(f"Erro ao inserir cliente PJ: {e}")
            return None
    
    def listar_clientes(self):
        """Lista todos os clientes (PF e PJ)"""
        query = """
        SELECT 
            c.id_cliente,
            c.email,
            c.telefone,
            c.endereco,
            COALESCE(pf.nome, pj.razao_social) as nome_razao,
            CASE 
                WHEN pf.id_cliente IS NOT NULL THEN 'PF'
                ELSE 'PJ'
            END as tipo,
            COALESCE(pf.cpf, pj.cnpj) as documento
        FROM cliente c
        LEFT JOIN pessoa_fisica pf ON c.id_cliente = pf.id_cliente
        LEFT JOIN pessoa_juridica pj ON c.id_cliente = pj.id_cliente
        ORDER BY c.id_cliente;
        """
        return self.execute_query(query)
    
    def buscar_cliente_por_id(self, id_cliente):
        """Busca cliente por ID com informações completas"""
        query = """
        SELECT 
            c.id_cliente,
            c.email,
            c.telefone,
            c.endereco,
            COALESCE(pf.nome, pj.razao_social) as nome_razao,
            CASE 
                WHEN pf.id_cliente IS NOT NULL THEN 'PF'
                ELSE 'PJ'
            END as tipo,
            COALESCE(pf.cpf, pj.cnpj) as documento,
            pf.data_nascimento
        FROM cliente c
        LEFT JOIN pessoa_fisica pf ON c.id_cliente = pf.id_cliente
        LEFT JOIN pessoa_juridica pj ON c.id_cliente = pj.id_cliente
        WHERE c.id_cliente = %s;
        """
        return self.execute_query(query, (id_cliente,))

    # MÉTODOS PARA MECÂNICOS
    
    def inserir_mecanico_efetivo(self, nome, telefone, especialidade, salario, registro_clt):
        """Insere um mecânico efetivo"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Inserir solicitante
                cursor.execute("INSERT INTO solicitante DEFAULT VALUES RETURNING id_solicitante;")
                id_solicitante = cursor.fetchone()[0]
                
                # Inserir mecânico
                cursor.execute("""
                    INSERT INTO mecanico (nome, telefone, especialidade, tipo_mecanico, id_solicitante) 
                    VALUES (%s, %s, %s, 'efetivo', %s) RETURNING matricula_mec;
                """, (nome, telefone, especialidade, id_solicitante))
                matricula = cursor.fetchone()[0]
                
                # Inserir dados específicos de efetivo
                cursor.execute("""
                    INSERT INTO efetivo (id_mecanico, salario, registro_clt) 
                    VALUES (%s, %s, %s);
                """, (matricula, salario, registro_clt))
                
                conn.commit()
                print(f"Mecânico efetivo '{nome}' inserido com sucesso! Matrícula: {matricula}")
                return matricula
                
        except Error as e:
            print(f"Erro ao inserir mecânico efetivo: {e}")
            return None
    
    def inserir_mecanico_freelancer(self, nome, telefone, especialidade, hora_servico):
        """Insere um mecânico freelancer"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Inserir solicitante
                cursor.execute("INSERT INTO solicitante DEFAULT VALUES RETURNING id_solicitante;")
                id_solicitante = cursor.fetchone()[0]
                
                # Inserir mecânico
                cursor.execute("""
                    INSERT INTO mecanico (nome, telefone, especialidade, tipo_mecanico, id_solicitante) 
                    VALUES (%s, %s, %s, 'freelancer', %s) RETURNING matricula_mec;
                """, (nome, telefone, especialidade, id_solicitante))
                matricula = cursor.fetchone()[0]
                
                # Inserir dados específicos de freelancer
                cursor.execute("""
                    INSERT INTO freelancer (id_mecanico, hora_servico) 
                    VALUES (%s, %s);
                """, (matricula, hora_servico))
                
                conn.commit()
                print(f"Mecânico freelancer '{nome}' inserido com sucesso! Matrícula: {matricula}")
                return matricula
                
        except Error as e:
            print(f"Erro ao inserir mecânico freelancer: {e}")
            return None
    
    def listar_mecanicos(self):
        """Lista todos os mecânicos com informações completas"""
        query = """
        SELECT 
            m.matricula_mec,
            m.nome,
            m.telefone,
            m.especialidade,
            m.tipo_mecanico,
            COALESCE(e.salario, f.hora_servico) as valor,
            e.registro_clt
        FROM mecanico m
        LEFT JOIN efetivo e ON m.matricula_mec = e.id_mecanico
        LEFT JOIN freelancer f ON m.matricula_mec = f.id_mecanico
        ORDER BY m.matricula_mec;
        """
        return self.execute_query(query)

    # MÉTODOS PARA VEÍCULOS
    
    def inserir_carro(self, marca, cor, modelo, ano, id_cliente, numero_portas, tipo_combustivel, capacidade_passageiros):
        """Insere um carro"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Inserir veículo
                cursor.execute("""
                    INSERT INTO veiculo (marca, cor, modelo, ano, id_cliente) 
                    VALUES (%s, %s, %s, %s, %s) RETURNING veiculo_id;
                """, (marca, cor, modelo, ano, id_cliente))
                veiculo_id = cursor.fetchone()[0]
                
                # Inserir dados específicos do carro
                cursor.execute("""
                    INSERT INTO carro (veiculo_id, numero_portas, tipo_combustivel, capacidade_passageiros) 
                    VALUES (%s, %s, %s, %s);
                """, (veiculo_id, numero_portas, tipo_combustivel, capacidade_passageiros))
                
                conn.commit()
                print(f"Carro {marca} {modelo} inserido com sucesso! ID: {veiculo_id}")
                return veiculo_id
                
        except Error as e:
            print(f"Erro ao inserir carro: {e}")
            return None
    
    def inserir_moto(self, marca, cor, modelo, ano, id_cliente, cilindrada, tipo_moto):
        """Insere uma moto"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Inserir veículo
                cursor.execute("""
                    INSERT INTO veiculo (marca, cor, modelo, ano, id_cliente) 
                    VALUES (%s, %s, %s, %s, %s) RETURNING veiculo_id;
                """, (marca, cor, modelo, ano, id_cliente))
                veiculo_id = cursor.fetchone()[0]
                
                # Inserir dados específicos da moto
                cursor.execute("""
                    INSERT INTO moto (veiculo_id, cilindrada, tipo_moto) 
                    VALUES (%s, %s, %s);
                """, (veiculo_id, cilindrada, tipo_moto))
                
                conn.commit()
                print(f"Moto {marca} {modelo} inserida com sucesso! ID: {veiculo_id}")
                return veiculo_id
                
        except Error as e:
            print(f"Erro ao inserir moto: {e}")
            return None
    
    def listar_veiculos_cliente(self, id_cliente):
        """Lista todos os veículos de um cliente"""
        query = """
        SELECT 
            v.veiculo_id,
            v.marca,
            v.cor,
            v.modelo,
            v.ano,
            CASE 
                WHEN c.veiculo_id IS NOT NULL THEN 'Carro'
                ELSE 'Moto'
            END as tipo_veiculo,
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

    # MÉTODOS PARA ORDENS DE SERVIÇO
    
    def criar_ordem_servico(self, descricao, id_solicitante, data_abertura=None, status='Aberta'):
        """Cria uma nova ordem de serviço"""
        if data_abertura is None:
            data_abertura = date.today()
        
        query = """
        INSERT INTO ordem_servico (descricao, data_abertura, status, id_solicitante) 
        VALUES (%s, %s, %s, %s) RETURNING id_os;
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (descricao, data_abertura, status, id_solicitante))
                id_os = cursor.fetchone()[0]
                conn.commit()
                print(f"Ordem de serviço criada com sucesso! ID: {id_os}")
                return id_os
        except Error as e:
            print(f"Erro ao criar ordem de serviço: {e}")
            return None
    
    def listar_ordens_servico(self, status=None):
        """Lista ordens de serviço, opcionalmente filtradas por status"""
        query = """
        SELECT 
            os.id_os,
            os.descricao,
            os.data_abertura,
            os.status,
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
        """Atualiza o status de uma ordem de serviço"""
        query = "UPDATE ordem_servico SET status = %s WHERE id_os = %s;"
        result = self.execute_query(query, (novo_status, id_os), fetch=False)
        if result:
            print(f"Status da OS {id_os} atualizado para '{novo_status}'")
        return result

    # MÉTODOS PARA PEÇAS
    
    def inserir_peca(self, nome_peca, qt_estoque, valor_uni):
        """Insere uma nova peça no estoque"""
        query = """
        INSERT INTO peca (nome_peca, qt_estoque, valor_uni) 
        VALUES (%s, %s, %s) RETURNING cod_peca;
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (nome_peca, qt_estoque, valor_uni))
                cod_peca = cursor.fetchone()[0]
                conn.commit()
                print(f"Peça '{nome_peca}' inserida com sucesso! Código: {cod_peca}")
                return cod_peca
        except Error as e:
            print(f"Erro ao inserir peça: {e}")
            return None
    
    def listar_estoque(self, estoque_baixo=None):
        """Lista o estoque de peças, opcionalmente mostrando apenas estoque baixo"""
        query = "SELECT cod_peca, nome_peca, qt_estoque, valor_uni FROM peca"
        params = None
        
        if estoque_baixo:
            query += " WHERE qt_estoque <= %s"
            params = (estoque_baixo,)
        
        query += " ORDER BY nome_peca;"
        
        return self.execute_query(query, params)
    
    def atualizar_estoque(self, cod_peca, nova_quantidade):
        """Atualiza a quantidade em estoque de uma peça"""
        query = "UPDATE peca SET qt_estoque = %s WHERE cod_peca = %s;"
        result = self.execute_query(query, (nova_quantidade, cod_peca), fetch=False)
        if result:
            print(f"Estoque da peça {cod_peca} atualizado para {nova_quantidade}")
        return result

    # RELATÓRIOS E CONSULTAS AVANÇADAS
    
    def relatorio_os_por_status(self):
        """Relatório de ordens de serviço agrupadas por status"""
        query = """
        SELECT 
            status,
            COUNT(*) as quantidade,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ordem_servico), 2) as percentual
        FROM ordem_servico 
        GROUP BY status 
        ORDER BY quantidade DESC;
        """
        return self.execute_query(query)
    
    def relatorio_servicos_por_mecanico(self):
        """Relatório de serviços executados por mecânico"""
        query = """
        SELECT 
            m.nome,
            m.especialidade,
            COUNT(es.id_servico) as servicos_executados,
            SUM(EXTRACT(EPOCH FROM es.tempo_gasto)/3600) as horas_trabalhadas
        FROM mecanico m
        LEFT JOIN execucao_servico es ON m.matricula_mec = es.id_mecanico
        GROUP BY m.matricula_mec, m.nome, m.especialidade
        ORDER BY servicos_executados DESC;
        """
        return self.execute_query(query)
    
    def clientes_mais_ativos(self, limite=10):
        """Lista os clientes mais ativos (com mais ordens de serviço)"""
        query = """
        SELECT 
            COALESCE(pf.nome, pj.razao_social) as cliente,
            c.email,
            c.telefone,
            COUNT(os.id_os) as total_os,
            MAX(os.data_abertura) as ultima_os
        FROM cliente c
        LEFT JOIN pessoa_fisica pf ON c.id_cliente = pf.id_cliente
        LEFT JOIN pessoa_juridica pj ON c.id_cliente = pj.id_cliente
        LEFT JOIN ordem_servico os ON c.id_solicitante = os.id_solicitante
        GROUP BY c.id_cliente, COALESCE(pf.nome, pj.razao_social), c.email, c.telefone
        HAVING COUNT(os.id_os) > 0
        ORDER BY total_os DESC
        LIMIT %s;
        """
        return self.execute_query(query, (limite,))

    def to_dataframe(self, query_result):
        """Converte resultado da query para DataFrame do pandas"""
        if query_result and 'columns' in query_result and 'data' in query_result:
            return pd.DataFrame(query_result['data'], columns=query_result['columns'])
        return pd.DataFrame()

def main():
    try:
        # Instancia o banco de dados (configurações vêm do .env)
        db = OficinaDatabase()
        
        print("=== SISTEMA DE OFICINA MECÂNICA ===")
        print("\n=== TESTE DE CONEXÃO ===")
        if not db.test_connection():
            print("Falha na conexão. Verifique as configurações no arquivo .env")
            return
        
        print("\n=== LISTANDO CLIENTES EXISTENTES ===")
        clientes = db.listar_clientes()
        if clientes:
            df_clientes = db.to_dataframe(clientes)
            print(df_clientes.to_string(index=False))
        
        print("\n=== LISTANDO MECÂNICOS ===")
        mecanicos = db.listar_mecanicos()
        if mecanicos:
            df_mecanicos = db.to_dataframe(mecanicos)
            print(df_mecanicos.to_string(index=False))
        
        print("\n=== ORDENS DE SERVIÇO ===")
        ordens = db.listar_ordens_servico()
        if ordens:
            df_ordens = db.to_dataframe(ordens)
            print(df_ordens.to_string(index=False))
        
        print("\n=== RELATÓRIO DE OS POR STATUS ===")
        status_report = db.relatorio_os_por_status()
        if status_report:
            df_status = db.to_dataframe(status_report)
            print(df_status.to_string(index=False))
        
        print("\n=== ESTOQUE DE PEÇAS ===")
        estoque = db.listar_estoque()
        if estoque:
            df_estoque = db.to_dataframe(estoque)
            print(df_estoque.to_string(index=False))
        
        print("\n=== CLIENTES MAIS ATIVOS ===")
        clientes_ativos = db.clientes_mais_ativos(5)
        if clientes_ativos:
            df_ativos = db.to_dataframe(clientes_ativos)
            print(df_ativos.to_string(index=False))
    
    except ValueError as e:
        print(f"Erro de configuração: {e}")
        print("Verifique se o arquivo .env existe e contém todas as variáveis necessárias.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()