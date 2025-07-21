from oficina.setup import SetupDatabase
from oficina.clientes import ClienteCRUD
from oficina.mecanicos import MecanicoCRUD
from oficina.veiculos import VeiculoCRUD
from oficina.ordens_servico import OrdemServicoCRUD
from oficina.pecas import PecaCRUD
from oficina.relatorios import RelatorioCRUD



# Testes aleatórios utilizando as funções para testar o uso delas


# 1. Criar tabelas
print("Criaçao das tabelas do BD")
SetupDatabase().criar_tabelas()

# 2. Inserir cliente pessoa física
cliente_crud = ClienteCRUD()
id_cliente = cliente_crud.inserir_cliente_pf(
    nome="Beatriz Andrade",
    cpf="12345678901",
    data_nascimento="1995-05-12",
    email="bia@exemplo.com",
    telefone="81990000000",
    endereco="Rua das Oficinas, 456"
)

# 3. Inserir mecânico efetivo
mecanico_crud = MecanicoCRUD()
id_mec = mecanico_crud.inserir_efetivo(
    nome="Pedro Mecanico",
    telefone="81998887777",
    especialidade="Freio",
    salario=3200.00,
    registro_clt="CLT9876"
)

# 4. Inserir veículo (carro)
veiculo_crud = VeiculoCRUD()
veiculo_id = veiculo_crud.inserir_carro(
    marca="Fiat",
    cor="Prata",
    modelo="Uno",
    ano=2010,
    id_cliente=id_cliente,
    numero_portas=4,
    tipo_combustivel="Gasolina",
    capacidade_passageiros=5
)

# 5. Criar ordem de serviço
ordem_crud = OrdemServicoCRUD()
id_os = ordem_crud.criar_ordem_servico(
    descricao="Troca de oleo e revisao de freios",
    id_solicitante=1  
)

# 6. Inserir peça
peca_crud = PecaCRUD()
peca_id = peca_crud.inserir_peca("Pastilha de Freio", 20, 45.50)

# 7. Listar clientes cadastrados
print("\nClientes cadastrados:")
resultado = cliente_crud.listar_clientes()
if resultado:
    for row in resultado['data']:
        print(row)

# 8. Listar mecânicos
print("\nMecanicos cadastrados:")
resultado = mecanico_crud.listar_mecanicos()
if resultado:
    for row in resultado['data']:
        print(row)

# 9. Listar peças em estoque
print("\nPecas em estoque:")
resultado = peca_crud.listar_estoque()
if resultado:
    for row in resultado['data']:
        print(row)

# 10. Mostrar relatório 
print("\nRelatóoio de ordens de servico por status:")
relatorios = RelatorioCRUD()
resultado = relatorios.os_por_status()
if resultado:
    for row in resultado['data']:
        print(row)
