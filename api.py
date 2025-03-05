import streamlit as st
import urllib.parse
import random
import psycopg2

# Número de WhatsApp para enviar o pedido
WHATSAPP_NUMBER = "+5599991831701"

# Senha do dono do restaurante para visualizar os pedidos
ADMIN_PASSWORD = "1234"

# Conexão com o PostgreSQL
DB_CONFIG = {
    "dbname": "restaurante_db",
    "user": "postgres",
    "password": "69427",
    "host": "localhost",
    "port": "5432"
}

def conectar_bd():
    return psycopg2.connect(**DB_CONFIG)

def criar_tabela():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            ticket_numero VARCHAR(10) UNIQUE,
            nome_cliente VARCHAR(255),
            endereco TEXT,
            telefone VARCHAR(20),
            itens TEXT,
            total NUMERIC(10,2),
            forma_pagamento VARCHAR(50),
            status VARCHAR(50) DEFAULT 'Aguardando'
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Criar a tabela no banco de dados
criar_tabela()

# Funções de manipulação de pedidos
def atualizar_status(ticket_numero, novo_status):
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute('''
        UPDATE pedidos SET status = %s WHERE ticket_numero = %s
    ''', (novo_status, ticket_numero))
    conn.commit()
    cur.close()
    conn.close()

def buscar_pedidos():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT ticket_numero, nome_cliente, endereco, telefone, itens, total, forma_pagamento, status FROM pedidos ORDER BY id DESC")
    pedidos = cur.fetchall()
    cur.close()
    conn.close()
    return pedidos

# Tela para o dono visualizar os pedidos
def visualizar_pedidos():
    """Tela para o dono visualizar os pedidos."""
    st.title("📋 Pedidos Recebidos")
    senha = st.text_input("Digite a senha para acessar", type="password")

    if senha == ADMIN_PASSWORD:
        pedidos = buscar_pedidos()
        if pedidos:
            for pedido in pedidos:
                ticket_numero, nome, endereco, telefone, itens, total, pagamento, status = pedido
                st.text_area(f"Pedido {ticket_numero}", f"Nome: {nome}\nEndereço: {endereco}\nTelefone: {telefone}\nItens: {itens}\nTotal: R$ {total:.2f}\nPagamento: {pagamento}\nStatus: {status}", height=150)
                novo_status = st.selectbox(f"Atualizar status do pedido {ticket_numero}", ["Aguardando", "Em Preparo", "Saiu para Entrega", "Concluído"], index=["Aguardando", "Em Preparo", "Saiu para Entrega", "Concluído"].index(status))
                if st.button(f"Atualizar Status {ticket_numero}"):
                    atualizar_status(ticket_numero, novo_status)
                    st.success(f"Status do pedido {ticket_numero} atualizado para {novo_status}")
    elif senha:
        st.error("Senha incorreta!")

if __name__ == "__main__":
    visualizar_pedidos()
