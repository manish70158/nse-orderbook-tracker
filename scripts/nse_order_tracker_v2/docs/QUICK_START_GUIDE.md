# Quick Start Guide - NSE Order Tracker V2

Get up and running in 5 minutes!

---

## Installation (2 minutes)

### Step 1: Clone/Download Files

Download these files to your project directory:
- `nse_web_scraper.py`
- `pdf_parser.py`
- `order_tracker_v2.py`
- `requirements.txt`

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install requests PyPDF2 pdfplumber
```

### Step 3: Verify Installation

```bash
python3 test_pdf_parser.py
```

You should see: `Success rate: 91.7%` (or similar)

---

## First Run (1 minute)

### Quick Test (No PDFs, Fast)

```bash
python3 order_tracker_v2.py --days 7 --no-pdfs
```

This will:
- Fetch announcements from last 7 days
- Search for order keywords
- Skip PDF downloads (faster)
- Save results to `data/orders_data.json`

### Output

```
==============================================================
Starting Order Tracker V2 Daily Scan
==============================================================

Previously processed: 0 orders
Tracking 50 Nifty 50 companies
Fetching announcements (last 7 days)...
Retrieved 45 total announcements
Searching for order-related announcements...
Found 3 order announcements
Filtered to 2 Nifty 50 orders

Processing new order: TCS
✓ TCS: ₹500.0 Cr

Processing new order: LT
✓ LT: ₹2500.0 Cr

==============================================================
Scan Summary
==============================================================
Total announcements: 45
Order announcements: 3
New orders found: 2
Total value: ₹3000.00 Cr
==============================================================
```

---

## Understanding the Output

### 1. JSON Data File

**Location:** `data/orders_data.json`

Contains all order details:

```json
[
  {
    "order_id": "TCS_28-05-2026_...",
    "symbol": "TCS",
    "company_name": "Tata Consultancy Services",
    "announcement_date": "28-05-2026",
    "subject": "Awarding of Order",
    "order_value": 500.0,
    "pdf_url": "https://...",
    "source": "NSE"
  }
]
```

### 2. Daily Report

**Location:** `data/report_20260528.txt`

Human-readable summary:

```
==============================================================
NSE Order Book Tracker V2 - Daily Report
==============================================================
Date: 2026-05-28

SUMMARY
--------------------------------------------------------------
Total Announcements:    45
Order Announcements:    3
New Orders Found:       2
Total Value:            ₹3000.00 Crores

NEW ORDERS
--------------------------------------------------------------
TCS - Tata Consultancy Services
  Date:        28-05-2026
  Value:       ₹500.0 Cr
  Subject:     Awarding of Order - Digital Project
```

### 3. Processed Orders

**Location:** `data/processed_orders.json`

Tracks already-processed orders (prevents duplicates):

```json
[
  "TCS_28-05-2026_123456789",
  "LT_27-05-2026_987654321"
]
```

---

## Common Use Cases

### Use Case 1: Daily Check (Quick)

```bash
python3 order_tracker_v2.py --days 1 --no-pdfs
```

Check today's orders only, no PDF downloads.

### Use Case 2: Weekly Report (Moderate)

```bash
python3 order_tracker_v2.py --days 7
```

Get last 7 days, with PDF parsing for accurate values.

### Use Case 3: Monthly Deep Dive (Comprehensive)

```bash
python3 order_tracker_v2.py --days 30
```

Full 30-day scan with complete PDF analysis.

### Use Case 4: All Companies (Not Just Nifty 50)

```bash
python3 order_tracker_v2.py --all
```

Include all listed companies, not just Nifty 50.

### Use Case 5: Custom Output Location

```bash
python3 order_tracker_v2.py --output my_custom_folder
```

Save data to a different directory.

---

## Reading the Data

### Python

```python
import json

# Load orders
with open('data/orders_data.json', 'r') as f:
    orders = json.load(f)

# Print summary
total_value = sum(order.get('order_value', 0) for order in orders)
print(f"Total orders: {len(orders)}")
print(f"Total value: ₹{total_value:.2f} Cr")

# Group by company
from collections import defaultdict
by_company = defaultdict(list)
for order in orders:
    by_company[order['symbol']].append(order)

for symbol, company_orders in sorted(by_company.items()):
    total = sum(o.get('order_value', 0) for o in company_orders)
    print(f"{symbol}: {len(company_orders)} orders, ₹{total:.2f} Cr")
```

### Excel

```python
import pandas as pd
import json

# Load data
with open('data/orders_data.json', 'r') as f:
    orders = json.load(f)

# Create DataFrame
df = pd.DataFrame(orders)

# Select key columns
df = df[['symbol', 'company_name', 'announcement_date', 'order_value', 'subject']]

# Export
df.to_excel('orders.xlsx', index=False)
print("Exported to orders.xlsx")
```

### Command Line

```bash
# Count orders
cat data/orders_data.json | python3 -c "import json, sys; print(len(json.load(sys.stdin)))"

