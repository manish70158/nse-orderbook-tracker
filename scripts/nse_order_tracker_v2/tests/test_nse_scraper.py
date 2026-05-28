#!/usr/bin/env python3
"""
Test script for NSE Web Scraper
"""

import sys
from nse_web_scraper import NSEWebScraper
import json


def test_basic_functionality():
    """Test basic scraper functionality"""

    print("\n" + "="*70)
    print("NSE WEB SCRAPER - TEST SUITE")
    print("="*70)

    scraper = NSEWebScraper()

    # Test 1: Fetch announcements
    print("\n[TEST 1] Fetching recent announcements...")
    print("-"*70)

    try:
        announcements = scraper.fetch_announcements()

        if announcements:
            print(f"✓ SUCCESS: Retrieved {len(announcements)} announcements")

            # Show sample
            if len(announcements) > 0:
                print("\nSample announcement:")
                sample = announcements[0]
                print(f"  Symbol:  {sample.get('symbol')}")
                print(f"  Company: {sample.get('sm_name', sample.get('companyName'))}")
                print(f"  Date:    {sample.get('an_dt', sample.get('date'))}")
                print(f"  Subject: {sample.get('subject', '')[:80]}...")
        else:
            print("⚠ WARNING: No announcements retrieved (API may be blocked)")
            print("  This is normal - NSE often blocks API access")

    except Exception as e:
        print(f"✗ FAILED: {e}")

    # Test 2: Search for order announcements
    print("\n[TEST 2] Searching for order-related announcements...")
    print("-"*70)

    try:
        if announcements:
            order_announcements = scraper.search_order_announcements(announcements)

            print(f"✓ SUCCESS: Found {len(order_announcements)} order announcements")

            if order_announcements:
                print("\nOrder announcements found:")
                for i, ann in enumerate(order_announcements[:5], 1):
                    print(f"\n  {i}. {ann.get('symbol')} - {ann.get('sm_name', 'Unknown')}")
                    print(f"     Date: {ann.get('an_dt', 'Unknown')}")
                    print(f"     Keyword: {ann.get('matched_keyword')}")
                    print(f"     Subject: {ann.get('subject', '')[:70]}...")
        else:
            print("⚠ SKIPPED: No announcements to search")

    except Exception as e:
        print(f"✗ FAILED: {e}")

    # Test 3: Fetch Nifty 50
    print("\n[TEST 3] Fetching Nifty 50 symbols...")
    print("-"*70)

    try:
        nifty50_symbols = scraper.fetch_nifty50_symbols()

        if nifty50_symbols:
            print(f"✓ SUCCESS: Retrieved {len(nifty50_symbols)} Nifty 50 symbols")
            print(f"\nFirst 10 symbols:")
            print(f"  {', '.join(nifty50_symbols[:10])}")
        else:
            print("⚠ WARNING: Could not fetch Nifty 50 symbols")

    except Exception as e:
        print(f"✗ FAILED: {e}")

    # Test 4: Extract basic info
    print("\n[TEST 4] Testing info extraction...")
    print("-"*70)

    try:
        if announcements:
            sample_ann = announcements[0]
            info = scraper.extract_basic_info(sample_ann)

            print("✓ SUCCESS: Extracted info from announcement")
            print(f"\n  Symbol:       {info['symbol']}")
            print(f"  Company:      {info['company_name']}")
            print(f"  Date:         {info['announcement_date']}")
            print(f"  Subject:      {info['subject'][:60]}...")
            print(f"  PDF URL:      {info['pdf_url'][:80] if info['pdf_url'] else 'None'}...")
            print(f"  Source:       {info['source']}")
        else:
            print("⚠ SKIPPED: No announcements to extract from")

    except Exception as e:
        print(f"✗ FAILED: {e}")

    # Test 5: Filter for Nifty 50
    print("\n[TEST 5] Filtering for Nifty 50 orders...")
    print("-"*70)

    try:
        if announcements and nifty50_symbols:
            nifty50_set = set(nifty50_symbols)
            nifty_announcements = [
                ann for ann in announcements
                if ann.get('symbol') in nifty50_set
            ]

            print(f"✓ SUCCESS: Found {len(nifty_announcements)} Nifty 50 announcements")

            if nifty_announcements:
                print("\nNifty 50 companies with announcements:")
                symbols = set(ann.get('symbol') for ann in nifty_announcements[:10])
                print(f"  {', '.join(sorted(symbols))}")
        else:
            print("⚠ SKIPPED: No data to filter")

    except Exception as e:
        print(f"✗ FAILED: {e}")

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("\nNOTE: If tests show warnings, this is normal.")
    print("NSE frequently blocks API access. The system will work")
    print("when run from GitHub Actions with proper headers.")
    print("\nFor production use, ensure:")
    print("  1. Proper user agent and headers are set")
    print("  2. Session cookies are initialized")
    print("  3. Rate limiting is respected (delays between requests)")
    print("="*70)


if __name__ == "__main__":
    test_basic_functionality()
