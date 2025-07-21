<img width="973" height="414" alt="image" src="https://github.com/user-attachments/assets/1d823c30-54a0-4d78-80e1-ca44c33ffbab" /># Projeto de BD - Sistema de Oficina Mecânica

Este projeto simula o funcionamento de uma oficina mecânica com controle de clientes, veículos, mecânicos, ordens de serviço e peças. Utilizamos a linguagem Python para integrar com O SQL

## Como rodar o código:

1. **Instale as dependências:**
_pip install -r requirements.txt_

2. **Crie o banco de dados no PostgreSQL:**
__CREATE DATABASE projeto_bd;_
Ou execute o arquivo create_database.sql
_Obs: As tabelas são criadas automaticamente nessa implementação do código_

3. **Configure um arquivo .env (exemplo):**

DB_HOST=localhost
DB_PORT=5432
DB_NAME=projeto_bd
DB_USER=postgres
DB_PASSWORD=sua_senha

4. **Execute no terminal:**
_cd src_
_python main.py_

```
Projeto-BD/
├── .env                   # Dados de conexão com o banco
├── requirements.txt       # Dependências do Python
├── README.md              # Este arquivo
├── projeto.sql            # Script opcional com a criação manual do banco
└── src/
    ├── main.py            # Script principal de execução
    └── oficina/           # Módulo com toda a lógica do sistema
        ├── __init__.py           # Torna a pasta um pacote Python
        ├── base.py               # Classe base com execute_query() reaproveitada por todos os CRUDs
        ├── db.py                 # Faz a conexão com o banco, usando .env
        ├── setup.py              # Cria todas as tabelas do banco automaticamente
        ├── clientes.py           # CRUD de clientes pessoa física e jurídica
        ├── mecanicos.py          # CRUD de mecânicos efetivos e freelancers
        ├── veiculos.py           # CRUD de carros e motos associados a clientes
        ├── ordens_servico.py     # Criação, atualização e listagem de ordens de serviço
        ├── pecas.py              # Cadastro de peças e controle de estoque
        └── relatorios.py         # Relatórios por status, clientes mais ativos e serviços executados
