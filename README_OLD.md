# 📊 NSE/BSE Order Book Tracker

**Automated stock market order announcement monitoring system with Telegram notifications**

Track high-value corporate order announcements from NSE and BSE exchanges in real-time. Get instant Telegram alerts when companies receive significant orders.

---

## 🎯 What Does This Do?

This system automatically:
1. ✅ Fetches daily corporate announcements from BSE and NSE
2. ✅ Filters for order-related announcements (new orders, order wins, contracts)
3. ✅ Extracts order values (in ₹ Crores)
4. ✅ Sends consolidated Telegram notifications
5. ✅ Runs daily via GitHub Actions (fully automated)

**Perfect for:** Investors, traders, and analysts tracking order book momentum in stocks.

---

## ✨ Features

- **Multi-Source Data**: Fetches from BSE (primary) with NSE fallback
- **Smart Filtering**: Identifies order announcements using keywords
- **Value Extraction**: Automatically extracts order values (₹X Cr, ₹X Lakh)
- **Telegram Integration**: Real-time mobile notifications
- **GitHub Actions**: Set-and-forget daily automation
- **Visual Dashboard**: Interactive HTML dashboard with charts
- **Mock Data Testing**: Test without hitting live APIs

---

## 📋 Prerequisites

- **Python 3.8+** (Python 3.9 or 3.10 recommended)
- **Telegram Account** (for notifications)
- **GitHub Account** (optional, for automation)
- **Internet Connection** (for API access)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone or Download the Project

```bash
# If you have git
git clone https://github.com/yourusername/28-May-2026OrderBook.git
cd 28-May-2026OrderBook

# Or download and extract the ZIP file, then navigate to the folder
```

### Step 2: Set Up Python Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependencies installed:**
- `flask` - Web framework
- `requests` - HTTP requests
- `pandas` - Data processing
- `bse` - BSE India API wrapper
- `pdfplumber`, `PyPDF2` - PDF processing
- `schedule` - Task scheduling
- `sqlalchemy` - Database support

### Step 4: Set Up Telegram Bot

You need a Telegram bot to receive notifications. Follow the detailed guide in [TELEGRAM_SETUP_GUIDE.md](TELEGRAM_SETUP_GUIDE.md).

**Quick version:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the **Bot Token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Send a message to your new bot
5. Get your **Chat ID** by visiting: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
6. Look for `"chat":{"id":123456789}` in the response

### Step 5: Configure Environment Variables

Create a `.env` file in the project root (or set environment variables):

```bash
# Create .env file
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
EOF
```

**Or export them directly in your terminal:**

**macOS/Linux:**
```bash
export TELEGRAM_BOT_TOKEN='123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
export TELEGRAM_CHAT_ID='123456789'
```

**Windows (Command Prompt):**
```cmd
set TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
set TELEGRAM_CHAT_ID=123456789
```

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
$env:TELEGRAM_CHAT_ID = "123456789"
```

---

## 🎮 Running Locally

### Option 1: Test with Mock Data (Recommended First)

Test the system without hitting live APIs:

```bash
cd scripts
python demo_with_mock_data.py
```

**Expected output:**
- Simulates fetching announcements
- Demonstrates filtering logic
- Shows Telegram notification format
- No actual API calls made

### Option 2: Run Live Order Check

Fetch real data from BSE/NSE and send Telegram notifications:

```bash
cd scripts
python daily_order_checker.py
```

**What happens:**
1. Fetches today's announcements from BSE
2. Falls back to NSE if BSE fails
3. Filters for order-related announcements
4. Extracts order values
5. Sends Telegram notification with results
6. Logs activity to console

**Sample console output:**
```
2026-05-28 10:30:15 - INFO - Fetching announcements from BSE...
2026-05-28 10:30:18 - INFO - BSE fetch successful: 45 announcements
2026-05-28 10:30:18 - INFO - Filtering for order announcements...
2026-05-28 10:30:18 - INFO - Found 3 order announcements
2026-05-28 10:30:18 - INFO - Extracting order values...
2026-05-28 10:30:19 - INFO - Sending Telegram notification...
2026-05-28 10:30:20 - INFO - ✅ Notification sent successfully!
```

### Option 3: Test Individual Components

**Test BSE integration:**
```bash
cd scripts
python test_bse_integration.py
```

**Test unified data fetcher:**
```bash
cd scripts
python -c "from unified_data_fetcher import get_order_announcements; print(get_order_announcements())"
```

**Test Telegram notifications:**
```bash
cd scripts
python -c "from telegram_notifier import send_notification; send_notification('Test message from Order Book Tracker!')"
```

---

## 📊 View the Dashboard

Open the interactive HTML dashboard to visualize data:

**macOS:**
```bash
open dashboard.html
```

**Linux:**
```bash
xdg-open dashboard.html
```

**Windows:**
```cmd
start dashboard.html
```

**Or:** Simply double-click `dashboard.html` in your file explorer.

The dashboard shows:
- 📈 Order announcement trends
- 📊 Company-wise distribution
- 💰 Order value summaries
- 📅 Daily tracking charts

---

## 🤖 Automated Daily Runs (GitHub Actions)

Set up fully automated daily checks that run in the cloud:

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: NSE/BSE Order Book Tracker"
git branch -M main
git remote add origin https://github.com/yourusername/28-May-2026OrderBook.git
git push -u origin main
```

