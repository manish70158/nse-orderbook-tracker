#!/usr/bin/env python3
"""
Discover NSE API endpoints by analyzing network requests
"""
import requests
import json

# NSE uses these API endpoints (from network inspection)
BASE_URL = "https://www.nseindia.com"

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nseindia.com/companies-listing/corporate-filings-announcements',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

# Create session to maintain cookies
session = requests.Session()
session.headers.update(HEADERS)

print("Step 1: Getting cookies by visiting homepage...")
try:
    response = session.get(BASE_URL, timeout=10)
    print(f"Homepage status: {response.status_code}")
    print(f"Cookies received: {len(session.cookies)}")
except Exception as e:
    print(f"Error visiting homepage: {e}")

print("\nStep 2: Trying to access announcements API...")

# Common NSE API endpoints for corporate announcements
api_endpoints = [
    "/api/corporate-announcements?index=equities",
    "/api/corporates-annc?index=equities",
    "/api/corporates-announcements",
    "/api/corporate-filings",
]

for endpoint in api_endpoints:
    url = BASE_URL + endpoint
    print(f"\nTrying: {url}")
    try:
        response = session.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Success! Got JSON with {len(data)} items")
                print(f"Sample keys: {list(data.keys()) if isinstance(data, dict) else 'List response'}")
                
                # Save successful response
                with open('nse_api_response.json', 'w') as f:
                    json.dump(data, f, indent=2)
                print("Saved response to nse_api_response.json")
                break
            except:
                print(f"Response is not JSON: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*60)
print("If none of these worked, we need to inspect the Network tab")
print("in Chrome DevTools to find the actual API endpoint.")
print("="*60)
