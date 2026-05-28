#!/usr/bin/env python3
"""
Telegram Notifier - Send order book updates via Telegram
"""

import os
import requests
from typing import List, Dict, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications to Telegram"""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram notifier

        Args:
            bot_token: Telegram Bot API token (or set TELEGRAM_BOT_TOKEN env var)
            chat_id: Telegram chat ID to send messages (or set TELEGRAM_CHAT_ID env var)
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')

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

    def send_order_summary(self, orders: List[Dict], date: Optional[str] = None) -> bool:
        """
        Send formatted order summary

        Args:
            orders: List of order dictionaries
            date: Date string for the summary (default: today)

        Returns:
            True if successful
        """
        if not orders:
            message = f"📊 <b>Order Book Update</b>\n\n"
            message += f"📅 Date: {date or datetime.now().strftime('%Y-%m-%d')}\n\n"
            message += "ℹ️ No new orders found today."
            return self.send_message(message)

        message = f"📊 <b>Order Book Update - Nifty 50</b>\n\n"
        message += f"📅 Date: {date or datetime.now().strftime('%Y-%m-%d')}\n"
        message += f"📈 Total Orders: <b>{len(orders)}</b>\n\n"

        total_value = 0
        for i, order in enumerate(orders, 1):
            symbol = order.get('symbol', 'Unknown')
            company = order.get('company_name', symbol)
            value = order.get('order_value', 0)
            desc = order.get('description', 'No description')

            # Truncate long descriptions
            if len(desc) > 150:
                desc = desc[:147] + "..."

            message += f"<b>{i}. {symbol}</b>\n"
            if value and value > 0:
                message += f"💰 Value: ₹{value:.2f} Cr\n"
                total_value += value
            message += f"📝 {desc}\n\n"

        if total_value > 0:
            message += f"💎 <b>Total Value: ₹{total_value:.2f} Crores</b>\n"

        message += f"\n🤖 <i>Automated update from NSE Order Book Tracker</i>"

        return self.send_message(message)

    def send_company_alert(self, company_order: Dict) -> bool:
        """
        Send alert for a specific company's order

        Args:
            company_order: Order dictionary

        Returns:
            True if successful
        """
        symbol = company_order.get('symbol', 'Unknown')
        company = company_order.get('company_name', symbol)
        value = company_order.get('order_value', 0)
        desc = company_order.get('description', 'No description')
        date = company_order.get('announcement_date', datetime.now().strftime('%Y-%m-%d'))

        message = f"🚨 <b>New Order Alert!</b>\n\n"
        message += f"🏢 <b>{company}</b> ({symbol})\n"
        message += f"📅 Date: {date}\n"

        if value and value > 0:
            message += f"💰 Value: <b>₹{value:.2f} Crores</b>\n\n"
        else:
            message += "\n"

        message += f"📝 <i>{desc}</i>\n\n"

        pdf_url = company_order.get('pdf_url')
        if pdf_url:
            message += f"🔗 <a href='{pdf_url}'>View Announcement</a>\n\n"

        message += f"🤖 <i>NSE Order Book Tracker</i>"

        return self.send_message(message)

    def send_daily_digest(self, summary_stats: Dict) -> bool:
        """
        Send daily digest with summary statistics

        Args:
            summary_stats: Dictionary with summary statistics

        Returns:
            True if successful
        """
        message = f"📊 <b>Daily Order Book Digest</b>\n\n"
        message += f"📅 {datetime.now().strftime('%A, %B %d, %Y')}\n\n"

        message += f"📈 <b>Today's Summary:</b>\n"
        message += f"• New Orders: {summary_stats.get('new_orders', 0)}\n"
        message += f"• Total Value: ₹{summary_stats.get('total_value', 0):.2f} Cr\n"
        message += f"• Companies: {summary_stats.get('companies_count', 0)}\n\n"

        # Top companies by order value
        top_companies = summary_stats.get('top_companies', [])
        if top_companies:
            message += f"🏆 <b>Top Companies:</b>\n"
            for rank, comp in enumerate(top_companies[:5], 1):
                message += f"{rank}. {comp['symbol']}: ₹{comp['value']:.2f} Cr\n"
            message += "\n"

        # Sector breakdown
        sector_data = summary_stats.get('sector_breakdown', {})
        if sector_data:
            message += f"📊 <b>Sector Breakdown:</b>\n"
            for sector, count in list(sector_data.items())[:5]:
                message += f"• {sector}: {count} orders\n"
            message += "\n"

        message += f"🤖 <i>Automated Daily Digest</i>"

        return self.send_message(message)

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
    """Test Telegram notifier"""
    print("=== Telegram Notifier Test ===\n")

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
        notifier = TelegramNotifier()

        # Test connection
        print("Testing connection...")
        if notifier.test_connection():
            print("✓ Connected successfully!\n")
        else:
            print("✗ Connection failed!\n")
            return

        # Send test order summary
        print("Sending test order summary...")
        test_orders = [
            {
                'symbol': 'TCS',
                'company_name': 'Tata Consultancy Services',
                'order_value': 500.0,
                'description': 'Won a large digital transformation project from a Fortune 500 client',
                'announcement_date': '2024-05-28'
            },
            {
                'symbol': 'LT',
                'company_name': 'Larsen & Toubro',
                'order_value': 2500.0,
                'description': 'Secured major infrastructure project for metro construction',
                'announcement_date': '2024-05-28'
            }
        ]

        if notifier.send_order_summary(test_orders):
            print("✓ Test summary sent!\n")

        # Send test alert
        print("Sending test alert...")
        if notifier.send_company_alert(test_orders[0]):
            print("✓ Test alert sent!\n")

        # Send test digest
        print("Sending test digest...")
        test_stats = {
            'new_orders': 15,
            'total_value': 12500.0,
            'companies_count': 8,
            'top_companies': [
                {'symbol': 'LT', 'value': 2500.0},
                {'symbol': 'TCS', 'value': 500.0}
            ],
            'sector_breakdown': {
                'Infrastructure': 5,
                'IT Services': 4,
                'Defense': 3,
                'Capital Goods': 3
            }
        }

        if notifier.send_daily_digest(test_stats):
            print("✓ Test digest sent!\n")

        print("✓ All tests completed successfully!")

    except ValueError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
