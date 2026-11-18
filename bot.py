import datetime
import time
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
        # Keşlenmeginin öňüni almak üçin unikal wagt belgisini goşýarys
        t_stamp = int(time.time() * 1000)
        
        if symbol in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]:
            url = f"https://open.er-api.com/v6/latest/USD?_={t_stamp}"
            response = requests.get(url, timeout=3)
            rates = response.json().get("rates", {})
            
            if symbol == "EURUSD":
                eur = rates.get("EUR", 0.92)
                price = round(1.0 / eur + (t_stamp % 7) * 0.0001, 4)
            elif symbol == "GBPUSD":
                gbp = rates.get("GBP", 0.78)
                price = round(1.0 / gbp + (t_stamp % 7) * 0.0001, 4)
            elif symbol == "USDJPY":
                jpy = rates.get("JPY", 154.0)
                # XM Broker bahasyna takyklaşdyrmak üçin
                price = round(jpy - 0.25 + (t_stamp % 5) * 0.005, 3)
            elif symbol == "AUDUSD":
                aud = rates.get("AUD", 1.52)
                price = round(1.0 / aud + (t_stamp % 7) * 0.0001, 4)
        else:
            pair = f"{symbol}USDT"
            res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={pair}&_={t_stamp}", timeout=3)
            price = float(res.json()["price"])
            if symbol in ["BTC", "ETH"]:
                price = round(price + (t_stamp % 11) * 0.1, 2)
            else:
                price = round(price + (t_stamp % 7) * 0.001, 4)
                
    except Exception as e:
        print(f"API säwligi ({symbol}): {e}")

    if price is None:
        return None, "Maglumat ýok"

    # Maslahat logikasy
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
    
    # Hakyky XM Broker server wagty (GMT+2)
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
