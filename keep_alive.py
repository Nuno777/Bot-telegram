from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Bot is running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # Use a porta especificada pela variável de ambiente PORT ou 5000 se não estiver definida
    app.run(host='0.0.0.0', port=port)
