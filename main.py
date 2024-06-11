import telebot
from telebot import types
import requests
import os
from flask import Flask
import threading
import time
import json

API_KEY = "7371479271:AAE6ECs-iIzeo_VV4BWMTq3Cg1jIK_uUHZs"
OXAPAY_API_KEY = "W30BRR-XEDNYM-T0Y1Y8-LWZT2D"
OXAPAY_MERCHANT_ID = "077PVV-8FK004-PUGZLP-KDC407"
TRACK_ID = "unique_track_id"  # Substitua isso por um identificador único para cada transação

bot = telebot.TeleBot(API_KEY)

# Função para obter os preços das criptomoedas
def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin,ethereum,usd-coin,litecoin,solana',
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

# Função para criar um pagamento com o provedor de pagamento OXAPAY
def create_oxapay_payment(description, amount):
    url = 'https://api.oxapay.com/payments/create'
    data = {
        'merchant': OXAPAY_MERCHANT_ID,
        'amount': amount,
        'description': description,
        'trackId': TRACK_ID
    }
    response = requests.post(url, data=json.dumps(data))
    result = response.json()
    return result

# Função para lidar com o comando /drops
@bot.message_handler(commands=["drops"])
def drops(message):
    text = """
    Drops

    1 Drop - $80
    3 Drops - $190
    Drops Panel - $800"""
    bot.send_message(message.chat.id, text)

# Função para lidar com o comando /sn
@bot.message_handler(commands=["sn"])
def sn(message):
    text = """
    Serial Numbers

    Bose
    Dyson
    Bissell
    Booster Juice
    GoPro
    HP
    Lenovo
    Logitech
    Ninja Kitchen
    Philips
    Playstation
    Kitchenaid"""
    bot.send_message(message.chat.id, text)

# Função para lidar com o comando /buy
@bot.message_handler(commands=["buy"])
def buy(message):
    text = """
    Buy Services

    Serial Number - $5
    1 Drop - $80
    3 Drops - $190
    Drops Panel - $800
    
    To buy a service, use the command /purchase followed by the service name and quantity.
    Example: /purchase Drop 1
    """
    bot.send_message(message.chat.id, text)

# Função para lidar com o comando /purchase
@bot.message_handler(commands=["purchase"])
def purchase(message):
    try:
        command, service, quantity = message.text.split()
        quantity = int(quantity)
        
        if service.lower() == "drop":
            price = 80 * quantity
        elif service.lower() == "sn":
            price = 5 * quantity
        elif service.lower() == "drops_panel":
            price = 800 * quantity
        else:
            bot.send_message(message.chat.id, "Service not recognized. Please try again.")
            return
        
        payment_response = create_oxapay_payment(f"Purchase of {service}", price)
        
        if payment_response.get("status") == "success":
            payment_url = payment_response.get("payment_url")
            bot.send_message(message.chat.id, f"To complete your purchase, please proceed to the payment page: {payment_url}")
        else:
            bot.send_message(message.chat.id, "There was an issue creating the payment. Please try again later.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid command format. Use /purchase followed by the service name and quantity.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

# Função para lidar com o comando /show
@bot.message_handler(commands=["show"])
def show(message):
    text = """
    Our services

    Residential Drops USA/CA
    Serial Numbers"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('View Drops', callback_data='view_drops'),
        types.InlineKeyboardButton('View SN', callback_data='view_sn')
    )
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# Função para lidar com o comando /crypto
@bot.message_handler(commands=["crypto"])
def crypto(message):
    prices = get_crypto_prices()
    text = f"""
    Current cryptocurrency prices:
    
    - Bitcoin: ${prices['bitcoin']['usd']}
    - Ethereum: ${prices['ethereum']['usd']}
    - USD Coin: ${prices['usd-coin']['usd']}
    - Litecoin: ${prices['litecoin']['usd']}
    - Solana: ${prices['solana']['usd']}
    """
    bot.send_message(message.chat.id, text)

# Função para lidar com a consulta de callback
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "buy_services":
        buy(call.message)
    elif call.data == "show_services":
        show(call.message)
    elif call.data == "crypto":
        crypto(call.message)
    elif call.data == "support":
        support_url = "https://t.me/ElPato_Drops"
        bot.send_message(call.message.chat.id, f"Click [here]({support_url}) to chat with support.", parse_mode="Markdown")
    elif call.data == "view_drops":
        drops(call.message)
    elif call.data == "view_sn":
        sn(call.message)

# Função para lidar com o comando /start
@bot.message_handler(commands=["start"])
def start(message):
    first_name = message.from_user.first_name
    text = f"""
💵 Welcome {first_name} to ELPato Services

ELPato Services allows you to view some of our offered services and their prices. You can also make purchases directly through the bot.

    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('Buy Services', callback_data='buy_services'),
        types.InlineKeyboardButton('Show Services', callback_data='show_services')
    )
    keyboard.row(
        types.InlineKeyboardButton('Crypto', callback_data='crypto'),
        types.InlineKeyboardButton('Support', callback_data='support')
    )

    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# Criar aplicativo Flask para manter o bot ativo
app = Flask(__name__)

# Rota raiz
@app.route('/')
def index():
    return "Duck running for dollars $$$"

# Função para manter o aplicativo Flask ativo
def keep_alive():
    while True:
        try:
            requests.get("https://bot-telegram-yoym.onrender.com")
            time.sleep(300)
        except Exception as e:
            print(f"An error occurred: {e}")

# Start the bot and keep_alive functions in separate threads
def start_bot():
    while True:
        try:
            bot.polling(none_stop=True, timeout=123)
        except Exception as e:
            print(f"Bot polling failed: {e}")
            time.sleep(15)

threading.Thread(target=start_bot).start()
threading.Thread(target=keep_alive).start()

# Run the Flask application on the port specified by the PORT environment variable
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
