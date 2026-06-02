import collections
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz  # For accurate Indian Timezone tracking

RAW_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

clean_token = RAW_TOKEN
for bad_word in ["https://", "http://", "api.telegram.org", "telegram.org", "bot", "/"]:
    clean_token = clean_token.replace(bad_word, "")

print("Connecting to live Kalyan Chart...")

url = "https://sattamatkadpboss.mobi"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

all_numbers = []

try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for td in soup.find_all('td'):
        text = td.text.strip().replace('-', '').replace(' ', '')
        if text.isdigit() and len(text) <= 4:
            all_numbers.extend(list(text))
            
except Exception as e:
    print(f"Network reading error: {e}")

if not all_numbers:
    print("Using exact historical baseline dataset...")
    all_numbers = list("5577225589071128679212901247535713601399144957802260")

# Calculate trends
digit_counts = collections.Counter(all_numbers)
top_items = digit_counts.most_common(2)

d1 = top_items[0][0] if len(top_items) > 0 else "7"
d2 = top_items[1][0] if len(top_items) > 1 else "2"

cut_numbers = {'1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4', '0':'5'}
c1 = cut_numbers.get(d1, "2")
c2 = cut_numbers.get(d2, "7")

# Generate live India Date and Time
ist_timezone = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist_timezone)
formatted_date = current_time_ist.strftime("%d-%m-%Y")
formatted_time = current_time_ist.strftime("%I:%M %p")

# Determine session variant based on hour (4 PM vs 6 PM runs)
current_hour = current_time_ist.hour
session_tag = "🔴 OPEN SESSION" if current_hour < 17 else "⚫ CLOSE SESSION"

# Format Telegram Message with live timestamps
message = (
    "📊 *KALYAN SYSTEM PREDICTIONS*\n"
    f"📅 *Date:* `{formatted_date}` | 🕒 *Time:* `{formatted_time}`\n"
    f"📌 *Market Timing:* `{session_tag}`\n"
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
            print("SUCCESS: Accurate timestamped panel dispatched to Telegram.")
        else:
            print(f"ERROR: {res.status_code}")
    except Exception as e:
        print(f"Failed to deliver: {e}")
