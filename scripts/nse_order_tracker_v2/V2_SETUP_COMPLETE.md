# ✅ NSE Order Book Tracker V2 - Setup Complete!

## What's New in V2

### 🎯 Key Improvements

1. **API-Based Scraping** (instead of browser automation)
   - 10x faster than Playwright approach
   - No browser crashes or timeout issues
   - Direct NSE API access: `https://www.nseindia.com/api/corporate-announcements`

2. **3-Day Default Lookback**
   - Changed from 30 days to 3 days for focused monitoring
   - Can be overridden with `--days` flag

3. **Telegram Notifications** ✨
   - Automatically sends alerts for high-value orders (≥₹500 Cr)
   - **NEW:** Attaches PDF files to Telegram messages
   - Filters and groups orders by value threshold
   - Each PDF includes company name and value caption
   - Requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` env variables

4. **Automatic PDF Cleanup** 🧹
   - Deletes PDFs older than 7 days (configurable)
   - Prevents disk space accumulation
   - Runs automatically before each scraping job
   - Logs files deleted and space freed

5. **V1 Workflow Disabled**
   - Old browser automation workflow marked as DISABLED
   - V2 GitHub Actions workflow updated to use API-based scraper

---

## 🚀 How to Use

### Local Execution

#### Basic Usage (3 days, Telegram enabled)
```bash
cd scripts/nse_order_tracker_v2
source venv/bin/activate
python orchestrator.py
```

#### Custom Days
```bash
python orchestrator.py --days 7
```

#### Without Telegram
```bash
python orchestrator.py --no-telegram
```

#### Custom Value Threshold
```bash
python orchestrator.py --threshold 1000  # Only notify for orders ≥₹1000 Cr
```

### Environment Variables

Create a `.env` file or set these in your environment:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

**How to get Telegram credentials:**
1. Create bot: Talk to [@BotFather](https://t.me/botfather) on Telegram
2. Get chat ID: Send a message to your bot, then visit:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```

---

## 📊 View Dashboard

The Flask dashboard is running at:
- **Main Dashboard:** http://localhost:5000
- **API Endpoints:**
  - `/api/data` - All order data (JSON)
  - `/api/summary` - Summary statistics
  - `/api/export` - Download Excel file
  - `/api/health` - Server health check

### Start Dashboard
```bash
cd scripts/nse_order_tracker_v2
source venv/bin/activate
python app.py &
```

### Stop Dashboard
```bash
pkill -f "python app.py"
```

---

## ⚙️ GitHub Actions Automation

### V2 Workflow (Enabled)

File: `.github/workflows/daily-scraper.yml`

**Features:**
- Runs daily at 9:30 AM IST (4:00 AM UTC)
- Uses V2 API-based scraper
- Fetches last 3 days of orders
- Sends Telegram notifications (if secrets configured)
- Uploads artifacts (JSON + Excel)
- Commits updated data to repository

**Required Secrets:**
```
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Add these in: Repository Settings → Secrets and variables → Actions

### V1 Workflow (Disabled)

File: `.github/workflows/daily-order-check.yml`

Status: ❌ DISABLED - replaced by V2 workflow

---

## 📁 Output Files

After running the orchestrator:

```
output/
├── orderbook_data.json     # Full order data with metadata
├── orderbook_data.xlsx     # Excel export with formatted values
└── summary.json            # Summary statistics

downloads/nse_pdfs/
└── COMPANY_YYYY-MM-DD.pdf  # Downloaded PDFs
```

---

## 🧪 Test Results

### Latest Test Run (1 day lookback)

```
✅ API Call: 3 seconds (vs 90+ seconds timeout with Playwright)
✅ Announcements: 1,015 fetched, 1 matched "awarding of order"
✅ PDF Download: LIKHITHA_2026-05-28.pdf (502 KB)
✅ Order Value Extracted: ₹121.04 Crores
✅ JSON/Excel Generated: Success
✅ Telegram: Gracefully disabled (no credentials)
```

**Performance:**
- Total Pipeline Duration: ~3 seconds
- Success Rate: 100%
- Browser Crashes: 0 (API-based approach)

---

## 🔧 Command-Line Options

```bash
python orchestrator.py [OPTIONS]

