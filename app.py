import streamlit as st
import urllib.parse
import random

# Número de WhatsApp para enviar o pedido
WHATSAPP_NUMBER = "+5599991831701"

# Senha do dono do restaurante para visualizar os pedidos
ADMIN_PASSWORD = "1234"  # Altere conforme necessário

# Banco de pedidos (simples, apenas para testes)
if "pedidos" not in st.session_state:
    st.session_state["pedidos"] = []

# Dados do menu com imagens
MENU = {
    "Pizza Margherita": {"preco": 30.0, "imagem": "imagens/OIP__1_-removebg-preview.png"},
    "Hambúrguer Artesanal": {"preco": 25.0, "imagem": "imagens/11013540.png"},
    "Lasanha Bolonhesa": {"preco": 35.0, "imagem": "imagens/3c42feb1-9d73-4c03-bcdd-a496e59f4994-removebg-preview.png"},
    "Salada Caesar": {"preco": 20.0, "imagem": "imagens/chicken-caesar-salad.jpg"},
    "Sushi Combo": {"preco": 50.0, "imagem": "imagens/img_dueto-min.png"}
}

def menu():
    """Tela do menu do restaurante."""
    st.markdown("<h1 style='text-align: center; color:rgb(255, 0, 0);'>Nosso Cardápio</h1>", unsafe_allow_html=True)
    
    search = st.text_input("Buscar no menu", "").lower()
    cols = st.columns(2)
    
    for index, (item, dados) in enumerate(MENU.items()):
        if search in item.lower():
            with cols[index % 2]:
                st.image(dados["imagem"], width=150)
                st.markdown(f"**{item}**")
                st.markdown(f"💲{dados['preco']:.2f}")
                if st.button(f"Adicionar {item}"):
                    st.session_state["carrinho"].append((item, dados['preco']))
                    st.success(f"{item} adicionado ao carrinho!")
    
    st.markdown("## Carrinho de Compras")
    if st.session_state["carrinho"]:
        total = 0
        pedido_texto = "Pedido:\n"
        for item, preco in st.session_state["carrinho"]:
            st.write(f"- {item}: R$ {preco:.2f}")
            pedido_texto += f"- {item}: R$ {preco:.2f}\n"
            total += preco
        st.write(f"**Total: R$ {total:.2f}**")
        pedido_texto += f"Total: R$ {total:.2f}\n"
        
        st.markdown("## Dados para Entrega")
        nome = st.text_input("Nome Completo")
        endereco = st.text_input("Endereço")
        telefone = st.text_input("Telefone")
        pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão de Crédito"])
        
        if st.button("Finalizar Pedido"):
            if nome and endereco and telefone:
                ticket_id = random.randint(1000, 9999)
                pedido_texto += f"Nome: {nome}\nEndereço: {endereco}\nTelefone: {telefone}\nPagamento: {pagamento}\nTicket: {ticket_id}"
                st.session_state["pedidos"].append(pedido_texto)
                
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
    """Tela para o dono visualizar os pedidos."""
    st.title("📋 Pedidos Recebidos")
    senha = st.text_input("Digite a senha para acessar", type="password")
    
    if senha == ADMIN_PASSWORD:
        if st.session_state["pedidos"]:
            for pedido in st.session_state["pedidos"]:
                st.text_area("Pedido Recebido:", pedido, height=150)
        else:
            st.write("Nenhum pedido recebido ainda.")
    elif senha:
        st.error("Senha incorreta!")

def main():
    """Função principal para controlar a navegação."""
    st.set_page_config(page_title="Restaurante", layout="centered")
    
    if "carrinho" not in st.session_state:
        st.session_state["carrinho"] = []
    
    menu_opcao = st.sidebar.radio("Navegação", ["Cardápio", "Pedidos (Dono)"])
    
    if menu_opcao == "Cardápio":
        menu()
    elif menu_opcao == "Pedidos (Dono)":
        visualizar_pedidos()

if __name__ == "__main__":
    main()
