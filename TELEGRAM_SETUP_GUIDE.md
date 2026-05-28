# Telegram Bot Setup Guide

## Step 1: Create the Bot

1. Open Telegram on your phone or computer
2. Search for **@BotFather**
3. Start a conversation and send: `/newbot`
4. Choose a name: **NSE Order Book Tracker** (or any name you like)
5. Choose a username: **nse_orderbook_tracker_bot** (must end with `_bot`)
6. BotFather will give you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
7. **Copy this token** - we'll need it

## Step 2: Get Your Chat ID

### Method 1: Using a Helper Bot (Easiest)
1. Search for **@userinfobot** on Telegram
2. Start a conversation
3. It will immediately show your chat ID (a number like `123456789`)
4. **Copy this number**

### Method 2: Manual Method
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
5. **Copy the id number**

## Step 3: Test the Bot

Once you have both:
- BOT_TOKEN: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- CHAT_ID: `123456789`

Test locally:
```bash
export TELEGRAM_BOT_TOKEN='your-token-here'
export TELEGRAM_CHAT_ID='your-chat-id-here'

cd nse-orderbook-tracker/scripts
python telegram_notifier.py
```

You should receive test messages on Telegram!

## For Group Notifications (Optional)

If you want notifications in a group:
1. Create a Telegram group
2. Add your bot to the group
3. Make the bot an admin (if needed)
4. Send a message in the group
5. Use the `/getUpdates` method above
6. The chat ID will be negative (like `-987654321`)
7. Use this negative number as your CHAT_ID

## Next: Add to GitHub Secrets

Once you have your credentials, we'll add them to GitHub secrets.
