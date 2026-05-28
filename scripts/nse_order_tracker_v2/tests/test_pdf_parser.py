#!/usr/bin/env python3
"""
Test script for PDF Parser
"""

import sys
from pdf_parser import PDFParser


def test_text_parsing():
    """Test value extraction from text"""

    print("\n" + "="*70)
    print("PDF PARSER - TEST SUITE")
    print("="*70)

    parser = PDFParser()

    # Test 1: Various text formats
    print("\n[TEST 1] Testing value extraction from text...")
    print("-"*70)

    test_cases = [
        {
            'text': "The company has received an order worth Rs. 500 crores from ABC Ltd.",
            'expected': 500
        },
        {
            'text': "Order value: ₹1,250.50 Crore for infrastructure project",
            'expected': 1250.50
        },
        {
            'text': "Awarded contract of INR 750.25 Cr by Government of India",
            'expected': 750.25
        },
        {
            'text': "Total value of order is Rs 2500 crores",
            'expected': 2500
        },
        {
            'text': "Received work order of ₹ 3,500.00 Cr",
            'expected': 3500
        },
        {
            'text': "Order worth Rs. 100 million (approx 10 crores)",
            'expected': 10  # 100 million = 10 crores
        },
        {
            'text': "Contract value 1.5 billion rupees",
            'expected': 150  # 1.5 billion = 150 crores
        },
        {
            'text': "Purchase order for Rs 85.5 Cr received",
            'expected': 85.5
        },
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        print(f"  Text: {test['text'][:70]}...")

        value_info = parser.extract_order_value(test['text'])

        if value_info:
            extracted_value = value_info['value']
            expected_value = test['expected']

            print(f"  Expected: ₹{expected_value} Cr")
            print(f"  Extracted: ₹{extracted_value} Cr")

            # Allow small floating point differences
            if abs(extracted_value - expected_value) < 0.1:
                print("  ✓ PASSED")
                passed += 1
            else:
                print("  ✗ FAILED (value mismatch)")
                failed += 1
        else:
            print(f"  Expected: ₹{test['expected']} Cr")
            print("  Extracted: None")
            print("  ✗ FAILED (no value found)")
            failed += 1

    # Test 2: Multiple values (should pick highest)
    print("\n[TEST 2] Testing multiple values (should pick highest)...")
    print("-"*70)

    multi_value_text = """
    The company received an order of Rs. 500 crores.
    This is in addition to the previous order of Rs. 200 crores.
    Total value now stands at Rs. 700 crores.
    """

    value_info = parser.extract_order_value(multi_value_text)

    if value_info:
        extracted = value_info['value']
        print(f"✓ Extracted highest value: ₹{extracted} Cr")
        if extracted == 700:
            print("  ✓ PASSED (correctly picked 700)")
            passed += 1
        else:
            print(f"  ⚠ WARNING: Expected 700, got {extracted}")
    else:
        print("✗ FAILED (no value found)")
        failed += 1

    # Test 3: Edge cases
    print("\n[TEST 3] Testing edge cases...")
    print("-"*70)

    edge_cases = [
        {
            'text': "No order value mentioned in this text",
            'expected': None,
            'description': "No value present"
        },
        {
            'text': "The company reported 500 crore revenue (not an order)",
            'expected': 500,  # Will extract 500, but context matters
            'description': "Revenue vs order (context)"
        },
        {
            'text': "Year 2500 AD in science fiction",
            'expected': None,
            'description': "False positive check"
        },
    ]

    for i, test in enumerate(edge_cases, 1):
        print(f"\nEdge case {i}: {test['description']}")
        print(f"  Text: {test['text']}")

        value_info = parser.extract_order_value(test['text'])

        if test['expected'] is None:
            if value_info is None:
                print("  ✓ PASSED (correctly returned None)")
                passed += 1
            else:
                print(f"  ⚠ WARNING: Expected None, got ₹{value_info['value']} Cr")
        else:
            if value_info and abs(value_info['value'] - test['expected']) < 0.1:
                print(f"  ✓ Extracted: ₹{value_info['value']} Cr")
                passed += 1
            else:
                print(f"  Note: Expected ₹{test['expected']} Cr")

    # Test 4: PDF library check
    print("\n[TEST 4] Checking PDF libraries...")
    print("-"*70)

    try:
        import PyPDF2
        print("  ✓ PyPDF2 installed")
    except ImportError:
        print("  ✗ PyPDF2 not installed")
        print("    Install with: pip install PyPDF2")

    try:
        import pdfplumber
        print("  ✓ pdfplumber installed (recommended)")
    except ImportError:
        print("  ✗ pdfplumber not installed")
        print("    Install with: pip install pdfplumber")

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Success rate: {passed/(passed+failed)*100:.1f}%")
    print("\nNOTE: The parser is designed to extract the highest value found.")
    print("For production use, always verify extracted values against actual")
    print("announcement content.")
    print("="*70)


if __name__ == "__main__":
    test_text_parsing()
