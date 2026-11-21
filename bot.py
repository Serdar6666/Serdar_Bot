import asyncio
import os
from datetime import datetime, timezone

import pandas as pd
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# ===== Sazlamalar =====
BOT_TOKEN = os.environ["BOT_TOKEN = os.environ["BOT_TOKEN"]   # Railway Variables-dan alynýar
INTERVAL = "1h"                     # şem wagty: 15m, 1h, 4h, 1d
RSI_BUY = 30
RSI_SELL = 70

# Menýuda görkeziljek bazarlar: ady -> Binance jübüti
MARKETS = {
    "₿ Bitcoin": "BTCUSDT",
    "Ξ Ethereum": "ETHUSDT",
    "BNB": "BNBUSDT",
    "Solana": "SOLUSDT",
    "XRP": "XRPUSDT",
    "Dogecoin": "DOGEUSDT",
}


def rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss)


def analyze(symbol):
    r = requests.get(
        "https://data-api.binance.vision/api/v3/klines",
        params={"symbol": symbol, "interval": INTERVAL, "limit": 200},
        timeout=10,
    )
    r.raise_for_status()
    closes = pd.Series([float(k[4]) for k in r.json()])

    price = closes.iloc[-1]
    value = rsi(closes).iloc[-1]
    ema20 = closes.ewm(span=20, adjust=False).mean().iloc[-1]
    ema50 = closes.ewm(span=50, adjust=False).mean().iloc[-1]
    trend = "ýokary 📈" if ema20 > ema50 else "aşak 📉"

    if value < RSI_BUY:
        signal = "🟢 BUY (satyn al)"
    elif value > RSI_SELL:
        signal = "🔴 SELL (sat)"
    else:
        signal = "🟡 GARAŞ (aýdyň signal ýok)"

    now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return (
        f"{symbol} ({INTERVAL})\n\n"
        f"Signal: {signal}\n"
        f"Baha: {price:,.4f}\n"
        f"RSI: {value:.1f}\n"
        f"Tendensiýa (EMA20/50): {trend}\n\n"
        f"🕒 {now}\n"
        f"⚠️ Maliýe maslahaty däl."
    )


def menu_keyboard():
    buttons = [
        InlineKeyboardButton(name, callback_data=f"m:{symbol}")
        for name, symbol in MARKETS.items()
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bazar saýla:", reply_markup=menu_keyboard())


async def on_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu":
        await query.edit_message_text("Bazar saýla:", reply_markup=menu_keyboard())
        return

    symbol = query.data.split(":", 1)[1]
    try:
        text = await asyncio.to_thread(analyze, symbol)
    except Exception:
        text = "Maglumat alyp bolmady, birazdan täzeden synap gör."

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔄 Täzele", callback_data=f"m:{symbol}"),
        InlineKeyboardButton("⬅️ Yza", callback_data="menu"),
    ]])
    await query.edit_message_text(text, reply_markup=keyboard)


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_click))
    app.run_polling()


if __name__ == "__main__":
    main()
