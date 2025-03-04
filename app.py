import streamlit as st
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

# Dados do menu com imagens
MENU = {
    "Pizza Margherita": {"preco": 30.0, "imagem": "imagens/OIP__1_-removebg-preview.png"},
    "Hambúrguer Artesanal": {"preco": 25.0, "imagem": "imagens/11013540.png"},
    "Lasanha Bolonhesa": {"preco": 35.0, "imagem": "imagens/3c42feb1-9d73-4c03-bcdd-a496e59f4994-removebg-preview.png"},
    "Salada Caesar": {"preco": 20.0, "imagem": "imagens/chicken-caesar-salad.jpg"},
    "Sushi Combo": {"preco": 50.0, "imagem": "imagens/img_dueto-min.png"}
}

def salvar_pedido(ticket_numero, nome, endereco, telefone, itens, total, pagamento):
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute(''' 
        INSERT INTO pedidos (ticket_numero, nome_cliente, endereco, telefone, itens, total, forma_pagamento) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (ticket_numero, nome, endereco, telefone, itens, total, pagamento))
    conn.commit()
    cur.close()
    conn.close()

def atualizar_status(ticket_numero, novo_status):
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute(''' 
        UPDATE pedidos SET status = %s WHERE ticket_numero = %s
    ''', (novo_status, ticket_numero))
    conn.commit()
    cur.close()
    conn.close()

def buscar_pedidos(status_filtro=None):
    conn = conectar_bd()
    cur = conn.cursor()
    query = "SELECT ticket_numero, nome_cliente, endereco, telefone, itens, total, forma_pagamento, status FROM pedidos"
    if status_filtro:
        query += " WHERE status = %s"
        cur.execute(query, (status_filtro,))
    else:
        cur.execute(query)
    pedidos = cur.fetchall()
    cur.close()
    conn.close()
    return pedidos

def menu():
    """Tela do menu do restaurante."""
    st.image("imagens/logo.png", width=100)
    st.title("Nosso Cardápio")
    search = st.text_input("Buscar no menu", "").lower()
    cols = st.columns(2)
    
    for index, (item, dados) in enumerate(MENU.items()):
        if search in item.lower():
            with cols[index % 2]:
                st.image(dados["imagem"], width=150)
                st.markdown(f"**{item}**")
                st.markdown(f"💲{dados['preco']:.2f}")
                quantidade = st.number_input(f"Quantidade de {item}", min_value=1, value=1, step=1, key=f"quantidade_{item}")
                if st.button(f"Adicionar {item}"):
                    for _ in range(quantidade):
                        st.session_state["carrinho"].append((item, dados['preco']))
                    st.success(f"{quantidade}x {item} adicionado(s) ao carrinho!")
    
    st.markdown("## Carrinho de Compras")
    if st.session_state["carrinho"]:
        total = 0
        itens = []
        for index, (item, preco) in enumerate(st.session_state["carrinho"]):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"- {item}: R$ {preco:.2f}")
            with col2:
                if st.button(f"❌", key=f"remover_{index}"):
                    st.session_state["carrinho"].pop(index)
                    st.rerun()
            itens.append(f"{item} (R$ {preco:.2f})")
            total += preco
        st.write(f"**Total: R$ {total:.2f}**")
        
        st.markdown("## Dados para Entrega")
        nome = st.text_input("Nome Completo")
        endereco = st.text_input("Endereço")
        telefone = st.text_input("Telefone")
        pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão de Crédito"])
        
        if st.button("Finalizar Pedido"):
            if nome and endereco and telefone:
                ticket_numero = str(random.randint(1000, 9999))
                salvar_pedido(ticket_numero, nome, endereco, telefone, ", ".join(itens), total, pagamento)
                st.success(f"Pedido realizado com sucesso! Ticket: {ticket_numero}")
                st.session_state["carrinho"] = []
            else:
                st.error("Por favor, preencha todos os campos de entrega.")
    else:
        st.write("Carrinho vazio")

def visualizar_pedidos():
    """Tela para o dono visualizar os pedidos."""
    st.title("📋 Pedidos Recebidos")
    senha = st.text_input("Digite a senha para acessar", type="password")
    
    if senha == ADMIN_PASSWORD:
        pedidos = buscar_pedidos()
        status_possiveis = ["Aguardando", "Em Preparo", "Saiu para Entrega", "Concluído"]
        if pedidos:
            for pedido in pedidos:
                ticket_numero, nome, endereco, telefone, itens, total, pagamento, status = pedido
                st.text_area(f"Pedido {ticket_numero}", f"Nome: {nome}\nEndereço: {endereco}\nTelefone: {telefone}\nItens: {itens}\nTotal: R$ {total:.2f}\nPagamento: {pagamento}\nStatus: {status}", height=150)
                
                # Usar os status possíveis no selectbox
                novo_status = st.selectbox(
                    f"Atualizar status do pedido {ticket_numero}",
                    status_possiveis,
                    index=status_possiveis.index(status) if status in status_possiveis else 0
                )
                
                if st.button(f"Atualizar Status {ticket_numero}"):
                    atualizar_status(ticket_numero, novo_status)
                    st.success(f"Status do pedido {ticket_numero} atualizado para {novo_status}")
    elif senha:
        st.error("Senha incorreta!")

def painel_delivery():
    """Tela para o dono visualizar pedidos no painel de delivery."""
    st.title("📋 Painel de Delivery")
    
    # Filtro de status
    status_filtro = st.selectbox("Filtrar pedidos por status", ["Aguardando", "Em Preparo", "Saiu para Entrega", "Concluído"])
    
    pedidos = buscar_pedidos(status_filtro)
    if pedidos:
        for pedido in pedidos:
            ticket_numero, nome, endereco, telefone, itens, total, pagamento, status = pedido
            st.text_area(f"Pedido {ticket_numero}", f"Nome: {nome}\nEndereço: {endereco}\nTelefone: {telefone}\nItens: {itens}\nTotal: R$ {total:.2f}\nPagamento: {pagamento}\nStatus: {status}", height=150)
    else:
        st.write("Nenhum pedido encontrado com esse status.")

def main():
    st.set_page_config(page_title="Restaurante", layout="centered")
    if "carrinho" not in st.session_state:
        st.session_state["carrinho"] = []
    
    menu_opcao = st.sidebar.radio("Navegação", ["Cardápio", "Pedidos (Dono)", "Painel Delivery"])
    
    if menu_opcao == "Cardápio":
        menu()
    elif menu_opcao == "Pedidos (Dono)":
        visualizar_pedidos()
    elif menu_opcao == "Painel Delivery":
        painel_delivery()
    
    st.markdown("---")
    st.markdown("Desenvolvido por Nelson Alves")
    st.markdown("Siga-nos no Instagram: [@nelsonalvz_12](https://instagram.com/nelsonalvz_12)")

if __name__ == "__main__":
    main()
