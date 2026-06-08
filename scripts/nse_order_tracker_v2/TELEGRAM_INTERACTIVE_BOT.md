# 🤖 Interactive Telegram Bot - Real-Time Data Fetching

This guide shows you how to set up the **interactive Telegram bot** that fetches data in real-time when you click buttons or send commands.

---

## 🎯 What's the Difference?

### **Before** (Static Daily Reports):
- Bot sends report once daily at 9:30 AM IST
- No interaction - just receives messages
- Can't request fresh data on-demand

### **After** (Interactive Bot):
- ✅ Send commands anytime (`/menu`, `/fetch`)
- ✅ Click buttons to choose date range
- ✅ Bot fetches fresh data in real-time
- ✅ Receive updated report within 30-60 seconds
- ✅ No need to open dashboard in browser

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd scripts/nse_order_tracker_v2
source venv/bin/activate

# Install base requirements (if not already installed)
pip install -r requirements.txt

# Install bot-specific dependencies
pip install -r requirements-bot.txt
```

### Step 2: Set Credentials

```bash
export TELEGRAM_BOT_TOKEN='your-bot-token'
export TELEGRAM_CHAT_ID='your-chat-id'  # Optional for bot server
```

### Step 3: Start the Bot Server

```bash
python telegram_bot_server.py
```

**Expected Output:**
```
============================================================
NSE Order Book Tracker - Telegram Bot Server
============================================================

Starting Telegram bot server...
Bot is ready to receive commands!
Available commands: /start, /menu, /fetch, /help
Press Ctrl+C to stop
```

**Keep this terminal open!** The bot server must run continuously to respond to your commands.

### Step 4: Test in Telegram

Open your Telegram app and message your bot:

1. `/start` - Get welcome message
2. `/menu` - See interactive buttons
3. Click a button (e.g., "📅 Last 1 Week")
4. Wait 10-60 seconds
5. Receive formatted report!

---

## 📱 How to Use

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Get welcome message and instructions | `/start` |
| `/menu` | Show interactive date range menu with buttons | `/menu` |
| `/fetch` | Fetch last 3 days (default) | `/fetch` |
| `/help` | Show help and command list | `/help` |

### Interactive Buttons

When you send `/menu`, you'll see clickable buttons:

```
🔍 Select Date Range

Choose how many days of order data to fetch:

• 1 Week - Fast (~10 sec)
• 2 Weeks - Moderate (~20 sec)
• 1 Month - Slower (~30 sec)
• 3 Months - Slowest (~60 sec)

⏳ Larger ranges take more time
📊 You'll receive a formatted report

[📅 Last 1 Week]  [📅 Last 2 Weeks]
[📅 Last 1 Month] [📅 Last 3 Months]
[🔄 Refresh (3 days)]
```

**Click any button** → Bot fetches data → Sends report to you!

---

## 🎬 Example Interaction

### Scenario: Get last week's orders

**You:** `/menu`

**Bot:** *Shows buttons*

**You:** *Click "📅 Last 1 Week"*

**Bot:**
```
⏳ Fetching 7 days of data...

Please wait 10-60 seconds.
This may take longer for larger date ranges.

🔄 Fetching from NSE API...
```

*After 10-20 seconds...*

**Bot:**
```
📊 NSE Order Book Tracker - Daily Report
━━━━━━━━━━━━━━━━━━━━━

🕐 Last Updated: 2026-05-30 14:45:23
📅 Period: Last 7 days

📈 SUMMARY
━━━━━━━━━━━━━━━━━━━━━
📋 Total Announcements: 12
💰 Total Order Value: ₹15,450.00 Cr
📊 Average Order Size: ₹1,287.50 Cr
🏢 Unique Companies: 8

[... table and details ...]
```

**Bot:**
```
✅ Report sent!

Fetched 7 days of data.
Found 12 announcements.

Use /menu for other date ranges.

