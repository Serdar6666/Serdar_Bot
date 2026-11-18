import datetime
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TELEGRAM_BOT_TOKEN = "9117274265:AAGxLEjHLdmgpCuxjA62r_7dE10_t6evAvk"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

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
        # Forex we Kripto üçin hakyky we takyk bazary çykarmak
        if symbol in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]:
            # Forex üçin hakyky mugt API (ExchangeRate-API v6 real-time)
            url = "https://open.er-api.com/v6/latest/USD"
            response = requests.get(url, timeout=5)
            rates = response.json().get("rates", {})
            
            if symbol == "EURUSD":
                price = 1.0 / rates.get("EUR", 1.08)
            elif symbol == "GBPUSD":
                price = 1.0 / rates.get("GBP", 1.28)
            elif symbol == "USDJPY":
                price = rates.get("JPY", 154.0)
            elif symbol == "AUDUSD":
                price = 1.0 / rates.get("AUD", 1.52)
        else:
            # Kripto üçin Binance
            pair = f"{symbol}USDT"
            res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={pair}", timeout=4)
            price = float(res.json()["price"])
    except Exception as e:
        print(f"API säwligi ({symbol}): {e}")

    if price is None:
        return None, "Maglumat ýok"

    # Hakyky baha görä maslahat (takyklyk üçin 4 ýa-da 2 san belgi)
    price = round(price, 4 if symbol != "USDJPY" else 3)
    
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
    
    xm_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).strftime('%Y-%m-%d  %H:%M:%S')
    
    if price is not None:
        text = (
            f"📊 **Bazar Maglumaty: {symbol}**\n\n"
            f"💰 Häzirki baha: `{price}`\n"
            f"📈 Maslahat: {advice}\n"
            f"🕒 XM Server Wagty: `{xm_time}`\n"
            f"💡 *Maglumat maksatly berilýär.*\n\n"
            f"👇 Başga bazar saýlaň:"
        )
    else:
        text = (
            f"📊 **Bazar Maglumaty: {symbol}**\n\n"
            f"⚠️ Häzirki wagtda bu bazar ýapyk ýa-da maglumat alyp bolmady.\n"
            f"🕒 XM Server Wagty: `{xm_time}`\n\n"
            f"👇 Başga bazar saýlaň:"
        )
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, reply_markup=get_market_keyboard(), parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot işe başlady...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
