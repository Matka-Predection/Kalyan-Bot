import collections
import requests
from bs4 import BeautifulSoup

print("Fetching live data from Kalyan Chart...")

url = "https://sattamatkadpboss.mobi"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    all_numbers = []
    for td in soup.find_all('td'):
        text = td.text.strip()
        if text.isdigit():
            all_numbers.extend(list(text))

    if not all_numbers:
        print("No data found. The site layout might have changed.")
        exit()

    digit_counts = collections.Counter(all_numbers)
    top_digits = [digit for digit, count in digit_counts.most_common(3)]

    cut_numbers = {'1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4', '0':'5'}
    d1, d2 = top_digits[0], top_digits[1]
    c1, c2 = cut_numbers[d1], cut_numbers[d2]

    print("\n===============================")
    print("   KALYAN AUTOMATED PREDICTIONS ")
    print("===============================")
    print(f"Strongest Single Digits: {d1}, {d2}")
    print(f"Top Target Jodis       : {d1}{d2}, {d2}{d1}, {d1}{c1}")
    print(f"Top Target Pannas      : {d1}{d2}0, 12{d1}, 35{d2}")
    print("===============================")

except Exception as e:
    print(f"An error occurred: {e}")
