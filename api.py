from flask import Flask, redirect, request
import urllib.parse

app = Flask(__name__)

@app.route('/redirect-to-whatsapp')
def redirect_to_whatsapp():
    phone_number = request.args.get('phone')
    message = request.args.get('message', 'Olá, gostaria de saber mais sobre seus serviços.')
    url = f"https://wa.me/{99991831701}?text={urllib.parse.quote('Gostaria de confimar meu pedido')}"
    return redirect(url)

if __name__ == '__main__':
    app.run(port=3000)