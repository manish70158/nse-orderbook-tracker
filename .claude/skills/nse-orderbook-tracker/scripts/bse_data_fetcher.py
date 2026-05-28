#!/usr/bin/env python3
"""
BSE Data Fetcher - Fetches corporate announcements from Bombay Stock Exchange
More reliable than NSE as it has less aggressive bot protection.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    from bse import BSE
    from bse.constants import CATEGORY
    BSE_AVAILABLE = True
except ImportError:
    BSE_AVAILABLE = False
    logging.warning("BSE library not available. Install with: pip install bse")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BSEFetcher:
    """Handles all BSE data fetching operations"""

    # BSE scrip codes for Nifty 50 companies (mapping from NSE symbols)
    # This is a comprehensive mapping of major Nifty 50 stocks
    NSE_TO_BSE_SCRIP = {
        'RELIANCE': '500325',
        'TCS': '532540',
        'HDFCBANK': '500180',
        'INFY': '500209',
        'HINDUNILVR': '500696',
        'ICICIBANK': '532174',
        'SBIN': '500112',
        'BHARTIARTL': '532454',
        'ITC': '500875',
        'KOTAKBANK': '500247',
        'LT': '500510',
        'AXISBANK': '532215',
        'BAJFINANCE': '500034',
        'ASIANPAINT': '500820',
        'MARUTI': '532500',
        'HCLTECH': '532281',
        'TITAN': '500114',
        'SUNPHARMA': '524715',
        'ULTRACEMCO': '532538',
        'NESTLEIND': '500790',
        'TATAMOTORS': '500570',
        'ONGC': '500312',
        'NTPC': '532555',
        'M&M': '500520',
        'TECHM': '532755',
        'POWERGRID': '532898',
        'BAJAJFINSV': '532978',
        'ADANIENT': '512599',
        'WIPRO': '507685',
        'JSWSTEEL': '500228',
        'TATASTEEL': '500470',
        'INDUSINDBK': '532187',
        'COALINDIA': '533278',
        'HINDALCO': '500440',
        'HDFCLIFE': '540777',
        'SBILIFE': '540719',
        'ADANIPORTS': '532921',
        'DRREDDY': '500124',
        'EICHERMOT': '505200',
        'GRASIM': '500300',
        'CIPLA': '500087',
        'BRITANNIA': '500825',
        'BPCL': '500547',
        'DIVISLAB': '532488',
        'APOLLOHOSP': '508869',
        'BAJAJ-AUTO': '532977',
        'TATACONSUM': '500800',
        'HEROMOTOCO': '500182',
        'UPL': '512070'
    }

    def __init__(self):
        if not BSE_AVAILABLE:
            raise ImportError("BSE library not installed. Install with: pip install bse")
        self.bse = None

    def fetch_nifty50_companies(self) -> List[Dict]:
        """
        Get Nifty 50 company list with BSE scrip codes

        Returns:
            List of dictionaries with company info
        """
        companies = []
        for nse_symbol, bse_scrip in self.NSE_TO_BSE_SCRIP.items():
            companies.append({
                'symbol': nse_symbol,
                'bse_scrip': bse_scrip,
                'company_name': nse_symbol  # Can be enhanced with full names
            })

        logger.info(f"Loaded {len(companies)} Nifty 50 companies with BSE scrip codes")
        return companies

    def fetch_announcements_for_company(
        self,
        scrip_code: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        category: str = CATEGORY.UPDATE
    ) -> List[Dict]:
        """
        Fetch BSE announcements for a specific company

        Args:
            scrip_code: BSE scrip code
            from_date: Start date (default: 6 months ago)
            to_date: End date (default: today)
            category: Announcement category

        Returns:
            List of announcement dictionaries
        """
        if not from_date:
            from_date = datetime.now() - timedelta(days=180)  # 6 months
        if not to_date:
            to_date = datetime.now()

        try:
            import tempfile
            import os

            # Create temporary download folder
            temp_dir = tempfile.mkdtemp()

            try:
                with BSE(download_folder=temp_dir) as bse:
                    # Try different categories to maximize data
                    announcements = []
                    for cat in [CATEGORY.UPDATE, CATEGORY.RESULT, CATEGORY.OTHERS]:
                        try:
                            ann = bse.announcements(
                                scripcode=scrip_code,
                                from_date=from_date.strftime('%d-%m-%Y'),
                                to_date=to_date.strftime('%d-%m-%Y'),
                                category=cat
                            )
                            if ann:
                                if isinstance(ann, list):
                                    announcements.extend(ann)
                                else:
                                    announcements.append(ann)
                        except:
                            pass  # Some categories might not have data

                    return announcements
            finally:
                # Cleanup temp directory
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

        except Exception as e:
            logger.warning(f"Error fetching announcements for scrip {scrip_code}: {e}")
            return []

    def fetch_all_nifty50_announcements(
        self,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Fetch announcements for all Nifty 50 companies

        Args:
            days_back: Number of days to look back (default: 30)

        Returns:
            List of all announcements with NSE symbol included
        """
        from_date = datetime.now() - timedelta(days=days_back)
        to_date = datetime.now()

        all_announcements = []

        for nse_symbol, bse_scrip in self.NSE_TO_BSE_SCRIP.items():
            logger.info(f"Fetching announcements for {nse_symbol} (BSE: {bse_scrip})...")

            try:
                announcements = self.fetch_announcements_for_company(
                    scrip_code=bse_scrip,
                    from_date=from_date,
                    to_date=to_date
                )

                # Add NSE symbol to each announcement
                for ann in announcements:
                    ann['symbol'] = nse_symbol
                    ann['bse_scrip'] = bse_scrip
                    ann['source'] = 'BSE'

                all_announcements.extend(announcements)
                logger.info(f"  Found {len(announcements)} announcements for {nse_symbol}")

                # Small delay to be respectful to BSE servers
                import time
                time.sleep(0.5)

            except Exception as e:
                logger.warning(f"Error fetching for {nse_symbol}: {e}")
                continue

        logger.info(f"Total announcements fetched from BSE: {len(all_announcements)}")
        return all_announcements

    def filter_order_announcements(
        self,
        announcements: List[Dict]
    ) -> List[Dict]:
        """
        Filter announcements for order-related content

        Args:
            announcements: List of all announcements

        Returns:
            Filtered list of order-related announcements
        """
        order_keywords = [
            'order', 'contract', 'win', 'award', 'awarded',
            'TCV', 'order book', 'secured', 'bagged', 'won contract',
            'purchase order', 'work order', 'LOI', 'letter of intent',
            'business win', 'project award', 'new order', 'order received'
        ]

        filtered = []
        for ann in announcements:
            # Get announcement text (BSE structure is different from NSE)
            text = ''

            # BSE announcements have different field names
            if isinstance(ann, dict):
                text = (
                    str(ann.get('Subject', '')) + ' ' +
                    str(ann.get('News', '')) + ' ' +
                    str(ann.get('Desc', '')) + ' ' +
                    str(ann.get('HEADLINE', '')) + ' ' +
                    str(ann.get('DISSEM_DT', ''))
                ).lower()

            # Check for order keywords
            if any(keyword in text for keyword in order_keywords):
                filtered.append(ann)

        logger.info(f"Filtered {len(filtered)} order-related announcements from {len(announcements)} total")
        return filtered

    def normalize_announcement(self, ann: Dict) -> Dict:
        """
        Normalize BSE announcement format to match NSE format

        Args:
            ann: BSE announcement dictionary

        Returns:
            Normalized announcement dictionary
        """
        # BSE announcements have different field structure
        # Normalize to NSE-like format for consistency

        return {
            'symbol': ann.get('symbol', ''),
            'sm_name': ann.get('symbol', ''),  # Could be enhanced with full name
            'an_dt': ann.get('DISSEM_DT', ann.get('NEWS_DT', '')),
            'attchmntText': ann.get('HEADLINE', ann.get('News', ann.get('Subject', ''))),
            'desc': ann.get('Desc', ''),
            'subject': ann.get('Subject', ''),
            'attchmntFile': ann.get('ATTACHMENTNAME', ''),
            'source': 'BSE',
            'bse_scrip': ann.get('bse_scrip', ''),
            'raw_data': ann  # Keep original data for reference
        }