### Step 2: Add Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add two secrets:
   - Name: `TELEGRAM_BOT_TOKEN` | Value: `your_bot_token`
   - Name: `TELEGRAM_CHAT_ID` | Value: `your_chat_id`

### Step 3: Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow will run automatically every day at 7:30 PM IST

### Step 4: Manual Trigger (Optional)

To run immediately:
1. Go to **Actions** tab
2. Click **"Daily Order Book Check"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait 30-60 seconds for the notification on Telegram

**Workflow schedule:**
- Runs daily at **7:30 PM IST** (2:00 PM UTC)
- Configured in `.github/workflows/daily-order-check.yml`
- Completely free on GitHub's runners

---

## 📂 Project Structure

```
28-May-2026OrderBook/
├── 📄 README.md                          ← You are here!
├── 📄 requirements.txt                   ← Python dependencies
├── 📄 dashboard.html                     ← Interactive dashboard
│
├── 📚 Documentation/
│   ├── BSE_INTEGRATION_GUIDE.md         ← How BSE integration works
│   ├── DEPLOYMENT_GUIDE.md              ← Detailed deployment guide
│   ├── IMPLEMENTATION_SUMMARY.md        ← Technical architecture
│   ├── TELEGRAM_SETUP_GUIDE.md          ← Telegram bot setup
│   └── PROJECT_STRUCTURE.md             ← File organization
│
├── 🐍 Scripts/
│   ├── daily_order_checker.py           ← Main orchestrator
│   ├── unified_data_fetcher.py          ← Multi-source data fetching
│   ├── bse_data_fetcher.py              ← BSE API integration
│   ├── nse_data_fetcher.py              ← NSE API integration
│   ├── telegram_notifier.py             ← Telegram notifications
│   ├── value_extractor.py               ← Extract order values
│   ├── test_bse_integration.py          ← Test suite
│   └── demo_with_mock_data.py           ← Mock data testing
│
└── 🤖 GitHub Actions/
    └── .github/workflows/
        └── daily-order-check.yml         ← Automation workflow
```

---

## 🛠️ Configuration Options

### Customizing the Workflow Schedule

Edit `.github/workflows/daily-order-check.yml`:

```yaml
on:
  schedule:
    - cron: '0 14 * * *'  # 2:00 PM UTC = 7:30 PM IST
    # Change to '30 3 * * *' for 9:00 AM IST (after market open)
    # Change to '30 10 * * *' for 4:00 PM IST (after market close)
```

### Customizing Keywords for Filtering

Edit `scripts/daily_order_checker.py` or `scripts/unified_data_fetcher.py`:

```python
ORDER_KEYWORDS = [
    'order', 'orders', 'contract', 'purchase order',
    'work order', 'supply order', 'PO', 'LOI', 'LOA',
    # Add your custom keywords here
    'tender', 'bid won', 'project awarded'
]
```

### Changing Notification Format

Edit `scripts/telegram_notifier.py` to customize the message format:

