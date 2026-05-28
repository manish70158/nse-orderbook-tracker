# 🚀 Start Your Live Dashboard

## Quick Start (2 Steps)

### Step 1: Install Dependencies (if not done already)

```bash
pip install flask flask-cors pandas openpyxl
```

### Step 2: Start the Flask Backend

```bash
python app.py
```

You should see:

```
============================================================
NSE Order Book Dashboard - Flask Backend
============================================================

Dashboard URL: http://localhost:5000
API Endpoints:
  - http://localhost:5000/api/summary
  - http://localhost:5000/api/timeline
  - http://localhost:5000/api/stats
  - http://localhost:5000/api/export

Press Ctrl+C to stop
============================================================

 * Running on http://0.0.0.0:5000
```

### Step 3: Open Dashboard

**Option A:** Click the URL
```
http://localhost:5000
```

**Option B:** Open directly
```bash
open http://localhost:5000
```

---

## 📊 How It Works

```
┌─────────────────────────────────────────┐
│   Your Browser                          │
│   http://localhost:5000                 │
└──────────────┬──────────────────────────┘
               │
               │ HTTP Request
               ▼
┌─────────────────────────────────────────┐
│   Flask Backend (app.py)                │
│   Port: 5000                            │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌─────────────┐ ┌──────────────┐
│ BSE API     │ │ NSE API      │
│ (Primary)   │ │ (Fallback)   │
└──────┬──────┘ └──────┬───────┘
       │               │
       └───────┬───────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Real Order Book Data                  │
│   - Live from BSE/NSE                   │
│   - Or Demo data if APIs blocked       │
└─────────────────────────────────────────┘
```

---

## 🎯 Data Flow

### 1. Dashboard Loads
- HTML fetches from `/api/summary`
- Gets aggregated company data
- Renders charts and tables

### 2. Backend Fetches Data
The Flask app tries in order:

**Priority 1: Live Data**
```python
unified_data_fetcher.py
  ├─ Try BSE API first (more reliable)
  ├─ Fallback to NSE API
  └─ Return aggregated results
```

**Priority 2: Demo Data**
If APIs fail (blocked by bot protection):
```python
Uses mock data with realistic values
```

### 3. Data Aggregation
```python
# Raw announcements → Aggregated by company
announcements = [
  {'symbol': 'TCS', 'order_value': 500, 'date': '2026-05-20'},
  {'symbol': 'TCS', 'order_value': 300, 'date': '2026-05-18'},
  {'symbol': 'LT', 'order_value': 2500, 'date': '2026-05-22'}
]

# Becomes:
companies = [
  {
    'symbol': 'TCS',
    'company_name': 'Tata Consultancy Services',
    'order_count': 2,
    'total_order_value': 800,
    'latest_order_date': '2026-05-20',
    'sector': 'IT',
    'source': 'BSE'
  },
  {
    'symbol': 'LT',
    'company_name': 'Larsen & Toubro',
    'order_count': 1,
    'total_order_value': 2500,
    'latest_order_date': '2026-05-22',
    'sector': 'Infrastructure',
    'source': 'NSE'
  }
]
```

---

## 🔌 API Endpoints

### GET `/api/summary`
Returns aggregated company data

**Response:**
```json
[
  {
    "symbol": "TCS",
    "company_name": "Tata Consultancy Services",
    "order_count": 5,
    "total_order_value": 2500,
    "latest_order_date": "2026-05-20",
    "sector": "IT",
    "source": "BSE",
    "orders": [...]
  }
]
```

### GET `/api/timeline`
Returns recent orders chronologically

**Response:**
```json
[
  {
    "symbol": "LT",
    "company_name": "Larsen & Toubro",
    "value": 2500,
    "date": "2026-05-22",
    "description": "Metro rail project",
    "source": "NSE"
  }
]
```

### GET `/api/stats`
Returns overall statistics

**Response:**
```json
{
  "total_companies": 10,
  "total_orders": 48,
  "total_value": 25600,
  "avg_order": 533.33,
  "last_updated": "2026-05-28T10:30:00",
  "data_source": "Live"
}
```

### GET `/api/export`
Downloads Excel file with all data

**Returns:** `nse_orderbook_20260528.xlsx`

