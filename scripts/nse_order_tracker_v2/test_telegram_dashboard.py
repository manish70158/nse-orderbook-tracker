#!/usr/bin/env python3
"""
Test script for dashboard-style Telegram notifications
Run this to verify Telegram messages look like the web dashboard
"""

import os
import sys
from pathlib import Path
from telegram_notifier import TelegramNotifier
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_dashboard_notification():
    """Test sending dashboard-style notification"""
    logger.info("="*80)
    logger.info("TESTING DASHBOARD-STYLE TELEGRAM NOTIFICATION")
    logger.info("="*80)

    # Check credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        logger.error("❌ Telegram credentials not found!")
        logger.info("\nSet environment variables:")
        logger.info("  export TELEGRAM_BOT_TOKEN='your-bot-token'")
        logger.info("  export TELEGRAM_CHAT_ID='your-chat-id'")
        return False

    try:
        # Initialize notifier
        notifier = TelegramNotifier(value_threshold=500.0)

        # Test connection
        logger.info("\n1. Testing Telegram connection...")
        if not notifier.test_connection():
            logger.error("✗ Connection failed!")
            return False
        logger.info("✓ Connected successfully!")

        # Create sample data (similar to real data structure)
        sample_orders = [
            {
                'symbol': 'TCS',
                'company_name': 'Tata Consultancy Services Ltd',
                'announcement_date': '2026-05-28',
                'order_value_crores': 450.0,
                'subject': 'Awarding of Order - Digital Transformation Project for Government Department',
                'local_pdf_path': 'downloads/nse_pdfs/NSE_TCS_20260528.pdf'
            },
            {
                'symbol': 'LT',
                'company_name': 'Larsen & Toubro Limited',
                'announcement_date': '2026-05-29',
                'order_value_crores': 2500.0,
                'subject': 'Order Book Update - Major Metro Rail Infrastructure Project',
                'local_pdf_path': 'downloads/nse_pdfs/NSE_LT_20260529.pdf'
            },
            {
                'symbol': 'RELIANCE',
                'company_name': 'Reliance Industries Limited',
                'announcement_date': '2026-05-29',
                'order_value_crores': 1800.0,
                'subject': 'Contract Award - Petrochemical Manufacturing Facility Expansion',
                'local_pdf_path': 'downloads/nse_pdfs/NSE_RELIANCE_20260529.pdf'
            },
            {
                'symbol': 'WIPRO',
                'company_name': 'Wipro Limited',
                'announcement_date': '2026-05-30',
                'order_value_crores': 380.0,
                'subject': 'Order Received - IT Modernization and Cloud Services',
                'local_pdf_path': None  # No PDF for this one
            },
            {
                'symbol': 'INFY',
                'company_name': 'Infosys Limited',
                'announcement_date': '2026-05-30',
                'order_value_crores': 620.0,
                'subject': 'New Contract - Enterprise Digital Solutions for Banking Sector',
                'local_pdf_path': 'downloads/nse_pdfs/NSE_INFY_20260530.pdf'
            }
        ]

        # Create summary
        sample_summary = {
            'total_announcements': len(sample_orders),
            'total_value_crores': sum(o['order_value_crores'] for o in sample_orders),
            'average_order_value': sum(o['order_value_crores'] for o in sample_orders) / len(sample_orders),
            'unique_companies': len(set(o['symbol'] for o in sample_orders)),
            'days': 3,
            'date_range': {
                'start': '2026-05-28',
                'end': '2026-05-30'
            }
        }

        logger.info("\n2. Sending dashboard-style summary...")
        logger.info(f"   - Total orders: {len(sample_orders)}")
        logger.info(f"   - Total value: ₹{sample_summary['total_value_crores']:.2f} Cr")
        logger.info(f"   - Companies: {sample_summary['unique_companies']}")

        # Send dashboard summary
        success = notifier.send_dashboard_summary(
            orders=sample_orders,
            summary=sample_summary,
            days=3,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        if success:
            logger.info("✓ Dashboard summary sent successfully!")
            logger.info("\nCheck your Telegram to see the formatted report!")
            logger.info("It should look similar to the web dashboard.")
        else:
            logger.error("✗ Failed to send dashboard summary")
            return False

        # Also test high-value alerts (separate message)
        logger.info("\n3. Sending high-value order alerts...")
        high_value = [o for o in sample_orders if o['order_value_crores'] >= 500]

        if high_value:
            telegram_orders = []
            for order in high_value:
                telegram_orders.append({
                    'symbol': order['symbol'],
                    'company_name': order['company_name'],
                    'order_value': order['order_value_crores'],
                    'description': order['subject'],
                    'announcement_date': order['announcement_date'],
                    'pdf_path': order.get('local_pdf_path', '')
                })

            alert_success = notifier.send_order_summary(
                telegram_orders,
                date=f"{sample_summary['date_range']['start']} to {sample_summary['date_range']['end']}",
                filter_by_value=True,
                attach_pdfs=False  # Don't actually attach PDFs in test
            )

            if alert_success:
                logger.info(f"✓ High-value alerts sent ({len(high_value)} orders ≥₹500 Cr)")
            else:
                logger.warning("✗ Failed to send high-value alerts")

        logger.info("\n" + "="*80)
        logger.info("TEST COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        logger.info("\nWhat you should see in Telegram:")
        logger.info("  1. Dashboard-style report with:")
        logger.info("     - Summary stats (total announcements, value, average, companies)")
        logger.info("     - Complete order list with all details")
        logger.info("     - Color-coded values (🟢 high, 🟡 medium, 🔵 low)")
        logger.info("     - PDF availability status")
        logger.info("  2. High-value order alerts (≥₹500 Cr)")
        logger.info("     - Separate message with filtered orders")
        logger.info("="*80)

        return True

    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = test_dashboard_notification()
    sys.exit(0 if success else 1)
