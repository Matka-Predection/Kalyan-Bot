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

def get_live_data():
    """Scrapes the chart and returns all digits and the latest active panna entry."""
    numbers = []
    latest_panna = ""
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Extract last row panna
            rows = soup.find_all('tr')
            if rows:
                for last_row in reversed(rows):
                    cells = [c.text.strip() for c in last_row.find_all('td') if c.text.strip()]
                    valid_pannas = [c for c in cells if c.isdigit() and len(c) == 3]
                    if valid_pannas:
                        latest_panna = valid_pannas[-1]
                        break
            
            # Extract historical digits
            for td in soup.find_all('td'):
                text = td.text.strip().replace('-', '').replace(' ', '')
                if text.isdigit() and len(text) <= 4:
                    numbers.extend(list(text))
    except Exception as e:
        print(f"Scrape warning: {e}")
    return numbers, latest_panna

print("Initializing live baseline data tracking...")
initial_numbers, baseline_panna = get_live_data()
print(f"Initial baseline Panna recorded: {baseline_panna}")

# Execution loop controls: scans every 10 seconds for up to 30 minutes (180 attempts)
max_checks = 180
check_interval = 10 
result_published = False

print("Starting live monitoring loop. Scanning site for changes every 10 seconds...")

for i in range(max_checks):
    current_numbers, current_panna = get_live_data()
    
    # Check if a new Panna has been posted or if the page data length has changed
    if (current_panna != baseline_panna and current_panna != "") or (len(current_numbers) > len(initial_numbers)):
        print(f"🔥 MATCH SEEN: New result published on website! Panna: {current_panna}")
        initial_numbers = current_numbers  # Update data pool with the newly published data
        baseline_panna = current_panna
        result_published = True
        break
        
    time.sleep(check_interval)

if not result_published:
    print("Timeout reached: No new update seen within 30 minutes. Dispatching current data.")

# --- Prediction Engine Calculations ---
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
session_tag = "🔴 OPEN SESSION" if current_time_ist.hour < 17 else "⚫ CLOSE SESSION"

# Generate Alert Layout
message = (
    "🚨 *KALYAN INSTANT RESULT PUBLISHED* 🚨\n"
    f"📅 *Date:* `{formatted_date}` | 🕒 *Time:* `{formatted_time}`\n"
    f"📌 *Market Timing:* `{session_tag}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"⚡ *LIVE RUNNING PANNA:* 🔥 `{baseline_panna if baseline_panna else 'Not Listed'}` 🔥\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "🔮 *Strongest Single Digits (OTC):*\n"
    f"👉 `{d1}` and `{d2}`\n\n"
    "🎲 *Top Target Jodis:* \n"
    f"👉 `{d1}{d2}`, `{d2}{d1}`, `{d1}{c1}`, `{d2}{c2}`\n\n"
    "📋 *Top Target Pannas:* \n"
    f"👉 `{d1}{d2}0`, `12{d1}`, `35{d2}`\n"
    "━━━━━━━━━━━━━━━━━━━━━"
)

# Dispatch Message
if clean_token and TELEGRAM_CHAT_ID:
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    base_domain = "api.telegram.org"
    endpoint_url = f"https://{base_domain}/bot{clean_token}/sendMessage"
    try:
        res = requests.post(endpoint_url, data=payload, timeout=15)
        if res.status_code == 200:
            print("SUCCESS: Instant update sent to Telegram.")
        else:
            print(f"Telegram error status: {res.status_code}")
    except Exception as e:
        print(f"Delivery failed: {e}")
