import telebot
from telebot import types
import requests
import os
from flask import Flask

CHAVE_API = "7371479271:AAE6ECs-iIzeo_VV4BWMTq3Cg1jIK_uUHZs"
OXAPAY_API_KEY = "OXAUwZmCgUDU9YBzNFGcZkRtvP"
OXAPAY_MERCHANT_ID = "077PVV-8FK004-PUGZLP-KDC407"

bot = telebot.TeleBot(CHAVE_API)

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

@bot.message_handler(commands=["drops"])
def drops(mensagem):
    text = """
    Drops

    1 Drop - $80
    3 Drops - $190
    Drops Painel - $800"""
    bot.send_message(mensagem.chat.id, text)

@bot.message_handler(commands=["sn"])
def sn(mensagem):
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
    bot.send_message(mensagem.chat.id, text)

@bot.message_handler(commands=["buy"])
def buy(mensagem):
    text = """
    Buy Services

    Serial Number - $5
    1 Drop - $80
    3 Drops - $190
    Drops Painel - $800
    
    To buy a service, use the command /purchase followed by the service name and quantity.
    Example: /purchase Drop 1
    """
    bot.send_message(mensagem.chat.id, text)

def create_oxapay_payment(description, amount, currency='USD'):
    url = "https://api.oxapay.com/v1/payments"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OXAPAY_API_KEY}"
    }
    data = {
        "merchant_id": OXAPAY_MERCHANT_ID,
        "description": description,
        "amount": amount,
        "currency": currency,
        "callback_url": "https://seuapp.render.com/callback",  # Substitua pelos URLs reais
        "success_url": "https://seuapp.render.com/success.html",
        "cancel_url": "https://seuapp.render.com/cancel.html"
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

@bot.message_handler(commands=["purchase"])
def purchase(mensagem):
    try:
        command, service, quantity = mensagem.text.split()
        quantity = int(quantity)
        
        if service.lower() == "drop":
            price = 80 * quantity
        elif service.lower() == "sn":
            price = 5 * quantity
        elif service.lower() == "drops_painel":
            price = 800 * quantity
        else:
            bot.send_message(mensagem.chat.id, "Service not recognized. Please try again.")
            return
        
        payment_response = create_oxapay_payment(f"Purchase of {service}", price)
        
        if payment_response.get("status") == "success":
            payment_url = payment_response.get("payment_url")
            bot.send_message(mensagem.chat.id, f"To complete your purchase, please proceed to the payment page: {payment_url}")
        else:
            bot.send_message(mensagem.chat.id, "There was an issue creating the payment. Please try again later.")
    except ValueError:
        bot.send_message(mensagem.chat.id, "Invalid command format. Use /purchase followed by the service name and quantity.")
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"An error occurred: {str(e)}")

@bot.message_handler(commands=["show"])
def show(mensagem):
    text = """
    Our services

    Residential Drops USA/CA /drops
    Serial Number /sn"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('View Drops', callback_data='view_drops'),
        types.InlineKeyboardButton('View SN', callback_data='view_sn')
    )
    keyboard.row(
        types.InlineKeyboardButton('Buy Services', callback_data='buy_services'),
        types.InlineKeyboardButton('Show Services', callback_data='show_services')
    )
    keyboard.row(
        types.InlineKeyboardButton('Crypto', callback_data='crypto'),
        types.InlineKeyboardButton('Support', callback_data='support')
    )
    bot.send_message(mensagem.chat.id, text, reply_markup=keyboard)

@bot.message_handler(commands=["crypto"])
def crypto(mensagem):
    prices = get_crypto_prices()
    text = f"""
    Current cryptocurrency prices:
    - Bitcoin: ${prices['bitcoin']['usd']}
    - Ethereum: ${prices['ethereum']['usd']}
    - USD Coin: ${prices['usd-coin']['usd']}
    - Litecoin: ${prices['litecoin']['usd']}
    - Solana: ${prices['solana']['usd']}
    """
    bot.send_message(mensagem.chat.id, text)

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

@bot.message_handler(commands=["start"])
def start(mensagem):
    first_name = mensagem.from_user.first_name
    text = f"""
💵 Welcome {first_name} to ELPato Services

ELPato Services allows you to show some services that we offer for a certain cost, where you can buy them.

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

    bot.send_message(mensagem.chat.id, text, reply_markup=keyboard)

# Crie uma aplicação Flask para manter o bot vivo
app = Flask(__name__)

@app.route('/')
def index():
    return "Duck running for dollars $$$"

# Inicie o bot em uma thread separada
import threading

def start_bot():
    bot.polling()

threading.Thread(target=start_bot).start()

# Execute a aplicação Flask na porta especificada pela variável de ambiente PORT
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
