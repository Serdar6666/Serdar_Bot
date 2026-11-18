import requests
import time

# --- SAZLAMALAR ---
TELEGRAM_BOT_TOKEN = "7996669637:AAEztTnfTpzndg_x_oHBn16G6_VvHPfkw8k"
CHAT_ID = "7556694843"
SYMBOL = "EURUSD"

last_price = None

def get_xm_price():
    try:
        # Alternatiw ygtybarly açyk baha çeşmesi (Forex Exchange rates)
        url = "https://open.er-api.com/v6/latest/EUR"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # EUR to USD bahasyny alýarys
        if "rates" in data and "USD" in data["rates"]:
            return float(data["rates"]["USD"])
        return None
    except Exception as e:
        print(f"Baha alyp bolmady: {e}")
        return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegrama ugradyp bolmady: {e}")

def main():
    global last_price
    print("Bot işe başlady... Bahalar gözlenýär.")
    
    while True:
        current_price = get_xm_price()
        
        if current_price is not None:
            print(current_price) # Baha barlamak üçin logda görkezer
            if last_price is not None:
                if current_price > last_price:
                    msg = f"📈 *Baha Galýar!*\nInstrument: `{SYMBOL}`\nTäze baha: `{current_price}` (Öňki: `{last_price}`)"
                    send_telegram_message(msg)
                elif current_price < last_price:
                    msg = f"📉 *Baha Düşýär!*\nInstrument: `{SYMBOL}`\nTäze baha: `{current_price}` (Öňki: `{last_price}`)"
                    send_telegram_message(msg)
            
            last_price = current_price
            
        # Her 60 sekuntdan bir gezek barlaýar
        time.sleep(60)

if __name__ == "__main__":
    main()
