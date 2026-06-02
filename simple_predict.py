import collections
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

RAW_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

clean_token = RAW_TOKEN
for bad_word in ["https://", "http://", "api.telegram.org", "telegram.org", "bot", "/"]:
    clean_token = clean_token.replace(bad_word, "")

print("Connecting to live Kalyan Chart...")

url = "https://sattamatkadpboss.mobi"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

all_numbers = []
running_panna = "Awaiting Live Update"

try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. Extract the actual Running Live Panna from the very last row of the table
    rows = soup.find_all('tr')
    if rows:
        # Scan backward from the last row to find the most recent non-empty entry
        for last_row in reversed(rows):
            cells = [cell.text.strip() for cell in last_row.find_all('td') if cell.text.strip()]
            valid_pannas = [c for c in cells if c.isdigit() and len(c) == 3]
            if valid_pannas:
                # The latest active 3-digit panel showing on the website chart
                running_panna = valid_pannas[-1]
                break

    # 2. Gather historical distribution for prediction logic
    for td in soup.find_all('td'):
        text = td.text.strip().replace('-', '').replace(' ', '')
        if text.isdigit() and len(text) <= 4:
            all_numbers.extend(list(text))
            
except Exception as e:
    print(f"Network tracking error: {e}")

if not all_numbers:
    all_numbers = list("5577225589071128679212901247535713601399144957802260")

# Logic calculations
digit_counts = collections.Counter(all_numbers)
top_items = digit_counts.most_common(2)

d1 = top_items[0][0] if len(top_items) > 0 else "7"
d2 = top_items[1][0] if len(top_items) > 1 else "2"

cut_numbers = {'1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4', '0':'5'}
c1 = cut_numbers.get(d1, "2")
c2 = cut_numbers.get(d2, "7")

# Timing Setup
ist_timezone = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist_timezone)
formatted_date = current_time_ist.strftime("%d-%m-%Y")
formatted_time = current_time_ist.strftime("%I:%M %p")
session_tag = "🔴 OPEN SESSION" if current_time_ist.hour < 17 else "⚫ CLOSE SESSION"

# Message layout containing the Live Running Panna
message = (
    "🎯 *KALYAN LIVE STATUS & PREDICTIONS*\n"
    f"📅 *Date:* `{formatted_date}` | 🕒 *Time:* `{formatted_time}`\n"
    f"📌 *Market Timing:* `{session_tag}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"⚡ *LIVE RUNNING PANNA:* 🔥 `{running_panna}` 🔥\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "🔮 *Strongest Single Digits (OTC):*\n"
    f"👉 `{d1}` and `{d2}`\n\n"
    "🎲 *Top Target Jodis:* \n"
    f"👉 `{d1}{d2}`, `{d2}{d1}`, `{d1}{c1}`, `{d2}{c2}`\n\n"
    "📋 *Top Target Pannas:* \n"
    f"👉 `{d1}{d2}0`, `12{d1}`, `35{d2}`\n"
    "━━━━━━━━━━━━━━━━━━━━━"
)

if clean_token and TELEGRAM_CHAT_ID:
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    base_domain = "api.telegram.org"
    endpoint_url = f"https://{base_domain}/bot{clean_token}/sendMessage"
    
    try:
        res = requests.post(endpoint_url, data=payload, timeout=15)
        if res.status_code == 200:
            print("SUCCESS: Live running panna data sent to Telegram.")
        else:
            print(f"ERROR: {res.status_code}")
    except Exception as e:
        print(f"Failed to deliver: {e}")
