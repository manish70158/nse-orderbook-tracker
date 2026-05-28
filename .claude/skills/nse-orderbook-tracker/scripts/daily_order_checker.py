#!/usr/bin/env python3
"""
Daily Order Checker - Main script for GitHub Actions
Fetches new orders and sends Telegram notifications
"""

import sys
import os
from datetime import datetime, timedelta
import json
import logging

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from unified_data_fetcher import UnifiedDataFetcher
from value_extractor import OrderValueExtractor
from telegram_notifier import TelegramNotifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailyOrderChecker:
    """Orchestrates daily order checking and notification"""

    def __init__(self):
        self.data_fetcher = UnifiedDataFetcher(prefer_bse=True)
        self.value_extractor = OrderValueExtractor()
        self.telegram = TelegramNotifier()
        self.cache_file = 'processed_announcements.json'

    def load_processed_announcements(self):
        """Load previously processed announcement IDs"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return set(json.load(f))
        return set()

    def save_processed_announcements(self, processed_ids):
        """Save processed announcement IDs"""
        with open(self.cache_file, 'w') as f:
            json.dump(list(processed_ids), f)

    def generate_announcement_id(self, announcement):
        """Generate unique ID for announcement"""
        return f"{announcement.get('symbol')}_{announcement.get('an_dt')}_{announcement.get('attchmntFile', '')}"

    def run(self):
        """Main execution method"""
        logger.info("Starting daily order check...")

        try:
            # Test Telegram connection
            if not self.telegram.test_connection():
                logger.error("Failed to connect to Telegram. Aborting.")
                return 1

            # Fetch Nifty 50 companies
            logger.info("Fetching Nifty 50 companies...")
            companies = self.data_fetcher.fetch_nifty50_companies()
            nifty50_symbols = {comp['symbol'] for comp in companies}
            logger.info(f"Tracking {len(nifty50_symbols)} companies")
            logger.info(f"Data source: {self.data_fetcher.last_successful_source}")

            # Fetch announcements (tries BSE first, falls back to NSE)
            logger.info("Fetching announcements from available sources...")
            announcements = self.data_fetcher.fetch_announcements(days_back=30)
            logger.info(f"Retrieved {len(announcements)} total announcements")
            logger.info(f"Primary source: {self.data_fetcher.last_successful_source}")

            # Filter for order-related announcements
            order_announcements = self.data_fetcher.filter_order_announcements(
                announcements,
                nifty50_symbols
            )
            logger.info(f"Found {len(order_announcements)} order-related announcements")

            # Load previously processed announcements
            processed_ids = self.load_processed_announcements()
            logger.info(f"Previously processed: {len(processed_ids)} announcements")

            # Filter for new announcements only
            new_orders = []
            new_ids = set()

            for ann in order_announcements:
                ann_id = self.generate_announcement_id(ann)

                if ann_id in processed_ids:
                    continue

                # Extract order value
                text = (
                    ann.get('attchmntText', '') + ' ' +
                    ann.get('desc', '') + ' ' +
                    ann.get('subject', '')
                )
                value_info = self.value_extractor.extract_value(text)

                # Prepare order data
                order = {
                    'symbol': ann.get('symbol'),
                    'company_name': ann.get('sm_name'),
                    'announcement_date': ann.get('an_dt'),
                    'description': ann.get('attchmntText', '')[:500],  # Limit length
                    'order_value': value_info['value'] if value_info else None,
                    'pdf_url': self.data_fetcher.get_announcement_pdf_url(ann),
                    'source': ann.get('source', 'Unknown')
                }

                new_orders.append(order)
                new_ids.add(ann_id)

                logger.info(f"New order: {order['symbol']} - ₹{order['order_value']} Cr")

            # Send notifications
            if new_orders:
                logger.info(f"Sending notification for {len(new_orders)} new orders...")

                # Send summary notification
                success = self.telegram.send_order_summary(
                    new_orders,
                    date=datetime.now().strftime('%Y-%m-%d')
                )

                if success:
                    logger.info("✓ Notification sent successfully")

                    # Update processed IDs
                    processed_ids.update(new_ids)
                    self.save_processed_announcements(processed_ids)

                    # Optionally send individual alerts for high-value orders
                    for order in new_orders:
                        if order.get('order_value', 0) > 1000:  # > 1000 Cr
                            logger.info(f"Sending high-value alert for {order['symbol']}")
                            self.telegram.send_company_alert(order)

                else:
                    logger.error("✗ Failed to send notification")
                    return 1

            else:
                logger.info("No new orders found")
                # Optionally send "no updates" message
                # self.telegram.send_message("📊 No new orders today")

            logger.info("Daily check completed successfully")
            return 0

        except Exception as e:
            logger.error(f"Error during daily check: {e}", exc_info=True)

            # Send error notification
            try:
                self.telegram.send_message(
                    f"⚠️ <b>Order Tracker Error</b>\n\n"
                    f"Error during daily check:\n<code>{str(e)}</code>"
                )
            except:
                pass

            return 1


def main():
    """Entry point"""
    checker = DailyOrderChecker()
    exit_code = checker.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
