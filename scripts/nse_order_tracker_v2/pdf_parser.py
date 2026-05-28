#!/usr/bin/env python3
"""
PDF Parser
Extracts order details from announcement PDFs
"""

import re
import logging
from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class OrderInfo:
    """Structured order information extracted from PDFs"""
    company_name: Optional[str] = None
    order_value: Optional[float] = None
    order_value_text: Optional[str] = None
    currency: str = 'INR'
    client_name: Optional[str] = None
    project_description: Optional[str] = None
    order_date: Optional[str] = None
    completion_period: Optional[str] = None
    confidence_score: float = 0.0

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
    PDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    logger.warning("pdfplumber not installed. Install with: pip install pdfplumber")
    PDFPLUMBER_AVAILABLE = False


class PDFParser:
    """Extracts order details from PDF files"""

    def __init__(self):
        self.value_patterns = self._compile_value_patterns()

    def _compile_value_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for value extraction"""

        patterns = [
            # ₹ XXX Crore(s)
            r'₹\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:crore|cr|crores)',

            # Rs. XXX Crore(s)
            r'rs\.?\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:crore|cr|crores)',

            # INR XXX Crore(s)
            r'inr\s*([0-9,]+(?:\.[0-9]+)?)\s*(?:crore|cr|crores)',

            # XXX Crore(s) (standalone)
            r'([0-9,]+(?:\.[0-9]+)?)\s*(?:crore|cr|crores)',

            # Worth/Value of ₹ XXX
            r'(?:worth|value|amount).*?₹\s*([0-9,]+(?:\.[0-9]+)?)',

            # Contract value of Rs. XXX
            r'(?:contract|order|value).*?rs\.?\s*([0-9,]+(?:\.[0-9]+)?)',

            # XXX Million/Billion (will convert to crores)
            r'([0-9,]+(?:\.[0-9]+)?)\s*(?:million|mn)',
            r'([0-9,]+(?:\.[0-9]+)?)\s*(?:billion|bn)',
        ]

        return [re.compile(p, re.IGNORECASE) for p in patterns]

    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None
        """

        # Try pdfplumber first (better extraction)
        if PDFPLUMBER_AVAILABLE:
            try:
                import pdfplumber
                text = ""
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                logger.info(f"Extracted {len(text)} characters using pdfplumber")
                return text
            except Exception as e:
                logger.error(f"pdfplumber extraction failed: {e}")

        # Fallback to PyPDF2
        if PDF_AVAILABLE:
            try:
                text = ""
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                logger.info(f"Extracted {len(text)} characters using PyPDF2")
                return text
            except Exception as e:
                logger.error(f"PyPDF2 extraction failed: {e}")

        logger.error("No PDF library available for extraction")
        return None

    def extract_order_value(self, text: str) -> Optional[Dict]:
        """
        Extract order value from text

        Args:
            text: Text to analyze

        Returns:
            Dictionary with value info or None
        """

        if not text:
            return None

        # Clean text
        text = text.lower()
        text = text.replace('\n', ' ')

        best_match = None
        highest_value = 0

        for pattern in self.value_patterns:
            matches = pattern.findall(text)

            for match in matches:
                # Clean the matched value
                value_str = str(match).replace(',', '').strip()

                try:
                    value = float(value_str)

                    # Convert million/billion to crores
                    if 'million' in pattern.pattern or 'mn' in pattern.pattern:
                        value = value / 10  # 1 million = 0.1 crore
                    elif 'billion' in pattern.pattern or 'bn' in pattern.pattern:
                        value = value * 100  # 1 billion = 100 crore

                    # Keep the highest value found
                    if value > highest_value:
                        highest_value = value
                        best_match = {
                            'value': round(value, 2),
                            'value_str': f"₹{value:.2f} Cr",
                            'pattern': pattern.pattern,
                            'original': match
                        }

                except (ValueError, TypeError):
                    continue

        if best_match:
            logger.info(f"Extracted value: ₹{best_match['value']} Cr")

        return best_match

    def extract_order_details(self, pdf_path: str) -> Dict:
        """
        Extract comprehensive order details from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with extracted details
        """

        result = {
            'pdf_path': pdf_path,
            'extraction_date': datetime.now().isoformat(),
            'success': False,
            'text': None,
            'order_value': None,
            'client_name': None,
            'project_name': None,
            'order_date': None,
            'delivery_date': None,
            'location': None,
            'summary': None
        }

        # Extract text
        text = self.extract_text_from_pdf(pdf_path)

        if not text:
            logger.error("Failed to extract text from PDF")
            return result

        result['text'] = text
        result['success'] = True

        # Extract order value
        value_info = self.extract_order_value(text)
        if value_info:
            result['order_value'] = value_info['value']

        # Extract client name (common patterns)
        client_patterns = [
            r'(?:client|customer|awarded by)[\s:]+([A-Z][A-Za-z\s&,.-]+?)(?:\.|,|\n)',
            r'(?:from|with)[\s]+([A-Z][A-Za-z\s&,.-]+?)(?:for|worth)',
        ]

        for pattern in client_patterns:
            match = re.search(pattern, text[:2000], re.IGNORECASE)
            if match:
                result['client_name'] = match.group(1).strip()
                break

        # Extract project name
        project_patterns = [
            r'(?:project|work)[\s:]+([A-Z][A-Za-z\s&,.-]+?)(?:\.|,|\n)',
            r'(?:for|regarding)[\s]+([A-Za-z\s&,.-]+?)(?:worth|value)',
        ]

        for pattern in project_patterns:
            match = re.search(pattern, text[:2000], re.IGNORECASE)
            if match:
                result['project_name'] = match.group(1).strip()
                break

        # Extract dates
        date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})',
        ]

        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text[:2000], re.IGNORECASE)
            dates_found.extend(matches)

        if dates_found:
            result['order_date'] = dates_found[0]

        # Generate summary (first 500 characters)
        summary = text[:500].replace('\n', ' ')
        summary = re.sub(r'\s+', ' ', summary).strip()
        result['summary'] = summary

        logger.info(f"Extracted details from {pdf_path}")
        logger.info(f"  Value: ₹{result['order_value']} Cr" if result['order_value'] else "  Value: Not found")
        logger.info(f"  Client: {result['client_name']}" if result['client_name'] else "  Client: Not found")

        return result

    def parse_text_for_value(self, text: str) -> Optional[float]:
        """
        Quick parse for value only (no PDF needed)

        Args:
            text: Text to parse

        Returns:
            Value in crores or None
        """

        value_info = self.extract_order_value(text)
        return value_info['value'] if value_info else None

    def parse_pdf(self, pdf_path: str) -> OrderInfo:
        """
        Parse PDF and return OrderInfo object (for orchestrator compatibility)

        Args:
            pdf_path: Path to PDF file

        Returns:
            OrderInfo object with extracted data
        """
        try:
            # Use existing extract_order_details method
            details = self.extract_order_details(pdf_path)

            # Convert dict to OrderInfo object
            order_info = OrderInfo(
                order_value=details.get('order_value'),
                order_value_text=details.get('value_text'),
                client_name=details.get('client_name'),
                project_description=details.get('summary'),
                order_date=details.get('order_date'),
                confidence_score=0.7 if details.get('order_value') else 0.0
            )

            return order_info

        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {e}")
            return OrderInfo()

    def parse_multiple_pdfs(self, pdf_paths: List[str]) -> Dict[str, OrderInfo]:
        """
        Parse multiple PDFs (for orchestrator compatibility)

        Args:
            pdf_paths: List of PDF file paths

        Returns:
            Dictionary mapping PDF path to OrderInfo
        """
        from pathlib import Path

        results = {}

        for pdf_path in pdf_paths:
            if not Path(pdf_path).exists():
                logger.warning(f"PDF not found: {pdf_path}")
                results[pdf_path] = OrderInfo()
                continue

            order_info = self.parse_pdf(pdf_path)
            results[pdf_path] = order_info

        return results


