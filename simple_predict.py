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
# We read the saved ID from the previous run and delete it to keep the chat clean
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

# --- 2. Live Scraper Loop ---
def get_live_data():
    numbers = []
    latest_panna = ""
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.find_all('tr')
            if rows:
                for last_row in reversed(rows):
                    cells = [c.text.strip() for c in last_row.find_all('td') if c.text.strip()]
                    valid_pannas = [c for c in cells if c.isdigit() and len(c) == 3]
                    if valid_pannas:
                        latest_panna = valid_pannas[-1]
                        break
            for td in soup.find_all('td'):
                text = td.text.strip().replace('-', '').replace(' ', '')
                if text.isdigit() and len(text) <= 4:
                    numbers.extend(list(text))
    except Exception as e:
        print(f"Scrape warning: {e}")
    return numbers, latest_panna

print("Scanning live chart data...")
initial_numbers, baseline_panna = get_live_data()

max_checks = 180
for i in range(max_checks):
    current_numbers, current_panna = get_live_data()
    if (current_panna != baseline_panna and current_panna != "") or (len(current_numbers) > len(initial_numbers)):
        initial_numbers = current_numbers
        baseline_panna = current_panna
        break
    time.sleep(10)

# --- 3. Prediction Math ---
digit_counts = collections.Counter(initial_numbers if initial_numbers else list("55772255"))
top_items = digit_counts.most_common(2)
d1 = top_items[0][0] if len(top_items) > 0 else "7"
d2 = top_items[1][0] if len(top_items) > 1 else "2"

cut_numbers = {'1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4', '0':'5'}
c1, c2 = cut_numbers.get(d1, "2"), cut_numbers.get(d2, "7")

ist_timezone = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist_timezone)
formatted_date = current_time_ist.strftime("%d-%m-%Y")
formatted_time = current_time_ist.strftime("%I:%M %p")
session_tag = "OPEN SESSION" if current_time_ist.hour < 17 else "CLOSE SESSION"

# --- 4. Generate Alert Message ---
tg_message = (
    "🚨 *KALYAN INSTANT RESULT* 🚨\n"
    f"📅 *Date:* `{formatted_date}` | 🕒 *Time:* `{formatted_time}`\n"
    f"📌 *Timing:* `{session_tag}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"⚡ *LIVE RUNNING PANNA:* 🔥 `{baseline_panna if baseline_panna else 'Not Listed'}` 🔥\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"🔮 *Single Digits:* `{d1}` and `{d2}`\n"
    f"🎲 *Top Jodis:* `{d1}{d2}`, `{d2}{d1}`, `{d1}{c1}`, `{d2}{c2}`\n"
    f"📋 *Top Pannas:* `{d1}{d2}0`, `12{d1}`, `35{d2}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "ℹ️ _This alert will self-delete when the next session updates._"
)

# --- 5. Dispatch Screenshot Image with Text Caption ---
if clean_token and TELEGRAM_CHAT_ID:
    # Generates a fresh picture snapshot of the live table layout
    screenshot_url = f"https://thum.io{url}"
    
    tg_url = f"https://telegram.org{clean_token}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": screenshot_url,
        "caption": tg_message,
        "parse_mode": "Markdown"
    }
    
    res = requests.post(tg_url, data=payload)
    if res.status_code == 200:
        # Save the new message ID so the next run can find it and delete it
        new_msg_id = res.json().get("result", {}).get("message_id")
        with open(log_file, "w") as f:
            f.write(str(new_msg_id))
        print(f"SUCCESS: Alert sent. Saved message ID: {new_msg_id}")
    else:
        print(f"Telegram error: {res.status_code}")
