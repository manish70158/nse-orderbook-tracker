# Telegram Bot Setup Guide for NSE Order Book Tracker

This guide will help you set up Telegram notifications for automated order alerts.

## Overview

The system will send you Telegram notifications for:
- New orders above ₹500 Crores (configurable threshold)
- Daily digest of high-value orders
- Individual alerts for orders exceeding ₹1000 Crores
- Error notifications if the automation fails

## Step 1: Create Your Telegram Bot

1. **Open Telegram** on your phone or computer

2. **Search for @BotFather** (official Telegram bot for creating bots)

3. **Start a conversation** and send the command:
   ```
   /newbot
   ```

4. **Choose a name** for your bot:
   - Example: `NSE Order Book Tracker`
   - This is the display name users will see

5. **Choose a username** (must end with `bot`):
   - Example: `nse_orderbook_tracker_bot`
   - This must be unique across all Telegram

6. **Copy your bot token**:
   - BotFather will give you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - **Keep this token secret!** It's like a password for your bot
   - Save it somewhere safe - you'll need it in Step 3

## Step 2: Get Your Chat ID

You need your Chat ID so the bot knows where to send messages.

### Method 1: Using @userinfobot (Easiest)

1. Search for **@userinfobot** on Telegram
2. Start a conversation with it
3. It will immediately show your Chat ID (a number like `123456789`)
4. **Copy this number** - you'll need it in Step 3

### Method 2: Using @RawDataBot (Alternative)

1. Search for **@RawDataBot** on Telegram
2. Start a conversation
3. Send any message
4. It will respond with JSON data containing your `"id"` field
5. Copy the number from the `"id"` field

### Method 3: Manual Method (Advanced)

1. Start a conversation with your new bot
2. Send it any message (like "hello")
3. Open this URL in your browser (replace `<BOT_TOKEN>` with your actual token):
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
   ```
4. You'll see JSON output. Look for:
   ```json
   "chat": {
     "id": 123456789,
     ...
   }
   ```
5. Copy the `id` number

## Step 3: Test Your Bot Locally

Before setting up automation, test that everything works:

1. **Set environment variables** (replace with your actual values):

   On macOS/Linux:
   ```bash
   export TELEGRAM_BOT_TOKEN='123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
   export TELEGRAM_CHAT_ID='123456789'
   ```

   On Windows (Command Prompt):
   ```cmd
   set TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   set TELEGRAM_CHAT_ID=123456789
   ```

   On Windows (PowerShell):
   ```powershell
   $env:TELEGRAM_BOT_TOKEN='123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
   $env:TELEGRAM_CHAT_ID='123456789'
   ```

2. **Run the test script**:
   ```bash
   python telegram_notifier.py
   ```

3. **Check your Telegram** - you should receive test messages!

## Step 4: Add to GitHub Secrets (For Automation)

To run the bot automatically via GitHub Actions:

1. **Go to your GitHub repository**

2. **Navigate to Settings** → **Secrets and variables** → **Actions**

3. **Click "New repository secret"**

4. **Add the first secret**:
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
   - Click "Add secret"

5. **Add the second secret**:
   - Name: `TELEGRAM_CHAT_ID`
   - Value: Your chat ID (e.g., `123456789`)
   - Click "Add secret"

6. **Verify** both secrets are added correctly

## Step 5: Configure Your Bot (Optional)

You can customize your bot's behavior:

### Change the Alert Threshold

Edit `daily_order_checker_enhanced.py` or pass as parameter:
```bash
python daily_order_checker_enhanced.py --threshold 1000
```

This will only alert for orders ≥ ₹1000 Crores instead of ₹500 Crores.

### Bot Profile Picture

1. Go back to @BotFather on Telegram
2. Send: `/mybots`
3. Select your bot
4. Choose "Edit Bot" → "Edit Botpic"
5. Upload an image (recommended: 512x512 pixels)

### Bot Description

1. In @BotFather, send: `/setdescription`
2. Choose your bot
3. Enter a description like:
   ```
   Automated tracker for NSE order book announcements.
   Sends alerts for high-value orders (≥₹500 Crores) from Nifty 50 companies.
   ```

## Using with Group Chats (Optional)

To receive notifications in a Telegram group:

1. **Create a Telegram group**
2. **Add your bot** to the group
3. **Make the bot an admin** (required for some features)
4. **Send a message** in the group
5. **Get the group Chat ID**:
   - Visit: `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
   - Look for the chat ID in the group messages
   - Group chat IDs are negative (like `-987654321`)
