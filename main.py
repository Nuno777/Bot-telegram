import telebot
from telebot import types
import requests
import os
from flask import Flask
import threading
import time

API_KEY = "7371479271:AAE6ECs-iIzeo_VV4BWMTq3Cg1jIK_uUHZs"
OXAPAY_API_KEY = "W30BRR-XEDNYM-T0Y1Y8-LWZT2D"
OXAPAY_MERCHANT_ID = "077PVV-8FK004-PUGZLP-KDC407"

bot = telebot.TeleBot(API_KEY)

# Function to get cryptocurrency prices
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
def drops(message):
    text = """
    Drops

    1 Drop - $80
    3 Drops - $190
    Drops Panel - $800"""
    bot.send_message(message.chat.id, text)

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

@bot.message_handler(commands=["buy"])
def buy(message):
    text = """
    Buy Services

    Serial Number - $5
    1 Drop - $80
    3 Drops - $190
    Drops Panel - $800
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('Serial Number', callback_data='buy_sn'),
        types.InlineKeyboardButton('Drops Panel', callback_data='buy_drops_panel')
    )
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

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
    elif call.data == "buy_sn":
        # Lógica para comprar serial number
    elif call.data == "buy_drops_panel":
        # Lógica para comprar drops panel

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

# Create a Flask application to keep the bot alive
app = Flask(__name__)

@app.route('/')
def index():
    return "Duck running for dollars $$$"

# Function to periodically send a request to keep the app alive
def keep_alive():
    while True:
        try:
            requests.get("https://bot-telegram-yoym.onrender.com")
            time.sleep(300)  # wait for 5 minutes
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