Options:
  --days INT              Days to look back (default: 3)
  --search TEXT           Search term (default: "awarding of order")
  --threshold FLOAT       Order value threshold in Crores (default: 500)
  --retention-days INT    Days to keep old PDFs before cleanup (default: 7)
  --telegram              Enable Telegram notifications (default: enabled)
  --no-telegram           Disable Telegram notifications
  --output-dir PATH       Output directory (default: output)
  --download-dir PATH     PDF download directory (default: downloads/nse_pdfs)

Examples:
  python orchestrator.py --days 7 --threshold 1000
  python orchestrator.py --search "merger" --no-telegram
  python orchestrator.py --days 1 --output-dir results
  python orchestrator.py --days 3 --retention-days 14  # Keep PDFs for 14 days
```

---

## 🎨 Dashboard Features

### Summary Cards
- Total Announcements (with date range)
- Total Order Value in Crores
- Average Order Size
- Unique Companies count

### Order Details Table
- Company symbol and name
- Announcement date
- Order value with color coding:
  - 🟢 Green: > ₹100 Cr (High)
  - 🟡 Orange: ₹50-100 Cr (Medium)
  - ⚪ Gray: < ₹50 Cr or Not Found (Low)
- Subject/Description
- PDF download status
- Direct PDF links

### Interactive Features
- Hover effects on cards
- Responsive design (works on mobile)
- Refresh button to reload data
- Export to Excel functionality
- Real-time data updates

---

## 📦 Dependencies

See `requirements.txt`:
```
requests
pandas
openpyxl
PyPDF2
pdfplumber
python-telegram-bot
flask
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 🔄 Architecture

```
orchestrator.py
├── nse_playwright_scraper.py (NSEAPIScraper)
│   ├── Fetch announcements from NSE API
│   └── Download PDFs
├── pdf_parser.py (PDFParser)
│   ├── Extract text using pdfplumber
│   └── Parse order values with regex
├── telegram_notifier.py (TelegramNotifier)
│   ├── Filter high-value orders
│   └── Send formatted notifications
└── Output
    ├── JSON files
    ├── Excel files
    └── Summary statistics

app.py (Flask Dashboard)
├── Load data from output/
├── Render HTML template
└── Serve API endpoints
```

---

## 📊 Sample Output

### Console Summary
```
============================================================
ORDER BOOK SUMMARY
============================================================
Total Announcements: 1
Orders with Values: 1
Total Value: ₹121.04 Crores
Average Order: ₹121.04 Crores
Largest Order: ₹121.04 Crores
Unique Companies: 1

Date Range: 2026-05-28 to 2026-05-28

Top Companies by Order Value:
  1. LIKHITHA   ₹121.04 Cr
============================================================
```

### Telegram Notification (if enabled)
```
📊 NSE Order Book Alert - 2026-05-28

High-Value Orders (≥₹500 Cr):
(none - all orders below threshold)

All Orders with Values:
1. LIKHITHA - ₹121.04 Cr
   Awarding of Order announcement
   📅 2026-05-28
   📄 PDF Link
```

---

## 🚦 Status

- ✅ V2 API Scraper: **WORKING**
- ✅ PDF Parser: **WORKING**
- ✅ Excel/JSON Output: **WORKING**
- ✅ Flask Dashboard: **RUNNING** (http://localhost:5000)
- ⚠️ Telegram Notifications: **READY** (needs credentials)
- ✅ GitHub Actions: **CONFIGURED** (needs secrets for Telegram)
- ✅ 3-Day Default: **IMPLEMENTED**
- ✅ V1 Workflow: **DISABLED**

---

## 🎯 Next Steps

1. **Add Telegram Credentials** (optional)
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   ```

2. **Configure GitHub Secrets** (for automation)
   - Go to Repository Settings → Secrets → New repository secret
   - Add `TELEGRAM_BOT_TOKEN`
   - Add `TELEGRAM_CHAT_ID`

3. **Test Daily Automation**
   - Workflow runs automatically at 9:30 AM IST
   - Or trigger manually: Actions tab → Daily NSE Order Book Scraper V2 → Run workflow

4. **Monitor Results**
   - Check dashboard: http://localhost:5000
   - View artifacts: GitHub Actions → Workflow run → Artifacts
   - Receive Telegram alerts for high-value orders

---

**🎉 V2 Setup Complete - Enjoy your automated NSE Order Book Tracker!**

- Dashboard: http://localhost:5000
- Flask Server PID: Check with `ps aux | grep app.py`
- Logs: `flask.log` in the scripts directory
