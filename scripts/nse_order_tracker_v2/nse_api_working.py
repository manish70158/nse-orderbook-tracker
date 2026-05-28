#!/usr/bin/env python3
import requests
import time
import json
import gzip

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nseindia.com/companies-listing/corporate-filings-announcements'
})

# Visit announcements page to get cookies
print("Getting cookies...")
resp = session.get('https://www.nseindia.com/companies-listing/corporate-filings-announcements', timeout=15)
print(f"Status: {resp.status_code}, Cookies: {len(session.cookies)}")
time.sleep(3)

# Fetch API data
print("\nFetching announcements...")
resp = session.get('https://www.nseindia.com/api/corporate-announcements?index=equities', timeout=15)
print(f"Status: {resp.status_code}, Content-Length: {len(resp.content)}")

# Manually decompress gzip
try:
    decompressed = gzip.decompress(resp.content)
    data = json.loads(decompressed)
    
    print(f"\nSuccess! Got {len(data)} announcements")
    
    # Filter for "awarding of order"
    filtered = [ann for ann in data if 'awarding of order' in ann.get('subject', '').lower()]
    print(f"Found {len(filtered)} announcements matching 'awarding of order'")
    
    # Show first 5
    for i, ann in enumerate(filtered[:5], 1):
        print(f"\n{i}. {ann.get('symbol')} - {ann.get('sm_name', ann.get('companyName', 'Unknown'))}")
        print(f"   Subject: {ann.get('subject', '')[:80]}...")
        print(f"   Date: {ann.get('an_dt', ann.get('date', 'N/A'))}")
        print(f"   PDF: {ann.get('attchmntFile', ann.get('attachment', 'N/A'))}")
    
    # Save all matching announcements
    with open('order_announcements.json', 'w') as f:
        json.dump(filtered, f, indent=2)
    print(f"\nSaved {len(filtered)} announcements to order_announcements.json")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