# Total value
cat data/orders_data.json | python3 -c "import json, sys; orders=json.load(sys.stdin); print(sum(o.get('order_value',0) for o in orders))"
```

---

## Setting Up Automation

### GitHub Actions (Recommended)

1. **Copy workflow file:**
   ```bash
   mkdir -p .github/workflows
   cp nse-order-tracker-v2.yml .github/workflows/
   ```

2. **Setup Telegram (optional):**
   - Create bot with [@BotFather](https://t.me/BotFather)
   - Get bot token and chat ID
   - Add to GitHub Secrets:
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_CHAT_ID`

3. **Enable workflow:**
   - Go to repository Actions tab
   - Enable workflows
   - Workflow runs daily at 9:30 AM IST

4. **Manual trigger:**
   - Actions → NSE Order Tracker V2 → Run workflow

### Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9:30 AM)
30 9 * * * cd /path/to/project && python3 order_tracker_v2.py --days 1
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:30 AM
4. Action: Start a program
   - Program: `python`
   - Arguments: `order_tracker_v2.py --days 1`
   - Start in: `/path/to/project`

---

## Troubleshooting

### Problem: No announcements fetched

**Symptom:**
```
Retrieved 0 total announcements
```

**Cause:** NSE is blocking API access (common)

**Solutions:**
1. Try again later (NSE blocks vary by time/IP)
2. Run from GitHub Actions (better success rate)
3. Check if NSE website is accessible
4. Wait a few hours and retry

### Problem: No order announcements found

**Symptom:**
```
Found 0 order announcements
```

**Cause:** No orders announced in the period, or keywords don't match

**Solutions:**
1. Increase days: `--days 30`
2. Try different time periods
3. Check if any announcements were fetched at all
4. Customize keywords in `nse_web_scraper.py`

### Problem: PDF download fails

**Symptom:**
```
Failed to download PDF: HTTP 403
```

**Cause:** NSE blocking, or PDF not available

**Solutions:**
1. Use `--no-pdfs` to skip PDF downloads
2. Some announcements don't have PDFs (normal)
3. Value extraction from text still works
4. Retry later

### Problem: Value extraction incorrect

**Symptom:** Wrong value or no value extracted

**Solutions:**
1. Check actual announcement manually
2. Values are extracted from text and PDF
3. Parser picks highest value found
4. Add custom regex patterns if needed
5. Some announcements don't mention value

---

## Tips & Best Practices

### 1. Start Small

Begin with `--days 7 --no-pdfs` for quick tests

### 2. Monitor GitHub Actions

Check Actions tab regularly for failures

### 3. Verify Important Values

Always cross-check high-value orders manually

### 4. Use Processed Tracking

Don't delete `processed_orders.json` - it prevents duplicates

### 5. Backup Data

Commit `data/` to git for historical tracking

### 6. Customize Keywords

Add industry-specific terms to search

### 7. Rate Limiting

Don't run multiple instances simultaneously

### 8. Schedule Wisely

Run after market hours (9:30 AM or 6:00 PM IST)

---

## Next Steps

### Level 1: Basic Usage ✓
- [x] Install dependencies
- [x] Run first scan
- [x] View results

### Level 2: Regular Tracking
- [ ] Set up GitHub Actions
- [ ] Configure Telegram notifications
- [ ] Run daily for a week

### Level 3: Analysis
- [ ] Export to Excel
- [ ] Create charts/graphs
- [ ] Track trends over time

### Level 4: Customization
- [ ] Add custom keywords
- [ ] Modify value patterns
- [ ] Integrate with other systems

---

## Common Questions

**Q: How often should I run this?**
A: Daily is sufficient. Orders are announced during market hours.

**Q: Do I need to download PDFs?**
A: No, but PDFs give more accurate values and details.

**Q: Can I run this for older data?**
A: Yes, use `--days 90` or more. NSE typically keeps 30-90 days.

**Q: Why Nifty 50 only?**
A: Focus on large companies. Use `--all` for everyone.

**Q: Is this legal?**
A: Yes, NSE data is public. Respect their ToS and rate limits.

**Q: Will this always work?**
A: NSE may block or change APIs. Maintain and update as needed.

---

## Command Reference

```bash
# Basic scan
python3 order_tracker_v2.py

# Quick test
python3 order_tracker_v2.py --days 7 --no-pdfs

# Full scan
python3 order_tracker_v2.py --days 30

# All companies
python3 order_tracker_v2.py --all

# Custom output
python3 order_tracker_v2.py --output my_data

# Combination
python3 order_tracker_v2.py --days 14 --all --no-pdfs --output weekly_data
```

---

## Help

```bash
python3 order_tracker_v2.py --help
```

Output:
```
usage: order_tracker_v2.py [-h] [--days DAYS] [--all] [--no-pdfs] [--output OUTPUT]

NSE Order Book Tracker V2

optional arguments:
  -h, --help       show this help message and exit
  --days DAYS      Days to look back (default: 30)
  --all            Include all companies (not just Nifty 50)
  --no-pdfs        Skip PDF downloads
  --output OUTPUT  Output directory (default: data)
```

---

**You're all set!** 🎉

For detailed information, see `README.md`

For GitHub Actions setup, see workflow file comments

For customization, see source code comments

Happy tracking! 📊
