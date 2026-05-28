# 🔧 Complete Setup Guide - NSE/BSE Order Book Tracker

**Beginner-friendly step-by-step instructions to get the system running locally**

---

## 📝 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Telegram Bot Setup](#telegram-bot-setup)
4. [Configuration](#configuration)
5. [First Run](#first-run)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher (3.9-3.10 recommended)
- **RAM**: 512 MB available
- **Disk Space**: 100 MB free
- **Internet**: Stable connection (for API calls)

### Check Your Python Version

Open terminal/command prompt and run:

```bash
python --version
# or
python3 --version
```

**Expected output:** `Python 3.9.x` or `Python 3.10.x`

**If Python is not installed:**
- **Windows**: Download from [python.org/downloads](https://www.python.org/downloads/)
- **macOS**: `brew install python3` (requires Homebrew)
- **Linux**: `sudo apt-get install python3 python3-pip python3-venv`

---

## 📥 Installation Steps

### Step 1: Download the Project

**Method A: Using Git (Recommended)**

```bash
# Clone the repository
git clone https://github.com/yourusername/28-May-2026OrderBook.git

# Navigate to the project folder
cd 28-May-2026OrderBook
```

**Method B: Download ZIP**

1. Go to the GitHub repository
2. Click **Code** → **Download ZIP**
3. Extract the ZIP file to a folder of your choice
4. Open terminal/command prompt
5. Navigate to the extracted folder:
   ```bash
   cd path/to/28-May-2026OrderBook
   ```

### Step 2: Create Virtual Environment

A virtual environment keeps project dependencies isolated.

**On macOS/Linux:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your terminal prompt should now show (venv)
```

**On Windows (Command Prompt):**

```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Your prompt should now show (venv)
```

**On Windows (PowerShell):**

```powershell
# Create virtual environment
python -m venv venv

# Activate it (may need to change execution policy first)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

With virtual environment activated:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**This will install:**
- `flask` - Web framework
- `requests` - HTTP requests
- `pandas` - Data analysis
- `openpyxl` - Excel support
- `bse` - BSE India API
- `pdfplumber`, `PyPDF2` - PDF parsing
- `schedule` - Task scheduling
- `sqlalchemy` - Database

**Installation time:** 2-3 minutes (depends on internet speed)

**Verify installation:**
```bash
pip list
```

You should see all the packages listed above.

---

## 🤖 Telegram Bot Setup

### Why Do I Need This?

The system sends notifications to your Telegram account when new order announcements are found. You need a Telegram bot to receive these messages.

### Step 1: Install Telegram

- **Mobile**: Download from App Store (iOS) or Google Play (Android)
- **Desktop**: Download from [telegram.org](https://telegram.org/)

### Step 2: Create a Telegram Bot

1. **Open Telegram** and search for `@BotFather` (official bot by Telegram)

2. **Start a chat** with BotFather and send:
   ```
   /newbot
   ```

3. **Choose a name** for your bot (e.g., "My Order Tracker")

4. **Choose a username** (must end with 'bot', e.g., "my_order_tracker_bot")

5. **Copy the Bot Token** - BotFather will send you a message like:
   ```
   Use this token to access the HTTP API:
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

   **⚠️ IMPORTANT:** Keep this token secret! It's like a password.

6. **Save the token** somewhere safe (you'll need it in Step 4)

### Step 3: Get Your Chat ID

The Chat ID identifies your Telegram account so the bot knows where to send messages.

1. **Send a message** to your new bot (type anything, like "Hello")

2. **Open this URL** in your browser (replace `<YOUR_BOT_TOKEN>` with your actual token):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```

   **Example:**
   ```
   https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrsTUVwxyz/getUpdates
   ```

3. **Find your Chat ID** in the JSON response:
   ```json
   {
     "ok": true,
     "result": [
       {
         "update_id": 12345678,
         "message": {
           "message_id": 1,
           "from": {
             "id": 987654321,  ← This is your Chat ID
             "is_bot": false,
             "first_name": "Your Name"
           },
           "chat": {
             "id": 987654321,  ← This is your Chat ID
             "first_name": "Your Name",
             "type": "private"
           },
           "text": "Hello"
         }
       }
     ]
   }
   ```

4. **Copy the Chat ID** (the number, e.g., `987654321`)

### Step 4: Test Your Bot

You can test if your bot works using this curl command:

**On macOS/Linux:**
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
     -d "chat_id=<YOUR_CHAT_ID>" \
     -d "text=Test message from Order Book Tracker!"
```

**On Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" `
    -Method Post `
    -Body @{chat_id="<YOUR_CHAT_ID>"; text="Test message from Order Book Tracker!"}
```

**Expected result:** You should receive a message on Telegram!

---

## ⚙️ Configuration

### Method 1: Using .env File (Recommended)

Create a `.env` file in the project root:

**On macOS/Linux:**
```bash
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOF
```

Then edit the file with your actual values:
```bash
nano .env
# or
open -e .env  # macOS TextEdit
```

**On Windows:**

Create a file named `.env` (using Notepad or any text editor) with this content:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
```

**File location:** Place `.env` in the same folder as `README.md`

### Method 2: Using Environment Variables

Instead of a `.env` file, you can set environment variables directly.

**On macOS/Linux (for current session):**
```bash
export TELEGRAM_BOT_TOKEN='123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
export TELEGRAM_CHAT_ID='987654321'
```

**To make it permanent on macOS/Linux:**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"' >> ~/.zshrc
echo 'export TELEGRAM_CHAT_ID="987654321"' >> ~/.zshrc
source ~/.zshrc
```

**On Windows (Command Prompt):**
```cmd
set TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
set TELEGRAM_CHAT_ID=987654321
```

**On Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
$env:TELEGRAM_CHAT_ID = "987654321"
```

**To make it permanent on Windows:**
1. Open **System Properties** → **Advanced** → **Environment Variables**
2. Click **New** under "User variables"
3. Add `TELEGRAM_BOT_TOKEN` with your token value
4. Add `TELEGRAM_CHAT_ID` with your chat ID
5. Click **OK** and restart your terminal

### Verify Configuration

Check if environment variables are set:

**macOS/Linux:**
```bash
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

**Windows (Command Prompt):**
```cmd
echo %TELEGRAM_BOT_TOKEN%
echo %TELEGRAM_CHAT_ID%
```

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN
$env:TELEGRAM_CHAT_ID
```

---

## 🎮 First Run

### Test 1: Mock Data Demo (Recommended First)

This runs the system with fake data to verify everything works without hitting live APIs.

```bash
# Navigate to scripts folder
cd scripts

# Run the demo
python demo_with_mock_data.py
```

**Expected output:**
```
🎬 Running Order Book Tracker Demo with Mock Data
================================================

📥 Step 1: Fetching announcements...
✅ Fetched 5 mock announcements

🔍 Step 2: Filtering for orders...
✅ Found 3 order-related announcements

💰 Step 3: Extracting values...
✅ Extracted values from 3 announcements

📱 Step 4: Sending Telegram notification...
[Mock Mode - Would send to Telegram]

📊 Summary:
- Total announcements: 5
- Order announcements: 3
- Total order value: ₹1500 Cr

Demo completed successfully! ✅
```

### Test 2: Telegram Notification Test

Verify that Telegram notifications work:

```bash
cd scripts
python -c "from telegram_notifier import send_notification; send_notification('✅ Test notification from Order Book Tracker!')"
```

**Expected result:** You should receive a test message on Telegram within seconds.

**If it fails:**
- Check your bot token and chat ID
- Verify environment variables are set
- Test bot manually using curl (see Telegram Setup Step 4)

### Test 3: BSE Integration Test

Test fetching live data from BSE:

```bash
cd scripts
python test_bse_integration.py
```

**Expected output:**
```
🧪 Testing BSE Integration
==========================

📡 Test 1: Fetch BSE announcements...
✅ Success! Fetched 45 announcements

🔍 Test 2: Filter for orders...
✅ Found 3 order announcements

💰 Test 3: Extract values...
✅ Extracted 2 values (1 without value)

📊 Sample Announcements:
1. RELIANCE - Receipt of Order - ₹450 Cr
2. TCS - Contract Award - Value not specified
3. BHARTIARTL - Purchase Order - ₹800 Cr

✅ All tests passed!
```

**If it fails:**
- Market might be closed (test only runs Mon-Fri during market hours)
- BSE API might be temporarily unavailable (script will fallback to NSE)
- Check internet connection

### Test 4: Full System Run (Live Data)

Run the complete system with live data:

```bash
cd scripts
python daily_order_checker.py
```

**What happens:**
1. Fetches today's announcements from BSE
2. Falls back to NSE if BSE fails
3. Filters for order-related announcements
4. Extracts order values
5. Sends Telegram notification

**Expected console output:**
```
2026-05-28 10:30:15 - INFO - Starting daily order book check...
2026-05-28 10:30:15 - INFO - Fetching announcements from BSE...
2026-05-28 10:30:18 - INFO - BSE fetch successful: 45 announcements
2026-05-28 10:30:18 - INFO - Filtering for order announcements...
2026-05-28 10:30:18 - INFO - Found 3 order announcements
2026-05-28 10:30:18 - INFO - Extracting order values...
2026-05-28 10:30:19 - INFO - Sending Telegram notification...
2026-05-28 10:30:20 - INFO - ✅ Notification sent successfully!
2026-05-28 10:30:20 - INFO - Daily check completed.
```

**Expected Telegram message:**
```
📊 NSE/BSE Order Book Update
Date: 28-May-2026

🎯 3 Order Announcements Found:

1. RELIANCE (BSE)
   📌 Receipt of Purchase Order
   💰 Value: ₹450 Crores

2. TCS (BSE)
   📌 Multi-year IT Services Contract
   💰 Value: ₹1200 Crores

3. BHARTIARTL (NSE)
   📌 5G Network Equipment Order
   💰 Value: ₹800 Crores

📊 Total Order Value: ₹2450 Crores
```

---

## ✅ Verification Checklist

After running the tests above, verify:

- [ ] Virtual environment is activated (`(venv)` in terminal prompt)
- [ ] All dependencies installed (`pip list` shows all packages)
- [ ] Telegram bot created and token obtained
- [ ] Chat ID retrieved from Telegram
- [ ] Environment variables set (`echo $TELEGRAM_BOT_TOKEN` shows token)
- [ ] Mock data demo runs successfully
- [ ] Telegram test notification received
- [ ] BSE integration test passes (or gracefully fails if market closed)
- [ ] Full system run completes and sends Telegram notification

**All checks passed?** 🎉 **You're ready to use the system!**

---

## 📊 View the Dashboard

Open the interactive HTML dashboard:

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

Or just double-click `dashboard.html` in your file explorer.

---

## 🐛 Troubleshooting

### Issue: "Python command not found"

**Windows:**
- Try `py` instead of `python`
- Or `python3` instead of `python`
- Make sure Python is added to PATH during installation

**macOS/Linux:**
- Use `python3` instead of `python`
- Check if Python is installed: `which python3`

### Issue: "Permission denied when activating venv"

**Windows PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux:**
```bash
chmod +x venv/bin/activate
```

### Issue: "pip install fails with SSL errors"

**Solution:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue: "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Telegram bot not responding"

**Check:**
1. Bot token is correct (no spaces, full token copied)
2. Chat ID is a number (no quotes in .env file)
3. You sent at least one message to the bot
4. Internet connection is working

**Test manually:**
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/getMe"
```

This should return bot details if token is valid.

### Issue: "BSE API returns no data"

**Possible causes:**
- Market is closed (weekends, holidays)
- No announcements today
- BSE API temporarily down

**Solution:**
- Run `python demo_with_mock_data.py` to test with sample data
- Wait and retry later
- System will automatically fallback to NSE

### Issue: "GitHub Actions workflow not running"

See the [Deployment Guide](DEPLOYMENT_GUIDE.md) for GitHub Actions troubleshooting.

---

## 🎯 Next Steps

Now that your system is set up:

1. **Schedule it**: Set up GitHub Actions for automatic daily runs ([Deployment Guide](DEPLOYMENT_GUIDE.md))
2. **Customize keywords**: Edit order filtering keywords in `scripts/daily_order_checker.py`
3. **Modify notifications**: Change message format in `scripts/telegram_notifier.py`
4. **Add stocks**: Create a watchlist to filter specific companies
5. **Explore data**: Check `dashboard.html` for visualizations

---

## 📚 Additional Resources

- **[Main README](README.md)**: Project overview and features
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Deploy to GitHub Actions
- **[BSE Integration Guide](BSE_INTEGRATION_GUIDE.md)**: BSE API details
- **[Telegram Setup Guide](TELEGRAM_SETUP_GUIDE.md)**: Detailed Telegram instructions

---

## 🎓 Understanding the System

### Data Flow

```
BSE API → unified_data_fetcher.py → daily_order_checker.py
   ↓
NSE API (fallback) → Filter orders → Extract values → Telegram notification
```

### Key Scripts

1. **`daily_order_checker.py`**: Main orchestrator, runs the entire pipeline
2. **`unified_data_fetcher.py`**: Fetches from BSE (primary) or NSE (fallback)
3. **`telegram_notifier.py`**: Sends notifications to your Telegram
4. **`value_extractor.py`**: Extracts order values from text (₹X Cr, ₹X Lakh)

### When to Run

- **Market open**: Mon-Fri, 9:15 AM - 3:30 PM IST
- **Best time**: After market close (4:00 PM - 7:00 PM IST) for complete data
- **Automated**: Set GitHub Actions to run at 7:30 PM IST daily

---

## ✅ Setup Complete!

You're all set! The system is now configured and ready to track order announcements.

**What's next?**
- Run it manually when needed: `cd scripts && python daily_order_checker.py`
- Set up automation: Follow [Deployment Guide](DEPLOYMENT_GUIDE.md)
- Customize: Edit keywords, notification format, etc.

**Questions?** Check the troubleshooting section or review the documentation.

---

**Last Updated:** May 28, 2026
**Setup Difficulty:** ⭐⭐ (Beginner-friendly)
