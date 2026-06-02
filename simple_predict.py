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

print("Initializing tracking engine...")
initial_numbers, baseline_panna = get_live_data()

# --- 3. Smart Monitoring Loop ---
max_checks = 180
check_interval = 10
result_published = False

# If a live panna is already present right now, bypass waiting entirely
if baseline_panna:
    print(f"Current live Panna detected instantly: {baseline_panna}. Skipping loop wait.")
    result_published = True
else:
    print("No live panna found yet. Entering loop monitoring state...")
    for i in range(max_checks):
        current_numbers, current_panna = get_live_data()
        
        # Trigger immediately if a new number gets published
        if current_panna != "" or (len(current_numbers) > len(initial_numbers)):
            print(f"New result published! Panna: {current_panna}")
            initial_numbers = current_numbers
            baseline_panna = current_panna
            result_published = True
            break
            
        time.sleep(check_interval)

if not result_published:
    print("Monitoring timeout reached. Processing baseline data trends.")

# Fallback data baseline check
if not initial_numbers:
    initial_numbers = list("5577225589071128679212901247535713601399144957802260")

# --- 4. Prediction Logic ---
digit_counts = collections.Counter(initial_numbers)
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

# --- 5. Generate Alert Message ---
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

# --- 6. Send to Telegram ---
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
            print(f"SUCCESS: Notification sent. Message ID: {new_msg_id}")
        else:
            print(f"Telegram returned error code: {res.status_code}")
    except Exception as e:
        print(f"Failed to deliver: {e}")
