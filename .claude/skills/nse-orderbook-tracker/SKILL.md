---
name: nse-orderbook-tracker
description: Build an automated NSE order book tracker for Nifty 50 companies that fetches future orders/unfilled order data from multiple sources (NSE/BSE announcements, concall transcripts, screener.in), displays trends in a professional web dashboard, and exports to Excel. Use this skill when the user wants to track company order books, monitor new contract wins, analyze order book trends, or needs a dashboard showing order backlog for Indian NSE-listed companies.
---

# NSE Order Book Tracker

Build a comprehensive order book tracking system for NSE Nifty 50 companies that aggregates data from multiple sources and presents it in a professional dashboard with Excel export capability.

## What This Skill Does

Creates an automated system to:
1. Monitor and fetch order book data (future orders/unfilled orders) from multiple sources
2. Track new order announcements and contract wins in real-time
3. Extract order book values from quarterly results and announcements
4. Display trends over the last 6 months in a professional web dashboard
5. Export all data to formatted Excel spreadsheets
6. **Run automated daily checks via GitHub Actions and send Telegram notifications**

## Understanding Order Book Data

**Order Book** refers to the total value of confirmed orders that a company has received but not yet executed/delivered. This is particularly relevant for:
- Capital goods companies (machinery, equipment manufacturers)
- Defense sector companies (HAL, BEL)
- Infrastructure and construction companies (L&T, IRCON)
- IT services companies (TCS, Infosys report TCV - Total Contract Value)
- Engineering and project-based businesses

Order book is a forward-looking indicator of future revenue and business pipeline.

## Data Sources Strategy

### Primary Sources

**1. NSE Corporate Announcements API** (Real-time order wins)
- Endpoint: `https://www.nseindia.com/api/corporate-announcements?index=equities`
- Provides real-time company announcements including order wins
- Free, no authentication required (needs proper User-Agent header)
- Returns JSON with PDF attachments containing detailed announcements

**2. BSE Announcements via BseIndiaApi**
- Python library: `pip install bse`
- Structured access to BSE corporate announcements
- Categories include general updates, results, board meetings
- Cross-validation source for NSE data

**3. Quarterly Results & Investor Presentations**
- Companies in capital-intensive sectors disclose order book in earnings presentations
- Available from company investor relations pages
- Often contain order book slides with quarter-over-quarter trends

### Optional/Enhancement Sources

**4. Screener.in** (Premium subscription)
- Some companies report historical order book data
- Particularly useful for defense, infrastructure, engineering sectors
- Requires premium subscription for operational metrics

**5. Conference Call Transcripts**
- Management discusses order book position in earnings calls
- Available from Trendlyne, company IR pages
- Requires NLP extraction of order book mentions

## Implementation Approach

Follow this phased approach to build the tracker:

### Phase 1: Data Collection Infrastructure

**1.1 Set up announcement monitoring**

Create a Python module that fetches announcements from NSE and BSE:

```python
# nse_fetcher.py
import requests
from datetime import datetime, timedelta

def fetch_nse_announcements(days_back=180):
    """Fetch NSE announcements for last N days"""
    url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def filter_order_announcements(announcements):
    """Filter for order-related announcements"""
    keywords = [
        'order', 'contract', 'win', 'award', 'awarded',
        'TCV', 'order book', 'secured', 'bagged', 'won contract'
    ]

    order_related = []
    for ann in announcements:
        text = (ann.get('attchmntText', '') + ' ' + ann.get('desc', '')).lower()
        if any(keyword in text for keyword in keywords):
            order_related.append(ann)

    return order_related
```

**1.2 Set up BSE data fetching**

```python
# bse_fetcher.py
from bse import BSE
from bse.constants import CATEGORY
from datetime import datetime, timedelta

def fetch_bse_announcements(scrip_code, months_back=6):
    """Fetch BSE announcements for a company"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months_back * 30)

    with BSE() as bse:
        announcements = bse.announcements(
            scripcode=scrip_code,
            from_date=start_date.strftime('%d-%m-%Y'),
            to_date=end_date.strftime('%d-%m-%Y'),
            category=CATEGORY.UPDATE
        )

    return announcements
```

