#!/usr/bin/env python3
"""
Flask Backend for NSE Order Book Dashboard
Serves real data from processed announcements and fetched orders
"""

from flask import Flask, jsonify, send_file, render_template_string
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from unified_data_fetcher import UnifiedDataFetcher
    from value_extractor import OrderValueExtractor
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    UnifiedDataFetcher = None
    OrderValueExtractor = None

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Paths
PROCESSED_FILE = os.path.join('scripts', 'processed_announcements.json')
DASHBOARD_FILE = 'dashboard.html'


def load_processed_announcements():
    """Load processed announcements from cache file"""
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            return json.load(f)
    return []


def fetch_live_data():
    """Fetch fresh data from NSE/BSE"""
    try:
        if not UnifiedDataFetcher or not OrderValueExtractor:
            return None

        fetcher = UnifiedDataFetcher(prefer_bse=True)
        extractor = OrderValueExtractor()

        # Fetch companies
        companies = fetcher.fetch_nifty50_companies()
        nifty50_symbols = {comp['symbol'] for comp in companies}

        # Fetch announcements (last 30 days)
        announcements = fetcher.fetch_announcements(days_back=30)

        # Filter for order-related
        order_announcements = fetcher.filter_order_announcements(
            announcements,
            nifty50_symbols
        )

        # Process announcements
        processed_data = []
        for ann in order_announcements:
            text = (
                ann.get('attchmntText', '') + ' ' +
                ann.get('desc', '') + ' ' +
                ann.get('subject', '')
            )
            value_info = extractor.extract_value(text)

            processed_data.append({
                'symbol': ann.get('symbol'),
                'company_name': ann.get('sm_name'),
                'announcement_date': ann.get('an_dt'),
                'description': ann.get('attchmntText', '')[:300],
                'order_value': value_info['value'] if value_info else None,
                'source': ann.get('source', 'Unknown')
            })

        return processed_data
    except Exception as e:
        print(f"Error fetching live data: {e}")
        return None


def get_mock_data():
    """Fallback mock data if live fetch fails"""
    return [
        {'symbol': 'TCS', 'company_name': 'Tata Consultancy Services', 'order_value': 500, 'announcement_date': '2026-05-20', 'description': 'Won digital transformation project', 'source': 'BSE'},
        {'symbol': 'RELIANCE', 'company_name': 'Reliance Industries', 'order_value': 1200, 'announcement_date': '2026-05-25', 'description': 'New refinery equipment order', 'source': 'BSE'},
        {'symbol': 'LT', 'company_name': 'Larsen & Toubro', 'order_value': 2500, 'announcement_date': '2026-05-22', 'description': 'Metro rail infrastructure project', 'source': 'NSE'},
        {'symbol': 'INFY', 'company_name': 'Infosys', 'order_value': 450, 'announcement_date': '2026-05-18', 'description': 'Cloud migration project', 'source': 'BSE'},
        {'symbol': 'WIPRO', 'company_name': 'Wipro', 'order_value': 350, 'announcement_date': '2026-05-19', 'description': 'IT services contract', 'source': 'BSE'},
        {'symbol': 'HCLTECH', 'company_name': 'HCL Technologies', 'order_value': 400, 'announcement_date': '2026-05-21', 'description': 'Software development order', 'source': 'BSE'},
        {'symbol': 'ONGC', 'company_name': 'ONGC', 'order_value': 680, 'announcement_date': '2026-05-23', 'description': 'Offshore drilling equipment', 'source': 'NSE'},
        {'symbol': 'MARUTI', 'company_name': 'Maruti Suzuki', 'order_value': 375, 'announcement_date': '2026-05-17', 'description': 'Vehicle supply order', 'source': 'NSE'},
    ]


