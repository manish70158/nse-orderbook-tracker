#!/usr/bin/env python3
"""
Unified Data Fetcher - Combines BSE and NSE data sources with fallback logic
Tries BSE first (more reliable), falls back to NSE if needed.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from bse_data_fetcher import BSEFetcher, BSE_AVAILABLE
from nse_data_fetcher import NSEFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedDataFetcher:
    """
    Unified data fetcher with multi-source fallback
    Priority: BSE (more reliable) -> NSE (fallback) -> Cached data
    """

    def __init__(self, prefer_bse: bool = True):
        """
        Initialize fetcher with source preference

        Args:
            prefer_bse: If True, try BSE first (default: True)
        """
        self.prefer_bse = prefer_bse
        self.bse_fetcher = BSEFetcher() if BSE_AVAILABLE else None
        self.nse_fetcher = NSEFetcher()
        self.last_successful_source = None

    def fetch_nifty50_companies(self) -> List[Dict]:
        """
        Fetch Nifty 50 company list

        Returns:
            List of company dictionaries
        """
        # Try BSE first if available and preferred
        if self.prefer_bse and self.bse_fetcher:
            try:
                logger.info("Fetching Nifty 50 companies from BSE...")
                companies = self.bse_fetcher.fetch_nifty50_companies()
                if companies:
                    logger.info(f"✓ Successfully fetched {len(companies)} companies from BSE")
                    self.last_successful_source = 'BSE'
                    return companies
            except Exception as e:
                logger.warning(f"BSE company fetch failed: {e}")

        # Fallback to NSE
        try:
            logger.info("Fetching Nifty 50 companies from NSE...")
            companies = self.nse_fetcher.fetch_nifty50_companies()
            if companies:
                logger.info(f"✓ Successfully fetched {len(companies)} companies from NSE")
                self.last_successful_source = 'NSE'
                return companies
        except Exception as e:
            logger.error(f"NSE company fetch failed: {e}")

        # If both failed, return hardcoded Nifty 50 list
        logger.warning("Both BSE and NSE failed. Using hardcoded Nifty 50 list.")
        return self._get_hardcoded_nifty50()

    def fetch_announcements(
        self,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Fetch corporate announcements from available sources

        Args:
            days_back: Number of days to look back (default: 30)

        Returns:
            List of announcements (normalized format)
        """
        announcements = []

        # Try BSE first if available and preferred
        if self.prefer_bse and self.bse_fetcher:
            try:
                logger.info(f"Fetching announcements from BSE (last {days_back} days)...")
                bse_announcements = self.bse_fetcher.fetch_all_nifty50_announcements(
                    days_back=days_back
                )

                if bse_announcements:
                    # Normalize BSE announcements to NSE-like format
                    normalized = [
                        self.bse_fetcher.normalize_announcement(ann)
                        for ann in bse_announcements
                    ]
                    announcements.extend(normalized)
                    logger.info(f"✓ Successfully fetched {len(normalized)} announcements from BSE")
                    self.last_successful_source = 'BSE'

            except Exception as e:
                logger.warning(f"BSE announcement fetch failed: {e}")

        # Try NSE (either as primary or fallback)
        if not announcements or not self.prefer_bse:
            try:
                logger.info("Fetching announcements from NSE...")
                nse_announcements = self.nse_fetcher.fetch_announcements()

                if nse_announcements:
                    # Add source tag
                    for ann in nse_announcements:
                        ann['source'] = 'NSE'

                    announcements.extend(nse_announcements)
                    logger.info(f"✓ Successfully fetched {len(nse_announcements)} announcements from NSE")

                    if not self.last_successful_source:
                        self.last_successful_source = 'NSE'

            except Exception as e:
                logger.warning(f"NSE announcement fetch failed: {e}")

        # Remove duplicates based on symbol and date
        announcements = self._deduplicate_announcements(announcements)

        logger.info(f"Total unique announcements fetched: {len(announcements)}")
        logger.info(f"Primary source used: {self.last_successful_source or 'None'}")

        return announcements

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
        # Use NSE fetcher's filter logic (works for both formats)
        filtered = self.nse_fetcher.filter_order_announcements(
            announcements,
            nifty50_symbols
        )

        return filtered

    def _deduplicate_announcements(self, announcements: List[Dict]) -> List[Dict]:
        """
        Remove duplicate announcements based on symbol and date

        Args:
            announcements: List of announcements

        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []

        for ann in announcements:
            # Create unique key from symbol and date
            key = f"{ann.get('symbol')}_{ann.get('an_dt')}"

            if key not in seen:
                seen.add(key)
                unique.append(ann)

        if len(announcements) > len(unique):
            logger.info(f"Removed {len(announcements) - len(unique)} duplicate announcements")

        return unique

    def _get_hardcoded_nifty50(self) -> List[Dict]:
        """
        Fallback: Return hardcoded Nifty 50 company list

        Returns:
            List of Nifty 50 companies
        """
        nifty50_symbols = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR',
            'ICICIBANK', 'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK',
            'LT', 'AXISBANK', 'BAJFINANCE', 'ASIANPAINT', 'MARUTI',
            'HCLTECH', 'TITAN', 'SUNPHARMA', 'ULTRACEMCO', 'NESTLEIND',
            'TATAMOTORS', 'ONGC', 'NTPC', 'M&M', 'TECHM',
            'POWERGRID', 'BAJAJFINSV', 'ADANIENT', 'WIPRO', 'JSWSTEEL',
            'TATASTEEL', 'INDUSINDBK', 'COALINDIA', 'HINDALCO', 'HDFCLIFE',
            'SBILIFE', 'ADANIPORTS', 'DRREDDY', 'EICHERMOT', 'GRASIM',
            'CIPLA', 'BRITANNIA', 'BPCL', 'DIVISLAB', 'APOLLOHOSP',
            'BAJAJ-AUTO', 'TATACONSUM', 'HEROMOTOCO', 'UPL'
        ]

        return [{'symbol': symbol, 'company_name': symbol} for symbol in nifty50_symbols]

    def get_announcement_pdf_url(self, announcement: Dict) -> Optional[str]:
        """
        Get PDF URL from announcement (works for both BSE and NSE)

        Args:
            announcement: Announcement dictionary

        Returns:
            PDF URL or None
        """
        source = announcement.get('source', 'NSE')

        if source == 'NSE':
            return self.nse_fetcher.get_announcement_pdf_url(announcement)
        elif source == 'BSE':
            # BSE PDF URLs (if available)
            pdf_filename = announcement.get('attchmntFile')
            if pdf_filename:
                # BSE PDF URL format (might need adjustment)
                return f"https://www.bseindia.com/xml-data/corpfiling/AttachHis/{pdf_filename}"

        return None


def main():
    """Example usage of UnifiedDataFetcher"""
    fetcher = UnifiedDataFetcher(prefer_bse=True)

    # Fetch Nifty 50 companies
    print("\n=== Fetching Nifty 50 Companies ===")
    companies = fetcher.fetch_nifty50_companies()
    nifty50_symbols = {comp['symbol'] for comp in companies}

    print(f"Found {len(companies)} companies")
    print(f"Source: {fetcher.last_successful_source}")
    if companies:
        print(f"Sample: {companies[0]}")

    # Fetch announcements
    print("\n=== Fetching Announcements ===")
    announcements = fetcher.fetch_announcements(days_back=7)
    print(f"Total announcements: {len(announcements)}")
    print(f"Source: {fetcher.last_successful_source}")

    # Filter for order-related announcements
    print("\n=== Filtering Order-Related Announcements ===")
    order_announcements = fetcher.filter_order_announcements(
        announcements,
        nifty50_symbols
    )

    print(f"Found {len(order_announcements)} order-related announcements")

    # Display samples
    if order_announcements:
        print("\n=== Sample Order Announcements ===")
        for i, ann in enumerate(order_announcements[:3], 1):
            print(f"\n{i}. {ann.get('symbol')} - {ann.get('sm_name')}")
            print(f"   Date: {ann.get('an_dt')}")
            print(f"   Source: {ann.get('source')}")
            print(f"   Description: {ann.get('attchmntText', '')[:150]}...")


if __name__ == "__main__":
    main()
