#!/usr/bin/env python3
"""
Orchestrator - Main pipeline that coordinates scraping, parsing, and data processing
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import pandas as pd

from nse_playwright_scraper import NSEAPIScraper
from pdf_parser import PDFParser, OrderInfo
from telegram_notifier import TelegramNotifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OrderBookOrchestrator:
    """Orchestrates the complete order book tracking pipeline"""

    def __init__(
        self,
        download_dir: str = 'downloads/nse_pdfs',
        output_dir: str = 'output',
        enable_telegram: bool = True,
        value_threshold: float = 500.0
    ):
        """
        Initialize orchestrator

        Args:
            download_dir: Directory for downloaded PDFs
            output_dir: Directory for output files
            enable_telegram: Enable Telegram notifications
            value_threshold: Minimum order value for alerts (in Crores)
        """
        self.scraper = NSEAPIScraper(download_dir=download_dir)
        self.parser = PDFParser()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.announcements: List[Dict] = []
        self.parsed_orders: Dict[str, OrderInfo] = {}

        # Initialize Telegram notifier
        self.telegram_enabled = enable_telegram
        self.value_threshold = value_threshold
        self.notifier = None

        if self.telegram_enabled:
            try:
                self.notifier = TelegramNotifier(value_threshold=value_threshold)
                logger.info("Telegram notifications enabled")
            except ValueError as e:
                logger.warning(f"Telegram notifications disabled: {e}")
                self.telegram_enabled = False

    def scrape_announcements(
        self,
        search_term: str = "awarding of order",
        days_back: int = 30
    ) -> List[Dict]:
        """
        Step 1: Scrape announcements from NSE

        Args:
            search_term: Search query
            days_back: Days to look back

        Returns:
            List of announcements
        """
        logger.info("="*60)
        logger.info("STEP 1: SCRAPING NSE ANNOUNCEMENTS")
        logger.info("="*60)

        self.announcements = self.scraper.scrape(
            search_term=search_term,
            days_back=days_back,
            download_pdfs=True
        )

        logger.info(f"Scraped {len(self.announcements)} announcements")
        return self.announcements

    def parse_pdfs(self) -> Dict[str, OrderInfo]:
        """
        Step 2: Parse downloaded PDFs to extract order values

        Returns:
            Dictionary of parsed order information
        """
        logger.info("\n" + "="*60)
        logger.info("STEP 2: PARSING PDFs")
        logger.info("="*60)

        # Get PDFs to parse
        pdfs_to_parse = [
            ann['local_pdf_path']
            for ann in self.announcements
            if ann.get('local_pdf_path')
        ]

        logger.info(f"Parsing {len(pdfs_to_parse)} PDFs...")

        self.parsed_orders = self.parser.parse_multiple_pdfs(pdfs_to_parse)

        logger.info(f"Parsed {len(self.parsed_orders)} PDFs")
        return self.parsed_orders

    def combine_data(self) -> List[Dict]:
        """
        Step 3: Combine scraped announcements with parsed PDF data

        Returns:
            List of enriched announcement dictionaries
        """
        logger.info("\n" + "="*60)
        logger.info("STEP 3: COMBINING DATA")
        logger.info("="*60)

        enriched_data = []

        for ann in self.announcements:
            # Get parsed PDF data if available
            pdf_path = ann.get('local_pdf_path')
            order_info = self.parsed_orders.get(pdf_path, OrderInfo())

            # Combine data
            enriched = {
                # From scraping
                'symbol': ann.get('symbol'),
                'company_name': ann.get('company_name'),
                'announcement_date': ann.get('announcement_date'),
                'subject': ann.get('subject'),
                'pdf_url': ann.get('pdf_url'),
                'local_pdf_path': ann.get('local_pdf_path'),
                'source': ann.get('source'),

                # From PDF parsing
                'order_value_crores': order_info.order_value,
                'order_value_text': order_info.order_value_text,
                'client_name': order_info.client_name,
                'project_description': order_info.project_description,
                'order_date': order_info.order_date,
                'completion_period': order_info.completion_period,
                'confidence_score': order_info.confidence_score,

                # Metadata
                'processed_at': datetime.now().isoformat()
            }

            enriched_data.append(enriched)

        logger.info(f"Combined {len(enriched_data)} records")
        return enriched_data

    def save_json(self, data: List[Dict], filename: str = 'orderbook_data.json'):
        """Save data to JSON file"""
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Saved JSON: {filepath}")
        return str(filepath)

    def save_excel(self, data: List[Dict], filename: str = 'orderbook_data.xlsx'):
        """Save data to Excel file"""
        filepath = self.output_dir / filename

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Reorder columns for better readability
        column_order = [
            'symbol', 'company_name', 'announcement_date',
            'order_value_crores', 'subject', 'client_name',
            'project_description', 'order_date', 'completion_period',
            'confidence_score', 'pdf_url', 'local_pdf_path',
            'order_value_text', 'source', 'processed_at'
        ]

        # Use only columns that exist
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]

        # Format numeric columns
        if 'order_value_crores' in df.columns:
            df['order_value_crores'] = df['order_value_crores'].apply(
                lambda x: f"₹{x:.2f} Cr" if pd.notna(x) and x > 0 else "Not found"
            )

        # Save to Excel
        df.to_excel(filepath, index=False, engine='openpyxl')

        logger.info(f"Saved Excel: {filepath}")
        return str(filepath)

    def generate_summary(self, data: List[Dict]) -> Dict:
        """Generate summary statistics"""
        logger.info("\n" + "="*60)
        logger.info("GENERATING SUMMARY")
        logger.info("="*60)

        # Filter records with valid order values
        valid_orders = [
            d for d in data
            if d.get('order_value_crores') and d['order_value_crores'] > 0
        ]

        summary = {
            'total_announcements': len(data),
            'orders_with_values': len(valid_orders),
            'total_value_crores': sum(d['order_value_crores'] for d in valid_orders),
            'average_order_value': sum(d['order_value_crores'] for d in valid_orders) / len(valid_orders) if valid_orders else 0,
            'max_order_value': max((d['order_value_crores'] for d in valid_orders), default=0),
            'min_order_value': min((d['order_value_crores'] for d in valid_orders), default=0),
            'unique_companies': len(set(d['symbol'] for d in data)),
            'date_range': {
                'start': min((d['announcement_date'] for d in data), default=None),
                'end': max((d['announcement_date'] for d in data), default=None)
            },
            'generated_at': datetime.now().isoformat()
        }

        # Top companies by order value
        company_totals = {}
        for d in valid_orders:
            symbol = d['symbol']
            value = d['order_value_crores']
            company_totals[symbol] = company_totals.get(symbol, 0) + value

        summary['top_companies'] = sorted(
            company_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return summary

    def print_summary(self, summary: Dict):
        """Print summary to console"""
        print(f"\n{'='*60}")
        print("ORDER BOOK SUMMARY")
        print(f"{'='*60}")
        print(f"Total Announcements: {summary['total_announcements']}")
        print(f"Orders with Values: {summary['orders_with_values']}")
        print(f"Total Value: ₹{summary['total_value_crores']:.2f} Crores")
        print(f"Average Order: ₹{summary['average_order_value']:.2f} Crores")
        print(f"Largest Order: ₹{summary['max_order_value']:.2f} Crores")
        print(f"Unique Companies: {summary['unique_companies']}")
        print(f"\nDate Range: {summary['date_range']['start']} to {summary['date_range']['end']}")
        print(f"\nTop Companies by Order Value:")
        for i, (symbol, value) in enumerate(summary['top_companies'], 1):
            print(f"  {i}. {symbol:10} ₹{value:,.2f} Cr")
        print(f"{'='*60}\n")

    def send_telegram_notifications(self, data: List[Dict], summary: Dict):
        """Send Telegram notifications for high-value orders"""
        logger.info("\n" + "="*60)
        logger.info("STEP 6: SENDING TELEGRAM NOTIFICATIONS")
        logger.info("="*60)

        try:
            # Prepare orders for Telegram format
            telegram_orders = []
            for item in data:
                value = item.get('order_value_crores', 0)
                if value and value > 0:
                    telegram_orders.append({
                        'symbol': item.get('symbol', 'Unknown'),
                        'company_name': item.get('company_name', ''),
                        'order_value': value,
                        'description': item.get('subject', ''),
                        'announcement_date': item.get('announcement_date', ''),
                        'pdf_url': item.get('pdf_url', '')
                    })

            # Send summary notification
            if telegram_orders:
                date_range = f"{summary['date_range']['start']} to {summary['date_range']['end']}"
                success = self.notifier.send_order_summary(
                    telegram_orders,
                    date=date_range,
                    filter_by_value=True
                )

                if success:
                    logger.info(f"✓ Telegram notification sent successfully")
                    # Count high-value orders
                    high_value_count = sum(1 for o in telegram_orders if o['order_value'] >= self.value_threshold)
                    if high_value_count > 0:
                        logger.info(f"  - {high_value_count} high-value orders (≥₹{self.value_threshold} Cr)")
                    else:
                        logger.info(f"  - No orders above ₹{self.value_threshold} Cr threshold")
                else:
                    logger.warning("✗ Failed to send Telegram notification")
            else:
                logger.info("No orders with values found to notify")

        except Exception as e:
            logger.error(f"Error sending Telegram notifications: {e}", exc_info=True)

    def run(
        self,
        search_term: str = "awarding of order",
        days_back: int = 30
    ):
        """
        Run the complete pipeline

        Args:
            search_term: Search query for NSE
            days_back: Days to look back
        """
        logger.info("STARTING ORDER BOOK ORCHESTRATOR")
        logger.info(f"Search: '{search_term}', Days: {days_back}\n")

        try:
            # Step 1: Scrape announcements
            self.scrape_announcements(search_term, days_back)

            if not self.announcements:
                logger.warning("No announcements found. Exiting.")
                return

            # Step 2: Parse PDFs
            self.parse_pdfs()

            # Step 3: Combine data
            enriched_data = self.combine_data()

            # Step 4: Save outputs
            logger.info("\n" + "="*60)
            logger.info("STEP 4: SAVING OUTPUTS")
            logger.info("="*60)

            json_file = self.save_json(enriched_data)
            excel_file = self.save_excel(enriched_data)

            # Step 5: Generate summary
            summary = self.generate_summary(enriched_data)
            summary_file = self.save_json(summary, 'summary.json')

            # Print summary
            self.print_summary(summary)

            # Step 6: Send Telegram notifications
            if self.telegram_enabled and self.notifier:
                self.send_telegram_notifications(enriched_data, summary)

            # Final output
            logger.info("="*60)
            logger.info("PIPELINE COMPLETE")
            logger.info("="*60)
            logger.info(f"JSON: {json_file}")
            logger.info(f"Excel: {excel_file}")
            logger.info(f"Summary: {summary_file}")
            logger.info("="*60)

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            raise


def main():
    """Entry point with argument parsing"""
    import argparse

    parser = argparse.ArgumentParser(description='NSE Order Book Tracker V2 (API-based)')
    parser.add_argument('--days', type=int, default=3, help='Days to look back (default: 3)')
    parser.add_argument('--search', type=str, default='awarding of order', help='Search term (default: "awarding of order")')
    parser.add_argument('--threshold', type=float, default=500, help='Order value threshold in Crores (default: 500)')
    parser.add_argument('--telegram', action='store_true', default=True, help='Enable Telegram notifications (default: enabled)')
    parser.add_argument('--no-telegram', action='store_true', help='Disable Telegram notifications')
    parser.add_argument('--output-dir', type=str, default='output', help='Output directory (default: output)')
    parser.add_argument('--download-dir', type=str, default='downloads/nse_pdfs', help='PDF download directory')

    args = parser.parse_args()

    # Determine if Telegram should be enabled
    enable_telegram = args.telegram and not args.no_telegram

    orchestrator = OrderBookOrchestrator(
        download_dir=args.download_dir,
        output_dir=args.output_dir,
        enable_telegram=enable_telegram,
        value_threshold=args.threshold
    )

    orchestrator.run(
        search_term=args.search,
        days_back=args.days
    )


if __name__ == "__main__":
    main()
