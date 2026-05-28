import requests
import time

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
})

# Visit homepage first
print("Visiting homepage...")
resp = session.get('https://www.nseindia.com/', timeout=15)
print(f"Homepage status: {resp.status_code}")
time.sleep(3)

# Visit announcements page
print("\nVisiting announcements page...")
resp = session.get('https://www.nseindia.com/companies-listing/corporate-filings-announcements', timeout=15)
print(f"Announcements page status: {resp.status_code}")
print(f"Cookies: {dict(session.cookies)}")
time.sleep(3)

# Try API
print("\nTrying API...")
resp = session.get('https://www.nseindia.com/api/corporate-announcements?index=equities', timeout=15)
print(f"API status: {resp.status_code}")
print(f"Content length: {len(resp.content)}")
print(f"Content type: {resp.headers.get('Content-Type')}")
print(f"First 500 bytes: {resp.content[:500]}")
print(f"\nResponse text: '{resp.text[:200]}'")