def main():
    """Test the PDF parser"""

    parser = PDFParser()

    # Test text parsing
    print("\n" + "="*60)
    print("TEST 1: Text parsing")
    print("="*60)

    test_texts = [
        "The company has received an order worth Rs. 500 crores from ABC Ltd.",
        "Order value: ₹1,250.50 Crore for infrastructure project",
        "Awarded contract of INR 750.25 Cr by Government of India",
        "Total value of order is Rs 2500 crores",
        "Contract worth $50 million (approx Rs 400 crores)",
    ]

    for text in test_texts:
        print(f"\nText: {text}")
        value_info = parser.extract_order_value(text)
        if value_info:
            print(f"  Extracted: ₹{value_info['value']} Cr")
            print(f"  Pattern: {value_info['pattern']}")
        else:
            print("  No value found")

    # Test PDF parsing (if PDF libraries are available)
    if PDF_AVAILABLE or PDFPLUMBER_AVAILABLE:
        print("\n" + "="*60)
        print("TEST 2: PDF parsing")
        print("="*60)
        print("PDF libraries available. Ready to parse PDF files.")
        print("\nUsage:")
        print("  parser = PDFParser()")
        print("  details = parser.extract_order_details('path/to/announcement.pdf')")
        print("  print(f\"Order value: ₹{details['order_value']} Cr\")")
    else:
        print("\n" + "="*60)
        print("NOTICE: PDF libraries not available")
        print("="*60)
        print("Install with:")
        print("  pip install PyPDF2 pdfplumber")


if __name__ == "__main__":
    main()
