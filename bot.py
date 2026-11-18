import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Siziň täze bot tokeniňiz
TELEGRAM_BOT_TOKEN = "9117274265:AAGxLEjHLdmgpCuxjA62r_7dE10_t6evAvk"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Bazar bahalaryny alyp berýän funksiýa
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
        print(f"Baha alnanda säwlik çykdy ({symbol}): {e}")
    return None

# /start ýazanynda çykjak düwmeler
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
        "Salam! Aşakdaky bazarlardan birini saýlaň we bahany görüň:", 
        reply_markup=markup
    )

# Düwmelere basylanda jogap beriş
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # callback_data içindäki simwoly alyp barlalyň
    symbol = call.data.replace("price_", "")
    price = get_market_price(symbol)
    
    if price is not None:
        text = (
            f"📊 **Bazar Maglumaty: {symbol}**\n\n"
            f"💰 Häzirki baha: `{price}`\n"
            f"📈 Maslahat: **Bazary öwreniň (Neutral)**\n"
            f"💡 *Maglumat maksatly berilýär.*"
        )
    else:
        text = f"Bagyşlaň, {symbol} boýunça maglumat alyp bolmady."
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot işe başlady...")
    # Timeout we baglanyşyk säwliklerini aýyrmak üçin esasy polling
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
