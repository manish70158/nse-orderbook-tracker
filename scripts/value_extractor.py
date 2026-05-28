#!/usr/bin/env python3
"""
Value Extractor - Extract monetary values from announcement text
Handles various formats: Rs. X crore, USD Y million, etc.
"""

import re
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderValueExtractor:
    """Extracts and normalizes order values from text"""

    # Exchange rate approximations (update periodically)
    USD_TO_INR = 83.0
    EUR_TO_INR = 90.0

    # Regex patterns for different formats
    PATTERNS = [
        # Rs. 500 crore, Rs. 500 Cr, Rs 500 crores
        r'Rs\.?\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|crores)',

        # ₹500 crore
        r'₹\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|crores)',

        # INR 500 crore/million
        r'INR\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|crores|million|mn)',

        # USD 50 million, USD 5 billion
        r'USD\s*([\d,]+(?:\.\d+)?)\s*(million|mn|billion|bn)',

        # US$ 50 million
        r'US\$\s*([\d,]+(?:\.\d+)?)\s*(million|mn|billion|bn)',

        # EUR 50 million
        r'EUR\s*([\d,]+(?:\.\d+)?)\s*(million|mn|billion|bn)',

        # $ 50 million (assume USD)
        r'\$\s*([\d,]+(?:\.\d+)?)\s*(million|mn|billion|bn)',

        # Worth Rs. 500 crore
        r'worth\s+Rs\.?\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|crores)',

        # Value of Rs. 500 crore
        r'value\s+of\s+Rs\.?\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|crores)',

        # Approximately Rs. 500 crore
        r'approximately\s+Rs\.?\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|crores)',
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.PATTERNS]

    def extract_value(self, text: str) -> Optional[Dict]:
        """
        Extract the first monetary value found in text

        Args:
            text: Announcement text to search

        Returns:
            Dictionary with value, currency, original_text or None
        """
        for pattern in self.compiled_patterns:
            match = pattern.search(text)
            if match:
                try:
                    value_str = match.group(1).replace(',', '')
                    value = float(value_str)
                    unit = match.group(2).lower()

                    # Determine currency
                    currency = self._determine_currency(match.group(0))

                    # Normalize to INR crores
                    normalized_value = self._normalize_to_inr_crores(value, unit, currency)

                    return {
                        'value': normalized_value,
                        'currency': 'INR',
                        'unit': 'Crores',
                        'original_value': value,
                        'original_unit': unit,
                        'original_currency': currency,
                        'original_text': match.group(0),
                        'confidence': self._calculate_confidence(match.group(0))
                    }
                except (ValueError, IndexError) as e:
                    logger.error(f"Error parsing value: {e}")
                    continue

        return None

    def extract_all_values(self, text: str) -> List[Dict]:
        """
        Extract all monetary values found in text

        Args:
            text: Announcement text to search

        Returns:
            List of value dictionaries
        """
        values = []
        for pattern in self.compiled_patterns:
            for match in pattern.finditer(text):
                try:
                    value_str = match.group(1).replace(',', '')
                    value = float(value_str)
                    unit = match.group(2).lower()
                    currency = self._determine_currency(match.group(0))
                    normalized_value = self._normalize_to_inr_crores(value, unit, currency)

                    values.append({
                        'value': normalized_value,
                        'currency': 'INR',
                        'unit': 'Crores',
                        'original_value': value,
                        'original_unit': unit,
                        'original_currency': currency,
                        'original_text': match.group(0),
                        'position': match.start(),
                        'confidence': self._calculate_confidence(match.group(0))
                    })
                except (ValueError, IndexError) as e:
                    logger.error(f"Error parsing value: {e}")
                    continue

        # Sort by position in text
        return sorted(values, key=lambda x: x['position'])

    def _determine_currency(self, matched_text: str) -> str:
        """Determine currency from matched text"""
        text_lower = matched_text.lower()
        if any(x in text_lower for x in ['usd', 'us$', '$']):
            return 'USD'
        elif 'eur' in text_lower or '€' in text_lower:
            return 'EUR'
        else:
            return 'INR'

    def _normalize_to_inr_crores(self, value: float, unit: str, currency: str) -> float:
        """
        Normalize value to INR crores

        Args:
            value: Numeric value
            unit: Unit (crore, million, billion)
            currency: Currency (INR, USD, EUR)

        Returns:
            Value in INR crores
        """
        # First normalize to crores in original currency
        if 'crore' in unit or 'cr' in unit:
            value_crores = value
        elif 'million' in unit or 'mn' in unit:
            value_crores = value / 10  # 1 crore = 10 million
        elif 'billion' in unit or 'bn' in unit:
            value_crores = value * 100  # 1 billion = 100 crores
        else:
            value_crores = value

        # Convert to INR if needed
        if currency == 'USD':
            value_crores = value_crores * self.USD_TO_INR / 100
        elif currency == 'EUR':
            value_crores = value_crores * self.EUR_TO_INR / 100

        return round(value_crores, 2)

    def _calculate_confidence(self, matched_text: str) -> float:
        """
        Calculate confidence score for extraction (0-1)

        Higher confidence for:
        - Clear currency symbols (Rs., ₹)
        - Standard units (crore, million)
        - Context words (worth, value of)
        """
        confidence = 0.5  # Base confidence

        # Increase confidence for clear patterns
        if any(x in matched_text.lower() for x in ['rs.', '₹', 'inr']):
            confidence += 0.2
        if any(x in matched_text.lower() for x in ['worth', 'value of', 'approximately']):
            confidence += 0.1
        if re.search(r'[\d,]+\.\d{2}', matched_text):  # Has decimals
            confidence += 0.1

        return min(confidence, 1.0)

    def is_order_value_plausible(self, value: float) -> bool:
        """
        Check if extracted value is plausible for an order

        Args:
            value: Value in INR crores

        Returns:
            True if plausible, False otherwise
        """
        # Order values typically range from 1 crore to 1 lakh crore
        # Values outside this range might be errors
        return 0.01 <= value <= 500000


def main():
    """Test the value extractor"""
    extractor = OrderValueExtractor()

    test_cases = [
        "Company awarded contract worth Rs. 500 crore",
        "Secured order of ₹2,500 Cr from government",
        "Won USD 50 million contract",
        "Order book stands at Rs 15,000 crores",
        "TCV of approximately Rs. 1,200.50 crore",
        "Multiple orders: Rs. 100 crore and Rs. 200 crore",
        "$25 million project from US client",
    ]

    print("=== Order Value Extraction Tests ===\n")

    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test}")

        # Extract single value
        result = extractor.extract_value(test)
        if result:
            print(f"  ✓ Extracted: ₹{result['value']} {result['unit']}")
            print(f"    Original: {result['original_text']}")
            print(f"    Confidence: {result['confidence']:.2f}")
            print(f"    Plausible: {extractor.is_order_value_plausible(result['value'])}")
        else:
            print(f"  ✗ No value found")

        # Extract all values
        all_values = extractor.extract_all_values(test)
        if len(all_values) > 1:
            print(f"  → Found {len(all_values)} total values:")
            for val in all_values:
                print(f"      • ₹{val['value']} Cr (from '{val['original_text']}')")

        print()


if __name__ == "__main__":
    main()
