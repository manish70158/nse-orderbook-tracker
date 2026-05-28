# NSE Order Book Tracker V3 (API-Based) 🚀

**Reliable NSE order announcement tracker using direct API calls** - No browser automation needed!

## What Changed from V2?

**V2 (Playwright):**
- ❌ Browser crashes on macOS
- ❌ Search functionality unreliable
- ❌ Slow and resource-intensive
- ❌ Required browser installation

**V3 (API-Based):**
- ✅ Uses NSE's official API endpoints
- ✅ 10x faster and more reliable
- ✅ No browser needed
- ✅ Handles 20,000+ announcements easily
- ✅ Works on all platforms

## Quick Start

```bash
# Run tracker for last 7 days
python orchestrator.py --days 7

# Run tracker for last 30 days
python orchestrator.py --days 30
```

## What It Does

1. **Fetches** announcements from NSE API (with date range)
2. **Filters** for "awarding of order" announcements
3. **Downloads** PDFs automatically
4. **Parses** PDFs to extract order values in Crores
5. **Generates** Excel + JSON reports

## Example Output

```
============================================================
ORDER BOOK SUMMARY
============================================================
Total Announcements: 4
Orders with Values: 2
Total Value: ₹127.32 Crores
Average Order: ₹63.66 Crores
Largest Order: ₹121.04 Crores

Date Range: 2026-05-25 to 2026-05-28

Top Companies by Order Value:
  1. LIKHITHA   ₹121.04 Cr
  2. ACMESOLAR  ₹6.28 Cr
============================================================
```

## Installation

```bash
# Install dependencies (no Playwright needed!)
pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- requests (for API calls)
- pandas (for Excel export)
- PyPDF2 / pdfplumber (for PDF parsing)
- openpyxl (for Excel generation)

## Command Line Options

```bash
python orchestrator.py \
    --days 30 \              # Days to look back (default: 30)
    --search "awarding" \    # Search term (default: "awarding of order")
    --threshold 500 \        # Alert threshold in Crores (default: 500)
    --output-dir output \    # Output directory (default: output)
    --download-dir downloads # PDF directory (default: downloads/nse_pdfs)
```

## Output Files

All generated in `output/` directory:
- `orderbook_data.json` - Complete data in JSON format
- `orderbook_data.xlsx` - Excel spreadsheet with formatting
- `summary.json` - Summary statistics

## API Details

**Endpoint:** `https://www.nseindia.com/api/corporate-announcements`

**Parameters:**
- `index=equities` - Fetch equity announcements
- `from_date=DD-MM-YYYY` - Start date
- `to_date=DD-MM-YYYY` - End date

**Authentication:** Requires session cookies from NSE website (handled automatically)

## Troubleshooting

**"API returned status 403"**
- The scraper automatically gets fresh cookies - just retry

**"No announcements found"**
- Try increasing `--days` parameter
- Check if NSE website is accessible

**"PDF parsing failed"**
- Some PDFs may have non-standard formats
- Check `local_pdf_path` in JSON output to verify download

## Performance

- Fetches 20,000+ announcements in ~3 seconds
- Downloads PDFs concurrently
- Processes entire pipeline in < 30 seconds

## Future Enhancements

- [ ] Telegram notifications for large orders
- [ ] Dashboard with Flask/Streamlit
- [ ] Historical trend analysis
- [ ] GitHub Actions automation
- [ ] Email alerts

## Credits

Built using:
- NSE India Corporate Filings API
- Python requests library
- pdfplumber for PDF text extraction

---

**Note:** This tool is for educational and research purposes. Always comply with NSE's terms of service.