### GET `/api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-28T10:30:00",
  "modules_loaded": {
    "UnifiedDataFetcher": true,
    "OrderValueExtractor": true
  }
}
```

---

## 🎨 Dashboard Features

### Real-Time Data
- ✅ Fetches from `/api/summary` on load
- ✅ Shows data source (Live/Demo)
- ✅ Displays last updated timestamp

### Interactive Charts
- **Top Companies Bar Chart** - Top 10 by order value
- **Monthly Trend Line** - Order flow over time
- **Sector Pie Chart** - Distribution by sector
- **Sector Bar Chart** - Comparative performance

### Data Table
- Sortable columns
- Search functionality
- Pagination (25 per page)
- Export to Excel

### Timeline View
- Recent announcements
- Chronological order
- Value and description

---

## 🔄 Refresh Data

### Manual Refresh
Click the "↻ Refresh" button in dashboard

### Programmatic Refresh
```javascript
fetch('/api/refresh')
  .then(r => r.json())
  .then(data => console.log(data));
```

### Auto-Refresh (Optional)
Add to dashboard HTML:
```javascript
// Auto-refresh every 5 minutes
setInterval(() => {
  refreshData();
}, 5 * 60 * 1000);
```

---

## 🐛 Troubleshooting

### Issue: "Flask backend not running"

**Solution:** Start Flask:
```bash
python app.py
```

### Issue: "No data displayed"

**Causes:**
1. NSE/BSE APIs blocked (normal)
2. No orders fetched yet

**Solutions:**
- Backend will use demo data automatically
- Run `python scripts/daily_order_checker.py` to fetch real data
- Check logs in terminal

### Issue: "Port 5000 already in use"

**Solution:** Kill existing process:
```bash
# Find process
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port
python app.py --port 5001
```

### Issue: "CORS errors in browser console"

**Solution:** flask-cors is installed and enabled
```bash
pip install flask-cors
```

### Issue: "Module not found"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📈 Get Real Data

### Option 1: Run Daily Checker
```bash
cd scripts
export TELEGRAM_BOT_TOKEN='your-token'
export TELEGRAM_CHAT_ID='your-chat-id'
python daily_order_checker.py
```

This fetches live data from BSE/NSE.

### Option 2: Let GitHub Actions Run
- GitHub Actions runs daily at 9:30 AM IST
- Fetches data automatically
- Dashboard shows latest when you refresh

### Option 3: Mock Data (Default)
- If APIs fail, backend uses realistic demo data
- You can still explore all features
- Charts and tables work perfectly

---

## 🔧 Configuration

### Change Port
Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Changed from 5000
```

### Enable Debug Mode
Already enabled in development:
```python
app.run(debug=True)  # Auto-reloads on code changes
```

### Production Mode
For production deployment:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

Or use gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🚀 Production Deployment

### Deploy to Cloud

**Heroku:**
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create nse-orderbook-dashboard
git push heroku main
```

**Railway:**
```bash
# Connect GitHub repo
# Railway auto-detects Flask app
# Click deploy
```

**Render:**
```bash
# Connect GitHub repo
# Set build command: pip install -r requirements.txt
# Set start command: gunicorn app:app
```

### Environment Variables
For production:
```bash
export FLASK_ENV=production
export TELEGRAM_BOT_TOKEN='your-token'
export TELEGRAM_CHAT_ID='your-chat-id'
```

---

## 📊 Data Sources

### Priority Order:
1. **BSE API** (Primary) - More reliable
2. **NSE API** (Fallback) - If BSE fails
3. **Demo Data** (Last resort) - If both APIs blocked

### Data Freshness:
- **Live fetch**: Real-time from APIs
- **Daily checker**: Runs at 9:30 AM IST
- **Manual fetch**: Run anytime

---

## ✅ Verification

After starting Flask, verify:

**1. Backend Running**
```bash
curl http://localhost:5000/api/health
```

Should return:
```json
{"status": "healthy", ...}
```

**2. Data Available**
```bash
curl http://localhost:5000/api/summary
```

Should return array of companies.

**3. Dashboard Loading**
Open http://localhost:5000 in browser
Should see beautiful terminal-style dashboard!

---

## 🎉 Success!

Your dashboard is now connected to live data!

**What's Happening:**
- ✅ Flask backend serving data
- ✅ Dashboard fetching from API
- ✅ Charts rendering real values
- ✅ Table showing actual companies
- ✅ Timeline displaying recent orders

**Next Steps:**
1. Run daily checker to populate with real data
2. Enable GitHub Actions for automation
3. Deploy to cloud for 24/7 access

---

**Questions?** Check the logs in your terminal where Flask is running!