def aggregate_company_data(announcements):
    """Aggregate announcements by company"""
    company_data = defaultdict(lambda: {
        'order_count': 0,
        'total_order_value': 0,
        'orders': [],
        'latest_order_date': None,
        'symbol': None,
        'company_name': None,
        'source': None
    })

    for ann in announcements:
        symbol = ann['symbol']
        company_data[symbol]['symbol'] = symbol
        company_data[symbol]['company_name'] = ann['company_name']
        company_data[symbol]['order_count'] += 1
        company_data[symbol]['source'] = ann.get('source', 'Unknown')

        if ann.get('order_value'):
            company_data[symbol]['total_order_value'] += ann['order_value']

        company_data[symbol]['orders'].append(ann)

        # Track latest order date
        ann_date = ann.get('announcement_date')
        if ann_date:
            if not company_data[symbol]['latest_order_date'] or ann_date > company_data[symbol]['latest_order_date']:
                company_data[symbol]['latest_order_date'] = ann_date

    return [data for data in company_data.values()]


def assign_sectors(companies):
    """Assign sectors to companies based on symbol"""
    sector_mapping = {
        'TCS': 'IT', 'INFY': 'IT', 'WIPRO': 'IT', 'HCLTECH': 'IT', 'TECHM': 'IT',
        'RELIANCE': 'Energy', 'ONGC': 'Energy', 'BPCL': 'Energy',
        'LT': 'Infrastructure', 'ADANIPORTS': 'Infrastructure',
        'HDFCBANK': 'Banking', 'ICICIBANK': 'Banking', 'SBIN': 'Banking', 'KOTAKBANK': 'Banking', 'AXISBANK': 'Banking',
        'MARUTI': 'Auto', 'TATAMOTORS': 'Auto', 'BAJAJ-AUTO': 'Auto', 'EICHERMOT': 'Auto', 'HEROMOTOCO': 'Auto',
        'HINDUNILVR': 'FMCG', 'ITC': 'FMCG', 'BRITANNIA': 'FMCG', 'NESTLEIND': 'FMCG', 'TATACONSUM': 'FMCG',
        'SUNPHARMA': 'Pharma', 'DRREDDY': 'Pharma', 'CIPLA': 'Pharma', 'DIVISLAB': 'Pharma',
        'NTPC': 'Power', 'POWERGRID': 'Power', 'COALINDIA': 'Power',
    }

    for company in companies:
        symbol = company['symbol']
        company['sector'] = sector_mapping.get(symbol, 'Others')

    return companies


@app.route('/')
def index():
    """Serve the dashboard HTML"""
    with open(DASHBOARD_FILE, 'r') as f:
        return f.read()


@app.route('/api/summary')
def get_summary():
    """Get aggregated company data"""
    try:
        # Try to fetch live data first
        announcements = fetch_live_data()

        # If live fetch fails, use mock data
        if not announcements or len(announcements) == 0:
            print("Using mock data (live fetch returned no results)")
            announcements = get_mock_data()

        # Aggregate by company
        companies = aggregate_company_data(announcements)

        # Assign sectors
        companies = assign_sectors(companies)

        # Sort by total order value
        companies.sort(key=lambda x: x['total_order_value'], reverse=True)

        return jsonify(companies)

    except Exception as e:
        print(f"Error in /api/summary: {e}")
        # Return mock data on error
        return jsonify(aggregate_company_data(get_mock_data()))


@app.route('/api/orders/<symbol>')
def get_company_orders(symbol):
    """Get all orders for a specific company"""
    try:
        announcements = fetch_live_data()

        if not announcements:
            announcements = get_mock_data()

        # Filter for specific company
        company_orders = [ann for ann in announcements if ann['symbol'] == symbol]

        # Sort by date (newest first)
        company_orders.sort(key=lambda x: x.get('announcement_date', ''), reverse=True)

        return jsonify(company_orders)

    except Exception as e:
        print(f"Error in /api/orders/{symbol}: {e}")
        return jsonify([])


