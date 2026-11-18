import requests
import time

# --- SAZLAMALAR ---
TELEGRAM_BOT_TOKEN = "7996669637:AAEztTnfTpzndg_x_oHBn16G6_VvHPfkw8k"
CHAT_ID = "7556694843"
SYMBOL = "EURUSD"                # Barlamak isleýän jübüňiz ýa-da instrumentiňiz

last_price = None

def get_xm_price():
    try:
        # Bazardaky nyrhlary alyp bérýän çeşme
        url = f"https://api.coinbase.com/v2/prices/{SYMBOL}-USD/spot"
        response = requests.get(url, timeout=10)
        data = response.json()
        price = float(data['data']['amount'])
        return price
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
