# NSE Order Book Tracker

Automated system to track future orders and contract wins for Nifty 50 companies with real-time monitoring, web dashboard, and Telegram notifications.

## Features

- 📊 **Real-time Monitoring**: Fetches order announcements from NSE/BSE APIs
- 🎯 **Nifty 50 Focus**: Tracks all 50 companies in the Nifty index
- 💰 **Value Extraction**: Automatically extracts order values from announcements
- 📈 **Web Dashboard**: Professional dashboard with charts and tables
- 📥 **Excel Export**: Export data with proper formatting
- 🤖 **GitHub Actions**: Automated daily checks without server maintenance
- 📱 **Telegram Alerts**: Get instant notifications for new orders

## Quick Start

### Prerequisites

- Python 3.11+
- GitHub account (for automation)
- Telegram account (for notifications)

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd nse-orderbook-tracker
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Test NSE data fetching:**
```bash
cd scripts
python nse_data_fetcher.py
```

## Setup Telegram Bot

### Step 1: Create Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name: "My Order Book Tracker"
4. Choose a username: "myorderbook_bot" (must end with _bot)
5. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Chat ID

1. Start a conversation with your bot
2. Send any message to it
3. Open this URL in your browser (replace `<BOT_TOKEN>`):
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
   ```
4. Look for `"chat":{"id": YOUR_CHAT_ID}` in the JSON
5. Copy the chat ID (a number like: `123456789`)

### Step 3: Test Locally

```bash
export TELEGRAM_BOT_TOKEN='your-bot-token-here'
export TELEGRAM_CHAT_ID='your-chat-id-here'

cd scripts
python telegram_notifier.py
```

You should receive test messages on Telegram!

## Setup GitHub Actions

### Step 1: Add GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add two secrets:
   - Name: `TELEGRAM_BOT_TOKEN`, Value: Your bot token
   - Name: `TELEGRAM_CHAT_ID`, Value: Your chat ID

### Step 2: Push Code

```bash
git add .
git commit -m "Add order book tracker with GitHub Actions"
git push origin main
```

### Step 3: Test Workflow

1. Go to **Actions** tab in your GitHub repo
2. Click on "Daily Order Book Check" workflow
3. Click **Run workflow** → **Run workflow**
4. Wait 1-2 minutes
5. Check Telegram for notification

### Step 4: Verify Schedule

The workflow runs automatically every day at 9:30 AM IST (4:00 AM UTC).

Check the Actions tab daily to ensure it's running successfully.

## Project Structure

```
nse-orderbook-tracker/
├── .github/
│   └── workflows/
│       └── daily-order-check.yml    # GitHub Actions workflow
├── scripts/
│   ├── nse_data_fetcher.py          # Fetch NSE announcements
│   ├── value_extractor.py           # Extract order values
│   ├── telegram_notifier.py         # Send Telegram messages
│   └── daily_order_checker.py       # Main automation script
├── evals/
│   └── evals.json                   # Test cases
├── SKILL.md                          # Complete implementation guide
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Running the Dashboard (Optional)

To run the full web dashboard locally:

1. **Set up database:**
```bash
python scripts/database.py
```

2. **Run data collection:**
```bash
python scripts/daily_order_checker.py
```

3. **Start Flask app:**
```bash
python app.py
```

4. Open browser: `http://localhost:5000`

## Notification Examples

### Daily Summary
```
📊 Order Book Update - Nifty 50

📅 Date: 2026-05-28
📈 Total Orders: 3

1. TCS
💰 Value: ₹500.00 Cr
📝 Won digital transformation project

2. LT
💰 Value: ₹2500.00 Cr
📝 Secured metro construction project

💎 Total Value: ₹3000.00 Crores
```

### High-Value Alert
```
🚨 New Order Alert!

🏢 Larsen & Toubro (LT)
📅 Date: 2026-05-28
💰 Value: 2500.00 Crores

📝 Secured major infrastructure project
🔗 View Announcement
```

## Customization

### Change Schedule

Edit `.github/workflows/daily-order-check.yml`:

```yaml
schedule:
  - cron: '30 12 * * *'  # 6 PM IST instead of 9:30 AM
```

### Track Specific Companies

Edit `scripts/daily_order_checker.py`:

```python
# Only track these companies
watchlist = {'TCS', 'INFY', 'LT', 'RELIANCE'}
nifty50_symbols = nifty50_symbols.intersection(watchlist)
```

### Adjust Value Threshold

```python
# Alert for orders > 500 Cr instead of 1000 Cr
if order.get('order_value', 0) > 500:
    self.telegram.send_company_alert(order)
```

## Troubleshooting

### Workflow Not Running

- Check `.github/workflows/` folder exists
- Verify cron syntax in YAML file
- Ensure workflow file name ends with `.yml` or `.yaml`

### Telegram Notification Failed

- Verify bot token and chat ID in GitHub Secrets
- Test locally with `python telegram_notifier.py`
- Check bot is not blocked

### NSE API Errors

- NSE may have rate limits or maintenance
- Workflow will retry next day automatically
- Check logs in Actions tab

### Duplicate Notifications

- Ensure `processed_announcements.json` is being committed
- Check workflow has write permissions
- Verify cache is working

## Monitoring

### View Workflow Status

- Go to **Actions** tab
- Green ✓ = Success
- Red ✗ = Failure

### Check Logs

1. Click on failed workflow run
2. Click on "check-orders" job
3. Expand steps to see details

### Error Alerts

The system sends automatic error notifications to Telegram when issues occur.

## Data Sources

- **NSE Corporate Announcements API**: Real-time order wins
- **BSE Announcements**: Cross-validation (optional)
- **Company Results**: Quarterly order book data (optional)

## Contributing

This is a project-level skill. Modify as needed for your requirements.

## License

Free to use and modify for personal and commercial purposes.

## Support

For issues or questions:
- Check SKILL.md for detailed implementation guide
- Review GitHub Actions logs
- Test scripts locally first

## Acknowledgments

- NSE India for public APIs
- BseIndiaApi Python library
- Telegram Bot API
- GitHub Actions
