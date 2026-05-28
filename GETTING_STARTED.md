# 🚀 Getting Started with NSE/BSE Order Book Tracker

**Welcome! This guide will help you choose the right way to get started based on your experience level.**

---

## 👤 Choose Your Path

### 🌟 I'm New to Programming
**→ Start here:** [QUICKSTART.md](QUICKSTART.md)

- Automated setup scripts
- Simple step-by-step instructions
- 5-minute setup
- No technical knowledge required

### 💻 I'm Comfortable with Code
**→ Start here:** [SETUP.md](SETUP.md)

- Detailed technical setup
- Manual configuration options
- Comprehensive troubleshooting
- Understanding the system architecture

### 🚀 I Just Want to Run It Now
**→ Quick commands:**

```bash
# macOS/Linux
./setup.sh   # One-time setup
./run.sh     # Run the tracker

# Windows
setup.bat    # One-time setup
run.bat      # Run the tracker
```

---

## 📚 Documentation Map

```
Start Here
    │
    ├── QUICKSTART.md ..................... ⚡ 5-minute quick start (beginners)
    │
    ├── GETTING_STARTED.md ................ 📍 You are here!
    │
    └── README.md ......................... 📖 Full project overview
        │
        ├── SETUP.md ...................... 🔧 Detailed setup guide
        │
        ├── TELEGRAM_SETUP_GUIDE.md ....... 🤖 Telegram bot setup
        │
        ├── DEPLOYMENT_GUIDE.md ........... ☁️  Deploy to GitHub Actions
        │
        ├── BSE_INTEGRATION_GUIDE.md ...... 📊 BSE API technical details
        │
        ├── IMPLEMENTATION_SUMMARY.md ..... 🏗️  Architecture & design
        │
        └── PROJECT_STRUCTURE.md .......... 📁 File organization
```

---

## 🎯 What Do You Want to Do?

### ✅ I want to set up the project
→ **[QUICKSTART.md](QUICKSTART.md)** (beginners) or **[SETUP.md](SETUP.md)** (advanced)

### ✅ I need help with Telegram
→ **[TELEGRAM_SETUP_GUIDE.md](TELEGRAM_SETUP_GUIDE.md)**

### ✅ I want to automate daily runs
→ **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

### ✅ I want to understand how it works
→ **[README.md](README.md)** and **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**

### ✅ I need to troubleshoot an issue
→ **[SETUP.md](SETUP.md)** → Troubleshooting section

### ✅ I want to see the code structure
→ **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**

---

## 🎮 Try Before Setup

Not ready to configure yet? Test with demo data:

```bash
# Install dependencies first
pip install -r requirements.txt

# Run demo (no configuration needed)
cd scripts
python demo_with_mock_data.py
```

This shows you how the system works without needing Telegram setup.

---

## 📊 System Overview

```
┌─────────────────────────────────────────────┐
│         NSE/BSE Order Book Tracker          │
└─────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
   BSE API (Primary)        NSE API (Fallback)
        │                         │
        └────────────┬────────────┘
                     ▼
          Filter Order Announcements
                     │
                     ▼
            Extract Order Values
                     │
                     ▼
         Send Telegram Notification
                     │
                     ▼
              📱 Your Phone
```

---

## 🛠️ Setup Methods

### Method 1: Automated Scripts (Recommended)
**Best for:** Beginners, quick setup
**Time:** 5 minutes

```bash
./setup.sh   # Handles everything automatically
```

### Method 2: Manual Setup
**Best for:** Advanced users, custom configurations
**Time:** 10-15 minutes

1. Create virtual environment
2. Install dependencies
3. Configure Telegram
4. Test components
5. Run the system

See [SETUP.md](SETUP.md) for details.

### Method 3: Docker (Coming Soon)
**Best for:** Production deployments
**Status:** Not yet implemented

---

## 📱 Telegram Setup (Required)

You need a Telegram bot to receive notifications. The process takes 2-3 minutes:

1. Create bot with @BotFather
2. Get bot token
3. Get your chat ID
4. Add to `.env` file

**Detailed guide:** [TELEGRAM_SETUP_GUIDE.md](TELEGRAM_SETUP_GUIDE.md)

---

## 🤖 Automation Options

