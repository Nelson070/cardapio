import streamlit as st
import urllib.parse

# Número do WhatsApp para enviar o pedido
WHATSAPP_NUMBER = "+5599991831701"  

# Dados do menu com imagens externas para reduzir peso
MENU = {
    "Pizza Margherita": {"preco": 30.0, "imagem": "https://example.com/OIP__1_-removebg-preview.png"},
    "Hambúrguer Artesanal": {"preco": 25.0, "imagem": "https://example.com/11013540.png"},
    "Lasanha Bolonhesa": {"preco": 35.0, "imagem": "https://example.com/3c42feb1-9d73-4c03-bcdd-a496e59f4994.jpg"},
    "Salada Caesar": {"preco": 20.0, "imagem": "https://example.com/chicken-caesar-salad.jpg"},
    "Sushi Combo": {"preco": 50.0, "imagem": "https://example.com/img_dueto-min.png"}
}

def menu():
    """Tela do menu do restaurante."""
    st.markdown("""
        <style>
            body {
                background-color: #D3D3D3;
                color: black;
                font-family: Arial, sans-serif;
            }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color:rgb(255, 0, 0);'>Nosso Cardápio</h1>", unsafe_allow_html=True)
    
    search = st.text_input("Buscar no menu", "")
    cols = st.columns(2)
    for index, (item, dados) in enumerate(MENU.items()):
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
        
        if st.button("Finalizar Pedido"):
            if nome and endereco and telefone:
                pedido_texto += f"Nome: {nome}\nEndereço: {endereco}\nTelefone: {telefone}"
                mensagem_whatsapp = urllib.parse.quote(pedido_texto)
                url_whatsapp = f"https://wa.me/{WHATSAPP_NUMBER}?text={mensagem_whatsapp}"
                st.markdown(f"[📲 Enviar Pedido pelo WhatsApp]({url_whatsapp})", unsafe_allow_html=True)
                st.success("Clique no link acima para finalizar o pedido no WhatsApp!")
                st.session_state["carrinho"] = []
            else:
                st.error("Por favor, preencha todos os campos de entrega.")
    else:
        st.write("Carrinho vazio")

def main():
    """Função principal para controlar a navegação."""
    st.set_page_config(page_title="Restaurante", layout="centered")
    
    if "carrinho" not in st.session_state:
        st.session_state["carrinho"] = []
    
    menu()

if __name__ == "__main__":
    main()