[🔄 Fetch Again]
```

---

## ⚙️ Setup for 24/7 Operation

The bot server needs to run continuously to respond to commands.

### Option 1: Run on Your Computer

```bash
# Start bot server
cd scripts/nse_order_tracker_v2
source venv/bin/activate
python telegram_bot_server.py

# Keep terminal open!
# Bot will respond to commands as long as this runs
```

**Pros:** Simple, local control
**Cons:** Computer must stay on

### Option 2: Run on VPS/Cloud Server

**Deploy to a VPS (DigitalOcean, AWS, etc.):**

```bash
# SSH into your server
ssh user@your-server.com

# Clone repo
git clone https://github.com/your-username/nse-orderbook-tracker
cd nse-orderbook-tracker/scripts/nse_order_tracker_v2

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set credentials
export TELEGRAM_BOT_TOKEN='your-token'

# Run with systemd (stays running after logout)
sudo nano /etc/systemd/system/nse-telegram-bot.service
```

**Service file content:**
```ini
[Unit]
Description=NSE Telegram Bot Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/nse-orderbook-tracker/scripts/nse_order_tracker_v2
Environment="TELEGRAM_BOT_TOKEN=your-token-here"
ExecStart=/path/to/venv/bin/python telegram_bot_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable nse-telegram-bot
sudo systemctl start nse-telegram-bot
sudo systemctl status nse-telegram-bot
```

**Pros:** Runs 24/7, auto-restart
**Cons:** Need VPS/server

### Option 3: Run with Screen/Tmux

```bash
# Install screen
sudo apt install screen  # or: brew install screen

# Start screen session
screen -S telegram-bot

# Start bot
cd scripts/nse_order_tracker_v2
source venv/bin/activate
python telegram_bot_server.py

# Detach: Press Ctrl+A then D
# Bot keeps running in background!