6. **Use this negative number** as your `TELEGRAM_CHAT_ID`

## Troubleshooting

### Bot not responding

**Problem**: Bot doesn't send messages

**Solutions**:
- Verify your bot token is correct (no extra spaces)
- Make sure you've started a conversation with the bot (send `/start`)
- Check that your chat ID is correct
- Test the connection: `python telegram_notifier.py`

### "Chat not found" error

**Problem**: Error message says "Bad Request: chat not found"

**Solutions**:
- Make sure you've sent at least one message to your bot
- Verify your chat ID is a number (not your username)
- For group chats, ensure the bot is added to the group

### Messages not formatted correctly

**Problem**: Messages show HTML tags instead of formatting

**Solutions**:
- The bot uses HTML parse mode by default
- Make sure special characters are escaped properly
- Test with a simple message first

### Rate limiting

**Problem**: Some messages don't get sent

**Solutions**:
- Telegram has rate limits (30 messages per second)
- Our code includes delays to prevent this
- If you're sending many messages, they may be queued

## Message Format Examples

The bot sends three types of messages:

### 1. High-Value Order Summary
```
🚨 High-Value Order Alert 🚨

📅 Date: 2026-05-28
📈 Orders Above ₹500 Cr: 3

1. LT
🏢 Larsen & Toubro
💰 Value: ₹2500.00 Crores
📝 Major metro construction project

2. RELIANCE
🏢 Reliance Industries
💰 Value: ₹5000.00 Crores
📝 Petrochemical complex setup

💎 Total Value: ₹7500.00 Crores

🔔 Showing orders ≥ ₹500 Cr only
🤖 Automated update from NSE Order Book Tracker
```

### 2. Individual High-Value Alert
```
🚨 High-Value Order Alert! 🚨

🏢 Larsen & Toubro (LT)
📅 Date: 2026-05-28
💰 Value: ₹2500.00 Crores

📝 Major infrastructure project for metro construction

🔗 View Announcement

⚠️ This order exceeds ₹500 Cr threshold
🤖 NSE Order Book Tracker
```

### 3. Daily Digest
```
📊 Daily Order Book Digest

📅 Thursday, May 28, 2026

🔥 High-Value Orders (≥₹500 Cr):
• Count: 3
• Total Value: ₹7500.00 Cr

🏆 Top High-Value Orders:
1. RELIANCE: ₹5000.00 Cr
2. LT: ₹2500.00 Cr

🤖 Automated Daily Digest
```

## Security Best Practices

1. **Never share your bot token** - treat it like a password
2. **Don't commit tokens to Git** - use environment variables or GitHub Secrets
3. **Regenerate token if exposed**:
   - Go to @BotFather
   - Send `/mybots`
   - Select your bot
   - Choose "API Token" → "Regenerate"
4. **Limit bot permissions** - only give necessary permissions in group chats
5. **Use group chats for team alerts** - don't share personal chat IDs

## Advanced Configuration

### Multiple Recipients

To send to multiple users/groups, you can:

1. Create a Telegram group with all recipients
2. Add the bot to the group
3. Use the group chat ID

Or modify the code to send to multiple chat IDs:

```python
chat_ids = ['123456789', '-987654321']  # Personal + Group
for chat_id in chat_ids:
    notifier = TelegramNotifier(chat_id=chat_id)
    notifier.send_order_summary(orders)
```

### Custom Thresholds per Chat

```python
# VIP group gets all orders ≥ ₹500 Cr
vip_notifier = TelegramNotifier(
    chat_id='VIP_GROUP_ID',
    value_threshold=500.0
)

# Management group only gets ≥ ₹1000 Cr
mgmt_notifier = TelegramNotifier(
    chat_id='MGMT_GROUP_ID',
    value_threshold=1000.0
)
```

## Getting Help

If you encounter issues:

1. **Check the logs** - error messages usually explain the problem
2. **Test manually** - run `python telegram_notifier.py` to isolate issues
3. **Verify credentials** - make sure token and chat ID are correct
4. **Check Telegram API status** - visit status.telegram.org
5. **Read Telegram Bot API docs** - core.telegram.org/bots/api

## Next Steps

Once your Telegram bot is set up:

1. ✓ Test local notifications
2. ✓ Add secrets to GitHub
3. ✓ Run the GitHub Actions workflow
4. ✓ Verify you receive automated notifications

Your bot is now ready to send automated alerts for high-value NSE orders!
