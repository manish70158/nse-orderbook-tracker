# 📎 Telegram PDF Attachments Feature

## Overview

The V2 NSE Order Book Tracker now automatically attaches PDF files to Telegram notifications for high-value orders. This allows you to receive both the alert message and the original announcement PDF directly in your Telegram chat.

---

## 🎯 Key Features

- **Automatic PDF Attachments**: PDFs are sent along with order alerts
- **Smart Filtering**: Only high-value orders (≥₹500 Cr) include PDFs
- **Captioned Documents**: Each PDF includes company name and order value
- **Non-Blocking**: If PDF send fails, the text alert is still delivered
- **Bandwidth Efficient**: PDFs are sent only for relevant high-value orders

---

## 📤 How It Works

### Message Flow

When a high-value order is detected:

1. **Text Alert Sent First**
   - Summary message with all high-value orders
   - Company names, values, descriptions
   - Quick overview without downloads

2. **PDF Attachments Follow**
   - One PDF per high-value order
   - Each PDF has a caption with company and value
   - Sent as Telegram documents (not images)
   - Can be viewed directly in Telegram or downloaded

### Example Telegram Notification

```
🚨 High-Value Order Alert 🚨

📅 Date: 2026-05-28
📈 Orders Above ₹500 Cr: 2

1. LT
🏢 Larsen & Toubro
💰 Value: ₹2,500.00 Crores
📝 Secured major infrastructure project...

2. RELIANCE
🏢 Reliance Industries
💰 Value: ₹1,200.00 Crores
📝 Petrochemical plant expansion...

💎 Total Value: ₹3,700.00 Crores

🔔 Showing orders ≥ ₹500 Cr only

[Followed by 2 PDF attachments]
📄 LT - Larsen & Toubro
💰 ₹2,500.00 Crores

📄 RELIANCE - Reliance Industries
💰 ₹1,200.00 Crores
```

---

## ⚙️ Configuration

### Enable/Disable PDF Attachments

PDF attachments are **enabled by default**. To disable:

#### In Code

```python
from telegram_notifier import TelegramNotifier

notifier = TelegramNotifier(value_threshold=500.0)

# Send summary WITHOUT PDFs
notifier.send_order_summary(
    orders,
    date="2026-05-28",
    filter_by_value=True,
    attach_pdfs=False  # Disable PDF attachments
)
```

#### In Orchestrator

The orchestrator automatically includes PDFs by default. To modify:

```python
# In orchestrator.py, line ~334
success = self.notifier.send_order_summary(
    telegram_orders,
    date=date_range,
    filter_by_value=True,
    attach_pdfs=True  # Change to False to disable
)
```

---

## 📋 Requirements

### Telegram Bot Permissions

Your Telegram bot must have permission to:
- Send messages (already required)
- Send documents/files (usually enabled by default)

No additional configuration needed - if your bot can send messages, it can send documents.

### File Size Limits

Telegram has file size limits:
- **Bots**: 50 MB per file
- **Typical NSE PDFs**: 200-800 KB

NSE announcement PDFs are typically well under 1 MB, so size limits are not a concern.

---

## 🛠️ Technical Details

### API Methods Used

1. **sendMessage** - For text alerts
   ```
   POST https://api.telegram.org/bot{TOKEN}/sendMessage
   ```

2. **sendDocument** - For PDF attachments
   ```
   POST https://api.telegram.org/bot{TOKEN}/sendDocument
   ```

### PDF Path Resolution

The system automatically handles PDF paths:

```python
# In orchestrator.py
telegram_orders.append({
    'symbol': 'LIKHITHA',
    'company_name': 'Likhitha Infrastructure',
    'order_value': 121.04,
    'description': 'Awarding of Order',
    'pdf_path': 'downloads/nse_pdfs/LIKHITHA_2026-05-28.pdf'  # Local path
})
```

### Error Handling

