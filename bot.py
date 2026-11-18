import os
import requests
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TELEGRAM_BOT_TOKEN = "9117274265:AAECiuQJHXhXf5ZY2jKgzZdagdF3hmTq_H0"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

def get_market_price(symbol):
    try:
        if symbol in ["EURUSD", "GBPUSD"]:
            base = symbol[:3]
            target = symbol[3:]
            url = f"https://open.er-api.com/v6/latest/{base}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if "rates" in data and target in data["rates"]:
                return float(data["rates"][target])
        elif symbol in ["BTC", "ETH"]:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            data = response.json()
            key = symbol.lower()
            if key in data and "usd" in data[key]:
                return float(data[key]["usd"])
    except Exception as e:
        print(f"Baha alyp bolmady ({symbol}): {e}")
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("💶 EUR/USD", callback_data="price_EURUSD"),
        InlineKeyboardButton("💷 GBP/USD", callback_data="price_GBPUSD"),
        InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data="price_BTC"),
        InlineKeyboardButton("Ξ Ethereum (ETH)", callback_data="price_ETH")
    )
    bot.send_message(
        message.chat.id, 
        "Salam! Aşakdaky bazarlardan birini saýlaň. Men size bahany we bazaryň ýagdaýyny görkezerin:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    symbol = call.data.split("_")[1]
    price = get_market_price(symbol)
    
    if price is not None:
        text = (
            f"📊 **Bazar Maglumaty: {symbol}**\n\n"
            f"💰 Häzirki baha: `{price}`\n"
            f"📈 Maslahat: **Bazary öwreniň (Neutral)**\n"
            f"💡 *Üns beriň: Maglumat maksatly berilýär.*"
        )
    else:
        text = f"Bagyşlaň, {symbol} boýunça maglumat alyp bolmady."
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def index():
    return "Bot bulutda işleýär!", 200

if __name__ == "__main__":
    # Railway tarapyndan berilýän port bilen işlemek üçin
    port = int(os.environ.get("PORT", 5000))
    
    # Webhook-y sazlamak (Railway-däki domen adyňyzy bolar ýaly)
    # Häzirçe bulutda durnukly işlemegi üçin polling ýerine web server açýarys
    app.run(host="0.0.0.0", port=port)
