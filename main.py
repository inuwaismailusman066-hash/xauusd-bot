from flask import Flask
from threading import Thread
import os
import requests
import time

app = Flask('')

@app.route('/')
def home():
    return "XAUUSD ICT/SMC Bot is Active 24/7!"

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
        print(f"🔴 Error sending msg: {e}")

def get_klines():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=15"
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

def analyze_ict():
    candles = get_klines()
    if not candles or len(candles) < 5:
        return

    c1, c2, c3 = candles[-4], candles[-3], candles[-2]
    current = candles[-1]

    # 1. FAIR VALUE GAP (FVG)
    bullish_fvg = c3['low'] > c1['high']
    bearish_fvg = c1['low'] > c3['high']

    # 2. LIQUIDITY SWEEPS (SSL / BSL)
    ssl_sweep = current['low'] < c1['low'] and current['close'] > c1['low']
    bsl_sweep = current['high'] > c1['high'] and current['close'] < c1['high']

    # 3. ORDER BLOCK (OB)
    valid_bullish_ob = c2['close'] < c2['open'] and current['close'] > c2['high']
    valid_bearish_ob = c2['close'] > c2['open'] and current['close'] < c2['low']

    # TURA SAƘO IDAN AKA SAMU ALAMAR BUY
    if bullish_fvg or ssl_sweep or valid_bullish_ob:
        fvg_txt = "✅ An samu Valid FVG" if bullish_fvg else "❌ A'a"
        sweep_txt = "✅ An samut SSL Sweep" if ssl_sweep else "❌ A'a"
        ob_txt = "✅ Valid Bullish OB" if valid_bullish_ob else "❌ A'a"

        msg = (
            f"🔥 *ICT ALAMAR BUY (XAUUSD 15m)* 🔥\n\n"
            f"💰 *Farashi a yanzu:* ${current['close']}\n\n"
            f"📊 *Bayanin ICT Pattern:*\n"
            f"🔹 Fair Value Gap (FVG): {fvg_txt}\n"
            f"🔹 Liquidity Sweep (SSL): {sweep_txt}\n"
            f"🔹 Order Block (OB): {ob_txt}\n\n"
            f"🎯 *Shawarar Ciniki:* Zaka iya neman damar **BUY**!"
        )
        send_telegram_message(msg)

    # TURA SAƘO IDAN AKA SAMU ALAMAR SELL
    elif bearish_fvg or bsl_sweep or valid_bearish_ob:
        fvg_txt = "✅ An samu Valid FVG" if bearish_fvg else "❌ A'a"
        sweep_txt = "✅ An samu BSL Sweep" if bsl_sweep else "❌ A'a"
        ob_txt = "✅ Valid Bearish OB" if valid_bearish_ob else "❌ A'a"

        msg = (
            f"🔻 *ICT ALAMAR SELL (XAUUSD 15m)* 🔻\n\n"
            f"💰 *Farashi a yanzu:* ${current['close']}\n\n"
            f"📊 *Bayanin ICT Pattern:*\n"
            f"🔹 Fair Value Gap (FVG): {fvg_txt}\n"
            f"🔹 Liquidity Sweep (BSL): {sweep_txt}\n"
            f"🔹 Order Block (OB): {ob_txt}\n\n"
            f"🎯 *Shawarar Ciniki:* Zaka iya neman damar **SELL**!"
        )
        send_telegram_message(msg)

# Gudanar da binciken kasuwa
while True:
    try:
        analyze_ict()
    except Exception as e:
        print(f"🔴 Error: {e}")
    time.sleep(300)  # Zai riƙa duba kasuwa a kowace minti 5
