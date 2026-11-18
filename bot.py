import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Siziň täze we hakyky tokeniňiz
TELEGRAM_BOT_TOKEN = "9117274265:AAGxLEjHLdmgpCuxjA62r_7dE10_t6evAvk"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Öňki bahalary ýadynda saklamak üçin
last_prices = {}

def get_market_analysis(symbol):
    try:
        price = None
        if symbol in ["EURUSD", "GBPUSD"]:
            base = symbol[:3]
            target = symbol[3:]
            url = f"https://open.er-api.com/v6/latest/{base}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if "rates" in data and target in data["rates"]:
                price = float(data["rates"][target])
        elif symbol in ["BTC", "ETH"]:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            data = response.json()
            key = symbol.lower()
            if key in data and "usd" in data[key]:
                price = float(data[key]["usd"])
        
        if price is not None:
            advice = "Bazary öwreniň (Neutral) ⚖️"
            if symbol in last_prices:
                if price > last_prices[symbol]:
                    advice = "🟢 **SATYN ALYŇ (BUY)** 🚀"
                elif price < last_prices[symbol]:
                    advice = "🔴 **SATYŇ (SELL)** 📉"
            
            last_prices[symbol] = price
            return price, advice
            
    except Exception as e:
        print(f"Baha alnanda säwlik çykdy ({symbol}): {e}")
    
    return None, "Maglumat ýok"

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
        "Salam! Bazary saýlaň, men size baha we hakyky algy-saty maslahatyny görkezerin:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    symbol = call.data.replace("price_", "")
    price, advice = get_market_analysis(symbol)
    
    if price is not None:
        text = (
            f"📊 **Bazar Maglumaty: {symbol}**\n\n"
            f"💰 Häzirki baha: `{price}`\n"
            f"📈 Maslahat: {advice}\n"
            f"💡 *Maglumat maksatly berilýär.*"
        )
    else:
        text = f"Bagyşlaň, {symbol} boýunça maglumat alyp bolmady."
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot işe başlady...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