```python
def send_document(self, file_path: str, caption: str = None) -> bool:
    """
    Robust PDF sending with error handling:
    - Checks if file exists before sending
    - Validates file path
    - Handles network errors gracefully
    - Logs failures without crashing
    """
```

**Failure Scenarios:**
- PDF file not found → Warning logged, continues
- Network timeout → Warning logged, continues
- Invalid file format → Warning logged, continues
- Text alert always sent regardless of PDF status

---

## 📊 Performance Impact

### Message Count

**Before PDF Attachments:**
- 1 message per batch (summary)

**After PDF Attachments:**
- 1 message (summary) + N documents (one per high-value order)

**Example:** 3 high-value orders = 4 Telegram API calls
- 1 text message
- 3 PDF documents

### Bandwidth Usage

| Component | Size per Order | Example (3 orders) |
|-----------|---------------|-------------------|
| Text message | ~500 bytes | 1.5 KB |
| PDF files | ~500 KB each | 1.5 MB |
| **Total** | - | **~1.5 MB** |

**Note:** PDFs are only sent for filtered high-value orders, not all announcements.

### Timing

- Text message: ~1 second
- Each PDF: ~2-3 seconds (upload time)
- **Total for 3 orders: ~7-10 seconds**

All sending happens sequentially to avoid rate limits.

---

## 🧪 Testing PDF Attachments

### Test Script

```python
#!/usr/bin/env python3
"""Test Telegram PDF attachment functionality"""

import os
from telegram_notifier import TelegramNotifier

# Ensure credentials are set
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

if not bot_token or not chat_id:
    print("❌ Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
    exit(1)

# Initialize notifier
notifier = TelegramNotifier(value_threshold=100.0)  # Lower threshold for testing

# Test order with PDF path
test_order = {
    'symbol': 'LIKHITHA',
    'company_name': 'Likhitha Infrastructure',
    'order_value': 121.04,
    'description': 'Awarding of order for infrastructure project',
    'announcement_date': '2026-05-28',
    'pdf_path': 'downloads/nse_pdfs/LIKHITHA_2026-05-28.pdf'
}

# Test 1: Send summary with PDF
print("Test 1: Sending order summary with PDF attachment...")
success = notifier.send_order_summary(
    [test_order],
    date='2026-05-28',
    filter_by_value=False,  # Don't filter for testing
    attach_pdfs=True
)
print(f"✓ Summary sent: {success}\n")

# Test 2: Send individual alert with PDF
print("Test 2: Sending individual company alert with PDF...")
success = notifier.send_company_alert(test_order, attach_pdf=True)
print(f"✓ Alert sent: {success}\n")

# Test 3: Send without PDF
print("Test 3: Sending without PDF attachment...")
success = notifier.send_order_summary(
    [test_order],
    date='2026-05-28',
    filter_by_value=False,
    attach_pdfs=False  # No PDF
)
print(f"✓ No-PDF summary sent: {success}\n")

print("✅ All tests complete!")
```

Save as `test_telegram_pdf.py` and run:

```bash
cd scripts/nse_order_tracker_v2
source venv/bin/activate
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python test_telegram_pdf.py
```

### Manual Testing

```bash
# Run scraper with Telegram enabled
python orchestrator.py --days 1

# Check logs for PDF attachment status
# Look for: "Sent X PDF attachment(s)"
```

---

## 🚨 Troubleshooting

### PDFs Not Attaching

**Problem:** Text alerts work, but PDFs don't appear

**Possible Causes:**

1. **PDF file doesn't exist**
   ```bash
   # Check if PDFs were downloaded
   ls -lh downloads/nse_pdfs/*.pdf
   ```

2. **Wrong path in data**
   ```python
   # Verify local_pdf_path is included
   print(item.get('local_pdf_path'))
   ```

3. **File too large** (unlikely for NSE PDFs)
   ```bash
   # Check file size
   du -h downloads/nse_pdfs/*.pdf
   ```

