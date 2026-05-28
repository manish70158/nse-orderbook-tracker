#!/usr/bin/env python3
"""
NSE Data Fetcher - Production-ready script for fetching NSE announcements
and Nifty 50 company data with robust error handling.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NSEFetcher:
    """Handles all NSE data fetching operations"""

    BASE_URL = "https://www.nseindia.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "DNT": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"'
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._initialize_session()

    def _initialize_session(self):
        """Initialize session by visiting NSE homepage to get cookies"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/",
                timeout=10
            )
            response.raise_for_status()
            logger.info("Session initialized successfully")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not initialize session from homepage (this is OK): {e}")
            logger.info("Will attempt direct API calls - NSE sometimes blocks homepage but allows API access")

    def fetch_nifty50_companies(self) -> List[Dict]:
        """
        Fetch current Nifty 50 constituents

        Returns:
            List of dictionaries with company info (symbol, name, industry)
        """
        url = f"{self.BASE_URL}/api/equity-stockIndices?index=NIFTY%2050"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            companies = []
            for stock in data.get('data', []):
                companies.append({
                    'symbol': stock.get('symbol', ''),
                    'company_name': stock.get('meta', {}).get('companyName', ''),
                    'industry': stock.get('meta', {}).get('industry', ''),
                    'last_price': stock.get('lastPrice', 0),
                    'change': stock.get('change', 0),
                    'pChange': stock.get('pChange', 0)
                })

            logger.info(f"Fetched {len(companies)} Nifty 50 companies")
            return companies

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Nifty 50 companies: {e}")
            return []
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing Nifty 50 data: {e}")
            return []

    def fetch_announcements(
        self,
        index: str = "equities",
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch corporate announcements from NSE

        Args:
            index: Index type (default: 'equities')
            from_date: Start date in DD-MM-YYYY format (optional)
            to_date: End date in DD-MM-YYYY format (optional)

        Returns:
            List of announcement dictionaries
        """
        url = f"{self.BASE_URL}/api/corporate-announcements"
        params = {"index": index}

        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date

        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            announcements = data if isinstance(data, list) else []
            logger.info(f"Fetched {len(announcements)} announcements")
            return announcements

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching announcements: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing announcements data: {e}")
            return []

    def filter_order_announcements(
        self,
        announcements: List[Dict],
        nifty50_symbols: Optional[set] = None
    ) -> List[Dict]:
        """
        Filter announcements for order-related content

        Args:
            announcements: List of all announcements
            nifty50_symbols: Set of Nifty 50 symbols to filter (optional)

        Returns:
            Filtered list of order-related announcements
        """
        order_keywords = [
            'order', 'contract', 'win', 'award', 'awarded',
            'TCV', 'order book', 'secured', 'bagged', 'won contract',
            'purchase order', 'work order', 'LOI', 'letter of intent',
            'business win', 'project award'
        ]

        filtered = []
        for ann in announcements:
            # Filter by Nifty 50 if provided
            if nifty50_symbols and ann.get('symbol') not in nifty50_symbols:
                continue

            # Check for order keywords
            text = (
                ann.get('attchmntText', '') + ' ' +
                ann.get('desc', '') + ' ' +
                ann.get('subject', '')
            ).lower()

            if any(keyword in text for keyword in order_keywords):
                filtered.append(ann)

        logger.info(f"Filtered {len(filtered)} order-related announcements from {len(announcements)} total")
        return filtered

    def get_announcement_pdf_url(self, announcement: Dict) -> Optional[str]:
        """
        Extract PDF URL from announcement

        Args:
            announcement: Announcement dictionary

        Returns:
            Full PDF URL or None
        """
        pdf_filename = announcement.get('attchmntFile')
        if pdf_filename:
            return f"{self.BASE_URL}/archives/nsccl/mwpl/{pdf_filename}"
        return None


def main():
    """Example usage of NSEFetcher"""
    fetcher = NSEFetcher()

    # Fetch Nifty 50 companies
    print("\n=== Fetching Nifty 50 Companies ===")
    companies = fetcher.fetch_nifty50_companies()
    nifty50_symbols = {comp['symbol'] for comp in companies}

    print(f"Found {len(companies)} companies")
    if companies:
        print(f"Sample: {companies[0]}")

    # Fetch announcements
    print("\n=== Fetching Announcements ===")
    announcements = fetcher.fetch_announcements()
    print(f"Total announcements: {len(announcements)}")

    # Filter for order-related announcements
    print("\n=== Filtering Order-Related Announcements ===")
    order_announcements = fetcher.filter_order_announcements(
        announcements,
        nifty50_symbols
    )

    print(f"Found {len(order_announcements)} order-related announcements for Nifty 50 companies")

    # Display sample
    if order_announcements:
        print("\n=== Sample Order Announcement ===")
        sample = order_announcements[0]
        print(f"Symbol: {sample.get('symbol')}")
        print(f"Company: {sample.get('sm_name')}")
        print(f"Date: {sample.get('an_dt')}")
        print(f"Description: {sample.get('attchmntText', '')[:200]}...")
        pdf_url = fetcher.get_announcement_pdf_url(sample)
        if pdf_url:
            print(f"PDF URL: {pdf_url}")


if __name__ == "__main__":
    main()
