#!/usr/bin/env python3
"""
NSE Corporate Announcements Scraper using API (v3)
Much more reliable than Playwright - uses direct API calls
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import json
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NSEAPIScraper:
    """Scrapes NSE corporate announcements using API"""

    def __init__(self, download_dir: str = 'downloads/pdfs'):
        self.base_url = "https://www.nseindia.com"
        self.api_url = f"{self.base_url}/api/corporate-announcements"
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/companies-listing/corporate-filings-announcements'
        }

    def _get_cookies(self):
        """Visit NSE website to get required cookies"""
        try:
            logger.info("Getting session cookies from NSE website...")
            response = self.session.get(
                f"{self.base_url}/companies-listing/corporate-filings-announcements",
                headers=self.headers,
                timeout=15
            )
            logger.info(f"Got cookies: {list(self.session.cookies.keys())}")
            return True
        except Exception as e:
            logger.error(f"Failed to get cookies: {e}")
            return False

    def fetch_announcements(
        self,
        days_back: int = 30,
        search_term: str = "awarding of order"
    ) -> List[Dict]:
        """
        Fetch announcements from NSE API

        Args:
            days_back: Number of days to look back
            search_term: Filter announcements by this term

        Returns:
            List of announcement dictionaries
        """
        logger.info(f"Fetching announcements for last {days_back} days")

        # Get cookies first
        if not self._get_cookies():
            return []

        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)

        params = {
            'index': 'equities',
            'from_date': from_date.strftime('%d-%m-%Y'),
            'to_date': to_date.strftime('%d-%m-%Y')
        }

        try:
            logger.info(f"Calling API: {self.api_url}")
            logger.info(f"Date range: {params['from_date']} to {params['to_date']}")

            response = self.session.get(
                self.api_url,
                headers=self.headers,
                params=params,
                timeout=60
            )

            if response.status_code != 200:
                logger.error(f"API returned status {response.status_code}")
                return []

            data = response.json()
            logger.info(f"Retrieved {len(data)} announcements from API")

            # Filter by search term
            search_lower = search_term.lower()
            filtered = [
                ann for ann in data
                if search_lower in ann.get('desc', '').lower() or
                   search_lower in ann.get('attchmntText', '').lower()
            ]

            logger.info(f"Filtered to {len(filtered)} announcements matching '{search_term}'")

            # Convert to our format
            announcements = []
            for ann in filtered:
                announcement = {
                    'symbol': ann.get('symbol', ''),
                    'company_name': ann.get('sm_name', ''),
                    'announcement_date': ann.get('sort_date', ann.get('an_dt', ''))[:10],
                    'subject': ann.get('desc', ''),
                    'description': ann.get('attchmntText', ''),
                    'pdf_url': ann.get('attchmntFile', ''),
                    'file_size': ann.get('fileSize', ''),
                    'source': 'NSE_API',
                    'scraped_at': datetime.now().isoformat()
                }
                announcements.append(announcement)

            return announcements

        except Exception as e:
            logger.error(f"Error fetching announcements: {e}", exc_info=True)
            return []

    def download_pdf(self, pdf_url: str, symbol: str, date: str) -> str:
        """Download PDF file"""
        if not pdf_url:
            return None

        try:
            filename = f"{symbol.replace('/', '_')}_{date}.pdf"
            filepath = self.download_dir / filename

            logger.info(f"Downloading: {filename}")
            response = self.session.get(pdf_url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Downloaded: {filename} ({len(response.content)} bytes)")
                return str(filepath)
            else:
                logger.warning(f"Failed to download {filename}: Status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return None

    def scrape(
        self,
        search_term: str = "awarding of order",
        days_back: int = 30,
        download_pdfs: bool = True
    ) -> List[Dict]:
        """Main scraping method"""
        try:
            # Fetch announcements
            announcements = self.fetch_announcements(days_back, search_term)

            if not announcements:
                logger.warning("No announcements found")
                return []

            # Download PDFs if requested
            if download_pdfs:
                logger.info(f"Downloading {len(announcements)} PDFs...")
                for ann in announcements:
                    if ann.get('pdf_url'):
                        pdf_path = self.download_pdf(
                            ann['pdf_url'],
                            ann['symbol'],
                            ann['announcement_date']
                        )
                        ann['local_pdf_path'] = pdf_path

            return announcements

        except Exception as e:
            logger.error(f"Scraping failed: {e}", exc_info=True)
            return []


if __name__ == "__main__":
    scraper = NSEAPIScraper(download_dir='downloads/nse_pdfs')
    announcements = scraper.scrape(search_term="awarding of order", days_back=30, download_pdfs=True)

    print(f"\n{'='*60}")
    print(f"FOUND {len(announcements)} ANNOUNCEMENTS")
    print(f"{'='*60}\n")

    for ann in announcements[:10]:
        print(f"{ann['symbol']:15} {ann['announcement_date']} - {ann['subject']}")
        if ann.get('local_pdf_path'):
            print(f"                PDF: {ann['local_pdf_path']}")
        print()
