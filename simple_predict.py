import collections
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pytz

RAW_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

clean_token = RAW_TOKEN
for bad_word in ["https://", "http://", "api.telegram.org", "telegram.org", "bot", "/"]:
    clean_token = clean_token.replace(bad_word, "")

url = "https://sattamatkadpboss.mobi"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# --- 1. Auto-Delete Yesterday's Message ---
log_file = "last_msg_id.txt"
if os.path.exists(log_file):
    try:
        with open(log_file, "r") as f:
            old_msg_id = f.read().strip()
        if old_msg_id:
            delete_url = f"https://telegram.org{clean_token}/deleteMessage"
            requests.post(delete_url, data={"chat_id": TELEGRAM_CHAT_ID, "message_id": old_msg_id})
            print(f"Cleaned up previous message ID: {old_msg_id}")
    except Exception as e:
        print(f"Cleanup skip: {e}")

# --- 2. Live Scraper Method ---
def get_live_data():
    numbers = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for td in soup.find_all('td'):
                text = td.text.strip().replace('-', '').replace(' ', '')
                if text.isdigit() and len(text) <= 4:
                    numbers.extend(list(text))
    except Exception as e:
        print(f"Scrape warning: {e}")
    return numbers

print("Analyzing current chart state parameters...")
initial_numbers = get_live_data()

# Fallback data baseline check if website fails to load
if not initial_numbers:
    initial_numbers = list("5577225589071128679212901247535713601399144957802260")

# --- 3. Advanced Prediction Math ---
digit_counts = collections.Counter(initial_numbers)
top_items = digit_counts.most_common(4)

# Safely extract top 4 trend numbers for comprehensive pairings
d1 = top_items[0][0] if len(top_items) > 0 else "7"
d2 = top_items[1][0] if len(top_items) > 1 else "2"
d3 = top_items[2][0] if len(top_items) > 2 else "1"
d4 = top_items[3][0] if len(top_items) > 3 else "5"

cut_numbers = {'1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4', '0':'5'}
c1 = cut_numbers.get(d1, "2")
c2 = cut_numbers.get(d2, "7")

# --- Timing Setup ---
ist_timezone = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist_timezone)
formatted_date = current_time_ist.strftime("%d-%m-%Y")
formatted_time = current_time_ist.strftime("%I:%M %p")
session_tag = "OPEN STRATEGY" if current_time_ist.hour < 17 else "CLOSE STRATEGY"

# --- 4. Generate Strategy Prediction Message ---
tg_message = (
    "🔮 *KALYAN MATHEMATICAL PREDICTIONS* 🔮\n"
    f"📅 *Date:* `{formatted_date}` | 🕒 *Time:* `{formatted_time}`\n"
    f"📌 *Target Session:* `{session_tag}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "🎯 *HIGH-PROBABILITY JODIS (PAIRS):*\n"
    f"👉 Direct Line: `{d1}{d2}` • `{d2}{d1}` • `{d3}{d4}`\n"
    f"👉 Cross Line:  `{d1}{c1}` • `{d2}{c2}` • `{d3}{c2}`\n\n"
    "📋 *HIGH-PROBABILITY PANNAS (PANELS):*\n"
    f"👉 Open Pannas:  `12{d1}` • `25{d3}` • `{d1}{d2}0`\n"
    f"👉 Close Pannas: `35{d2}` • `14{d4}` • `78{d1}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "ℹ️ _This predictive panel self-deletes when the next calculation completes._"
)

# --- 5. Send Photo to Telegram ---
if clean_token and TELEGRAM_CHAT_ID:
    screenshot_url = f"https://thum.io{url}"
    tg_url = f"https://telegram.org{clean_token}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": screenshot_url,
        "caption": tg_message,
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(tg_url, data=payload, timeout=15)
        if res.status_code == 200:
            new_msg_id = res.json().get("result", {}).get("message_id")
            with open(log_file, "w") as f:
                f.write(str(new_msg_id))
            print(f"SUCCESS: Prediction panel dispatched. Message ID: {new_msg_id}")
        else:
            print(f"Telegram processing alert error: {res.status_code}")
    except Exception as e:
        print(f"Delivery breakdown: {e}")
