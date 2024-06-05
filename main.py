import telebot
import requests

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
        "callback_url": "https://seuapp.herokuapp.com/callback",  # Substitua pelo seu callback real
        "success_url": "https://seuapp.herokuapp.com/success.html",  # Substitua pelo seu success URL real
        "cancel_url": "https://seuapp.herokuapp.com/cancel.html"  # Substitua pelo seu cancel URL real
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
    bot.send_message(mensagem.chat.id, text)

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

@bot.message_handler(commands=["start"])
def start(mensagem):
    text = """
💵 Welcome to ELPato Services

ELPato Services allows you to show some services that we offer for a certain cost, where you can buy them.

Buy the services /buy
Show services /show
Cryptocurrency prices /crypto

👤 Support: @ElPato_Drops
    """
    bot.send_message(mensagem.chat.id, text)

bot.polling()
