#!/usr/bin/env python3
"""
Telegram Notifier - Send order book updates via Telegram
Enhanced with 500 crore threshold filtering and PDF attachments
"""

import os
import requests
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications to Telegram with filtering for high-value orders"""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None,
                 value_threshold: float = 500.0):
        """
        Initialize Telegram notifier

        Args:
            bot_token: Telegram Bot API token (or set TELEGRAM_BOT_TOKEN env var)
            chat_id: Telegram chat ID to send messages (or set TELEGRAM_CHAT_ID env var)
            value_threshold: Minimum order value in crores to send alert (default: 500)
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.value_threshold = value_threshold

        if not self.bot_token or not self.chat_id:
            raise ValueError(
                "Telegram credentials not provided. Set TELEGRAM_BOT_TOKEN and "
                "TELEGRAM_CHAT_ID environment variables or pass them to constructor."
            )

        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to Telegram

        Args:
            message: Message text (supports HTML or Markdown)
            parse_mode: 'HTML' or 'Markdown'

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Message sent successfully to Telegram")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def send_document(self, file_path: str, caption: Optional[str] = None,
                     parse_mode: str = "HTML") -> bool:
        """
        Send a document (PDF) to Telegram

        Args:
            file_path: Path to the document file
            caption: Optional caption for the document (supports HTML or Markdown)
            parse_mode: 'HTML' or 'Markdown'

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.api_url}/sendDocument"

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            logger.error(f"File not found: {file_path}")
            return False

        try:
            with open(file_path, 'rb') as document:
                files = {'document': (file_path_obj.name, document, 'application/pdf')}
                data = {
                    'chat_id': self.chat_id,
                    'parse_mode': parse_mode
                }

                if caption:
                    data['caption'] = caption

                response = requests.post(url, data=data, files=files, timeout=30)
                response.raise_for_status()
                logger.info(f"Document sent successfully: {file_path_obj.name}")
                return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send document {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return False

    def filter_high_value_orders(self, orders: List[Dict]) -> List[Dict]:
        """
        Filter orders above value threshold

        Args:
            orders: List of order dictionaries

        Returns:
            Filtered list of high-value orders
        """
        high_value = [
            order for order in orders
            if order.get('order_value', 0) >= self.value_threshold
        ]
        logger.info(f"Filtered {len(high_value)} orders above ₹{self.value_threshold} Cr threshold")
        return high_value

    def send_order_summary(self, orders: List[Dict], date: Optional[str] = None,
                          filter_by_value: bool = True, attach_pdfs: bool = True) -> bool:
        """
        Send formatted order summary with optional PDF attachments

        Args:
            orders: List of order dictionaries (should include 'pdf_path' key if attach_pdfs=True)
            date: Date string for the summary (default: today)
            filter_by_value: Whether to filter by value threshold (default: True)
            attach_pdfs: Whether to attach PDF files (default: True)

        Returns:
            True if successful
        """
        # Filter by threshold if enabled
        if filter_by_value:
            filtered_orders = self.filter_high_value_orders(orders)
        else:
            filtered_orders = orders

        if not filtered_orders:
            message = f"📊 <b>Order Book Update</b>\n\n"
            message += f"📅 Date: {date or datetime.now().strftime('%Y-%m-%d')}\n\n"
            message += f"ℹ️ No orders found above ₹{self.value_threshold} Crores threshold today."
            return self.send_message(message)

        message = f"🚨 <b>High-Value Order Alert</b> 🚨\n\n"
        message += f"📅 Date: {date or datetime.now().strftime('%Y-%m-%d')}\n"
        message += f"📈 Orders Above ₹{self.value_threshold} Cr: <b>{len(filtered_orders)}</b>\n\n"

        total_value = 0
        for i, order in enumerate(filtered_orders, 1):
            symbol = order.get('symbol', 'Unknown')
            company = order.get('company_name', symbol)
            value = order.get('order_value', 0)
            desc = order.get('description', 'No description')

            # Truncate long descriptions
            if len(desc) > 150:
                desc = desc[:147] + "..."

            message += f"<b>{i}. {symbol}</b>\n"
            message += f"🏢 {company}\n"
            if value and value > 0:
                message += f"💰 Value: <b>₹{value:.2f} Crores</b>\n"
                total_value += value
            message += f"📝 {desc}\n\n"

        if total_value > 0:
            message += f"💎 <b>Total Value: ₹{total_value:.2f} Crores</b>\n"

        message += f"\n🔔 Showing orders ≥ ₹{self.value_threshold} Cr only"

        # Send the summary message first
        if not self.send_message(message):
            return False

        # Send PDFs if enabled and available
        if attach_pdfs:
            pdfs_sent = 0
            for order in filtered_orders:
                pdf_path = order.get('pdf_path')
                if pdf_path and Path(pdf_path).exists():
                    symbol = order.get('symbol', 'Unknown')
                    company = order.get('company_name', symbol)
                    value = order.get('order_value', 0)

                    caption = f"📄 <b>{symbol}</b> - {company}\n"
                    caption += f"💰 ₹{value:.2f} Crores"

                    if self.send_document(pdf_path, caption=caption):
                        pdfs_sent += 1
                    else:
                        logger.warning(f"Failed to send PDF for {symbol}")

            if pdfs_sent > 0:
                logger.info(f"Sent {pdfs_sent} PDF attachment(s)")

        return True

    def send_company_alert(self, company_order: Dict, attach_pdf: bool = True) -> bool:
        """
        Send alert for a specific company's order (only if above threshold) with optional PDF

        Args:
            company_order: Order dictionary (should include 'pdf_path' key if attach_pdf=True)
            attach_pdf: Whether to attach the PDF file (default: True)

        Returns:
            True if successful, False if below threshold or error
        """
        value = company_order.get('order_value', 0)

        # Check threshold
        if value < self.value_threshold:
            logger.info(f"Order value ₹{value} Cr below threshold ₹{self.value_threshold} Cr, skipping alert")
            return False

        symbol = company_order.get('symbol', 'Unknown')
        company = company_order.get('company_name', symbol)
        desc = company_order.get('description', 'No description')
        date = company_order.get('announcement_date', datetime.now().strftime('%Y-%m-%d'))

        message = f"🚨 <b>High-Value Order Alert!</b> 🚨\n\n"
        message += f"🏢 <b>{company}</b> ({symbol})\n"
        message += f"📅 Date: {date}\n"
        message += f"💰 Value: <b>₹{value:.2f} Crores</b>\n\n"
        message += f"📝 <i>{desc}</i>\n\n"

        pdf_url = company_order.get('pdf_url')
        if pdf_url:
            message += f"🔗 <a href='{pdf_url}'>View Announcement</a>\n\n"

        message += f"⚠️ This order exceeds ₹{self.value_threshold} Cr threshold\n"
        message += f"🤖 <i>NSE Order Book Tracker</i>"

        # Send the alert message
        if not self.send_message(message):
            return False

        # Send PDF if enabled and available
        if attach_pdf:
            pdf_path = company_order.get('pdf_path')
            if pdf_path and Path(pdf_path).exists():
                caption = f"📄 <b>{symbol}</b> - {company}\n💰 ₹{value:.2f} Crores"
                if self.send_document(pdf_path, caption=caption):
                    logger.info(f"PDF attached for {symbol}")
                else:
                    logger.warning(f"Failed to attach PDF for {symbol}")

        return True

    def send_daily_digest(self, summary_stats: Dict, include_all: bool = False) -> bool:
        """
        Send daily digest with summary statistics

        Args:
            summary_stats: Dictionary with summary statistics
            include_all: Include all orders or just high-value (default: False)

        Returns:
            True if successful
        """
        message = f"📊 <b>Daily Order Book Digest</b>\n\n"
        message += f"📅 {datetime.now().strftime('%A, %B %d, %Y')}\n\n"

        high_value_count = summary_stats.get('high_value_orders', 0)
        high_value_total = summary_stats.get('high_value_total', 0)

        message += f"🔥 <b>High-Value Orders (≥₹{self.value_threshold} Cr):</b>\n"
        message += f"• Count: {high_value_count}\n"
        message += f"• Total Value: ₹{high_value_total:.2f} Cr\n\n"

        if include_all:
            message += f"📈 <b>All Orders Summary:</b>\n"
            message += f"• New Orders: {summary_stats.get('new_orders', 0)}\n"
            message += f"• Total Value: ₹{summary_stats.get('total_value', 0):.2f} Cr\n"
            message += f"• Companies: {summary_stats.get('companies_count', 0)}\n\n"

        # Top companies by order value (above threshold)
        top_companies = summary_stats.get('top_high_value_companies', [])
        if top_companies:
            message += f"🏆 <b>Top High-Value Orders:</b>\n"
            for rank, comp in enumerate(top_companies[:5], 1):
                message += f"{rank}. {comp['symbol']}: ₹{comp['value']:.2f} Cr\n"
            message += "\n"

        # Sector breakdown (high-value only)
        sector_data = summary_stats.get('high_value_sector_breakdown', {})
        if sector_data:
            message += f"📊 <b>Sector Breakdown (High-Value):</b>\n"
            for sector, count in list(sector_data.items())[:5]:
                message += f"• {sector}: {count} orders\n"
            message += "\n"

        message += f"🤖 <i>Automated Daily Digest</i>"

        return self.send_message(message)

    def send_dashboard_summary(self, orders: List[Dict], summary: Dict,
                               days: int = 3, timestamp: Optional[str] = None) -> bool:
        """
        Send comprehensive dashboard-style summary with all orders in formatted table
        Similar to the web dashboard interface

        Args:
            orders: List of all order dictionaries
            summary: Summary statistics dictionary
            days: Number of days covered
            timestamp: Timestamp string (default: now)

        Returns:
            True if successful
        """
        if not timestamp:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Header with emoji
        message = "📊 <b>NSE Order Book Tracker - Daily Report</b>\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━\n\n"

        # Timestamp
        message += f"🕐 <i>Last Updated: {timestamp}</i>\n"
        message += f"📅 <i>Period: Last {days} days</i>\n\n"

        # Summary Cards
        message += "📈 <b>SUMMARY</b>\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"📋 Total Announcements: <b>{summary.get('total_announcements', 0)}</b>\n"
        message += f"💰 Total Order Value: <b>₹{summary.get('total_value_crores', 0):.2f} Cr</b>\n"
        message += f"📊 Average Order Size: <b>₹{summary.get('average_order_value', 0):.2f} Cr</b>\n"
        message += f"🏢 Unique Companies: <b>{summary.get('unique_companies', 0)}</b>\n\n"

        if not orders:
            message += "ℹ️ <i>No order announcements found in this period.</i>\n\n"
            message += f"🤖 <i>Automated Daily Report</i>"
            return self.send_message(message)

        # Orders Table Header
        message += "📋 <b>ORDER DETAILS</b>\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━\n\n"

        # Split orders into chunks if too many (Telegram has 4096 char limit)
        chunk_size = 10
        total_orders = len(orders)

        for chunk_start in range(0, total_orders, chunk_size):
            chunk_end = min(chunk_start + chunk_size, total_orders)
            chunk_orders = orders[chunk_start:chunk_end]

            chunk_message = ""
            if chunk_start > 0:
                chunk_message = f"📋 <b>ORDER DETAILS (continued {chunk_start+1}-{chunk_end})</b>\n"
                chunk_message += f"━━━━━━━━━━━━━━━━━━━━━\n\n"

            for i, order in enumerate(chunk_orders, chunk_start + 1):
                symbol = order.get('symbol', 'N/A')
                company = order.get('company_name', 'N/A')
                date = order.get('announcement_date', 'N/A')
                value = order.get('order_value_crores', 0)
                subject = order.get('subject', '')[:80]  # Truncate
                has_pdf = order.get('local_pdf_path') is not None

                # Format order entry
                chunk_message += f"<b>{i}. {symbol}</b>\n"
                chunk_message += f"   🏢 {company}\n"
                chunk_message += f"   📅 {date}\n"

                if value and value > 0:
                    # Color indicators using emojis
                    if value > 100:
                        indicator = "🟢"  # High value
                    elif value > 50:
                        indicator = "🟡"  # Medium value
                    else:
                        indicator = "🔵"  # Low value
                    chunk_message += f"   💰 {indicator} <b>₹{value:.2f} Cr</b>\n"
                else:
                    chunk_message += f"   💰 <i>Value not found</i>\n"

                if subject:
                    chunk_message += f"   📝 {subject}{'...' if len(order.get('subject', '')) > 80 else ''}\n"

                chunk_message += f"   📄 {'✓ PDF Available' if has_pdf else '⚠ No PDF'}\n"
                chunk_message += "\n"

            # Send chunk
            if chunk_start == 0:
                full_message = message + chunk_message
            else:
                full_message = chunk_message

            # Add footer only to last chunk
            if chunk_end >= total_orders:
                full_message += f"━━━━━━━━━━━━━━━━━━━━━\n"
                full_message += f"📊 Showing {total_orders} order(s)\n"
                full_message += f"🔔 Threshold: ≥₹{self.value_threshold} Cr for alerts\n\n"
                full_message += f"🤖 <i>Automated Daily Report</i>"

            # Send this chunk
            if not self.send_message(full_message):
                logger.error(f"Failed to send message chunk {chunk_start}-{chunk_end}")
                return False

        return True

    def test_connection(self) -> bool:
        """
        Test Telegram bot connection

        Returns:
            True if connection successful
        """
        url = f"{self.api_url}/getMe"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                logger.info(f"Connected to Telegram bot: {bot_info.get('username')}")
                return True
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            return False


def main():
    """Test Telegram notifier with 500 crore threshold"""
    print("=== Telegram Notifier Test (500 Cr Threshold) ===\n")

    # Check for credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("❌ Error: Telegram credentials not found!")
        print("\nPlease set environment variables:")
        print("  export TELEGRAM_BOT_TOKEN='your-bot-token'")
        print("  export TELEGRAM_CHAT_ID='your-chat-id'")
        print("\nTo create a bot:")
        print("  1. Message @BotFather on Telegram")
        print("  2. Send /newbot and follow instructions")
        print("  3. Copy the bot token")
        print("\nTo get chat ID:")
        print("  1. Start a chat with your bot")
        print("  2. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
        print("  3. Look for 'chat':{'id': YOUR_CHAT_ID}")
        return

    try:
        # Initialize with 500 crore threshold
        notifier = TelegramNotifier(value_threshold=500.0)

        # Test connection
        print("Testing connection...")
        if notifier.test_connection():
            print("✓ Connected successfully!\n")
        else:
            print("✗ Connection failed!\n")
            return

        # Test orders - mix of high and low value
        print("Testing with sample orders (threshold: ₹500 Cr)...")
        test_orders = [
            {
                'symbol': 'TCS',
                'company_name': 'Tata Consultancy Services',
                'order_value': 450.0,  # Below threshold
                'description': 'Digital transformation project',
                'announcement_date': '2026-05-28'
            },
            {
                'symbol': 'LT',
                'company_name': 'Larsen & Toubro',
                'order_value': 2500.0,  # Above threshold
                'description': 'Secured major infrastructure project for metro construction',
                'announcement_date': '2026-05-28'
            },
            {
                'symbol': 'RELIANCE',
                'company_name': 'Reliance Industries',
                'order_value': 1200.0,  # Above threshold
                'description': 'Petrochemical plant expansion contract',
                'announcement_date': '2026-05-28'
            }
        ]

        print(f"\nSending summary (will filter to show only ≥₹500 Cr orders)...")
        if notifier.send_order_summary(test_orders):
            print("✓ Summary sent (only high-value orders)!\n")

        # Test individual alert
        print("Sending individual alert for high-value order...")
        if notifier.send_company_alert(test_orders[1]):  # LT - 2500 Cr
            print("✓ High-value alert sent!\n")

        # Test alert for low-value order (should be skipped)
        print("Testing alert for low-value order (should be skipped)...")
        if not notifier.send_company_alert(test_orders[0]):  # TCS - 450 Cr
            print("✓ Correctly skipped low-value order\n")

        # Send test digest
        print("Sending test digest...")
        test_stats = {
            'high_value_orders': 2,
            'high_value_total': 3700.0,
            'new_orders': 15,
            'total_value': 12500.0,
            'companies_count': 8,
            'top_high_value_companies': [
                {'symbol': 'LT', 'value': 2500.0},
                {'symbol': 'RELIANCE', 'value': 1200.0}
            ],
            'high_value_sector_breakdown': {
                'Infrastructure': 1,
                'Oil & Gas': 1
            }
        }

        if notifier.send_daily_digest(test_stats):
            print("✓ Test digest sent!\n")

        print("✓ All tests completed successfully!")
        print(f"\nNote: Only orders ≥ ₹{notifier.value_threshold} Cr are sent as alerts")

    except ValueError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
