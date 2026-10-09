from flask import Flask
from threading import Thread
import os
import requests
import time

app = Flask('')

@app.route('/')
def home():
    return "XAUUSD Signal Bot Active 24/7!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

keep_alive()

TELEGRAM_TOKEN = "8504549527:AAF3rFrquLB68NP2G7vy8zSF6H-Qt8oM2hg"
CHAT_ID = "8566780139"

last_signal = None  # Don gudun tura sako iri daya maimaitai

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"🔴 Error sending Telegram msg: {e}")

def get_klines():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=10"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            candles = []
            for c in data:
                candles.append({
                    'open': float(c[1]),
                    'high': float(c[2]),
                    'low': float(c[3]),
                    'close': float(c[4])
                })
            return candles
    except Exception as e:
        print(f"🔴 Market error: {e}")
    return None

def check_signals():
    global last_signal
    candles = get_klines()
    if not candles or len(candles) < 4:
        return

    c1, c2, c3 = candles[-4], candles[-3], candles[-2]
    curr = candles[-1]
    price = round(curr['close'], 2)

    # Alamomin Direction
    is_bullish = curr['close'] > curr['open']
    bullish_fvg = c3['low'] > c1['high']
    bearish_fvg = c1['low'] > c3['high']

    # 1. ALAMAR BUY
    if (is_bullish or bullish_fvg) and last_signal != "BUY":
        entry = price
        tp1 = round(entry + 3.0, 2)   # +30 Pips
        tp2 = round(entry + 7.0, 2)   # +70 Pips
        tp3 = round(entry + 12.0, 2)  # +120 Pips
        sl  = round(entry - 6.0, 2)   # -60 Pips

        msg = (
            f"🟢 *XAUUSD Buy Now*\n\n"
            f"📉 *Entry:* {entry}\n\n"
            f"🎯 *TP¹:* {tp1}\n"
            f"🎯 *TP²:* {tp2}\n"
            f"🎯 *TP³:* {tp3}\n\n"
            f"❌ *SL:* {sl}"
        )
        send_telegram_message(msg)
        last_signal = "BUY"

    # 2. ALAMAR SELL
    elif (not is_bullish or bearish_fvg) and last_signal != "SELL":
        entry = price
        tp1 = round(entry - 3.0, 2)   # -30 Pips
        tp2 = round(entry - 7.0, 2)   # -70 Pips
        tp3 = round(entry - 12.0, 2)  # -120 Pips
        sl  = round(entry + 6.0, 2)   # +60 Pips

        msg = (
            f"🔴 *XAUUSD Sell Now*\n\n"
            f"📉 *Entry:* {entry}\n\n"
            f"🎯 *TP¹:* {tp1}\n"
            f"🎯 *TP²:* {tp2}\n"
            f"🎯 *TP³:* {tp3}\n\n"
            f"❌ *SL:* {sl}"
        )
        send_telegram_message(msg)
        last_signal = "SELL"

while True:
    try:
        check_signals()
    except Exception as e:
        print(f"🔴 Error: {e}")
    time.sleep(300)  # Bincika a kowane minti 5
