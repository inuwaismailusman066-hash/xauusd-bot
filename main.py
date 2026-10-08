from flask import Flask
from threading import Thread
import os
import requests
import time

app = Flask('')

@app.route('/')
def home():
    return "XAUUSD ICT Bot is Active & Running 24/7!"

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
        print(f"🔴 Market data fetch error: {e}")
    return None

last_signal = None  # Don gudun tura saƙo iri ɗaya a jere

def analyze_market():
    global last_signal
    try:
        candles = get_klines()
        if not candles or len(candles) < 5:
            return

        c1, c2, c3 = candles[-4], candles[-3], candles[-2]
        current_candle = candles[-1]
        
        # ICT Patterns
        bullish_fvg = c3['low'] > c1['high']
        bearish_fvg = c1['low'] > c3['high']
        ssl_sweep = current_candle['low'] < c1['low'] and current_candle['close'] > c1['low']
        bsl_sweep = current_candle['high'] > c1['high'] and current_candle['close'] < c1['high']

        # Dabarar gano Buy ko Sell na gaba ɗaya
        is_bullish = current_candle['close'] > current_candle['open']

        # BUY SIGNAL
        if bullish_fvg or ssl_sweep or (is_bullish and last_signal != "BUY"):
            quality = "🔥 MAI ƘARFI (ICT)" if (bullish_fvg or ssl_sweep) else "⚡ ALAMA TA KULLUM"
            msg = (
                f"🚀 *ALAMAR BUY ({quality})*\n\n"
                f"💰 *Farashi:* ${current_candle['close']}\n"
                f"🟢 *Bullish FVG:* {'E' if bullish_fvg else 'A\'a'}\n"
                f"🧹 *SSL Sweep:* {'E' if ssl_sweep else 'A\'a'}\n\n"
                "📍 *Kasuwa:* XAUUSD (Gold)"
            )
            send_telegram_message(msg)
            last_signal = "BUY"

        # SELL SIGNAL
        elif bearish_fvg or bsl_sweep or (not is_bullish and last_signal != "SELL"):
            quality = "🔥 MAI ƘARFI (ICT)" if (bearish_fvg or bsl_sweep) else "⚡ ALAMA TA KULLUM"
            msg = (
                f"🔻 *ALAMAR SELL ({quality})*\n\n"
                f"💰 *Farashi:* ${current_candle['close']}\n"
                f"🔴 *Bearish FVG:* {'E' if bearish_fvg else 'A\'a'}\n"
                f"🧹 *BSL Sweep:* {'E' if bsl_sweep else 'A\'a'}\n\n"
                "📍 *Kasuwa:* XAUUSD (Gold)"
            )
            send_telegram_message(msg)
            last_signal = "SELL"

    except Exception as e:
        print(f"🔴 Error in market analysis: {e}")

while True:
    try:
        analyze_market()
    except Exception as e:
        print(f"🔴 Loop error: {e}")
    time.sleep(60)
