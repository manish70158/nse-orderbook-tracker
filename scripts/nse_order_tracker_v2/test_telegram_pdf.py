#!/usr/bin/env python3
"""
Test Telegram PDF attachment functionality
Run this to verify PDFs are being sent correctly
"""

import os
import sys
from pathlib import Path
from telegram_notifier import TelegramNotifier

def main():
    print("="*60)
    print("TELEGRAM PDF ATTACHMENT TEST")
    print("="*60 + "\n")

    # Check credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("❌ Telegram credentials not found!")
        print("\nPlease set environment variables:")
        print("  export TELEGRAM_BOT_TOKEN='your-bot-token'")
        print("  export TELEGRAM_CHAT_ID='your-chat-id'")
        print("\nSee docs/TELEGRAM_SETUP_GUIDE.md for help\n")
        return 1

    try:
        # Initialize notifier with low threshold for testing
        notifier = TelegramNotifier(value_threshold=100.0)
        print("✓ Notifier initialized\n")

        # Test connection
        print("Testing connection...")
        if not notifier.test_connection():
            print("❌ Connection failed!\n")
            return 1
        print("✓ Connected successfully\n")

        # Check for test PDF
        pdf_path = 'downloads/nse_pdfs/LIKHITHA_2026-05-28.pdf'
        if not Path(pdf_path).exists():
            print(f"❌ Test PDF not found: {pdf_path}")
            print("\nPlease run orchestrator first to download PDFs:")
            print("  python orchestrator.py --days 1\n")
            return 1

        print(f"✓ Found test PDF: {pdf_path}\n")

        # Test order data
        test_order = {
            'symbol': 'LIKHITHA',
            'company_name': 'Likhitha Infrastructure',
            'order_value': 121.04,
            'description': 'Awarding of order for infrastructure project',
            'announcement_date': '2026-05-28',
            'pdf_path': pdf_path,
            'pdf_url': 'https://www.nseindia.com/...'
        }

        # Test 1: Send summary with PDF attachment
        print("Test 1: Sending order summary WITH PDF attachment...")
        success = notifier.send_order_summary(
            [test_order],
            date='2026-05-28 (Test)',
            filter_by_value=False,  # Don't filter for testing
            attach_pdfs=True
        )

        if success:
            print("✓ Summary and PDF sent successfully!\n")
        else:
            print("❌ Failed to send summary\n")
            return 1

        # Test 2: Send summary WITHOUT PDF attachment (for comparison)
        print("Test 2: Sending order summary WITHOUT PDF attachment...")
        success = notifier.send_order_summary(
            [test_order],
            date='2026-05-28 (Test - No PDF)',
            filter_by_value=False,
            attach_pdfs=False
        )

        if success:
            print("✓ Text-only summary sent successfully!\n")
        else:
            print("❌ Failed to send text-only summary\n")
            return 1

        # Test 3: Send individual company alert with PDF
        print("Test 3: Sending individual company alert WITH PDF...")
        success = notifier.send_company_alert(test_order, attach_pdf=True)

        if success:
            print("✓ Company alert and PDF sent successfully!\n")
        else:
            print("❌ Failed to send company alert\n")
            return 1

        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nCheck your Telegram chat to see:")
        print("  1. Order summary with PDF attachment")
        print("  2. Order summary without PDF (text only)")
        print("  3. Individual company alert with PDF")
        print("\nPDFs should appear as document attachments with captions.\n")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
