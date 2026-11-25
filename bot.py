import os
import pandas as pd
import yfinance as yf
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler,
                          CommandHandler, ContextTypes)

TOKEN = os.getenv("BOT_TOKEN")  # Railway Variables-da BOT_TOKEN goý

# Menýu: ady -> yfinance simwoly
MARKETS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "XAU/USD (Altyn)": "GC=F",
    "BTC/USD": "BTC-USD",
    "ETH/USD": "ETH-USD",
}


def analyze(symbol: str, interval="15m", period="5d"):
    df = yf.download(symbol, interval=interval, period=period, progress=False)
    if df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    c, h, l = df["Close"], df["High"], df["Low"]

    ema_fast = c.ewm(span=20, adjust=False).mean()
    ema_slow = c.ewm(span=50, adjust=False).mean()

    delta = c.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = 100 - 100 / (1 + gain / loss)

    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()

    price = float(c.iloc[-1])
    r = float(rsi.iloc[-1])
    a = float(atr.iloc[-1])
    up = ema_fast.iloc[-1] > ema_slow.iloc[-1]

    if up and 45 < r < 70:
        signal = "BUY 🟢"
        sl, tp = price - 1.5 * a, price + 3 * a
    elif (not up) and 30 < r < 55:
        signal = "SELL 🔴"
        sl, tp = price + 1.5 * a, price - 3 * a
    else:
        return f"⚪ WAIT (signal ýok)\nBaha: {price:.5f}\nRSI: {r:.1f}"

    return (f"{signal}\nBaha: {price:.5f}\nSL: {sl:.5f}\nTP: {tp:.5f}\n"
            f"RSI: {r:.1f}\nTF: {interval}\n\n⚠️ Kepillik ýok, töwekgelçiligi dolandyr.")


def menu():
    rows = [[InlineKeyboardButton(n, callback_data=n)] for n in MARKETS]
    return InlineKeyboardMarkup(rows)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bazary saýla:", reply_markup=menu())


async def pick(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    name = q.data
    text = analyze(MARKETS[name]) or "Maglumat tapylmady."
    await q.message.reply_text(f"📊 {name}\n{text}", reply_markup=menu())


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(pick))
    app.run_polling()


if __name__ == "__main__":
    main()
  
