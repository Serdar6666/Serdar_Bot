import requests
import time

TELEGRAM_BOT_TOKEN = "9117274265:AAECiuQJHXhXf5ZY2jKgzZdagdF3hmTq_H0"

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

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegrama ugradyp bolmady: {e}")

def main():
    print("Bot göni HTTP arkaly işe başlady...")
    offset = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35)
            data = response.json()
            
            if "result" in data:
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    
                    # Eger ulanyjydan habar gelen bolsa
                    if "message" in update:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"].get("text", "")
                        
                        if text == "/start":
                            markup = {
                                "inline_keyboard": [
                                    [{"text": "💶 EUR/USD", "callback_data": "EURUSD"}, {"text": "💷 GBP/USD", "callback_data": "GBPUSD"}],
                                    [{"text": "₿ Bitcoin (BTC)", "callback_data": "BTC"}, {"text": "Ξ Ethereum (ETH)", "callback_data": "ETH"}]
                                ]
                            }
                            send_message(chat_id, "Salam! Aşakdaky bazarlardan birini saýlaň:", reply_markup=markup)
                    
                    # Eger düwmä basylan bolsa (callback query)
                    elif "callback_query" in update:
                        callback = update["callback_query"]
                        chat_id = callback["message"]["chat"]["id"]
                        symbol = callback["data"]
                        callback_id = callback["id"]
                        
                        # Callback bildirişini aýyrmak
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery", json={"callback_query_id": callback_id})
                        
                        price = get_market_price(symbol)
                        if price is not None:
                            msg = f"📊 *Bazar Maglumaty: {symbol}*\n\n💰 Häzirki baha: `{price}`\n📈 Maslahat: **Bazary öwreniň (Neutral)**"
                        else:
                            msg = f"Bagyşlaň, {symbol} boýunça maglumat alyp bolmady."
                            
                        send_message(chat_id, msg)
                        
        except Exception as e:
            print(f"Säwlik: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