@app.route('/api/timeline')
def get_timeline():
    """Get recent orders in timeline format"""
    try:
        announcements = fetch_live_data()

        if not announcements:
            announcements = get_mock_data()

        # Filter for orders with values
        timeline = [ann for ann in announcements if ann.get('order_value')]

        # Sort by date (newest first)
        timeline.sort(key=lambda x: x.get('announcement_date', ''), reverse=True)

        # Limit to recent 20
        timeline = timeline[:20]

        # Format for timeline display
        formatted = []
        for ann in timeline:
            formatted.append({
                'symbol': ann['symbol'],
                'company_name': ann['company_name'],
                'value': ann['order_value'],
                'date': ann['announcement_date'],
                'description': ann['description'],
                'source': ann.get('source', 'Unknown')
            })

        return jsonify(formatted)

    except Exception as e:
        print(f"Error in /api/timeline: {e}")
        return jsonify([])


@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    try:
        announcements = fetch_live_data()

        if not announcements:
            announcements = get_mock_data()

        companies = aggregate_company_data(announcements)

        total_companies = len(companies)
        total_orders = sum(c['order_count'] for c in companies)
        total_value = sum(c['total_order_value'] for c in companies)
        avg_order = total_value / total_orders if total_orders > 0 else 0

        return jsonify({
            'total_companies': total_companies,
            'total_orders': total_orders,
            'total_value': total_value,
            'avg_order': avg_order,
            'last_updated': datetime.now().isoformat(),
            'data_source': 'Live' if announcements != get_mock_data() else 'Demo'
        })

    except Exception as e:
        print(f"Error in /api/stats: {e}")
        return jsonify({
            'total_companies': 0,
            'total_orders': 0,
            'total_value': 0,
            'avg_order': 0,
            'last_updated': datetime.now().isoformat(),
            'data_source': 'Error'
        })


@app.route('/api/refresh')
def refresh_data():
    """Force refresh data from sources"""
    try:
        announcements = fetch_live_data()

        if announcements and len(announcements) > 0:
            return jsonify({
                'success': True,
                'message': f'Fetched {len(announcements)} announcements',
                'count': len(announcements)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data fetched, using cached/demo data',
                'count': 0
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'count': 0
        })


@app.route('/api/export')
def export_to_excel():
    """Export data to Excel"""
    try:
        announcements = fetch_live_data()

        if not announcements:
            announcements = get_mock_data()

        companies = aggregate_company_data(announcements)

        # Create DataFrames
        summary_df = pd.DataFrame([{
            'Symbol': c['symbol'],
            'Company': c['company_name'],
            'Order Count': c['order_count'],
            'Total Value (Cr)': c['total_order_value'],
            'Avg Value (Cr)': c['total_order_value'] / c['order_count'] if c['order_count'] > 0 else 0,
            'Latest Order': c['latest_order_date'],
            'Source': c.get('source', 'Unknown')
        } for c in companies])

        announcements_df = pd.DataFrame([{
            'Symbol': ann['symbol'],
            'Company': ann['company_name'],
            'Date': ann['announcement_date'],
            'Value (Cr)': ann.get('order_value', 0),
            'Description': ann['description'],
            'Source': ann.get('source', 'Unknown')
        } for ann in announcements])

        # Export to Excel
        excel_path = 'orderbook_export.xlsx'
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            announcements_df.to_excel(writer, sheet_name='All Orders', index=False)

            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
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

        return send_file(excel_path, as_attachment=True, download_name=f'nse_orderbook_{datetime.now().strftime("%Y%m%d")}.xlsx')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'modules_loaded': {
            'UnifiedDataFetcher': UnifiedDataFetcher is not None,
            'OrderValueExtractor': OrderValueExtractor is not None
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("NSE Order Book Dashboard - Flask Backend")
    print("=" * 60)
    print(f"\nDashboard URL: http://localhost:5000")
    print(f"API Endpoints:")
    print(f"  - http://localhost:5000/api/summary")
    print(f"  - http://localhost:5000/api/timeline")
    print(f"  - http://localhost:5000/api/stats")
    print(f"  - http://localhost:5000/api/export")
    print(f"\nPress Ctrl+C to stop")
    print("=" * 60)
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
