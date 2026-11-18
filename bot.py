import requests
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- SAZLAMALAR ---
TELEGRAM_BOT_TOKEN = "7996669637:AAEN5UD8K4nu7N_Ro_7bEJovfVt3tReUSSY"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Bazar maglumatlaryny alyp berýän esasy funksiýa
code_symbols = {
    "EURUSD": "EUR",
    "GBPUSD": "GBP",
    "BTC": "BTC",
    "ETH": "ETH"
}

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
            # Kripto bahalary üçin açyk API
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            data = response.json()
            key = symbol.lower()
            if key in data and "usd" in data[key]:
                return float(data[key]["usd"])
    except Exception as e:
        print(f"Baha alyp bolmady ({symbol}): {e}")
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
        "Salam! Aşakdaky bazarlardan / aktivlerden birini saýlaň. Men size bahany we bazaryň ýagdaýyny (satmaly / satyn almaly) aýdyp bererin:", 
        reply_markup=markup
    )

# Düwmelere basylanda jogap beriş logikasy
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    symbol = call.data.split("_")[1]
    price = get_market_price(symbol)
    
    if price is not None:
        # Ýönekeý analitika mysaly (Baha we çaklama signal)
        # Hakyky täjirçilik üçin tehniki indikatorlar goşup bolar
        signal = "Häzirki wagtda bazary öwreniň (Neutral)"
        advice = "Garaşly ýagdaý"
        
        # Mysal üçin ýönekeý logika
        text = (
            f"📊 **Bazar Maglumaty: {symbol}**\n\n"
            f"💰 Häzirki baha: `{price}`\n"
            f"📈 Maslahat: **{advice}**\n"
            f"💡 *Üns beriň: Bu diňe maglumat maksatly berilýär, karary özüňiz alyň.*"
        )
    else:
        text = f"Bagyşlaň, {symbol} boýunça maglumat alyp bolmady."
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

if __name__ == "__main__":
    print("Interaktiw Bazar Boti işe başlady...")
    bot.infinity_polling()
