#!/usr/bin/env python3
"""
Demo script with mock NSE data to demonstrate the complete workflow
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from value_extractor import OrderValueExtractor

# Mock NSE announcements (realistic format)
MOCK_ANNOUNCEMENTS = [
    {
        'symbol': 'TCS',
        'sm_name': 'Tata Consultancy Services Limited',
        'an_dt': '28-May-2026 10:30:00',
        'attchmntText': 'TCS announces winning a large digital transformation deal worth Rs. 1,200 crore from a leading US-based Fortune 500 financial services client',
        'attchmntFile': 'TCS_28052026_announcement.pdf',
        'desc': 'General Updates',
        'meta': {'industry': 'IT - Software'}
    },
    {
        'symbol': 'LT',
        'sm_name': 'Larsen & Toubro Limited',
        'an_dt': '27-May-2026 15:45:00',
        'attchmntText': 'L&T secures mega order worth Rs. 5,500 crores for construction of metro rail project in major Indian city. The project includes civil works, E&M systems, and station development.',
        'attchmntFile': 'LT_27052026_announcement.pdf',
        'desc': 'Press Release',
        'meta': {'industry': 'Construction'}
    },
    {
        'symbol': 'INFY',
        'sm_name': 'Infosys Limited',
        'an_dt': '26-May-2026 11:20:00',
        'attchmntText': 'Infosys wins multi-year contract valued at USD 150 million from European telecom major for cloud migration and application modernization services',
        'attchmntFile': 'INFY_26052026_announcement.pdf',
        'desc': 'Business Update',
        'meta': {'industry': 'IT - Software'}
    },
    {
        'symbol': 'HDFCBANK',
        'sm_name': 'HDFC Bank Limited',
        'an_dt': '28-May-2026 09:15:00',
        'attchmntText': 'HDFC Bank announces launch of new digital banking platform. Investment in technology infrastructure.',
        'attchmntFile': 'HDFC_28052026_announcement.pdf',
        'desc': 'Press Release',
        'meta': {'industry': 'Banking'}
    },
    {
        'symbol': 'RELIANCE',
        'sm_name': 'Reliance Industries Limited',
        'an_dt': '25-May-2026 14:30:00',
        'attchmntText': 'Reliance announces order book of Rs. 85,000 crores across various business segments including petrochemicals, retail, and digital services',
        'attchmntFile': 'RELIANCE_25052026_announcement.pdf',
        'desc': 'General Updates',
        'meta': {'industry': 'Diversified'}
    },
    {
        'symbol': 'WIPRO',
        'sm_name': 'Wipro Limited',
        'an_dt': '24-May-2026 16:00:00',
        'attchmntText': 'Wipro bags deal worth approximately Rs. 800 crore for IT infrastructure modernization project',
        'attchmntFile': 'WIPRO_24052026_announcement.pdf',
        'desc': 'Business Update',
        'meta': {'industry': 'IT - Software'}
    }
]

NIFTY50_COMPANIES = {
    'TCS': {'company_name': 'Tata Consultancy Services', 'industry': 'IT - Software'},
    'LT': {'company_name': 'Larsen & Toubro', 'industry': 'Construction'},
    'INFY': {'company_name': 'Infosys', 'industry': 'IT - Software'},
    'HDFCBANK': {'company_name': 'HDFC Bank', 'industry': 'Banking'},
    'RELIANCE': {'company_name': 'Reliance Industries', 'industry': 'Diversified'},
    'WIPRO': {'company_name': 'Wipro', 'industry': 'IT - Software'},
}


def demo_order_extraction():
    """Demonstrate order value extraction from mock announcements"""
    print("=" * 70)
    print("NSE ORDER BOOK TRACKER - DEMO WITH MOCK DATA")
    print("=" * 70)
    print()

    extractor = OrderValueExtractor()

    # Filter order-related announcements
    order_keywords = ['order', 'contract', 'win', 'award', 'TCV', 'deal', 'project']

    print("📊 STEP 1: Filtering Order-Related Announcements")
    print("-" * 70)

    order_announcements = []
    for ann in MOCK_ANNOUNCEMENTS:
        text = ann['attchmntText'].lower()
        if any(keyword in text for keyword in order_keywords):
            order_announcements.append(ann)
            print(f"✓ {ann['symbol']}: {ann['attchmntText'][:80]}...")

    print(f"\n🎯 Found {len(order_announcements)} order-related announcements")
    print()

    # Extract order values
    print("💰 STEP 2: Extracting Order Values")
    print("-" * 70)

    extracted_orders = []
    total_value = 0

    for ann in order_announcements:
        text = ann['attchmntText']
        value_info = extractor.extract_value(text)

        if value_info:
            order = {
                'symbol': ann['symbol'],
                'company_name': ann['sm_name'],
                'announcement_date': ann['an_dt'],
                'description': ann['attchmntText'][:200],
                'order_value': value_info['value'],
                'original_text': value_info['original_text'],
                'confidence': value_info['confidence']
            }
            extracted_orders.append(order)
            total_value += value_info['value']

            print(f"\n{ann['symbol']} - {ann['sm_name']}")
            print(f"  💰 Value: ₹{value_info['value']:.2f} Crores")
            print(f"  📝 Extracted from: '{value_info['original_text']}'")
            print(f"  🎯 Confidence: {value_info['confidence']:.0%}")
        else:
            print(f"\n{ann['symbol']} - Could not extract value")

    print()
    print("=" * 70)
    print(f"📈 SUMMARY")
    print("=" * 70)
    print(f"Total Orders Processed: {len(extracted_orders)}")
    print(f"Total Order Value: ₹{total_value:,.2f} Crores")
    print(f"Average Order Size: ₹{total_value/len(extracted_orders):,.2f} Crores")
    print()

    # Show telegram-style notification
    print("📱 TELEGRAM NOTIFICATION PREVIEW")
    print("=" * 70)
    print()
    print("📊 Order Book Update - Nifty 50")
    print()
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📈 Total Orders: {len(extracted_orders)}")
    print()

    for i, order in enumerate(extracted_orders, 1):
        print(f"{i}. {order['symbol']}")
        print(f"💰 Value: ₹{order['order_value']:.2f} Cr")
        desc = order['description']
        if len(desc) > 100:
            desc = desc[:97] + "..."
        print(f"📝 {desc}")
        print()

    print(f"💎 Total Value: ₹{total_value:,.2f} Crores")
    print()
    print("🤖 Automated update from NSE Order Book Tracker")
    print()

    # Sector breakdown
    print("=" * 70)
    print("📊 SECTOR BREAKDOWN")
    print("=" * 70)

    sector_stats = {}
    for order in extracted_orders:
        industry = NIFTY50_COMPANIES.get(order['symbol'], {}).get('industry', 'Unknown')
        if industry not in sector_stats:
            sector_stats[industry] = {'count': 0, 'value': 0}
        sector_stats[industry]['count'] += 1
        sector_stats[industry]['value'] += order['order_value']

    for sector, stats in sorted(sector_stats.items(), key=lambda x: x[1]['value'], reverse=True):
        print(f"{sector:20} : {stats['count']} orders, ₹{stats['value']:,.2f} Cr")

    print()
    print("✅ Demo completed successfully!")
    print()
    print("NOTE: This demo uses mock data. In production, the system fetches")
    print("      real-time data from NSE/BSE APIs and sends actual Telegram notifications.")


if __name__ == "__main__":
    demo_order_extraction()
