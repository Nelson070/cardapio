import streamlit as st
import random
import urllib.parse
import psycopg2

# Número de WhatsApp para enviar o pedido
WHATSAPP_NUMBER = "+5599991831701"

# Senha do dono do restaurante para visualizar os pedidos
ADMIN_PASSWORD = "1234"

DB_CONFIG = {
    "dbname": "restaurante_db",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": "5432"
}

def conectar_bd():
    """Função para conectar ao banco de dados PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)

def criar_tabela():
    """Cria a tabela de pedidos no banco de dados, caso não exista."""
    with conectar_bd() as conn:
        with conn.cursor() as cur:
            cur.execute(''' 
                CREATE TABLE IF NOT EXISTS pedidos (
                    id SERIAL PRIMARY KEY,
                    ticket_numero VARCHAR(10) UNIQUE,
                    nome_cliente VARCHAR(255),
                    endereco TEXT,
                    cep VARCHAR(20),
                    telefone VARCHAR(20),
                    itens TEXT,
                    total NUMERIC(10,2),
                    forma_pagamento VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'Aguardando'
                )
            ''')
            conn.commit()

# Salvar pedido no banco
def salvar_pedido(ticket_numero, nome, endereco, cep, telefone, itens, total, pagamento):
    """Salva um pedido no banco de dados."""
    try:
        with conectar_bd() as conn:
            with conn.cursor() as cur:
                cur.execute(''' 
                    INSERT INTO pedidos (ticket_numero, nome_cliente, endereco, cep, telefone, itens, total, forma_pagamento) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (ticket_numero, nome, endereco, cep, telefone, itens, total, pagamento))
            conn.commit()  # 🔥 Salva as alterações no banco
        print(f"✅ Pedido {ticket_numero} salvo com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar pedido: {e}")

# Atualizar status do pedido
def atualizar_status(ticket_numero, novo_status):
    with conectar_bd() as conn:
        with conn.cursor() as cur:
            cur.execute(''' 
                UPDATE pedidos SET status = %s WHERE ticket_numero = %s
            ''', (novo_status, ticket_numero))
            conn.commit()

# Buscar pedidos no banco de dados
def buscar_pedidos(status_filtro=None):
    with conectar_bd() as conn:
        with conn.cursor() as cur:
            query = "SELECT ticket_numero, nome_cliente, endereco, cep, telefone, itens, total, forma_pagamento, status FROM pedidos"
            if status_filtro:
                query += " WHERE status = %s"
                cur.execute(query, (status_filtro,))
            else:
                cur.execute(query)
            return cur.fetchall()

# Criar a tabela no banco de dados
criar_tabela()

# Inicializando session_state
if "carrinho" not in st.session_state:
    st.session_state["carrinho"] = []

# Dados do menu com URLs das imagens
MENU = {
    "Pizza Margherita": {"preco": 30.0, "imagem": "imagens/OIP__1_-removebg-preview.png"},
    "Hambúrguer Artesanal": {"preco": 25.0, "imagem": "imagens/11013540.png"},
    "Lasanha Bolonhesa": {"preco": 35.0, "imagem": "imagens/3c42feb1-9d73-4c03-bcdd-a496e59f4994-removebg-preview.png"},
    "Salada Caesar": {"preco": 20.0, "imagem": "imagens/chicken-caesar-salad.jpg"},
    "Sushi Combo": {"preco": 50.0, "imagem": "imagens/img_dueto-min.png"}
}

# Logo do restaurante
LOGO_URL = "imagens/logo.png"

def menu():
    """Tela do menu do restaurante."""
    st.image(LOGO_URL, width=100)
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
        cep = st.text_input("Cep")
        telefone = st.text_input("Telefone")
        pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão de Crédito"])
        
        if st.button("Finalizar Pedido"):
            if nome and endereco and telefone:
                ticket_id = random.randint(1000, 9999)
                
                # Formatando a mensagem para WhatsApp
                itens_formatados = "\n".join([f"{item} (R$ {preco:.2f})" for item, preco in st.session_state["carrinho"]])
                total_formatado = f"R$ {total:.2f}"
                pedido_texto = f"""
Pedido {ticket_id}
Nome: {nome}
Endereço: {endereco}
Cep: {cep}
Telefone: {telefone}
Itens:
{itens_formatados}
Total: {total_formatado}
Pagamento: {pagamento}
"""
                # Salvar no banco de dados
                salvar_pedido(ticket_id, nome, endereco, cep, telefone, itens_formatados, total, pagamento)
                
                # Codificando a mensagem para URL
                mensagem_whatsapp = urllib.parse.quote(pedido_texto)
                url_whatsapp = f"https://wa.me/{WHATSAPP_NUMBER}?text={mensagem_whatsapp}"
                st.markdown(f"[📲 Enviar Pedido pelo WhatsApp]({url_whatsapp})", unsafe_allow_html=True)
                st.success(f"Pedido realizado com sucesso! Ticket: {ticket_id}")
                st.session_state["carrinho"] = []
            else:
                st.error("Por favor, preencha todos os campos de entrega.")
    else:
        st.write("Carrinho vazio")

def visualizar_pedidos():
    st.title("📋 Pedidos Recebidos")
    senha = st.text_input("Digite a senha para acessar", type="password")
    
    if senha == ADMIN_PASSWORD:
        pedidos = buscar_pedidos()
        if pedidos:
            for pedido in pedidos:
                ticket_numero, nome_cliente, endereco, cep, telefone, itens, total, forma_pagamento, status = pedido
                st.text_area(f"Pedido {ticket_numero}", f"Nome: {nome_cliente}\nEndereço: {endereco}\nCep: {cep}\nTelefone: {telefone}\nItens: {itens}\nTotal: R$ {total:.2f}\nPagamento: {forma_pagamento}\nStatus: {status}", height=150)
                novo_status = st.selectbox(f"Atualizar status do pedido {ticket_numero}", ["Aguardando", "Em Preparo", "Saiu para Entrega", "Concluído"], key=f"status_{ticket_numero}")
                if st.button(f"Atualizar {ticket_numero}"):
                    atualizar_status(ticket_numero, novo_status)
                    st.success(f"Status do pedido {ticket_numero} atualizado para {novo_status}")
        else:
            st.write("Nenhum pedido encontrado.")
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
            ticket_numero, nome_cliente, endereco, cep, telefone, itens, total, forma_pagamento, status = pedido
            st.text_area(f"Pedido {ticket_numero}", f"Nome: {nome_cliente}\nEndereço: {endereco}\nCep: {cep}\nTelefone: {telefone}\nItens: {itens}\nTotal: R$ {total:.2f}\nPagamento: {forma_pagamento}\nStatus: {status}", height=150)
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
