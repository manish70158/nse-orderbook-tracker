#!/usr/bin/env python3
"""
Test script to verify orchestrator works for different date ranges
Run this to test before using the web interface
"""

import sys
from pathlib import Path
from orchestrator import OrderBookOrchestrator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_fetch(days):
    """Test fetching data for specified days"""
    logger.info("="*80)
    logger.info(f"TESTING: Fetch {days} days of data")
    logger.info("="*80)

    try:
        # Create orchestrator (disable Telegram for testing)
        orchestrator = OrderBookOrchestrator(
            enable_telegram=False,
            value_threshold=500
        )

        # Run pipeline
        logger.info(f"Starting orchestrator for {days} days...")
        orchestrator.run(
            search_term="awarding of order",
            days_back=days
        )

        # Check output
        output_file = Path('output/orderbook_data.json')
        if output_file.exists():
            import json
            with open(output_file, 'r') as f:
                data = json.load(f)

            logger.info("="*80)
            logger.info(f"✓ SUCCESS: Fetched {len(data)} announcements")
            logger.info("="*80)

            # Show sample
            if data:
                logger.info("Sample data:")
                for i, order in enumerate(data[:3], 1):
                    logger.info(f"  {i}. {order.get('symbol')} - {order.get('company_name')}")
                    logger.info(f"     Date: {order.get('announcement_date')}")
                    logger.info(f"     Value: ₹{order.get('order_value_crores', 0)} Cr")
                    logger.info("")

            return True
        else:
            logger.error("✗ FAILED: Output file not created")
            return False

    except Exception as e:
        logger.error(f"✗ FAILED: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    # Test different ranges
    test_cases = [7, 30, 90]

    if len(sys.argv) > 1:
        # Test specific days from command line
        try:
            days = int(sys.argv[1])
            test_cases = [days]
        except ValueError:
            logger.error("Please provide a valid number of days")
            sys.exit(1)

    results = {}
    for days in test_cases:
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST {test_cases.index(days) + 1}/{len(test_cases)}")
        logger.info(f"{'='*80}\n")

        success = test_fetch(days)
        results[days] = success

        if not success:
            logger.warning(f"Test failed for {days} days, stopping tests")
            break

    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    for days, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status}: {days} days")
    logger.info("="*80)
