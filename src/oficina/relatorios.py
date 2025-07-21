from .base import BaseCRUD

class RelatorioCRUD(BaseCRUD):
    def os_por_status(self):
        query = """
        SELECT status, COUNT(*) as quantidade,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ordem_servico), 2) as percentual
        FROM ordem_servico 
        GROUP BY status 
        ORDER BY quantidade DESC;
        """
        return self.execute_query(query)

    def servicos_por_mecanico(self):
        query = """
        SELECT m.nome, m.especialidade,
        COUNT(es.id_servico) as servicos_executados,
        SUM(EXTRACT(EPOCH FROM es.tempo_gasto)/3600) as horas_trabalhadas
        FROM mecanico m
        LEFT JOIN execucao_servico es ON m.matricula_mec = es.id_mecanico
        GROUP BY m.matricula_mec, m.nome, m.especialidade
        ORDER BY servicos_executados DESC;
        """
        return self.execute_query(query)

    def clientes_mais_ativos(self, limite=10):
        query = """
        SELECT COALESCE(pf.nome, pj.razao_social) as cliente, c.email, c.telefone,
        COUNT(os.id_os) as total_os, MAX(os.data_abertura) as ultima_os
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
