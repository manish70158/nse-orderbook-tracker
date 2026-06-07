#!/usr/bin/env python3
"""
Telegram Bot Server - Interactive bot for real-time data fetching
Listens for commands and fetches data on-demand from Telegram
"""

import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from datetime import datetime
from orchestrator import OrderBookOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramBotServer:
    """Interactive Telegram bot for real-time order book updates"""

    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")

        self.app = Application.builder().token(self.bot_token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Register command and callback handlers"""
        # Commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("fetch", self.fetch_command))
        self.app.add_handler(CommandHandler("menu", self.menu_command))

        # Callback queries (button clicks)
        self.app.add_handler(CallbackQueryHandler(self.button_callback))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "👋 <b>Welcome to NSE Order Book Tracker Bot!</b>\n\n"
            "I can fetch real-time order book data for you.\n\n"
            "<b>Commands:</b>\n"
            "/menu - Show date range options\n"
            "/fetch - Fetch latest data (3 days)\n"
            "/help - Show help message\n\n"
            "Click /menu to get started!",
            parse_mode='HTML'
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "📖 <b>NSE Order Book Tracker - Help</b>\n\n"
            "<b>Available Commands:</b>\n"
            "• /menu - Show interactive date range menu\n"
            "• /fetch - Fetch last 3 days (default)\n"
            "• /help - Show this help message\n\n"
            "<b>How it works:</b>\n"
            "1. Click /menu to see options\n"
            "2. Select a date range (1 week, 2 weeks, etc.)\n"
            "3. Bot fetches data from NSE API\n"
            "4. You receive formatted report in ~30-60 seconds\n\n"
            "<b>Features:</b>\n"
            "✓ Real-time data from NSE\n"
            "✓ Table format with color indicators\n"
            "✓ High-value order alerts\n"
            "✓ PDF attachments for major orders\n\n"
            "💡 <i>Tip: Use buttons in /menu for quick access</i>"
        )
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def fetch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /fetch command - fetch data with default 3 days"""
        await self.fetch_data(update, context, days=3, from_callback=False)

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /menu command - show interactive date range menu"""
        keyboard = [
            [
                InlineKeyboardButton("📅 Last 1 Week", callback_data="fetch_7"),
                InlineKeyboardButton("📅 Last 2 Weeks", callback_data="fetch_14")
            ],
            [
                InlineKeyboardButton("📅 Last 1 Month", callback_data="fetch_30"),
                InlineKeyboardButton("📅 Last 3 Months", callback_data="fetch_90")
            ],
            [
                InlineKeyboardButton("🔄 Refresh (3 days)", callback_data="fetch_3")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🔍 <b>Select Date Range</b>\n\n"
            "Choose how many days of order data to fetch:\n\n"
            "• <b>1 Week</b> - Fast (~10 sec)\n"
            "• <b>2 Weeks</b> - Moderate (~20 sec)\n"
            "• <b>1 Month</b> - Slower (~30 sec)\n"
            "• <b>3 Months</b> - Slowest (~60 sec)\n\n"
            "⏳ <i>Larger ranges take more time</i>\n"
            "📊 <i>You'll receive a formatted report</i>",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()  # Acknowledge the click

        # Parse callback data
        if query.data.startswith("fetch_"):
            days = int(query.data.split("_")[1])
            await self.fetch_data(update, context, days=days, from_callback=True)

    async def fetch_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                        days: int = 3, from_callback: bool = False):
        """
        Fetch data from NSE API and send report

        Args:
            update: Telegram update object
            context: Telegram context
            days: Number of days to fetch
            from_callback: True if called from button callback
        """
        # Get chat for sending messages
        if from_callback:
            query = update.callback_query
            chat_id = query.message.chat_id
            message = query.message
        else:
            chat_id = update.effective_chat.id
            message = update.message

        # Send "fetching" message
        status_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ <b>Fetching {days} days of data...</b>\n\n"
                 f"Please wait 10-60 seconds.\n"
                 f"This may take longer for larger date ranges.\n\n"
                 f"🔄 <i>Fetching from NSE API...</i>",
            parse_mode='HTML'
        )

        try:
            logger.info(f"Fetching {days} days of data for chat {chat_id}")

            # Create orchestrator and run
            orchestrator = OrderBookOrchestrator(
                enable_telegram=False,  # Don't send via notifier, we'll send manually
                value_threshold=500
            )

            # Run the pipeline
            orchestrator.run(
                search_term="awarding of order",
                days_back=days
            )

            # Load the generated data
            import json
            from pathlib import Path

            data_file = Path('output/orderbook_data.json')
            summary_file = Path('output/summary.json')

            if not data_file.exists():
                await status_msg.edit_text(
                    "❌ <b>Error</b>\n\n"
                    "No data file generated. Please try again.",
                    parse_mode='HTML'
                )
                return

            with open(data_file, 'r') as f:
                orders = json.load(f)

            with open(summary_file, 'r') as f:
                summary = json.load(f)

            # Update status message
            await status_msg.edit_text(
                f"✓ <b>Data fetched successfully!</b>\n\n"
                f"Found {len(orders)} announcements.\n"
                f"Sending formatted report...",
                parse_mode='HTML'
            )

            # Send dashboard summary using telegram_notifier
            from telegram_notifier import TelegramNotifier

            notifier = TelegramNotifier(value_threshold=500)
            success = notifier.send_dashboard_summary(
                orders=orders,
                summary=summary,
                days=days,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                send_interactive_menu=False  # Don't send menu again
            )

            if success:
                # Delete the status message
                await status_msg.delete()

                # Send completion message with menu
                keyboard = [[InlineKeyboardButton("🔄 Fetch Again", callback_data=f"fetch_{days}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ <b>Report sent!</b>\n\n"
                         f"Fetched {days} days of data.\n"
                         f"Found {len(orders)} announcements.\n\n"
                         f"Use /menu for other date ranges.",
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )

                logger.info(f"Successfully sent report for {days} days to chat {chat_id}")
            else:
                await status_msg.edit_text(
                    "❌ <b>Error sending report</b>\n\n"
                    "Data was fetched but failed to send report.\n"
                    "Please try again.",
                    parse_mode='HTML'
                )

        except Exception as e:
            logger.error(f"Error fetching data: {e}", exc_info=True)
            await status_msg.edit_text(
                f"❌ <b>Error</b>\n\n"
                f"Failed to fetch data: {str(e)}\n\n"
                f"Please try again or contact support.",
                parse_mode='HTML'
            )

    def run(self):
        """Start the bot"""
        logger.info("Starting Telegram bot server...")
        logger.info("Bot is ready to receive commands!")
        logger.info("Available commands: /start, /menu, /fetch, /help")
        logger.info("Press Ctrl+C to stop")

        # Start polling
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    print("="*60)
    print("NSE Order Book Tracker - Telegram Bot Server")
    print("="*60)
    print()

    # Check credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set!")
        print()
        print("Please set your Telegram bot token:")
        print("  export TELEGRAM_BOT_TOKEN='your-bot-token'")
        print()
        print("Get token from @BotFather on Telegram")
        sys.exit(1)

    try:
        # Create and run bot server
        bot_server = TelegramBotServer()
        bot_server.run()

    except KeyboardInterrupt:
        print("\n\n✓ Bot server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
