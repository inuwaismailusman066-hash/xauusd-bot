from flask import Flask
from threading import Thread
import os
import requests
import time
from datetime import datetime, timezone

app = Flask('')

@app.route('/')
def home():
    return "XAUUSD Bot Test Mode Active!"

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
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Response: {response.text}")
    except Exception as e:
        print(f"🔴 Error sending message: {e}")

# SAQON GWAJI (Test Message da zaran bot ya fara aiki)
def send_startup_test():
    msg = (
        "🟢 *GWAJIN BOT (TEST SUCCESSFUL)* 🟢\n\n"
        "✨ Bot ɗinka na XAUUSD yana aiki daidai!\n"
        "📱 Lambobin Telegram ɗinka sun haɗu da kyau.\n"
        "📊 Yanzu yana jira ne kasuwa ta buɗe ranar Litinin domin fara turo sigina da labarai."
    )
    send_telegram_message(msg)

# Aika sakon gwaji sau ɗaya idan ya fara
send_startup_test()

last_signal = None

def check_upcoming_news():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            events = res.json()
            now = datetime.now(timezone.utc)
            for event in events:
                if event.get('impact') == 'High' and event.get('country') == 'USD':
                    date_str = event.get('date')
                    event_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    diff_minutes = (event_time - now).total_seconds() / 60
                    if 4 <= diff_minutes <= 6:
                        title = event.get('title')
                        msg = (
                            f"⚠️ *GARGAƊI: BARRAN LABARIN TASIRI (HIGH IMPACT)* ⚠️\n\n"
                            f"📊 *Sunan Labari:* {title}\n"
                            f"💵 *Kasuwa:* USD / XAUUSD (Gold)\n"
                            f"⏰ *Lokaci:* Zai fito nan da minti 5 masu zuwa!"
                        )
                        send_telegram_message(msg)
    except Exception as e:
        print(f"🔴 News check error: {e}")

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

    is_bullish = curr['close'] > curr['open']
    bullish_fvg = c3['low'] > c1['high']
    bearish_fvg = c1['low'] > c3['high']

    if (is_bullish or bullish_fvg) and last_signal != "BUY":
        entry = price
        tp1 = round(entry + 3.0, 2)
        tp2 = round(entry + 7.0, 2)
        tp3 = round(entry + 12.0, 2)
        sl  = round(entry - 6.0, 2)

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

    elif (not is_bullish or bearish_fvg) and last_signal != "SELL":
        entry = price
        tp1 = round(entry - 3.0, 2)
        tp2 = round(entry - 7.0, 2)
        tp3 = round(entry - 12.0, 2)
        sl  = round(entry + 6.0, 2)

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
        check_upcoming_news()
        check_signals()
    except Exception as e:
        print(f"🔴 Loop Error: {e}")
    time.sleep(300)
