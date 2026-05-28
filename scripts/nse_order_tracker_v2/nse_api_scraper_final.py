#!/usr/bin/env python3
"""
NSE Corporate Announcements API Scraper
Uses direct API calls instead of Playwright browser automation
More reliable and faster than web scraping
"""

import requests
import logging
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NSEAPIScraper:
    """Scrapes NSE corporate announcements using direct API calls"""

    def __init__(self, download_dir: str = 'downloads/pdfs'):
        """
        Initialize the API scraper

        Args:
            download_dir: Directory to save downloaded PDFs
        """
        self.base_url = "https://www.nseindia.com"
        self.api_url = f"{self.base_url}/api/corporate-announcements"
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self._setup_headers()

    def _setup_headers(self):
        """Set up headers to mimic a real browser"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': f'{self.base_url}/companies-listing/corporate-filings-announcements'
        })

    def get_cookies(self):
        """Get cookies by visiting the announcements page"""
        try:
            logger.info("Getting cookies from NSE website...")
            response = self.session.get(
                f'{self.base_url}/companies-listing/corporate-filings-announcements',
                timeout=15
            )

            if response.status_code == 200:
                logger.info(f"Got {len(self.session.cookies)} cookies")
                time.sleep(2)  # Human-like delay
                return True
            else:
                logger.error(f"Failed to get cookies: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error getting cookies: {e}")
            return False

    def fetch_announcements(self, index: str = 'equities') -> List[Dict]:
        """
        Fetch announcements from NSE API

        Args:
            index: Type of securities (equities, sme, debt, mf, etc.)

        Returns:
            List of announcement dictionaries
        """
        try:
            params = {'index': index}
            logger.info(f"Fetching announcements from API (index={index})...")

            response = self.session.get(
                self.api_url,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Fetched {len(data)} announcements")
                return data
            else:
                logger.error(f"API request failed: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error fetching announcements: {e}", exc_info=True)
            return []

    def filter_announcements(
        self,
        announcements: List[Dict],
        search_term: str = "awarding of order",
        days_back: int = 30
    ) -> List[Dict]:
        """
        Filter announcements by search term and date

        Args:
            announcements: List of announcements
            search_term: Search query
            days_back: Number of days to look back

        Returns:
            Filtered list of announcements
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        search_lower = search_term.lower()
        filtered = []

        for ann in announcements:
            # Parse date
            try:
                date_str = ann.get('an_dt', '')
                # Format: "28-May-2026 23:55:24"
                ann_date = datetime.strptime(date_str, '%d-%b-%Y %H:%M:%S')
            except:
                logger.debug(f"Could not parse date: {ann.get('an_dt')}")
                continue

            # Skip if too old
            if ann_date < cutoff_date:
                continue

            # Check if search term matches
            desc = ann.get('desc', '').lower()
            text = ann.get('attchmntText', '').lower()

            if search_lower in desc or search_lower in text:
                filtered.append(ann)

        logger.info(f"Filtered {len(filtered)} announcements matching '{search_term}'")
        return filtered

    def convert_to_standard_format(self, announcements: List[Dict]) -> List[Dict]:
        """
        Convert API response to standard format

        Args:
            announcements: List of API announcements

        Returns:
            List in standard format compatible with orchestrator
        """
        converted = []

        for ann in announcements:
            try:
                # Parse date
                date_str = ann.get('an_dt', '')
                try:
                    ann_date = datetime.strptime(date_str, '%d-%b-%Y %H:%M:%S')
                    formatted_date = ann_date.strftime('%Y-%m-%d')
                except:
                    formatted_date = date_str

                # Construct PDF URL
                pdf_url = ann.get('attchmntFile')
                if pdf_url and not pdf_url.startswith('http'):
                    pdf_url = f"https://nsearchives.nseindia.com/corporate/{pdf_url}"

                standard = {
                    'symbol': ann.get('symbol', '').strip(),
                    'company_name': ann.get('sm_name', '').strip(),
                    'announcement_date': formatted_date,
                    'subject': ann.get('attchmntText', ann.get('desc', '')).strip(),
                    'pdf_url': pdf_url,
                    'source': 'NSE_API',
                    'scraped_at': datetime.now().isoformat(),

                    # Extra fields
                    'desc': ann.get('desc', ''),
                    'isin': ann.get('sm_isin', ''),
                    'file_size': ann.get('fileSize', '')
                }

                converted.append(standard)

            except Exception as e:
                logger.warning(f"Error converting announcement: {e}")
                continue

        return converted

    def download_pdf(self, pdf_url: str, symbol: str, date: str) -> Optional[str]:
        """
        Download PDF file

        Args:
            pdf_url: URL of the PDF
            symbol: Company symbol
            date: Announcement date

        Returns:
            Path to downloaded file or None
        """
        if not pdf_url:
            return None

        try:
            logger.info(f"Downloading PDF for {symbol}...")

            # Generate filename
            safe_symbol = symbol.replace('/', '_')
            filename = f"{safe_symbol}_{date}.pdf"
            filepath = self.download_dir / filename

            # Download
            response = self.session.get(pdf_url, timeout=30)

            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                logger.info(f"Downloaded: {filename}")
                return str(filepath)
            else:
                logger.error(f"Failed to download PDF: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error downloading PDF for {symbol}: {e}")
            return None

    def scrape(
        self,
        search_term: str = "awarding of order",
        days_back: int = 30,
        download_pdfs: bool = True
    ) -> List[Dict]:
        """
        Main scraping method

        Args:
            search_term: Term to search for
            days_back: Days to look back
            download_pdfs: Whether to download PDFs

        Returns:
            List of announcements with data
        """
        try:
            # Get cookies first
            if not self.get_cookies():
                logger.error("Failed to get cookies")
                return []

            # Fetch announcements
            raw_announcements = self.fetch_announcements()

            if not raw_announcements:
                logger.warning("No announcements fetched")
                return []

            # Filter
            filtered = self.filter_announcements(
                raw_announcements,
                search_term,
                days_back
            )

            # Convert to standard format
            announcements = self.convert_to_standard_format(filtered)

            if not announcements:
                logger.warning("No announcements matched criteria")
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
                        time.sleep(1)  # Rate limiting

            return announcements

        except Exception as e:
            logger.error(f"Scraping failed: {e}", exc_info=True)
            return []


async def main():
    """Example usage (async wrapper for compatibility)"""
    scraper = NSEAPIScraper(download_dir='downloads/nse_pdfs')

    # Scrape announcements
    announcements = scraper.scrape(
        search_term="awarding of order",
        days_back=30,
        download_pdfs=True
    )

    # Save results
    output_file = 'nse_announcements_api.json'
    with open(output_file, 'w') as f:
        json.dump(announcements, f, indent=2)

    logger.info(f"Saved {len(announcements)} announcements to {output_file}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"SCRAPING SUMMARY")
    print(f"{'='*60}")
    print(f"Total announcements: {len(announcements)}")
    print(f"Companies: {len(set(a['symbol'] for a in announcements))}")
    print(f"{'='*60}\n")

    # Print first few
    for ann in announcements[:5]:
        print(f"{ann['symbol']:10} {ann['announcement_date']} - {ann['subject'][:60]}...")


if __name__ == "____main__":
    import asyncio
    asyncio.run(main())
