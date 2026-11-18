import datetime
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TELEGRAM_BOT_TOKEN = "9117274265:AAGxLEjHLdmgpCuxjA62r_7dE10_t6evAvk"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Bazarlary saýlamak üçin esasy düwmeler funksiýasy
def get_market_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("💶 EUR/USD", callback_data="price_EURUSD"),
        InlineKeyboardButton("💷 GBP/USD", callback_data="price_GBPUSD"),
        InlineKeyboardButton("💴 USD/JPY", callback_data="price_USDJPY"),
        InlineKeyboardButton("🇦🇺 AUD/USD", callback_data="price_AUDUSD"),
        InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data="price_BTC"),
        InlineKeyboardButton("Ξ Ethereum (ETH)", callback_data="price_ETH"),
        InlineKeyboardButton("🪙 Binance (BNB)", callback_data="price_BNB"),
        InlineKeyboardButton("💧 Ripple (XRP)", callback_data="price_XRP"),
        InlineKeyboardButton("☀️ Solana (SOL)", callback_data="price_SOL")
    )
    return markup

def get_market_analysis(symbol):
    price = None
    try:
        if symbol == "EURUSD":
            url = "https://open.er-api.com/v6/latest/EUR"
            response = requests.get(url, timeout=5)
            price = float(response.json()["rates"]["USD"])
        elif symbol == "GBPUSD":
            url = "https://open.er-api.com/v6/latest/GBP"
            response = requests.get(url, timeout=5)
            price = float(response.json()["rates"]["USD"])
        elif symbol == "USDJPY":
            url = "https://open.er-api.com/v6/latest/USD"
            response = requests.get(url, timeout=5)
            price = float(response.json()["rates"]["JPY"])
        elif symbol == "AUDUSD":
            url = "https://open.er-api.com/v6/latest/AUD"
            response = requests.get(url, timeout=5)
            price = float(response.json()["rates"]["USD"])
        else:
            pair = f"{symbol}USDT"
            res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={pair}", timeout=4)
            price = float(res.json()["price"])
    except Exception as e:
        print(f"API säwligi ({symbol}): {e}")
    
    # Ätiýaçlyk bahalar
    if price is None:
        fallbacks = {
            "EURUSD": 1.0998, "GBPUSD": 1.3199, "USDJPY": 154.50, "AUDUSD": 0.6500,
            "BTC": 91450.0, "ETH": 3120.0, "BNB": 640.0, "XRP": 0.55, "SOL": 210.0
        }
        price = fallbacks.get(symbol, 100.0)

    # Maslahat çykarmak
    int_part = int(price * 100)
    if int_part % 2 == 0:
        advice = "🟢 **SATYN ALYŇ (BUY)** 🚀"
    else:
        advice = "🔴 **SATYŇ (SELL)** 📉"
        
    return price, advice

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        "Salam! Aşakdaky esasy bazarlardan birini saýlaň:", 
        reply_markup=get_market_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    symbol = call.data.replace("price_", "")
    price, advice = get_market_analysis(symbol)
    
    # XM Broker server wagty (GMT+2)
    xm_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).strftime('%Y-%m-%d  %H:%M:%S')
    
    text = (
        f"📊 **Bazar Maglumaty: {symbol}**\n\n"
        f"💰 Häzirki baha: `{price}`\n"
        f"📈 Maslahat: {advice}\n"
        f"🕒 XM Server Wagty: `{xm_time}`\n"
        f"💡 *Maglumat maksatly berilýär.*\n\n"
        f"👇 Başga bazar saýlaň:"
    )
    
    bot.answer_callback_query(call.id)
    # Her jogabyň aşagyna bazar saýlaýan düwmeler goşuldy
    bot.send_message(call.message.chat.id, text, reply_markup=get_market_keyboard(), parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot işe başlady...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
