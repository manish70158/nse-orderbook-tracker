#!/usr/bin/env python3
"""
NSE Corporate Announcements Scraper using Playwright
Scrapes the NSE website for order-related announcements
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NSEPlaywrightScraper:
    """Scrapes NSE corporate announcements using Playwright"""

    def __init__(self, download_dir: str = 'downloads/pdfs'):
        """
        Initialize the scraper

        Args:
            download_dir: Directory to save downloaded PDFs
        """
        self.base_url = "https://www.nseindia.com/companies-listing/corporate-filings-announcements"
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None  # Store playwright instance

    async def initialize(self, headless: bool = True):
        """
        Initialize Playwright browser

        Args:
            headless: Run browser in headless mode
        """
        logger.info("Initializing Playwright browser...")

        self.playwright = await async_playwright().start()

        # Use WebKit (works on macOS, Chromium crashes)
        logger.info("Attempting to launch WebKit browser...")
        try:
            self.browser = await self.playwright.webkit.launch(
                headless=headless
            )
            logger.info("Successfully launched WebKit browser")
        except Exception as e:
            logger.error(f"WebKit launch failed: {e}")
            raise RuntimeError(f"Failed to launch WebKit browser: {e}")

        # Create context with download settings
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            accept_downloads=True
        )

        self.page = await context.new_page()

        # Add extra headers to avoid bot detection
        await self.page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        logger.info("Browser initialized successfully")

    async def navigate_to_announcements(self):
        """Navigate to NSE corporate announcements page"""
        logger.info(f"Navigating to {self.base_url}")

        try:
            # Navigate to page with longer timeout
            await self.page.goto(self.base_url, wait_until='domcontentloaded', timeout=90000)

            # Wait for page to load and JavaScript to initialize
            await asyncio.sleep(5)

            logger.info("Successfully loaded NSE announcements page")
            return True

        except PlaywrightTimeout:
            logger.error("Timeout while loading NSE page")
            return False
        except Exception as e:
            logger.error(f"Error navigating to NSE page: {e}")
            return False

    async def search_announcements(self, search_term: str = "awarding of order", days_back: int = 30):
        """
        Search for announcements with specific term

        Args:
            search_term: Search query (default: "awarding of order")
            days_back: Number of days to look back

        Returns:
            List of announcement dictionaries
        """
        logger.info(f"Searching for: '{search_term}' (last {days_back} days)")

        announcements = []

        try:
            # Alternative approach: Load ALL announcements and filter locally
            # The search functionality on NSE website is not working reliably

            logger.info("Loading all announcements (will filter locally)...")

            # Step 1: Wait for page to be ready
            await self.page.wait_for_selector('.subjectAutoComplete', timeout=30000)
            await asyncio.sleep(3)  # Wait for JS initialization

            # Step 2: Click Refresh button to load all announcements
            logger.info("Clicking Refresh to load all announcements...")
            try:
                refresh_link = await self.page.query_selector('a[onclick*="CFRefresh"][onclick*="CFanncEquity"]')
                if refresh_link:
                    await refresh_link.click()
                    logger.info("Clicked Refresh button")
                    await asyncio.sleep(10)  # Wait longer for AJAX to load all data
                else:
                    logger.error("Refresh button not found")
                    return []
            except Exception as e:
                logger.error(f"Could not click Refresh button: {e}")
                return []

            # Step 3: Wait for results container to have content
            await asyncio.sleep(3)
            logger.info("Waiting for results container to populate...")

            # The results are loaded into a div, not a table
            results_container_selector = '#table-CFanncEquity'

            try:
                # Wait for the container to exist
                await self.page.wait_for_selector(results_container_selector, timeout=15000)
                logger.info("Results container found")

                # Wait for content to load (table/rows to appear inside)
                await asyncio.sleep(3)

                # Check if container has content
                container = await self.page.query_selector(results_container_selector)
                if not container:
                    raise Exception("Results container not found")

                # Get inner HTML to check if it has content
                inner_html = await container.inner_html()

                if not inner_html or len(inner_html.strip()) < 100:
                    logger.warning("Results container is empty or has minimal content")
                    # Try clicking refresh button to trigger data load
                    logger.info("Trying to click refresh button...")
                    refresh_buttons = await self.page.query_selector_all('a[onclick*="CFRefresh"]')
                    if refresh_buttons:
                        await refresh_buttons[0].click()
                        await asyncio.sleep(5)

                # Now look for actual table elements inside the container
                table_selectors = [
                    f'{results_container_selector} table',
                    f'{results_container_selector} tbody',
                    f'{results_container_selector} .table',
                    results_container_selector
                ]

                table_found = False
                for selector in table_selectors:
                    try:
                        await self.page.wait_for_selector(selector, timeout=5000)
                        # Check if it has rows
                        rows = await self.page.query_selector_all(f'{selector} tr, {selector} [role="row"]')
                        if len(rows) > 0:
                            logger.info(f"Found results with selector: {selector} ({len(rows)} rows)")
                            table_found = True
                            break
                    except:
                        continue

                if not table_found:
                    logger.error("No results found after search")
                    # Take screenshot for debugging
                    screenshot_path = self.download_dir / 'debug_no_results.png'
                    await self.page.screenshot(path=str(screenshot_path), full_page=True)
                    logger.info(f"Screenshot saved to: {screenshot_path}")

                    # Save HTML for debugging
                    html_path = self.download_dir / 'debug_page.html'
                    html = await self.page.content()
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html)
                    logger.info(f"Page HTML saved to: {html_path}")

                    return []

                await asyncio.sleep(2)

                # Extract announcements from the container and filter locally for search term
                all_announcements = await self._extract_announcements_from_container(days_back)

                # Filter for search term (case-insensitive)
                search_lower = search_term.lower()
                announcements = [
                    ann for ann in all_announcements
                    if search_lower in ann['subject'].lower()
                ]

                logger.info(f"Filtered {len(announcements)} announcements matching '{search_term}' from {len(all_announcements)} total")

            except PlaywrightTimeout as e:
                logger.error(f"Timeout waiting for results: {e}")
                return []

            logger.info(f"Found {len(announcements)} announcements")
            return announcements

        except PlaywrightTimeout as e:
            logger.error(f"Timeout during search: {e}")
            # Take screenshot for debugging
            try:
                screenshot_path = self.download_dir / 'debug_timeout.png'
                await self.page.screenshot(path=str(screenshot_path), full_page=True)
                logger.info(f"Debug screenshot saved to: {screenshot_path}")
            except:
                pass
            return []
        except Exception as e:
            logger.error(f"Error during search: {e}", exc_info=True)
            return []

    async def _extract_announcements_from_container(self, days_back: int) -> List[Dict]:
        """Extract announcement data from results container (div-based table)"""
        announcements = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        try:
            # Try both regular table rows and custom div-based rows
            row_selectors = [
                '#table-CFanncEquity table tbody tr',
                '#table-CFanncEquity tr',
                '#table-CFanncEquity [role="row"]',
                'table tbody tr'
            ]

            rows = []
            for selector in row_selectors:
                rows = await self.page.query_selector_all(selector)
                if len(rows) > 0:
                    logger.info(f"Found {len(rows)} rows with selector: {selector}")
                    break

            if not rows:
                logger.warning("No rows found in results")
                return []

            logger.info(f"Processing {len(rows)} rows...")

            for row in rows:
                try:
                    # Skip header rows
                    is_header = await row.evaluate('el => el.tagName === "TH" || el.querySelector("th") !== null')
                    if is_header:
                        continue

                    # Extract data from columns (td or role="cell")
                    cells = await row.query_selector_all('td, [role="cell"]')

                    if len(cells) < 4:
                        logger.debug(f"Row has insufficient cells: {len(cells)}")
                        continue

                    # Extract cell data (NSE announcements typically have: Symbol, Company, Date, Subject, Attachment)
                    symbol = await cells[0].inner_text()
                    company_name = await cells[1].inner_text() if len(cells) > 1 else ""
                    date_str = await cells[2].inner_text() if len(cells) > 2 else ""
                    subject = await cells[3].inner_text() if len(cells) > 3 else ""

                    # Parse date
                    try:
                        ann_date = datetime.strptime(date_str.strip(), '%d-%b-%Y')
                    except ValueError:
                        try:
                            ann_date = datetime.strptime(date_str.strip(), '%d-%m-%Y')
                        except ValueError:
                            try:
                                ann_date = datetime.strptime(date_str.strip(), '%Y-%m-%d')
                            except ValueError:
                                logger.warning(f"Could not parse date: {date_str}")
                                continue

                    # Skip if too old
                    if ann_date < cutoff_date:
                        continue

                    # Look for PDF link (usually in last cell)
                    pdf_link = None
                    if len(cells) > 4:
                        pdf_button = await cells[-1].query_selector('a, button')
                        if pdf_button:
                            pdf_link = await pdf_button.get_attribute('href')
                            if not pdf_link:
                                # Might be onclick handler
                                onclick = await pdf_button.get_attribute('onclick')
                                if onclick:
                                    # Try to extract URL from onclick
                                    import re
                                    url_match = re.search(r'["\']([^"\']*\.pdf[^"\']*)["\']', onclick, re.IGNORECASE)
                                    if url_match:
                                        pdf_link = url_match.group(1)

                    if pdf_link and not pdf_link.startswith('http'):
                        pdf_link = f"https://www.nseindia.com{pdf_link}"

                    announcement = {
                        'symbol': symbol.strip(),
                        'company_name': company_name.strip(),
                        'announcement_date': ann_date.strftime('%Y-%m-%d'),
                        'subject': subject.strip(),
                        'pdf_url': pdf_link,
                        'source': 'NSE_Playwright',
                        'scraped_at': datetime.now().isoformat()
                    }

                    announcements.append(announcement)
                    logger.info(f"Extracted: {symbol.strip()} - {subject.strip()[:50]}...")

                except Exception as e:
                    logger.warning(f"Error extracting row data: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting container data: {e}", exc_info=True)
            return []

        logger.info(f"Successfully extracted {len(announcements)} announcements")
        return announcements

    async def _extract_announcements_from_table(self, days_back: int) -> List[Dict]:
        """Extract announcement data from results table (legacy method)"""
        announcements = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        try:
            # Get all table rows
            rows = await self.page.query_selector_all('table tbody tr')
            logger.info(f"Processing {len(rows)} table rows...")

            for row in rows:
                try:
                    # Extract data from columns
                    cells = await row.query_selector_all('td')

                    if len(cells) < 5:
                        continue

                    # Extract cell data
                    symbol = await cells[0].inner_text()
                    company_name = await cells[1].inner_text()
                    date_str = await cells[2].inner_text()
                    subject = await cells[3].inner_text()

                    # Parse date
                    try:
                        ann_date = datetime.strptime(date_str.strip(), '%d-%b-%Y')
                    except ValueError:
                        try:
                            ann_date = datetime.strptime(date_str.strip(), '%d-%m-%Y')
                        except ValueError:
                            logger.warning(f"Could not parse date: {date_str}")
                            continue

                    # Skip if too old
                    if ann_date < cutoff_date:
                        continue

                    # Look for PDF link
                    pdf_link = None
                    pdf_button = await cells[-1].query_selector('a')
                    if pdf_button:
                        pdf_link = await pdf_button.get_attribute('href')
                        if pdf_link and not pdf_link.startswith('http'):
                            pdf_link = f"https://www.nseindia.com{pdf_link}"

                    announcement = {
                        'symbol': symbol.strip(),
                        'company_name': company_name.strip(),
                        'announcement_date': ann_date.strftime('%Y-%m-%d'),
                        'subject': subject.strip(),
                        'pdf_url': pdf_link,
                        'source': 'NSE_Playwright',
                        'scraped_at': datetime.now().isoformat()
                    }

                    announcements.append(announcement)
                    logger.info(f"Extracted: {symbol} - {subject[:50]}...")

                except Exception as e:
                    logger.warning(f"Error extracting row data: {e}")
                    continue

            return announcements

        except Exception as e:
            logger.error(f"Error extracting table data: {e}", exc_info=True)
            return []

    async def download_pdf(self, pdf_url: str, symbol: str, date: str) -> Optional[str]:
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

            # Start waiting for download
            async with self.page.expect_download() as download_info:
                # Click download link or navigate
                if pdf_url.startswith('http'):
                    await self.page.goto(pdf_url)
                else:
                    # Find and click the link on the page
                    await self.page.click(f'a[href="{pdf_url}"]')

            download = await download_info.value

            # Save to file
            await download.save_as(filepath)

            logger.info(f"Downloaded: {filename}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error downloading PDF for {symbol}: {e}")
            return None

    async def download_all_pdfs(self, announcements: List[Dict]) -> List[Dict]:
        """
        Download PDFs for all announcements

        Args:
            announcements: List of announcement dictionaries

        Returns:
            Updated announcements with local PDF paths
        """
        logger.info(f"Downloading {len(announcements)} PDFs...")

        for ann in announcements:
            if ann.get('pdf_url'):
                pdf_path = await self.download_pdf(
                    ann['pdf_url'],
                    ann['symbol'],
                    ann['announcement_date']
                )
                ann['local_pdf_path'] = pdf_path

                # Small delay between downloads
                await asyncio.sleep(1)

        logger.info("PDF downloads complete")
        return announcements

    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")

        if self.playwright:
            await self.playwright.stop()
            logger.info("Playwright stopped")

    async def scrape(
        self,
        search_term: str = "awarding of order",
        days_back: int = 30,
        download_pdfs: bool = True,
        headless: bool = True
    ) -> List[Dict]:
        """
        Main scraping method - orchestrates the entire process

        Args:
            search_term: Term to search for
            days_back: Days to look back
            download_pdfs: Whether to download PDFs
            headless: Run browser in headless mode

        Returns:
            List of announcements with data
        """
        try:
            # Initialize browser
            try:
                await self.initialize(headless=headless)
                logger.info("Browser initialization complete")
            except Exception as e:
                logger.error(f"Failed to initialize browser: {e}", exc_info=True)
                raise

            # Navigate to page
            try:
                if not await self.navigate_to_announcements():
                    logger.error("Failed to navigate to announcements page")
                    return []
            except Exception as e:
                logger.error(f"Navigation error: {e}", exc_info=True)
                raise

            # Search for announcements
            announcements = await self.search_announcements(search_term, days_back)

            if not announcements:
                logger.warning("No announcements found")
                return []

            # Download PDFs if requested
            if download_pdfs:
                announcements = await self.download_all_pdfs(announcements)

            return announcements

        except Exception as e:
            logger.error(f"Scraping failed: {e}", exc_info=True)
            return []
        finally:
            await self.close()


async def main():
    """Example usage"""
    scraper = NSEPlaywrightScraper(download_dir='downloads/nse_pdfs')

    # Scrape announcements
    announcements = await scraper.scrape(
        search_term="awarding of order",
        days_back=30,
        download_pdfs=True,
        headless=False  # Set to True in production
    )

    # Save results
    output_file = 'nse_announcements.json'
    with open(output_file, 'w') as f:
        json.dump(announcements, f, indent=2)

    logger.info(f"Saved {len(announcements)} announcements to {output_file}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"SCRAPING SUMMARY")
    print(f"{'='*60}")
    print(f"Total announcements: {len(announcements)}")
    print(f"Companies: {len(set(a['symbol'] for a in announcements))}")
    print(f"Date range: {min(a['announcement_date'] for a in announcements) if announcements else 'N/A'} to {max(a['announcement_date'] for a in announcements) if announcements else 'N/A'}")
    print(f"{'='*60}\n")

    # Print first few
    for ann in announcements[:5]:
        print(f"{ann['symbol']:10} {ann['announcement_date']} - {ann['subject'][:60]}...")


if __name__ == "__main__":
    asyncio.run(main())
