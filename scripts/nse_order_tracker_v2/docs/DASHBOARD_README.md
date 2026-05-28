# 📊 NSE Order Book Tracker with Playwright

**Complete automated solution for scraping, parsing, and visualizing NSE corporate order announcements**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![Playwright](https://img.shields.io/badge/Playwright-1.40-green?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## ✨ Features

### 🤖 **Automated Web Scraping**
- Uses Playwright to navigate NSE corporate announcements page
- Searches for "awarding of order" announcements
- Handles dynamic JavaScript content
- Bypasses bot detection
- Downloads PDFs automatically

### 📄 **Intelligent PDF Parsing**
- Extracts order values (Rs. X Crores)
- Identifies client names
- Extracts project descriptions
- Finds order dates and completion periods
- Multiple extraction methods (PyPDF2 + pdfplumber)

### 📊 **Beautiful Dashboard**
- Modern dark-themed interface
- Interactive data tables with search/sort
- Visual charts (Chart.js)
- Timeline view of announcements
- Company-wise aggregation
- Excel export functionality

### ⚙️ **GitHub Actions Automation**
- Runs daily at 9:30 AM IST
- Automatically commits updated data
- Saves historical data
- Sends notifications on failure

### 💾 **Excel Export**
- One-click download of all data
- Properly formatted columns
- Includes all extracted information
- Date-stamped filenames

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd nse-orderbook-tracker

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Run the Scraper

```bash
# Run complete pipeline (scraping + parsing + saving)
python orchestrator.py

# This will:
# - Scrape NSE announcements
# - Download PDFs
# - Extract order values
# - Save to output/orderbook_data.json
# - Save to output/orderbook_data.xlsx
# - Generate summary statistics
```

### 3. Start the Dashboard

```bash
# Start Flask server
python app.py

# Open browser
open http://localhost:5000
```

That's it! Your dashboard will display all scraped data.

---

## 📁 Project Structure

```
nse-orderbook-tracker/
│
├── nse_playwright_scraper.py   # Main scraper (Playwright)
├── pdf_parser.py                # PDF extraction logic
├── orchestrator.py              # Pipeline coordinator
├── app.py                       # Flask API server
├── dashboard.html               # Frontend interface
├── requirements.txt             # Python dependencies
│
├── .github/workflows/
│   └── daily-scraper.yml        # GitHub Actions automation
│
├── downloads/
│   └── nse_pdfs/               # Downloaded PDFs
│
├── output/
│   ├── orderbook_data.json     # Scraped + parsed data
│   ├── orderbook_data.xlsx     # Excel export
│   └── summary.json            # Statistics
│
├── test_scraper.py             # Scraper tests
├── test_pdf_parser.py          # Parser tests
│
└── README.md                   # This file
```

---

## 🔧 How It Works

### Step 1: Web Scraping (Playwright)

```python
from nse_playwright_scraper import NSEPlaywrightScraper

scraper = NSEPlaywrightScraper(download_dir='downloads/nse_pdfs')

announcements = await scraper.scrape(
    search_term="awarding of order",
    days_back=30,
    download_pdfs=True,
    headless=True
)
```

**What it does:**
1. Launches Chromium browser
2. Navigates to NSE corporate announcements page
3. Finds search input with class `subjectAutoComplete`
4. Enters "awarding of order" and presses Enter
5. Waits for results table to load
6. Extracts company symbol, name, date, subject, PDF link
7. Downloads PDFs for each announcement
8. Returns structured data

### Step 2: PDF Parsing

```python
from pdf_parser import PDFParser

parser = PDFParser()
order_info = parser.parse_pdf('path/to/announcement.pdf')

print(f"Order Value: ₹{order_info.order_value} Cr")
print(f"Client: {order_info.client_name}")
print(f"Project: {order_info.project_description}")
```

**What it extracts:**
- Order values in various formats:
  - Rs. 500 Crores
  - Rs 500 Cr
  - 5,00,000 Lakhs
  - 500 Million
- Client/customer names
- Project descriptions
- Order dates
- Completion periods

### Step 3: Data Orchestration

```python
from orchestrator import OrderBookOrchestrator

orchestrator = OrderBookOrchestrator()

await orchestrator.run(
    search_term="awarding of order",
    days_back=30,
    headless=True
)
```

**What it does:**
1. Runs scraper → gets announcements
2. Runs parser → extracts order values from PDFs
3. Combines data → merges scraping + parsing results
4. Saves JSON → `output/orderbook_data.json`
5. Saves Excel → `output/orderbook_data.xlsx`
6. Generates summary → statistics and aggregations

### Step 4: Dashboard Visualization

```python
# Start Flask server
python app.py
```

**Dashboard features:**
- **Overview Tab**: Top companies chart, recent activity
- **Companies Tab**: Aggregated data by company, sortable table
- **Timeline Tab**: Chronological view of announcements
- **All Data Tab**: Complete dataset with search/filter

**API Endpoints:**
- `GET /api/data` - All order data
- `GET /api/summary` - Company aggregations
- `GET /api/timeline` - Recent orders
- `GET /api/stats` - Dashboard statistics
- `GET /api/export` - Download Excel
- `GET /api/health` - Health check

---

## 🤖 GitHub Actions Automation

### Setup

1. **Copy workflow file:**
   ```bash
   mkdir -p .github/workflows
   cp daily-scraper.yml .github/workflows/
   ```

2. **Enable GitHub Actions:**
   - Go to repository → Actions tab
   - Enable workflows

3. **Set up secrets (optional):**
   - For Telegram notifications, email alerts, etc.

### What it does

**Runs daily at 9:30 AM IST:**
1. Checks out repository
2. Installs Python + dependencies
3. Installs Playwright + Chromium
4. Runs `orchestrator.py`
5. Saves results to `output/`
6. Commits and pushes updated data
7. Uploads artifacts (JSON/Excel files)

**Manual trigger:**
- Go to Actions → Daily NSE Order Book Scraper → Run workflow

---

## 📊 Dashboard Screenshots

### Overview Tab
- Statistics cards (Total Orders, Total Value, etc.)
- Bar chart showing top companies
- Recent activity feed

### Companies Tab
- Sortable table with company aggregations
- Total orders per company
- Total and average order values

### Timeline Tab
- Chronological timeline view
- Visual timeline with order details
- Quick scanning of recent announcements

### All Data Tab
- Complete dataset in table format
- Search, sort, filter capabilities
- Excel export button

---

## 🧪 Testing

### Test Scraper

```bash
# Full test (with browser visible)
python test_scraper.py

# Quick test (headless)
python test_scraper.py --quick
```

**Tests:**
- Browser initialization
- Page navigation
- Search functionality
- Data extraction
- PDF downloads

### Test PDF Parser

```bash
# Test extraction patterns
python test_pdf_parser.py

# Test specific PDF
python test_pdf_parser.py --pdf path/to/file.pdf

# Run all tests
python test_pdf_parser.py --all
```

**Tests:**
- Value extraction (various formats)
- Client name extraction
- Project description extraction
- Date extraction
- Full PDF parsing

---

## ⚙️ Configuration

### Change Search Term

Edit `orchestrator.py`:
```python
await orchestrator.run(
    search_term="contract awarded",  # Changed
    days_back=30,
    headless=True
)
```

### Change Download Directory

```python
scraper = NSEPlaywrightScraper(
    download_dir='my_custom_dir/pdfs'
)
```

### Change Flask Port

Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Changed
```

### Adjust Schedule

Edit `.github/workflows/daily-scraper.yml`:
```yaml
schedule:
  # Run at 6:00 AM UTC (11:30 AM IST)
  - cron: '0 6 * * *'
```

---

## 📦 Dependencies

```
# Core
flask==3.0.0
flask-cors==4.0.0
pandas==2.1.4
openpyxl==3.1.2

# Web Scraping
playwright==1.40.0
beautifulsoup4==4.12.2

# PDF Processing
PyPDF2==3.0.1
pdfplumber==0.10.3

# Utilities
requests==2.31.0
python-dateutil==2.8.2
python-dotenv==1.0.0
```

Install all:
```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 🐛 Troubleshooting

### "Playwright not found"
```bash
playwright install chromium
playwright install-deps  # On Linux
```

### "No announcements found"
- Check NSE website is accessible
- Try running with `headless=False` to see browser
- Verify search term matches NSE announcements

### "PDF extraction failed"
- Ensure PDF is not corrupted
- Check PDF is not image-based (OCR not supported)
- Try different PDF libraries

### "Dashboard shows no data"
- Run `orchestrator.py` first to generate data
- Check `output/orderbook_data.json` exists
- Restart Flask server: `python app.py`

### "Port 5000 already in use"
```bash
# Find process using port
lsof -i :5000

# Kill it
kill -9 <PID>

# Or change port in app.py
```

---

## 📈 Data Format

### Announcement Schema

```json
{
  "symbol": "TCS",
  "company_name": "Tata Consultancy Services",
  "announcement_date": "2024-05-15",
  "subject": "Awarding of Order - Digital Transformation",
  "pdf_url": "https://nseindia.com/...",
  "local_pdf_path": "downloads/nse_pdfs/TCS_2024-05-15.pdf",
  "order_value_crores": 500.0,
  "order_value_text": "Rs. 500 Crores",
  "client_name": "Government of India",
  "project_description": "Digital transformation project",
  "order_date": "15-May-2024",
  "completion_period": "24 months",
  "confidence_score": 0.85,
  "source": "NSE_Playwright"
}
```

---

## 🚀 Deployment

### Local Development
```bash
python app.py
# Access at http://localhost:5000
```

### Heroku
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create nse-orderbook
git push heroku main
```

### Railway / Render
1. Connect GitHub repository
2. Auto-detected as Flask app
3. Click deploy
4. Set environment variables if needed

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps
COPY . .
CMD ["python", "app.py"]
```

```bash
docker build -t nse-orderbook .
docker run -p 5000:5000 nse-orderbook
```

---

## 📝 Usage Examples

### Basic Scraping
```python
import asyncio
from nse_playwright_scraper import NSEPlaywrightScraper

async def main():
    scraper = NSEPlaywrightScraper()
    data = await scraper.scrape(
        search_term="awarding of order",
        days_back=7,
        headless=True
    )
    print(f"Found {len(data)} announcements")

asyncio.run(main())
```

### Parse Multiple PDFs
```python
from pdf_parser import PDFParser
from pathlib import Path

parser = PDFParser()
pdf_files = list(Path('downloads/nse_pdfs').glob('*.pdf'))

results = parser.parse_multiple_pdfs([str(p) for p in pdf_files])

for pdf_path, order_info in results.items():
    if order_info.order_value:
        print(f"{Path(pdf_path).name}: ₹{order_info.order_value:.2f} Cr")
```

### API Integration
```python
import requests

# Get all data
response = requests.get('http://localhost:5000/api/data')
data = response.json()

print(f"Total orders: {data['count']}")

# Export to Excel
excel_url = 'http://localhost:5000/api/export'
with open('orderbook.xlsx', 'wb') as f:
    f.write(requests.get(excel_url).content)
```

---

## 🎯 Roadmap

- [x] Playwright-based scraping
- [x] PDF value extraction
- [x] Interactive dashboard
- [x] Excel export
- [x] GitHub Actions automation
- [ ] BSE integration
- [ ] Email notifications
- [ ] Telegram bot
- [ ] Historical trend analysis
- [ ] ML-based value prediction
- [ ] Multi-language support
- [ ] Mobile app

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Credits

**Built with:**
- [Playwright](https://playwright.dev/) - Browser automation
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Chart.js](https://www.chartjs.org/) - Charts
- [DataTables](https://datatables.net/) - Interactive tables
- [PyPDF2](https://pypdf2.readthedocs.io/) - PDF processing
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF text extraction

**Data from:**
- [NSE India](https://www.nseindia.com/) - Corporate announcements

---

## 📞 Support

Having issues? Please:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search [existing issues](../../issues)
3. Create a new issue with:
   - Error message
   - Steps to reproduce
   - System info (OS, Python version)

---

## ⭐ Star History

If you find this project useful, please give it a star!

---

**Version:** 1.0.0
**Last Updated:** 2026-05-28
**Status:** ✅ Production Ready

---

Made with ❤️ for the trading community
