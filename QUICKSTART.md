# ⚡ Quick Start Guide

**Get the NSE/BSE Order Book Tracker running in 5 minutes!**

---

## 🎯 For Absolute Beginners

### Step 1: Get the Code (1 minute)

Download and extract the project to your computer, or clone it:
```bash
git clone https://github.com/yourusername/28-May-2026OrderBook.git
cd 28-May-2026OrderBook
```

### Step 2: Run Setup (2 minutes)

**On macOS/Linux:**
```bash
./setup.sh
```

**On Windows:**
```cmd
setup.bat
```

This installs everything automatically!

### Step 3: Get Telegram Credentials (2 minutes)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the **Bot Token**
4. Send a message to your new bot
5. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` to get your **Chat ID**

### Step 4: Configure (30 seconds)

Edit the `.env` file:

**macOS/Linux:**
```bash
nano .env
```

**Windows:**
```cmd
notepad .env
```

Replace the placeholders with your actual values:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
```

Save and close.

### Step 5: Run! (30 seconds)

**On macOS/Linux:**
```bash
./run.sh
```

**On Windows:**
```cmd
run.bat
```

**That's it!** You'll get a Telegram notification with today's order announcements! 🎉

---

## 📱 What You'll Get

A Telegram message like this:

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

## 🤖 Automate It (Optional)

Want daily automatic notifications? Set up GitHub Actions:

1. Push code to GitHub
2. Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as GitHub Secrets
3. Enable GitHub Actions
4. Get notifications every day at 7:30 PM IST automatically!

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for details.

---

## 📊 View Dashboard

Open `dashboard.html` in your browser to see:
- 📈 Order trends
- 📊 Company distribution
- 💰 Value summaries

**macOS:** `open dashboard.html`
**Linux:** `xdg-open dashboard.html`
**Windows:** `start dashboard.html`

---

## 🆘 Need Help?

**Setup failed?** → Check [SETUP.md](SETUP.md) for detailed troubleshooting

**Telegram not working?** → See [TELEGRAM_SETUP_GUIDE.md](TELEGRAM_SETUP_GUIDE.md)

**Want to understand more?** → Read [README.md](README.md)

---

## 🎮 Testing Without Real Data

Want to test first? Run the demo:

**macOS/Linux:**
```bash
cd scripts
python demo_with_mock_data.py
```

**Windows:**
```cmd
cd scripts
python demo_with_mock_data.py
```

This shows how it works with fake data (no Telegram credentials needed).

---

## 📋 Command Cheat Sheet

```bash
# Setup (run once)
./setup.sh              # macOS/Linux
setup.bat               # Windows

# Run the tracker
./run.sh                # macOS/Linux
run.bat                 # Windows

# View dashboard
open dashboard.html     # macOS
xdg-open dashboard.html # Linux
start dashboard.html    # Windows

# Test with fake data
cd scripts && python demo_with_mock_data.py

# Activate virtual environment manually
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

---

## ✅ Success Checklist

- [ ] Setup script ran successfully
- [ ] Got Telegram bot token from @BotFather
- [ ] Got Chat ID from Telegram API
- [ ] Edited .env file with real values
- [ ] Ran `./run.sh` or `run.bat`
- [ ] Received Telegram notification

**All done?** You're tracking order books! 🚀

---

**Next:** Automate daily runs with GitHub Actions ([DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md))

---

**Estimated Time:** 5-10 minutes for first-time setup
**Difficulty:** ⭐ Easy (automated scripts handle everything)
