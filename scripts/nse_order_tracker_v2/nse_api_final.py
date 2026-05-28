#!/usr/bin/env python3
import requests
import time
import json

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

try:
    # Parse JSON directly
    data = json.loads(resp.content)
    
    print(f"\nSuccess! Got {len(data)} announcements")
    
    # Filter for "awarding of order"
    filtered = [ann for ann in data if 'awarding of order' in ann.get('subject', '').lower()]
    print(f"Found {len(filtered)} announcements matching 'awarding of order'")
    
    # Show all matching
    for i, ann in enumerate(filtered, 1):
        print(f"\n{i}. {ann.get('symbol')} - {ann.get('sm_name', ann.get('companyName', 'Unknown'))}")
        print(f"   Subject: {ann.get('subject', '')}")
        print(f"   Date: {ann.get('an_dt', ann.get('date', 'N/A'))}")
        
        # Find PDF attachment
        pdf = ann.get('attchmntFile', ann.get('attachment', ann.get('csvFile', 'N/A')))
        if pdf and pdf != 'N/A':
            full_pdf_url = f"https://nsearchives.nseindia.com/corporate/{pdf}"
            print(f"   PDF: {full_pdf_url}")
    
    # Save all matching announcements
    with open('order_announcements.json', 'w') as f:
        json.dump(filtered, f, indent=2)
    print(f"\n{'='*60}")
    print(f"Saved {len(filtered)} announcements to order_announcements.json")
    print(f"{'='*60}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