def main():
    """Example usage of BSEFetcher"""
    if not BSE_AVAILABLE:
        print("❌ BSE library not installed. Install with: pip install bse")
        return

    fetcher = BSEFetcher()

    # Fetch Nifty 50 companies
    print("\n=== Nifty 50 Companies with BSE Codes ===")
    companies = fetcher.fetch_nifty50_companies()
    print(f"Loaded {len(companies)} companies")
    print(f"Sample: {companies[0]}")

    # Fetch announcements for a single company (for quick testing)
    print("\n=== Testing with Reliance (500325) ===")
    reliance_announcements = fetcher.fetch_announcements_for_company(
        scrip_code='500325',  # Reliance
        from_date=datetime.now() - timedelta(days=30)
    )
    print(f"Found {len(reliance_announcements)} announcements for Reliance")

    if reliance_announcements:
        print(f"\nSample announcement: {reliance_announcements[0]}")

    # Test order filtering
    print("\n=== Testing Order Filtering ===")
    order_related = fetcher.filter_order_announcements(reliance_announcements)
    print(f"Order-related announcements: {len(order_related)}")

    # Optionally fetch all Nifty 50 (takes longer)
    # print("\n=== Fetching All Nifty 50 Announcements ===")
    # all_announcements = fetcher.fetch_all_nifty50_announcements(days_back=7)
    # print(f"Total announcements: {len(all_announcements)}")


if __name__ == "__main__":
    main()