4. **Bot permissions**
   - Telegram bots can send files by default
   - Check bot settings with @BotFather if needed

### Timeout Errors

**Problem:** "Failed to send document: timeout"

**Solution:**
- Increase timeout in `send_document()` (default: 30 seconds)
- Check network connection
- PDFs are sent sequentially, so 5+ PDFs may take time

### Rate Limiting

**Problem:** "Too many requests" error from Telegram

**Solution:**
- Telegram allows ~30 messages/second per bot
- Our sequential sending prevents this
- If hitting limits, increase delay between PDFs

---

## 💡 Best Practices

### 1. Keep Threshold High

```python
# Good: Only high-value orders get PDFs
notifier = TelegramNotifier(value_threshold=500.0)

# Bad: Too many PDFs, clutters chat
notifier = TelegramNotifier(value_threshold=10.0)
```

### 2. Monitor PDF Cleanup

PDFs are auto-deleted after 7 days by default. Ensure cleanup is working:

```bash
# Check PDF directory size
du -sh downloads/nse_pdfs/

# Should stay under 50-100 MB with cleanup
```

### 3. Verify in GitHub Actions

When running automated daily jobs, check workflow logs:

```yaml
# Should see in logs:
# "Sent 2 PDF attachment(s)"
# "PDF attached for SYMBOL"
```

### 4. Handle Missing PDFs Gracefully

Code already handles missing PDFs gracefully:
- Text alert always sent
- Missing PDFs logged as warnings
- Process continues without failing

---

## 📝 API Reference

### TelegramNotifier Methods

#### `send_document(file_path, caption=None, parse_mode="HTML")`

Send a PDF document to Telegram.

**Parameters:**
- `file_path` (str): Absolute or relative path to PDF
- `caption` (str, optional): Text caption (supports HTML)
- `parse_mode` (str): "HTML" or "Markdown"

**Returns:**
- `bool`: True if successful

**Example:**
```python
success = notifier.send_document(
    "downloads/nse_pdfs/COMPANY_2026-05-28.pdf",
    caption="<b>COMPANY</b> - ₹500 Cr"
)
```

#### `send_order_summary(orders, date=None, filter_by_value=True, attach_pdfs=True)`

Send order summary with optional PDF attachments.

**Parameters:**
- `orders` (List[Dict]): Order dictionaries with 'pdf_path' key
- `date` (str, optional): Date string for summary
- `filter_by_value` (bool): Filter by threshold (default: True)
- `attach_pdfs` (bool): Attach PDF files (default: True)

**Returns:**
- `bool`: True if successful

#### `send_company_alert(company_order, attach_pdf=True)`

Send individual company alert with optional PDF.

**Parameters:**
- `company_order` (Dict): Order dictionary with 'pdf_path' key
- `attach_pdf` (bool): Attach PDF file (default: True)

**Returns:**
- `bool`: True if successful, False if below threshold

---

## 🔗 Related Documentation

- **V2_SETUP_COMPLETE.md** - Main V2 setup guide
- **PDF_CLEANUP_GUIDE.md** - PDF cleanup and retention
- **docs/TELEGRAM_SETUP_GUIDE.md** - Telegram bot setup
- **telegram_notifier.py** - Source code with full implementation

---

## 📊 Summary

| Feature | Status | Details |
|---------|--------|---------|
| PDF Attachments | ✅ Enabled | Automatic for high-value orders |
| Caption Support | ✅ Enabled | Company name + order value |
| Error Handling | ✅ Robust | Non-blocking, logs warnings |
| File Size Limit | ✅ No Issue | NSE PDFs typically < 1 MB |
| Performance Impact | ✅ Minimal | ~2-3 sec per PDF |
| Configuration | ✅ Flexible | Can enable/disable per call |
| Backward Compatible | ✅ Yes | Existing code works without changes |

**Default Behavior:** PDF attachments are **automatically enabled** for all high-value orders (≥₹500 Cr).

No configuration needed - it just works! 🎉
