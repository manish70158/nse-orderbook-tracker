# Telegram Message Format Examples

This document shows exactly what you'll see in Telegram with the new table format and interactive buttons.

---

## Message 1: Dashboard Summary with Table

```
📊 NSE Order Book Tracker - Daily Report
━━━━━━━━━━━━━━━━━━━━━

🕐 Last Updated: 2026-05-30 14:30:00
📅 Period: Last 3 days

📈 SUMMARY
━━━━━━━━━━━━━━━━━━━━━
📋 Total Announcements: 5
💰 Total Order Value: ₹5,750.00 Cr
📊 Average Order Size: ₹1,150.00 Cr
🏢 Unique Companies: 5

📋 ORDER DETAILS (Table Format)
━━━━━━━━━━━━━━━━━━━━━

╔═══════════════════════════════════════════════╗
║  #  Symbol    Value(Cr)  Date        PDF      ║
╠═══════════════════════════════════════════════╣
║  1  TCS       🔵 450.0  05-28   ✓     ║
║  2  LT        🟢2500.0  05-29   ✓     ║
║  3  RELIANCE  🟢1800.0  05-29   ✓     ║
║  4  WIPRO     🔵 380.0  05-30   ✗     ║
║  5  INFY      🟡 620.0  05-30   ✓     ║
╚═══════════════════════════════════════════════╝

Showing 5 of 5 orders (top by date)

📋 DETAILED VIEW (Top 5)
━━━━━━━━━━━━━━━━━━━━━

1. TCS - Tata Consultancy Services
   📅 2026-05-28  💰 🔵 ₹450.00 Cr
   📝 Awarding of Order - Digital Transformation Project...
   📄 ✓ PDF

2. LT - Larsen & Toubro Limited
   📅 2026-05-29  💰 🟢 ₹2,500.00 Cr
   📝 Order Book Update - Major Metro Rail Infrastructure...
   📄 ✓ PDF

3. RELIANCE - Reliance Industries Limi
   📅 2026-05-29  💰 🟢 ₹1,800.00 Cr
   📝 Contract Award - Petrochemical Manufacturing...
   📄 ✓ PDF

4. WIPRO - Wipro Limited
   📅 2026-05-30  💰 🔵 ₹380.00 Cr
   📝 Order Received - IT Modernization and Cloud...
   📄 ✗ No PDF

5. INFY - Infosys Limited
   📅 2026-05-30  💰 🟡 ₹620.00 Cr
   📝 New Contract - Enterprise Digital Solutions...
   📄 ✓ PDF

━━━━━━━━━━━━━━━━━━━━━
📊 Total: 5 order(s)
🔔 Threshold: ≥₹500 Cr for alerts

🤖 Automated Daily Report
```

---

## Message 2: Interactive Menu with Buttons

```
🔍 Quick Access Menu

Select a date range to fetch fresh data:
• Get latest orders for your chosen period
• Receive updated report instantly

Note: This requires manual trigger via dashboard
Visit: http://your-dashboard-url.com
```

**Interactive Buttons (clickable):**

```
┌─────────────────────────────────────────┐
│  📅 Last 1 Week  │  📅 Last 2 Weeks     │
├─────────────────────────────────────────┤
│  📅 Last 1 Month  │  📅 Last 3 Months   │
├─────────────────────────────────────────┤
│         🌐 Open Dashboard               │
└─────────────────────────────────────────┘
```

**What happens when you click:**
- Each button opens your dashboard URL in browser
- You can then use the web interface to fetch data

---

## Message 3: High-Value Alerts

```
🚨 High-Value Order Alert 🚨

📅 Date: 2026-05-28 to 2026-05-30
📈 Orders Above ₹500 Cr: 3

1. LT
🏢 Larsen & Toubro Limited
💰 Value: ₹2,500.00 Crores
📝 Order Book Update - Major Metro Rail Infrastructure Project

2. RELIANCE
🏢 Reliance Industries Limited
💰 Value: ₹1,800.00 Crores
📝 Contract Award - Petrochemical Manufacturing Facility

3. INFY
🏢 Infosys Limited
💰 Value: ₹620.00 Crores
📝 New Contract - Enterprise Digital Solutions

💎 Total Value: ₹4,920.00 Crores

🔔 Showing orders ≥ ₹500 Cr only
```

---

## Message 4+: PDF Attachments

For each high-value order:

```
📄 LT - Larsen & Toubro Limited
💰 ₹2,500.00 Crores

[PDF file: NSE_LT_20260529.pdf]
```

---

## Legend

**Color Indicators in Table:**
- 🟢 = High value (>₹100 Cr)
- 🟡 = Medium value (₹50-100 Cr)
- 🔵 = Low value (<₹50 Cr)

**PDF Status:**
- ✓ = PDF available
- ✗ = No PDF

**Table Features:**
- Monospace formatting for alignment
- Box-drawing characters for borders
- Fixed-width columns for readability
- Top 15 orders shown in table
- Top 5 orders shown in detailed view

---

## How It Works

1. **Daily at 9:30 AM IST:**
   - Message 1: Dashboard summary with table
   - Message 2: Interactive menu with buttons
   - Message 3: High-value order alerts
   - Messages 4+: PDF attachments for each high-value order

2. **Interactive Buttons:**
   - Click any button to open dashboard in browser
   - Use web interface for advanced filtering
   - Buttons are always visible (don't expire)

3. **Table Format:**
   - Uses `<pre>` HTML tag for monospace
   - Box-drawing characters: ╔ ║ ═ ╗ etc.
   - Fixed column widths for alignment
   - Emoji indicators for quick scanning

---

## Test It Now

Run the test script to see the actual Telegram messages:

```bash
cd scripts/nse_order_tracker_v2
source venv/bin/activate

# Make sure credentials are set
export TELEGRAM_BOT_TOKEN='your-token'
export TELEGRAM_CHAT_ID='your-chat-id'

# Run test
python test_telegram_dashboard.py
```

Check your Telegram to see:
1. ✅ Table format with borders
2. ✅ Interactive buttons
3. ✅ Color-coded values
4. ✅ PDF status indicators

---

## Notes

- **Table width:** Optimized for mobile Telegram app
- **Message length:** Splits into chunks if >15 orders
- **Button links:** Update URLs in `telegram_notifier.py` line ~380
- **Formatting:** Uses HTML (supported by Telegram)
- **Monospace:** `<pre>` tag ensures alignment

---

**Questions?**

- Table not aligned? Check if Telegram displays monospace fonts correctly
- Buttons not working? Verify URLs are set in the code
- Colors not showing? Make sure your Telegram supports emojis