**1.3 Get Nifty 50 company list**

Create a function to fetch current Nifty 50 constituents:

```python
# nifty50_companies.py
import requests
import pandas as pd

def get_nifty50_companies():
    """Fetch current Nifty 50 constituents"""
    # NSE provides this data
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    data = response.json()

    companies = []
    for stock in data['data']:
        companies.append({
            'symbol': stock['symbol'],
            'company_name': stock['meta']['companyName'],
            'industry': stock['meta']['industry']
        })

    return pd.DataFrame(companies)
```

### Phase 2: Data Extraction & Processing

**2.1 Extract order values from announcements**

When announcements contain order values, they're typically in formats like:
- "Rs. 500 crore"
- "Rs 2,500 Cr"
- "₹1000 crores"
- "USD 50 million"

Create extraction logic:

```python
# value_extractor.py
import re

def extract_order_value(text):
    """Extract order value from announcement text"""
    patterns = [
        r'Rs\.?\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|crores)',
        r'₹\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|crores)',
        r'INR\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|crores|million)',
        r'USD\s*([\d,]+(?:\.\d+)?)\s*(million|billion)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1).replace(',', ''))
            unit = match.group(2).lower()
            currency = 'INR' if any(x in pattern for x in ['Rs', '₹', 'INR']) else 'USD'

            # Normalize to INR crores
            if 'million' in unit:
                value = value / 10  # Rough conversion
            elif currency == 'USD':
                value = value * 83 / 100  # Convert USD to INR crores (approx)

            return {
                'value': value,
                'currency': 'INR',
                'unit': 'Crores',
                'original_text': match.group(0)
            }

    return None
```

**2.2 Download and parse PDF attachments**

Many announcements have PDF attachments with detailed information:

```python
# pdf_parser.py
import requests
import pdfplumber

def download_and_parse_pdf(pdf_url):
    """Download NSE announcement PDF and extract text"""
    response = requests.get(pdf_url)

    with open('temp_announcement.pdf', 'wb') as f:
        f.write(response.content)

    text = ""
    with pdfplumber.open('temp_announcement.pdf') as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text
```

**2.3 Parse quarterly results for order book data**

Some companies directly report order book in results:

```python
# quarterly_parser.py
def parse_order_book_from_results(company_symbol):
    """
    Extract order book from quarterly results
    Look for earnings presentations, investor presentations
    """
    # This would involve:
    # 1. Fetching latest quarterly result announcement from NSE/BSE
    # 2. Downloading investor presentation PDF
    # 3. Scanning for "Order Book" slide
    # 4. Extracting the value

    # Implementation depends on company-specific formats
    pass
```

### Phase 3: Database & Storage

Store collected data for historical tracking:

```python
# database.py
import sqlite3
from datetime import datetime

def init_database():
    """Create database schema for order book tracking"""
    conn = sqlite3.connect('orderbook_tracker.db')
    cursor = conn.cursor()

    # Announcements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            company_name TEXT,
            announcement_date DATE NOT NULL,
            source TEXT,
            category TEXT,
            description TEXT,
            order_value REAL,
            currency TEXT,
            pdf_url TEXT,
            extracted_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Order book snapshots table (quarterly)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_book_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            company_name TEXT,
            quarter TEXT,
            fiscal_year INTEGER,
            order_book_value REAL,
            currency TEXT,
            source TEXT,
            reported_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def save_announcement(symbol, company_name, date, source, description,
                      order_value=None, pdf_url=None, extracted_text=None):
    """Save announcement to database"""
    conn = sqlite3.connect('orderbook_tracker.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO announcements
        (symbol, company_name, announcement_date, source, description,
         order_value, currency, pdf_url, extracted_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (symbol, company_name, date, source, description,
          order_value, 'INR', pdf_url, extracted_text))

    conn.commit()
    conn.close()
```

### Phase 4: Dashboard Creation

Build a professional web dashboard using HTML, JavaScript, and charting libraries.

**4.1 Backend API**

Create a Flask API to serve data:

```python
# app.py
from flask import Flask, jsonify, render_template, send_file
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/companies')
def get_companies():
    """Get list of all tracked companies"""
    conn = sqlite3.connect('orderbook_tracker.db')
    query = "SELECT DISTINCT symbol, company_name FROM announcements ORDER BY symbol"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return jsonify(df.to_dict('records'))

@app.route('/api/orders/<symbol>')
def get_company_orders(symbol):
    """Get all orders for a company in last 6 months"""
    conn = sqlite3.connect('orderbook_tracker.db')
    six_months_ago = (datetime.now() - timedelta(days=180)).date()

    query = """
        SELECT announcement_date, description, order_value, source
        FROM announcements
        WHERE symbol = ? AND announcement_date >= ?
        ORDER BY announcement_date DESC
    """
    df = pd.read_sql_query(query, conn, params=(symbol, six_months_ago))
    conn.close()
    return jsonify(df.to_dict('records'))

@app.route('/api/summary')
def get_summary():
    """Get summary statistics for all companies"""
    conn = sqlite3.connect('orderbook_tracker.db')

    query = """
        SELECT
            symbol,
            company_name,
            COUNT(*) as order_count,
            SUM(order_value) as total_order_value,
            MAX(announcement_date) as latest_order_date
        FROM announcements
        WHERE announcement_date >= date('now', '-6 months')
        GROUP BY symbol, company_name
        ORDER BY total_order_value DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return jsonify(df.to_dict('records'))

@app.route('/api/export')
def export_to_excel():
    """Export all data to Excel"""
    conn = sqlite3.connect('orderbook_tracker.db')

    # Read all data
    announcements_df = pd.read_sql_query(
        "SELECT * FROM announcements WHERE announcement_date >= date('now', '-6 months')",
        conn
    )

    summary_df = pd.read_sql_query("""
        SELECT
            symbol,
            company_name,
            COUNT(*) as order_count,
            SUM(order_value) as total_order_value,
            MAX(announcement_date) as latest_order_date
        FROM announcements
        WHERE announcement_date >= date('now', '-6 months')
        GROUP BY symbol, company_name
    """, conn)

    conn.close()

    # Create Excel file
    excel_path = 'orderbook_export.xlsx'
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        announcements_df.to_excel(writer, sheet_name='All Orders', index=False)

        # Format sheets
        workbook = writer.book
        for sheet in workbook.sheetnames:
            worksheet = workbook[sheet]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

    return send_file(excel_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**4.2 Frontend Dashboard**

Create a professional HTML dashboard with charts:

```html
<!-- templates/dashboard.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NSE Order Book Tracker - Nifty 50</title>

    <!-- Chart.js for visualizations -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>

    <!-- DataTables for professional table display -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .controls {
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }

        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(56, 239, 125, 0.4);
        }

        .content {
            padding: 30px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .stat-card h3 {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }

        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
        }

        .chart-container {
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .chart-container h2 {
            margin-bottom: 20px;
            color: #333;
        }

        table.dataTable {
            width: 100%;
            border-collapse: collapse;
        }

        table.dataTable thead th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }

        table.dataTable tbody td {
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }

        table.dataTable tbody tr:hover {
            background: #f8f9fa;
        }

        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.2em;
            color: #667eea;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 NSE Order Book Tracker</h1>
            <p>Real-time Order Book Monitoring for Nifty 50 Companies</p>
        </div>

        <div class="controls">
            <div>
                <button class="btn btn-primary" onclick="refreshData()">🔄 Refresh Data</button>
                <button class="btn btn-success" onclick="exportToExcel()">📥 Export to Excel</button>
            </div>
            <div>
                <span id="lastUpdated" style="color: #666;"></span>
            </div>
        </div>

        <div class="content">
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>Loading order book data...</p>
            </div>

            <div id="dashboard" style="display: none;">
                <!-- Statistics Cards -->
                <div class="stats-grid">
                    <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                        <h3>Total Companies Tracked</h3>
                        <div class="value" id="totalCompanies">0</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                        <h3>Total Order Value (Cr)</h3>
                        <div class="value" id="totalOrderValue">0</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                        <h3>Orders in Last 6 Months</h3>
                        <div class="value" id="totalOrders">0</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                        <h3>Latest Update</h3>
                        <div class="value" style="font-size: 1.5em;" id="latestUpdate">Today</div>
                    </div>
                </div>

                <!-- Top Companies Chart -->
                <div class="chart-container">
                    <h2>🏆 Top 10 Companies by Order Book Value</h2>
                    <canvas id="topCompaniesChart"></canvas>
                </div>

                <!-- Orders Timeline Chart -->
                <div class="chart-container">
                    <h2>📈 Order Announcements Timeline</h2>
                    <canvas id="timelineChart"></canvas>
                </div>

                <!-- Detailed Table -->
                <div class="chart-container">
                    <h2>📋 Detailed Order Book Data</h2>
                    <table id="ordersTable" class="display">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Company Name</th>
                                <th>Order Count</th>
                                <th>Total Value (Cr)</th>
                                <th>Latest Order Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let summaryData = [];

        async function loadData() {
            try {
                const response = await fetch('/api/summary');
                summaryData = await response.json();

                displayStatistics();
                renderCharts();
                populateTable();

                document.getElementById('loading').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('lastUpdated').textContent =
                    `Last updated: ${new Date().toLocaleString()}`;
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('loading').innerHTML =
                    '<p style="color: red;">Error loading data. Please try again.</p>';
            }
        }

        function displayStatistics() {
            const totalCompanies = summaryData.length;
            const totalOrderValue = summaryData.reduce((sum, item) =>
                sum + (item.total_order_value || 0), 0);
            const totalOrders = summaryData.reduce((sum, item) =>
                sum + (item.order_count || 0), 0);

            document.getElementById('totalCompanies').textContent = totalCompanies;
            document.getElementById('totalOrderValue').textContent =
                totalOrderValue.toFixed(0);
            document.getElementById('totalOrders').textContent = totalOrders;
        }

        function renderCharts() {
            // Top Companies Chart
            const top10 = summaryData
                .sort((a, b) => (b.total_order_value || 0) - (a.total_order_value || 0))
                .slice(0, 10);

            const ctx1 = document.getElementById('topCompaniesChart').getContext('2d');
            new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: top10.map(item => item.symbol),
                    datasets: [{
                        label: 'Order Value (Crores)',
                        data: top10.map(item => item.total_order_value || 0),
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Value in Crores'
                            }
                        }
                    }
                }
            });

            // Timeline Chart (placeholder - would need actual date-wise data)
            const ctx2 = document.getElementById('timelineChart').getContext('2d');
            new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Monthly Order Announcements',
                        data: [12, 19, 15, 25, 22, 30],
                        borderColor: 'rgba(118, 75, 162, 1)',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: true
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        function populateTable() {
            const tableBody = document.getElementById('tableBody');
            tableBody.innerHTML = '';

            summaryData.forEach(item => {
                const row = `
                    <tr>
                        <td><strong>${item.symbol}</strong></td>
                        <td>${item.company_name || '-'}</td>
                        <td>${item.order_count || 0}</td>
                        <td>₹${(item.total_order_value || 0).toFixed(2)}</td>
                        <td>${item.latest_order_date || '-'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 6px 12px; font-size: 0.9em;"
                                    onclick="viewDetails('${item.symbol}')">
                                View Details
                            </button>
                        </td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });

            $('#ordersTable').DataTable({
                order: [[3, 'desc']],
                pageLength: 25
            });
        }

        function viewDetails(symbol) {
            alert(`Loading detailed order history for ${symbol}...`);
            // This would open a modal or navigate to detail page
        }

        async function refreshData() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('dashboard').style.display = 'none';
            await loadData();
        }

        async function exportToExcel() {
            window.location.href = '/api/export';
        }

        // Load data on page load
        window.onload = loadData;
    </script>
</body>
</html>
```

### Phase 5: Automation & Scheduling

Set up automated data collection that runs periodically:

```python
# scheduler.py
import schedule
import time
from nse_fetcher import fetch_nse_announcements, filter_order_announcements
from value_extractor import extract_order_value
from database import save_announcement
from nifty50_companies import get_nifty50_companies

def collect_order_data():
    """Main data collection job"""
    print(f"Starting data collection at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Get Nifty 50 companies
    nifty50 = get_nifty50_companies()
    nifty50_symbols = set(nifty50['symbol'].tolist())

    # Fetch NSE announcements
    announcements = fetch_nse_announcements()
    order_announcements = filter_order_announcements(announcements)

    # Process each announcement
    for ann in order_announcements:
        symbol = ann.get('symbol', '')

        # Only process Nifty 50 companies
        if symbol not in nifty50_symbols:
            continue

        # Extract order value
        text = ann.get('attchmntText', '') + ' ' + ann.get('desc', '')
        order_info = extract_order_value(text)

        # Save to database
        save_announcement(
            symbol=symbol,
            company_name=ann.get('sm_name', ''),
            date=ann.get('an_dt', ''),
            source='NSE',
            description=ann.get('attchmntText', ''),
            order_value=order_info['value'] if order_info else None
        )

        print(f"Saved order announcement for {symbol}")

    print(f"Data collection completed. Processed {len(order_announcements)} announcements.")

def run_scheduler():
    """Run the scheduler"""
    # Run immediately on start
    collect_order_data()

    # Schedule periodic runs
    schedule.every(30).minutes.do(collect_order_data)  # Every 30 minutes

    print("Scheduler started. Press Ctrl+C to stop.")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    run_scheduler()
```

### Phase 6: Enhancement Features

**Conference Call Transcript Analysis** (Optional)

If the user wants to extract order book mentions from concall transcripts:

```python
# concall_analyzer.py
import re

def analyze_concall_for_orderbook(transcript_text):
    """
    Extract order book related information from conference call transcript
    """
    # Split into Q&A and management commentary sections
    sections = transcript_text.split('\n\n')

    order_book_mentions = []

    for section in sections:
        # Look for order book patterns
        patterns = [
            r'order book.*?(?:stands at|is|totaling|worth)\s*Rs\.?\s*([\d,]+)\s*crore',
            r'outstanding orders.*?Rs\.?\s*([\d,]+)\s*crore',
            r'order backlog.*?Rs\.?\s*([\d,]+)\s*crore',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, section, re.IGNORECASE)
            for match in matches:
                order_book_mentions.append({
                    'value': float(match.group(1).replace(',', '')),
                    'context': match.group(0),
                    'section': section[:200]  # First 200 chars for context
                })

    return order_book_mentions
```

### Phase 7: GitHub Actions Automation with Telegram Notifications

Set up automated daily order checking that runs on GitHub Actions and sends alerts via Telegram.

**Why GitHub Actions?**
- Free for public repositories (2,000 minutes/month for private repos)
- No server maintenance required
- Reliable scheduled execution
- Persistent storage via git commits
- Easy to monitor and debug

**7.1 Set up Telegram Bot**

Before implementing automation, create a Telegram bot:

1. **Create Bot:**
   - Message `@BotFather` on Telegram
   - Send `/newbot` and follow instructions
   - Choose a name and username for your bot
   - Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Chat ID:**
   - Start a conversation with your bot
   - Send any message to it
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Look for `"chat":{"id": YOUR_CHAT_ID}` in the JSON response
   - Your chat ID is a number (e.g., `123456789`)

3. **For Group Notifications (Optional):**
   - Add your bot to a group
   - Make it an admin (if needed)
   - Get the group chat ID from `/getUpdates` (will be negative, e.g., `-987654321`)

**7.2 Configure GitHub Secrets**

Add Telegram credentials to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add two secrets:
   - Name: `TELEGRAM_BOT_TOKEN`, Value: Your bot token
   - Name: `TELEGRAM_CHAT_ID`, Value: Your chat ID

**7.3 GitHub Actions Workflow**

The workflow file `.github/workflows/daily-order-check.yml` is already provided in the skill. It:

- Runs daily at 9:30 AM IST (4:00 AM UTC) - after market opens
- Can be manually triggered via "Actions" tab
- Also runs on push to test changes
- Uses Python 3.11
- Caches dependencies for faster execution
- Stores processed announcements to avoid duplicate notifications
- Commits the processed announcements file back to repo

**Key features of the workflow:**

```yaml
on:
  schedule:
    - cron: '0 4 * * *'  # Daily at 9:30 AM IST
  workflow_dispatch:      # Manual trigger
  push:                   # Auto-test on changes
```

**7.4 Daily Order Checker Script**

The `daily_order_checker.py` script orchestrates the entire process:

**Flow:**
1. Load previously processed announcements (to avoid duplicates)
2. Fetch Nifty 50 company list
3. Fetch latest NSE announcements
4. Filter for order-related announcements
5. Extract order values using regex
6. Send Telegram notification with new orders
7. Save processed announcement IDs
8. Send individual alerts for high-value orders (>1000 Cr)

**Duplicate Prevention:**
- Each announcement gets a unique ID: `{symbol}_{date}_{filename}`
- IDs are stored in `processed_announcements.json`
- File is committed back to repo after each run
- Only new announcements trigger notifications

**7.5 Notification Formats**

**Daily Summary Notification:**
```
📊 Order Book Update - Nifty 50

📅 Date: 2026-05-28
📈 Total Orders: 5

1. TCS
💰 Value: ₹500.00 Cr
📝 Won digital transformation project from Fortune 500 client

2. LT
💰 Value: ₹2500.00 Cr
📝 Secured major infrastructure project for metro construction

💎 Total Value: ₹3000.00 Crores

🤖 Automated update from NSE Order Book Tracker
```

**High-Value Alert (>1000 Cr):**
```
🚨 New Order Alert!

🏢 Larsen & Toubro (LT)
📅 Date: 2026-05-28
💰 Value: 2500.00 Crores

📝 Secured major infrastructure project for metro construction

🔗 View Announcement

🤖 NSE Order Book Tracker
```

**7.6 Testing the Automation**

**Local Testing:**

1. Set environment variables:
```bash
export TELEGRAM_BOT_TOKEN='your-bot-token'
export TELEGRAM_CHAT_ID='your-chat-id'
```

2. Test Telegram connection:
```bash
cd scripts
python telegram_notifier.py
```

3. Run the daily checker:
```bash
python daily_order_checker.py
```

4. Verify you receive the notification on Telegram

**GitHub Actions Testing:**

1. Push the code to GitHub
2. Go to "Actions" tab in your repository
3. Click on "Daily Order Book Check" workflow
4. Click "Run workflow" to trigger manually
5. Wait for execution (takes 1-2 minutes)
6. Check Telegram for notification
7. Check workflow logs for any errors

**7.7 Monitoring and Debugging**

**View Workflow Runs:**
- Go to "Actions" tab to see all runs
- Green checkmark = success
- Red X = failure

**Debug Failed Runs:**
- Click on the failed run
- Click on "check-orders" job
- Expand steps to see detailed logs
- Common issues:
  - Telegram credentials not set → Check GitHub Secrets
  - NSE API timeout → Will retry next run
  - Value extraction errors → Check announcement format

**Error Notifications:**
The script automatically sends error alerts to Telegram when something goes wrong:
```
⚠️ Order Tracker Error

Error during daily check:
<error details>
```

**7.8 Customization Options**

**Change Schedule:**
Edit the cron expression in `.github/workflows/daily-order-check.yml`:
```yaml
# Run at different time (e.g., 6 PM IST = 12:30 PM UTC)
- cron: '30 12 * * *'

# Run twice daily (9 AM and 6 PM IST)
- cron: '30 3,12 * * *'

# Run every 6 hours
- cron: '0 */6 * * *'
```

**Filter by Company:**
Modify `daily_order_checker.py` to track specific companies:
```python
# Only track specific symbols
watchlist = {'TCS', 'INFY', 'LT', 'RELIANCE', 'HDFCBANK'}
nifty50_symbols = nifty50_symbols.intersection(watchlist)
```

**Filter by Sector:**
```python
# Only track IT companies
it_companies = [c for c in companies if 'IT' in c.get('industry', '')]
nifty50_symbols = {c['symbol'] for c in it_companies}
```

**Adjust Value Threshold for Alerts:**
```python
# Send individual alerts for orders > 500 Cr instead of 1000 Cr
if order.get('order_value', 0) > 500:
    self.telegram.send_company_alert(order)
```

**7.9 Advanced Features**

**Weekly Digest:**
Add a separate workflow for weekly summaries:

```yaml
# .github/workflows/weekly-digest.yml
name: Weekly Order Digest
on:
  schedule:
    - cron: '0 14 * * 0'  # Sunday 7:30 PM IST
  workflow_dispatch:
```

**Multi-Channel Notifications:**
Send to multiple Telegram groups:
```python
# In telegram_notifier.py
def send_to_multiple_channels(self, message, chat_ids):
    for chat_id in chat_ids:
        self.chat_id = chat_id
        self.send_message(message)
```

**Slack Integration:**
Replace Telegram with Slack webhooks:
```python
# slack_notifier.py
def send_slack_message(webhook_url, message):
    response = requests.post(
        webhook_url,
        json={'text': message}
    )
```

**Email Notifications:**
Add email alerts for critical orders:
```python
# email_notifier.py
import smtplib
from email.message import EmailMessage

def send_email_alert(order):
    msg = EmailMessage()
    msg['Subject'] = f"New Order: {order['symbol']}"
    msg['From'] = 'tracker@example.com'
    msg['To'] = 'your-email@example.com'
    msg.set_content(f"Order Value: ₹{order['order_value']} Cr")

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('username', 'password')
        smtp.send_message(msg)
```

**7.10 Cost and Limits**

**GitHub Actions:**
- **Free tier:** 2,000 minutes/month (more than enough for daily runs)
- **Each run:** ~2 minutes
- **Monthly usage:** ~60 minutes (running once daily)
- **Well within free limits**

**Telegram API:**
- Completely free
- Rate limits: 30 messages/second
- More than sufficient for this use case

**NSE/BSE APIs:**
- No rate limits documented
- Be respectful: don't run more frequently than every 15 minutes

**7.11 Production Best Practices**

1. **Error Handling:**
   - All API calls have try-catch blocks
   - Telegram error notifications
   - Workflow artifacts uploaded on failure

2. **Duplicate Prevention:**
   - Announcement IDs tracked in git
   - Prevents same notification twice
   - Survives across workflow runs

3. **Logging:**
   - Detailed logs for debugging
   - Timestamps for all operations
   - Log levels (INFO, ERROR)

4. **Testing:**
   - Manual workflow trigger for testing
   - Local test scripts
   - Dry-run mode option

5. **Maintenance:**
   - Monitor workflow runs weekly
   - Update dependencies monthly
   - Review error patterns

**7.12 Implementation Steps for Automation**

When the user requests GitHub Actions automation:

1. Ensure all base scripts are created:
   - `nse_data_fetcher.py`
   - `value_extractor.py`
   - `telegram_notifier.py`
   - `daily_order_checker.py`

2. Create `.github/workflows/daily-order-check.yml`

3. Guide user to:
   - Create Telegram bot
   - Get bot token and chat ID
   - Add secrets to GitHub

4. Test locally first:
   ```bash
   cd scripts
   export TELEGRAM_BOT_TOKEN='...'
   export TELEGRAM_CHAT_ID='...'
   python telegram_notifier.py  # Test connection
   python daily_order_checker.py  # Test full flow
   ```

5. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Add GitHub Actions automation"
   git push
   ```

6. Trigger workflow manually from Actions tab

7. Verify notification received on Telegram

8. Monitor daily runs for a week

9. Customize as needed (schedule, filters, thresholds)

**Common Issues:**

| Issue | Solution |
|-------|----------|
| Workflow doesn't run | Check cron syntax, ensure workflow file in `.github/workflows/` |
| Telegram notification fails | Verify secrets are set correctly, test bot token |
| Duplicate notifications | Ensure `processed_announcements.json` is being committed |
| NSE API 403 error | Update User-Agent header, add retry logic |
| No orders found | Normal if no new announcements, optional "no updates" message |

## Key Success Factors

1. **Reliable Data Collection**: The NSE/BSE APIs must be monitored with proper error handling and retry logic
2. **Accurate Value Extraction**: Regular expressions and NLP must be tested against real announcements
3. **Data Quality**: Implement validation to ensure extracted values make sense (e.g., flag values > 100,000 crores as suspicious)
4. **User Experience**: Dashboard should load quickly and provide clear, actionable insights
5. **Export Quality**: Excel exports should be well-formatted with proper column widths, headers, and formatting

## Implementation Checklist

When building this system, ensure you:

- [ ] Install required dependencies: `flask`, `requests`, `pandas`, `openpyxl`, `bse`, `pdfplumber`, `schedule`
- [ ] Create database schema with proper indexes
- [ ] Implement NSE announcement fetching with proper headers
- [ ] Set up BSE announcement fetching for cross-validation
- [ ] Build value extraction with comprehensive regex patterns
- [ ] Create Flask API endpoints for all data access
- [ ] Design professional dashboard with responsive layout
- [ ] Implement Chart.js visualizations for trends
- [ ] Set up DataTables for sortable/searchable data grid
- [ ] Create Excel export with proper formatting
- [ ] Test with real Nifty 50 company data
- [ ] Set up scheduler for automated data collection
- [ ] Add error logging and monitoring
- [ ] **Create Telegram bot and get credentials**
- [ ] **Set up GitHub Actions workflow for daily automation**
- [ ] **Implement Telegram notification system**
- [ ] **Test automation locally and on GitHub Actions**
- [ ] Document the system for future maintenance

## Testing Strategy

Test the system with these scenarios:

1. **New Order Announcement**: Simulate NSE/BSE announcing a new order win for a Nifty 50 company
2. **Quarterly Results**: Test extraction of order book from quarterly result PDFs
3. **Multiple Orders Same Day**: Verify system handles multiple announcements for same company
4. **Value Extraction Edge Cases**: Test with different formats (lakhs, crores, millions, billions)
5. **Dashboard Performance**: Load dashboard with 6 months of historical data
6. **Excel Export**: Verify all data exports correctly with proper formatting

## Maintenance Considerations

- NSE/BSE website changes may break scraping logic - monitor error logs
- Announcement formats may vary by company - continuously improve extraction patterns
- Database may grow large over time - implement archival strategy
- Dashboard performance may degrade with large datasets - consider pagination
- Exchange APIs may have rate limits - implement respectful request throttling

## Expected Output Structure

When the user triggers this skill, you should deliver:

1. **Project structure**:
   ```
   orderbook_tracker/
   ├── app.py (Flask application)
   ├── nse_fetcher.py
   ├── bse_fetcher.py
   ├── value_extractor.py
   ├── pdf_parser.py
   ├── database.py
   ├── nifty50_companies.py
   ├── scheduler.py
   ├── orderbook_tracker.db (SQLite database)
   ├── templates/
   │   └── dashboard.html
   ├── requirements.txt
   └── README.md
   ```

2. **Running instructions** in README
3. **Sample data** for testing
4. **Excel export** template showing expected format

## Common Issues and Solutions

**Issue**: NSE API returns 403 Forbidden
**Solution**: Use proper User-Agent header and potentially rotate headers

**Issue**: Order values not extracted correctly
**Solution**: Review announcement text format and update regex patterns

**Issue**: Dashboard loads slowly
**Solution**: Implement caching, pagination, or database indexes

**Issue**: Excel export fails for large datasets
**Solution**: Use streaming export or split into multiple sheets

**Issue**: Missing order book data for some companies
**Solution**: Not all companies report order book; focus on capital-intensive sectors

---

When the user invokes this skill, ask clarifying questions if needed, then systematically implement each phase. Start with Phase 1 (data collection infrastructure), test it with real Nifty 50 companies, then proceed to subsequent phases. Show progress and results at each stage.
