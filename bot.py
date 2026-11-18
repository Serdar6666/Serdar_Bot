import requests
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- TÄZE BOT TOKENI ---
TELEGRAM_BOT_TOKEN = "9117274265:AAECiuQJHXhXf5ZY2jKgzZdagdF3hmTq_H0"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

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

if __name__ == "__main__":
    print("Interaktiw Bazar Boti işe başlady...")
    bot.infinity_polling()
