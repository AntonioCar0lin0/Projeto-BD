from db import get_conn

with get_conn() as conn:            # abre e fecha conexão automaticamente
    with conn.cursor() as cur:
        # 1) inserir solicitante
        cur.execute(
            "INSERT INTO solicitante DEFAULT VALUES RETURNING id_solicitante"
        )
        id_solic = cur.fetchone()[0]
        print("✔ solicitante:", id_solic)

        # 2) inserir cliente
        cur.execute(
            """
            INSERT INTO cliente (email, telefone, endereco, id_solicitante)
            VALUES (%s, %s, %s, %s)
            RETURNING id_cliente
            """,
            ("teste@ex.com", "81990000000", "Rua Exemplo, 123", id_solic),
        )
        id_cli = cur.fetchone()[0]
        print("✔ cliente:", id_cli)

        # 3) total de clientes
        cur.execute("SELECT COUNT(*) FROM cliente")
        print("📊 total:", cur.fetchone()[0])

        # 4) atualizar telefone
        cur.execute(
            "UPDATE cliente SET telefone = %s WHERE id_cliente = %s",
            ("81998887766", id_cli),
        )
        print("✔ telefone atualizado")

print("💾 transações commitadas; conexão encerrada")
