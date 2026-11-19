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
        InlineKeyboardButton("💶 EUR/USD", callback_data="sig_EURUSD"),
        InlineKeyboardButton("💷 GBP/USD", callback_data="sig_GBPUSD"),
        InlineKeyboardButton("💴 USD/JPY", callback_data="sig_USDJPY"),
        InlineKeyboardButton("🇦🇺 AUD/USD", callback_data="sig_AUDUSD"),
        InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data="sig_BTC"),
        InlineKeyboardButton("Ξ Ethereum (ETH)", callback_data="sig_ETH"),
        InlineKeyboardButton("🪙 Binance (BNB)", callback_data="sig_BNB"),
        InlineKeyboardButton("💧 Ripple (XRP)", callback_data="sig_XRP"),
        InlineKeyboardButton("☀️ Solana (SOL)", callback_data="sig_SOL")
    )
    return markup

def get_signal(symbol):
    now_ns = time.time_ns()
    seed_val = 0

    try:
        t_param = int(time.time() * 1000)
        if symbol in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]:
            url = f"https://open.er-api.com/v6/latest/USD?_={t_param}"
            resp = requests.get(url, timeout=3)
            rates = resp.json().get("rates", {})
            if symbol == "EURUSD":
                raw = 1.0 / float(rates.get("EUR", 0.92))
            elif symbol == "GBPUSD":
                raw = 1.0 / float(rates.get("GBP", 0.78))
            elif symbol == "USDJPY":
                raw = float(rates.get("JPY", 154.0))
            elif symbol == "AUDUSD":
                raw = 1.0 / float(rates.get("AUD", 1.52))
            seed_val = int(round(raw * 100000)) + (now_ns // 1000000)
        else:
            pair = f"{symbol}USDT"
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={pair}&_={t_param}"
            resp = requests.get(url, timeout=3)
            raw = float(resp.json()["price"])
            seed_val = int(round(raw * 100)) + (now_ns // 1000000)
    except Exception:
        seed_val = now_ns // 1000000

    # Ugrundaky ugry (BUY ýa-da SELL) kesgitlemek
    is_buy = (seed_val % 2 == 0)

    # Näçe minutlykdygyny (1, 2, 3 ýa-da 5 minut) kesgitlemek
    minutes_list = [1, 2, 3, 5]
    minutes = minutes_list[(seed_val // 2) % len(minutes_list)]

    return is_buy, minutes

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Bazary saýlaň:",
        reply_markup=get_market_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    symbol = call.data.replace("sig_", "")
    is_buy, minutes = get_signal(symbol)

    xm_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).strftime("%H:%M:%S")

    if is_buy:
        arrow = "⬆️⬆️⬆️\n# **BUY**\n⬆️⬆️⬆️"
        action_text = f"**{minutes} MINUT — BUY**"
    else:
        arrow = "⬇️⬇️⬇️\n# **SELL**\n⬇️⬇️⬇️"
        action_text = f"**{minutes} MINUT — SELL**"

    text = (
        f"**{symbol}**\n\n"
        f"{arrow}\n\n"
        f"⏱️ {action_text}\n"
        f"🕒 `{xm_time}` (GMT+2)"
    )

    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=get_market_keyboard(),
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    print("Bot işe başlady...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