# Reattach later:
screen -r telegram-bot
```

**Pros:** Easy, runs in background
**Cons:** Computer must stay on

---

## 🔧 Configuration

### Change Default Days

Edit `telegram_bot_server.py` line ~60:

```python
async def fetch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fetch command - fetch data with default 3 days"""
    await self.fetch_data(update, context, days=7, from_callback=False)  # Changed from 3 to 7
```

### Change Threshold

Edit `telegram_bot_server.py` line ~120:

```python
orchestrator = OrderBookOrchestrator(
    enable_telegram=False,
    value_threshold=1000  # Changed from 500 to 1000
)
```

### Add More Button Options

Edit `telegram_bot_server.py` line ~70:

```python
keyboard = [
    [
        InlineKeyboardButton("📅 Last 1 Week", callback_data="fetch_7"),
        InlineKeyboardButton("📅 Last 2 Weeks", callback_data="fetch_14")
    ],
    [
        InlineKeyboardButton("📅 Last 1 Month", callback_data="fetch_30"),
        InlineKeyboardButton("📅 Last 3 Months", callback_data="fetch_90")
    ],
    [
        InlineKeyboardButton("📅 Last 6 Months", callback_data="fetch_180")  # NEW
    ]
]
```

---

## 🐛 Troubleshooting

### "TELEGRAM_BOT_TOKEN not set"

**Problem:** Bot token environment variable missing

**Solution:**
```bash
export TELEGRAM_BOT_TOKEN='123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
```

### "Bot not responding to commands"

**Problem:** Bot server not running

**Solution:**
```bash
# Check if bot server is running
ps aux | grep telegram_bot_server

# If not running, start it
python telegram_bot_server.py
```

### "Fetching takes too long"

**Problem:** Large date ranges (90 days) take time

**Solution:**
- This is normal for 3-month requests
- Use smaller ranges for faster results
- 7 days: ~10 seconds
- 30 days: ~30 seconds
- 90 days: ~60 seconds

### "Error fetching data"

**Problem:** Orchestrator failed

**Solution:**
```bash
# Test orchestrator directly
python orchestrator.py --days 7

# Check logs for errors
# Common issues:
# - Network connectivity
# - NSE API rate limiting
# - Disk space for PDFs
```

### "Button clicks don't work"

**Problem:** Bot not receiving callback queries

**Solution:**
- Ensure bot server is running
- Check terminal for error messages
- Restart bot server:
  ```bash
  # Ctrl+C to stop
  python telegram_bot_server.py  # Restart
  ```

---

## 📊 How It Works

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    TELEGRAM                         │
│                                                     │
│  User sends: /menu                                  │
│  Bot shows: [Buttons]                               │
│  User clicks: "Last 1 Week"                         │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│           telegram_bot_server.py                    │
│                                                     │
│  1. Receives button callback                        │
│  2. Parses: "fetch_7" → 7 days                      │
│  3. Calls orchestrator                              │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│              orchestrator.py                        │
│                                                     │
│  1. Fetches from NSE API                            │
│  2. Downloads PDFs                                  │
│  3. Parses order values                             │
│  4. Saves to JSON                                   │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│           telegram_notifier.py                      │
│                                                     │
│  1. Formats data as table                           │
│  2. Sends to Telegram                               │
│  3. User receives report                            │
└─────────────────────────────────────────────────────┘
```

### Key Components

1. **telegram_bot_server.py** - Listens for commands
2. **orchestrator.py** - Fetches and processes data
3. **telegram_notifier.py** - Formats and sends messages

---

## 🎯 Best Practices

### For Daily Use:

1. **Start bot server once:**
   ```bash
   screen -S telegram-bot
   python telegram_bot_server.py
   # Ctrl+A, D to detach
   ```

2. **Use commands as needed:**
   - Quick check: `/fetch` (3 days)
   - Weekly review: `/menu` → "Last 1 Week"
   - Monthly analysis: `/menu` → "Last 1 Month"

3. **Keep bot running 24/7:**
   - Use systemd service (recommended)
   - Or use screen/tmux
   - Or deploy to cloud server

### For Production:

1. **Deploy to VPS** with systemd
2. **Set up monitoring** (check if bot is running)
3. **Configure auto-restart** on failure
4. **Log rotation** for bot logs
5. **Backup credentials** securely

---

## 🔐 Security Notes

- **Bot token** is sensitive - keep it secret
- **Don't commit** token to git
- **Use environment variables** only
- **Limit bot access** to your chat ID only (optional)

To restrict bot to specific users, add this check in `telegram_bot_server.py`:

```python
ALLOWED_CHAT_IDS = [123456789, 987654321]  # Your chat IDs

async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ALLOWED_CHAT_IDS:
        await update.message.reply_text("⛔ Unauthorized access")
        return
    # ... rest of command
```

---

## 📈 Performance

**Response Times:**
- Command received: Instant
- Data fetching: 10-60 seconds (depends on days)
- Report sent: Within 1 second after fetch

**Resource Usage:**
- Memory: ~100 MB (bot server + orchestrator)
- CPU: Low (idle), High (during fetch)
- Network: ~1-5 MB per fetch

---

## ✅ Quick Checklist

Before first use:
- [ ] Bot token obtained from @BotFather
- [ ] Token exported: `export TELEGRAM_BOT_TOKEN='...'`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Bot server started: `python telegram_bot_server.py`
- [ ] Sent `/start` to bot in Telegram
- [ ] Tested `/menu` command
- [ ] Clicked a button
- [ ] Received formatted report

For 24/7 operation:
- [ ] Deployed to VPS or using screen/tmux
- [ ] Bot stays running after logout
- [ ] Systemd service configured (optional)
- [ ] Monitoring set up (optional)

---

## 🎉 You're Ready!

**Now you have:**
- ✅ Interactive Telegram bot
- ✅ Real-time data fetching
- ✅ Clickable date range buttons
- ✅ On-demand reports (no waiting for daily schedule)
- ✅ No need to open dashboard in browser

**Try it now:**
```bash
python telegram_bot_server.py
```

Then open Telegram and send: `/menu`

**Click a button and watch the magic happen!** ✨📊

