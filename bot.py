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
      InlineKeyboardButton("☀️ Solana (SOL)", callback_data="sig_SOL"),
  )
  return markup


def calc_ema(values, period):
  if not values:
    return 0.0
  k = 2 / (period + 1)
  ema = values[0]
  for v in values[1:]:
    ema = v * k + ema * (1 - k)
  return ema


def calc_rsi(closes, period=14):
  if len(closes) <= period:
    return 50.0
  gains = []
  losses = []
  for i in range(1, len(closes)):
    diff = closes[i] - closes[i - 1]
    gains.append(max(diff, 0.0))
    losses.append(max(-diff, 0.0))
  avg_gain = sum(gains[-period:]) / period
  avg_loss = sum(losses[-period:]) / period
  if avg_loss == 0:
    return 100.0
  rs = avg_gain / avg_loss
  return 100.0 - (100.0 / (1.0 + rs))


def get_filtered_signal(symbol):
  """
    Gaýtarýar:
      status: "UP", "DOWN", ýa-da "WAIT"
      minutes: 1, 2, 3 ýa-da 5 (diňe UP/DOWN wagtynda)
    """
  closes = []
  t_param = int(time.time() * 1000)

  try:
    if symbol not in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]:
      pair = f"{symbol}USDT"
      url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval=1m&limit=45&_={t_param}"
      resp = requests.get(url, timeout=4)
      klines = resp.json()
      if isinstance(klines, list) and len(klines) >= 25:
        for k in klines:
          closes.append(float(k[4]))
  except Exception as e:
    print(f"Klines säwligi ({symbol}): {e}")

  if len(closes) >= 25:
    rsi = calc_rsi(closes, 14)
    ema_fast = calc_ema(closes[-12:], 7)
    ema_slow = calc_ema(closes[-30:], 21)
    # Soňky 3 şemçäniň momentumy (umumy üýtgeşme)
    momentum = closes[-1] - closes[-4]

    # Ýokary gidiş şertleri: EMA gysga > EMA uzyn, Momentum > 0, RSI aşa gyzmadyk (< 72)
    bullish_ok = (ema_fast > ema_slow) and (momentum > 0) and (rsi < 72)

    # Aşak gidiş şertleri: EMA gysga < EMA uzyn, Momentum < 0, RSI aşa düşmedik (> 28)
    bearish_ok = (ema_fast < ema_slow) and (momentum < 0) and (rsi > 28)

    if bullish_ok:
      if rsi < 40:
        minutes = 3
      elif rsi < 55:
        minutes = 2
      else:
        minutes = 1
      return "UP", minutes

    if bearish_ok:
      if rsi > 60:
        minutes = 3
      elif rsi > 45:
        minutes = 2
      else:
        minutes = 1
      return "DOWN", minutes

    # Şertler doly gabat gelmese ýa-da garşylykly bolsa — ýalan signal bermeýär
    return "WAIT", None

  # Eger şemçe taryhy alynmadyk bolsa (meselem Forex ýa-da wagtlaýyn arakesme)
  return "WAIT", None


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.send_message(
      message.chat.id, "Bazary saýlaň:", reply_markup=get_market_keyboard()
  )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  symbol = call.data.replace("sig_", "")
  status, minutes = get_filtered_signal(symbol)
  xm_time = (
      datetime.datetime.utcnow() + datetime.timedelta(hours=2)
  ).strftime("%H:%M:%S")

  if status == "UP":
    big_arrow = "⬆️⬆️⬆️⬆️⬆️\n⬆️⬆️⬆️⬆️⬆️\n⬆️⬆️⬆️⬆️⬆️"
    body = f"{big_arrow}\n\n⏱️ **{minutes} MINUT**\n🕒 `{xm_time}` (GMT+2)"
  elif status == "DOWN":
    big_arrow = "⬇️⬇️⬇️⬇️⬇️\n⬇️⬇️⬇️⬇️⬇️\n⬇️⬇️⬇️⬇️⬇️"
    body = f"{big_arrow}\n\n⏱️ **{minutes} MINUT**\n🕒 `{xm_time}` (GMT+2)"
  else:
    body = f"⏸️ **GARAŞYŇ**\n\n🕒 `{xm_time}` (GMT+2)"

  text = f"**{symbol}**\n\n{body}"

  bot.answer_callback_query(call.id)
  bot.send_message(
      call.message.chat.id,
      text,
      reply_markup=get_market_keyboard(),
      parse_mode="Markdown",
  )


if __name__ == "__main__":
  print("Bot işe başlady...")
  bot.infinity_polling(timeout=60, long_polling_timeout=60)
