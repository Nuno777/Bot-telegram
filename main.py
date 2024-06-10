import telebot
from telebot import types
import requests
import os
from flask import Flask

CHAVE_API = "7371479271:AAE6ECs-iIzeo_VV4BWMTq3Cg1jIK_uUHZs"
OXAPAY_API_KEY = "W30BRR-XEDNYM-T0Y1Y8-LWZT2D"
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
    
    Para comprar um serviço, use o comando /purchase seguido do nome do serviço e quantidade.
    Exemplo: /purchase Drop 1
    """
    bot.send_message(mensagem.chat.id, text)

def create_oxapay_payment(description, amount, currency='USD'):
    url = "https://api.oxapay.com/merchants/request"
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
        "success_url": "https://success-32ub.onrender.com",
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
            bot.send_message(mensagem.chat.id, "Serviço não reconhecido. Por favor, tente novamente.")
            return
        
        payment_response = create_oxapay_payment(f"Purchase of {service}", price)
        
        if payment_response.get("status") == "success":
            payment_url = payment_response.get("payment_url")
            bot.send_message(mensagem.chat.id, f"Para completar sua compra, por favor prossiga para a página de pagamento: {payment_url}")
        else:
            bot.send_message(mensagem.chat.id, "Houve um problema ao criar o pagamento. Por favor, tente novamente mais tarde.")
    except ValueError:
        bot.send_message(mensagem.chat.id, "Formato de comando inválido. Use /purchase seguido do nome do serviço e quantidade.")
    except Exception as e:
        bot.send_message(mensagem.chat.id, f"Ocorreu um erro: {str(e)}")

@bot.message_handler(commands=["show"])
def show(mensagem):
    text = """
    Nossos serviços

    Residential Drops USA/CA
    Serial Numbers"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('View Drops', callback_data='view_drops'),
        types.InlineKeyboardButton('View SN', callback_data='view_sn')
    )
    bot.send_message(mensagem.chat.id, text, reply_markup=keyboard)

@bot.message_handler(commands=["crypto"])
def crypto(mensagem):
    prices = get_crypto_prices()
    text = f"""
    Preços atuais das criptomoedas:
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
        bot.send_message(call.message.chat.id, f"Clique [aqui]({support_url}) para conversar com o suporte.", parse_mode="Markdown")
    elif call.data == "view_drops":
        drops(call.message)
    elif call.data == "view_sn":
        sn(call.message)

@bot.message_handler(commands=["start"])
def start(mensagem):
    first_name = mensagem.from_user.first_name
    text = f"""
💵 Bem-vindo {first_name} aos Serviços ELPato

Os Serviços ELPato permitem que você veja alguns serviços que oferecemos por um determinado custo, onde você pode comprá-los.

    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('Comprar Serviços', callback_data='buy_services'),
        types.InlineKeyboardButton('Mostrar Serviços', callback_data='show_services')
    )
    keyboard.row(
        types.InlineKeyboardButton('Cripto', callback_data='crypto'),
        types.InlineKeyboardButton('Suporte', callback_data='support')
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
