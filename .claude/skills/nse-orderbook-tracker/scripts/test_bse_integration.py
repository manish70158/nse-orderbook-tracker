#!/usr/bin/env python3
"""
Test BSE Integration - Verify that BSE data fetching works correctly
Run this before pushing to GitHub to ensure everything is working.
"""

import sys
from datetime import datetime

# Test imports
try:
    from bse import BSE
    from bse.constants import CATEGORY
    print("✓ BSE library imported successfully")
except ImportError as e:
    print(f"✗ BSE library import failed: {e}")
    print("  Install with: pip install bse")
    sys.exit(1)

try:
    from bse_data_fetcher import BSEFetcher
    print("✓ BSEFetcher imported successfully")
except ImportError as e:
    print(f"✗ BSEFetcher import failed: {e}")
    sys.exit(1)

try:
    from unified_data_fetcher import UnifiedDataFetcher
    print("✓ UnifiedDataFetcher imported successfully")
except ImportError as e:
    print(f"✗ UnifiedDataFetcher import failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("TEST 1: BSE Connection")
print("="*60)

try:
    import tempfile
    temp_dir = tempfile.mkdtemp()

    with BSE(download_folder=temp_dir) as bse:
        # Try to fetch announcements for a known scrip (Reliance)
        announcements = bse.announcements(
            scripcode='500325',  # Reliance
            from_date='01-04-2026',
            to_date='28-05-2026',
            category=CATEGORY.UPDATE
        )

        if announcements:
            print(f"✓ Successfully fetched {len(announcements) if isinstance(announcements, list) else 1} announcements from BSE")
            if isinstance(announcements, list) and announcements:
                print(f"  Sample: {list(announcements[0].keys())[:5]}...")
        else:
            print("⚠ No announcements found (this might be normal if there are no recent announcements)")

except Exception as e:
    print(f"✗ BSE connection failed: {e}")
    print("  This might be a network issue or API rate limit")

print("\n" + "="*60)
print("TEST 2: BSEFetcher Class")
print("="*60)

try:
    fetcher = BSEFetcher()
    print("✓ BSEFetcher initialized")

    # Test company list
    companies = fetcher.fetch_nifty50_companies()
    print(f"✓ Loaded {len(companies)} Nifty 50 companies with BSE scrip codes")

    if companies:
        print(f"  Sample: {companies[0]}")

except Exception as e:
    print(f"✗ BSEFetcher test failed: {e}")

print("\n" + "="*60)
print("TEST 3: Fetch Recent Announcements")
print("="*60)

try:
    fetcher = BSEFetcher()

    # Fetch announcements for just a few companies (faster test)
    test_companies = [
        ('TCS', '532540'),
        ('RELIANCE', '500325'),
        ('INFY', '500209')
    ]

    total_announcements = 0
    for symbol, scrip in test_companies:
        announcements = fetcher.fetch_announcements_for_company(
            scrip_code=scrip,
            from_date=datetime(2026, 5, 1),
            to_date=datetime(2026, 5, 28)
        )

        count = len(announcements) if isinstance(announcements, list) else (1 if announcements else 0)
        total_announcements += count
        print(f"  {symbol} ({scrip}): {count} announcements")

    print(f"✓ Total announcements fetched: {total_announcements}")

except Exception as e:
    print(f"✗ Announcement fetch failed: {e}")

print("\n" + "="*60)
print("TEST 4: UnifiedDataFetcher with BSE Priority")
print("="*60)

try:
    unified = UnifiedDataFetcher(prefer_bse=True)
    print("✓ UnifiedDataFetcher initialized with BSE priority")

    # Test company fetch
    companies = unified.fetch_nifty50_companies()
    print(f"✓ Fetched {len(companies)} companies")
    print(f"  Source used: {unified.last_successful_source}")

    # Test announcement fetch (limited to recent days for speed)
    print("\n  Fetching announcements (this may take a minute)...")
    announcements = unified.fetch_announcements(days_back=7)
    print(f"✓ Fetched {len(announcements)} announcements")
    print(f"  Primary source: {unified.last_successful_source}")

    if announcements:
        # Test order filtering
        order_announcements = unified.filter_order_announcements(announcements)
        print(f"✓ Found {len(order_announcements)} order-related announcements")

        if order_announcements:
            print(f"\n  Sample order announcement:")
            sample = order_announcements[0]
            print(f"    Symbol: {sample.get('symbol')}")
            print(f"    Date: {sample.get('an_dt')}")
            print(f"    Source: {sample.get('source')}")
            print(f"    Description: {sample.get('attchmntText', '')[:100]}...")

except Exception as e:
    print(f"✗ UnifiedDataFetcher test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST 5: Daily Order Checker Integration")
print("="*60)

try:
    from daily_order_checker import DailyOrderChecker
    print("✓ DailyOrderChecker imported successfully")

    # Check that it's using UnifiedDataFetcher
    checker = DailyOrderChecker()
    if hasattr(checker, 'data_fetcher'):
        print("✓ DailyOrderChecker is using UnifiedDataFetcher")
        if isinstance(checker.data_fetcher, UnifiedDataFetcher):
            print("✓ data_fetcher is correctly instantiated as UnifiedDataFetcher")
        else:
            print("✗ data_fetcher is not a UnifiedDataFetcher instance")
    else:
        print("✗ DailyOrderChecker is still using old NSEFetcher")

except Exception as e:
    print(f"✗ DailyOrderChecker integration test failed: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

print("""
✅ If all tests passed, you're ready to push to GitHub!
⚠️  If some tests failed due to network/API issues but imports work, it's OK.
❌ If imports failed, fix the dependencies before pushing.

Next steps:
1. Push these changes to GitHub
2. Go to your repository's Actions tab
3. Manually trigger the "Daily Order Book Check" workflow
4. Check Telegram for notifications
5. Monitor the workflow logs

The system will now try BSE first (more reliable), and only fall back
to NSE if BSE is unavailable. This should significantly improve
the success rate of your automated checks!
""")
