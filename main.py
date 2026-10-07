import requests
import time

TELEGRAM_TOKEN = "8504549527:AAF3rFrquLB68NP2G7vy8z5F6H-Qt8oM2hg"
CHAT_ID = "8566780139"

DEMAND_LOW = 4090.0
DEMAND_HIGH = 4120.0

SUPPLY_LOW = 4170.0
SUPPLY_HIGH = 4180.0

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        if res_data.get("ok"):
            print("✅ Alert ya tafi Telegram!")
        else:
            print(f"❌ Kuskure: {res_data}")
    except Exception as e:
        print(f"❌ Network issue: {e}")

def get_gold_price():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        return data.get('rates', {}).get('XAU', None)
    except:
        return None

print("=== BOT ƊINKA YA FARA AIKI A SERVER ===")
send_telegram_message(f"🚀 XAU/USD Signal Bot dinka yanzu yana aiki 24/7 a Server!\n\n📈 Supply: {SUPPLY_LOW} - {SUPPLY_HIGH}\n📉 Demand: {DEMAND_LOW} - {DEMAND_HIGH}")

last_signal = None

while True:
    price = get_gold_price()
    if price:
        print(f"Farashin yanzu: ${price}")
        
        if DEMAND_LOW <= price <= DEMAND_HIGH and last_signal != "BUY":
            msg = f"🚨 ALERT: BUY XAUUSD!\n\n🎯 Gold ya shiga DEMAND ZONE!\nPrice: ${price}\nZone: {DEMAND_LOW} - {DEMAND_HIGH}"
            send_telegram_message(msg)
            last_signal = "BUY"
            
        elif SUPPLY_LOW <= price <= SUPPLY_HIGH and last_signal != "SELL":
            msg = f"🚨 ALERT: SELL XAUUSD!\n\n🎯 Gold ya shiga SUPPLY ZONE!\nPrice: ${price}\nZone: {SUPPLY_LOW} - {SUPPLY_HIGH}"
            send_telegram_message(msg)
            last_signal = "SELL"
            
        elif price < DEMAND_LOW or (DEMAND_HIGH < price < SUPPLY_LOW) or price > SUPPLY_HIGH:
            last_signal = None
            
    time.sleep(60)