### Option 1: GitHub Actions (Recommended)
- **Free** (using GitHub's servers)
- Runs automatically every day
- No need to keep your computer on
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Option 2: Local Cron Job (macOS/Linux)
```bash
crontab -e
# Add: 0 14 * * * cd /path/to/project && ./run.sh
```

### Option 3: Windows Task Scheduler
- Open Task Scheduler
- Create task to run `run.bat` daily
- Set time to 7:30 PM

### Option 4: Manual Run
```bash
./run.sh    # Run whenever you want
```

---

## 📊 What You'll Track

The system monitors:

- ✅ **Order Announcements**: New orders, contracts, purchase orders
- ✅ **Order Values**: Extracted in ₹ Crores or ₹ Lakhs
- ✅ **Company Details**: Stock symbol, exchange (NSE/BSE)
- ✅ **Daily Updates**: Consolidated report every day

**Example notification:**
```
📊 NSE/BSE Order Book Update
🎯 3 Order Announcements Found:

1. RELIANCE - ₹450 Cr Purchase Order
2. TCS - ₹1200 Cr IT Services Contract
3. BHARTIARTL - ₹800 Cr Equipment Order

📊 Total: ₹2450 Crores
```

---

## 🎯 Success Milestones

Follow these checkpoints:

### Milestone 1: Installation ✅
- [ ] Downloaded/cloned the project
- [ ] Ran setup script successfully
- [ ] Virtual environment created
- [ ] Dependencies installed

### Milestone 2: Configuration ✅
- [ ] Created Telegram bot
- [ ] Got bot token and chat ID
- [ ] Created/edited `.env` file
- [ ] Credentials verified

### Milestone 3: Testing ✅
- [ ] Ran mock data demo
- [ ] Tested Telegram notification
- [ ] Ran full system test
- [ ] Received real notification

### Milestone 4: Automation ✅ (Optional)
- [ ] Pushed to GitHub
- [ ] Added GitHub Secrets
- [ ] Enabled GitHub Actions
- [ ] Workflow ran successfully

---

## 🆘 Common Issues & Quick Fixes

### "Python not found"
```bash
# Try these commands
python3 --version
python --version
py --version
```

### "Permission denied" on scripts
```bash
chmod +x setup.sh run.sh
```

### "Telegram notification failed"
- Check bot token is correct
- Verify chat ID is a number
- Test bot manually with curl

### "No announcements found"
- Market might be closed
- No announcements today
- Try demo: `python demo_with_mock_data.py`

**More help:** [SETUP.md](SETUP.md) → Troubleshooting section

---

## 📈 Next Steps After Setup

1. **Run it daily**: Set up GitHub Actions for automation
2. **Customize keywords**: Edit filtering logic in `daily_order_checker.py`
3. **Build a watchlist**: Track specific companies
4. **Analyze trends**: Use the dashboard to visualize data
5. **Export data**: Add CSV/Excel export functionality

---

## 🎓 Learning Resources

### Understanding the Code
- `scripts/daily_order_checker.py` - Main orchestrator
- `scripts/unified_data_fetcher.py` - Data fetching logic
- `scripts/telegram_notifier.py` - Notification system

### Python Learning
If you're new to Python, these files are beginner-friendly starting points:
- `demo_with_mock_data.py` - Simple demo script
- `value_extractor.py` - Text parsing logic

### API Integration
Learn about APIs from:
- `bse_data_fetcher.py` - BSE API integration
- `nse_data_fetcher.py` - NSE API integration

---

## 💡 Pro Tips

1. **Test first**: Always run `demo_with_mock_data.py` before live runs
2. **Check logs**: Console output shows what's happening
3. **Market timing**: Best time to run is after market close (4-7 PM IST)
4. **Backup config**: Keep a copy of your `.env` file safely
5. **Update regularly**: Pull latest changes from GitHub

---

## 🤝 Community & Support

### Having Issues?
1. Check the troubleshooting section in [SETUP.md](SETUP.md)
2. Review the logs for error messages
3. Test individual components
4. Re-run setup script

### Want to Contribute?
- Report bugs
- Suggest features
- Improve documentation
- Submit pull requests

---

## 📋 Quick Reference Card

```
┌─────────────────────────────────────────┐
│        Essential Commands               │
├─────────────────────────────────────────┤
│ Setup:     ./setup.sh                   │
│ Run:       ./run.sh                     │
│ Test:      cd scripts &&                │
│            python demo_with_mock_data.py│
│ Dashboard: open dashboard.html          │
│ Help:      Read README.md               │
└─────────────────────────────────────────┘
```

---

## 🎉 Ready to Start?

**Choose your path:**

- **Quick & Easy:** [QUICKSTART.md](QUICKSTART.md) → 5 minutes
- **Detailed Setup:** [SETUP.md](SETUP.md) → 15 minutes
- **Just Run It:** `./setup.sh` then `./run.sh`

**Questions?** Check the documentation map above to find the right guide.

---

**Happy Tracking! 📊📱**

---

**Last Updated:** May 28, 2026
**Project Status:** ✅ Ready for Production