```python
def format_order_message(announcements):
    # Customize message format here
    message = "🚀 Daily Order Book Report\n\n"
    # ... your custom format
    return message
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Telegram notification failed"

**Solution:**
1. Verify your bot token and chat ID are correct
2. Check environment variables are set:
   ```bash
   echo $TELEGRAM_BOT_TOKEN
   echo $TELEGRAM_CHAT_ID
   ```
3. Test bot manually:
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" \
        -d "chat_id=<YOUR_CHAT_ID>&text=Test"
   ```

### Issue: "BSE/NSE API returns no data"

**Possible causes:**
- Market is closed (weekends, holidays)
- No announcements today
- API rate limiting or network issues

**Solution:**
- Run `python scripts/demo_with_mock_data.py` to test with sample data
- Check if APIs are accessible: `curl https://api.bseindia.com/`
- Wait and retry after a few minutes

### Issue: "GitHub Actions workflow not running"

**Solution:**
1. Check if Actions are enabled: Go to **Settings** → **Actions** → **General**
2. Verify secrets are set: **Settings** → **Secrets and variables** → **Actions**
3. Check workflow logs: **Actions** tab → Click on the workflow run
4. Manually trigger: **Actions** → **Daily Order Book Check** → **Run workflow**

---

## 📚 Additional Documentation

- **[BSE Integration Guide](BSE_INTEGRATION_GUIDE.md)**: How the BSE API integration works
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Step-by-step deployment to production
- **[Telegram Setup Guide](TELEGRAM_SETUP_GUIDE.md)**: Detailed Telegram bot configuration
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)**: Technical architecture details

---

## 🔒 Security & Privacy

- ⚠️ **Never commit `.env` files or tokens to GitHub**
- ✅ Use GitHub Secrets for sensitive credentials
- ✅ `.gitignore` is configured to exclude sensitive files
- ✅ API tokens should be rotated periodically
- ✅ Telegram bot should only be accessible by you (check chat ID)

---

## 🎯 Use Cases

### 1. Stock Research
Monitor which companies are winning new orders to identify growth opportunities.

### 2. Portfolio Tracking
Get alerts when your portfolio companies announce new orders.

### 3. Sector Analysis
Track order trends in specific sectors (IT, Manufacturing, Infrastructure).

### 4. Competitor Intelligence
Monitor order book activity of competitors in your industry.

### 5. Investment Timing
Use order announcements as signals for potential stock price movements.

---

## 📈 Sample Output

**Telegram Notification Example:**

```
📊 NSE/BSE Order Book Update
Date: 28-May-2026

🎯 3 Order Announcements Found:

1. RELIANCE (NSE)
   📌 Receipt of Purchase Order worth ₹450 Cr
   💰 Value: ₹450 Crores

2. TCS (BSE)
   📌 Multi-year IT Services Contract - ₹1200 Cr
   💰 Value: ₹1200 Crores

3. BHARTIARTL (NSE)
   📌 5G Network Equipment Order ₹800 Cr
   💰 Value: ₹800 Crores

📊 Total Order Value: ₹2450 Crores
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

---

## 📄 License

This project is for educational and personal use. Please check the terms of service for NSE/BSE data usage.

---

## 🙏 Credits

- **BSE India** - Corporate announcements API
- **NSE India** - Corporate announcements data
- **Telegram** - Notification platform
- **GitHub Actions** - Free automation runner

---

## 📞 Support

Having issues? Here's how to get help:

1. **Check the documentation**: Most common issues are covered in the guides
2. **Review troubleshooting section**: See common problems above
3. **Check logs**: Look at console output for error messages
4. **Test components individually**: Use the test scripts to isolate issues

---

## 🚀 Quick Command Reference

```bash
# Activate virtual environment
source venv/bin/activate              # macOS/Linux
venv\Scripts\activate                 # Windows

# Install dependencies
pip install -r requirements.txt

# Run main script
cd scripts && python daily_order_checker.py

# Test with mock data
cd scripts && python demo_with_mock_data.py

# View dashboard
open dashboard.html                   # macOS
xdg-open dashboard.html              # Linux
start dashboard.html                 # Windows

# Deactivate virtual environment
deactivate
```

---

**Made with ❤️ for the Indian stock market community**

**Last Updated:** May 28, 2026
