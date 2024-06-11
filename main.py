import telebot
from telebot import types
import requests
import os
from flask import Flask

API_KEY = os.environ.get("TELEGRAM_API_KEY")
OXAPAY_API_KEY = os.environ.get("OXAPAY_API_KEY")
OXAPAY_MERCHANT_ID = os.environ.get("OXAPAY_MERCHANT_ID")

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
    
    To buy a service, use the command /purchase followed by the service name and quantity.
    Example: /purchase Drop 1
    """
    bot.send_message(message.chat.id, text)

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

# Start the bot in a separate thread
import threading

def start_bot():
    bot.polling()

threading.Thread(target=start_bot).start()

# Run the Flask application on the port specified by the PORT environment variable
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
