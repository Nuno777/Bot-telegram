from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    # Processar a notificação aqui (por exemplo, atualizar o status do pedido no banco de dados)
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run()
