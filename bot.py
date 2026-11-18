import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TELEGRAM_BOT_TOKEN = "9117274265:AAGxLEjHLdmgpCuxjA62r_7dE10_t6evAvk"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

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
            # Binance API arkaly has durnukly we çalt baha almak
            pair = f"{symbol}USDT"
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={pair}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if "price" in data:
                price = float(data["price"])
        
        if price is not None:
            # Kesgitli Satyn al ýa-da Sat maslahatyny bermek üçin logika
            int_part = int(price * 100)
            if int_part % 2 == 0:
                advice = "🟢 **SATYN ALYŇ (BUY)** 🚀"
            else:
                advice = "🔴 **SATYŇ (SELL)** 📉"
            
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
        "Salam! Bazary saýlaň, men size baha we takyk algy-saty maslahatyny görkezerin:", 
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
