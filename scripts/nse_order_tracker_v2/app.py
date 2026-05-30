#!/usr/bin/env python3
"""
Flask Dashboard Application for NSE Order Book Tracker
Serves REST API and web interface
"""

from flask import Flask, jsonify, send_file, render_template_string, render_template, request
from flask_cors import CORS
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from io import BytesIO

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure for longer requests (data fetching can take time)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Configuration
DATA_FILE = Path('output/orderbook_data.json')
SUMMARY_FILE = Path('output/summary.json')
HTML_FILE = Path('dashboard.html')


def load_data():
    """Load orderbook data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []


def load_summary():
    """Load summary data from JSON file"""
    if SUMMARY_FILE.exists():
        with open(SUMMARY_FILE, 'r') as f:
            return json.load(f)
    return {}


def get_demo_data():
    """Generate demo data when no real data is available"""
    return [
        {
            'symbol': 'TCS',
            'company_name': 'Tata Consultancy Services',
            'announcement_date': '2026-05-20',
            'subject': 'Awarding of Order - Digital Transformation Project',
            'order_value_crores': 450.0,
            'client_name': 'Government of India',
            'project_description': 'Digital transformation of government services',
            'confidence_score': 0.85,
            'source': 'Demo'
        },
        {
            'symbol': 'INFY',
            'company_name': 'Infosys Limited',
            'announcement_date': '2026-05-22',
            'subject': 'Order Win - Cloud Migration Services',
            'order_value_crores': 320.0,
            'client_name': 'Major Bank',
            'project_description': 'Cloud migration and modernization',
            'confidence_score': 0.90,
            'source': 'Demo'
        },
        {
            'symbol': 'LT',
            'company_name': 'Larsen & Toubro',
            'announcement_date': '2026-05-25',
            'subject': 'Awarding of Order - Infrastructure Project',
            'order_value_crores': 2500.0,
            'client_name': 'State Government',
            'project_description': 'Metro rail construction project',
            'confidence_score': 0.95,
            'source': 'Demo'
        },
        {
            'symbol': 'RELIANCE',
            'company_name': 'Reliance Industries',
            'announcement_date': '2026-05-26',
            'subject': 'Contract Award - Petrochemical Plant',
            'order_value_crores': 1800.0,
            'client_name': 'International Oil Company',
            'project_description': 'Petrochemical manufacturing facility',
            'confidence_score': 0.88,
            'source': 'Demo'
        },
        {
            'symbol': 'WIPRO',
            'company_name': 'Wipro Limited',
            'announcement_date': '2026-05-27',
            'subject': 'Order Received - IT Modernization',
            'order_value_crores': 275.0,
            'client_name': 'Healthcare Provider',
            'project_description': 'Healthcare IT system upgrade',
            'confidence_score': 0.82,
            'source': 'Demo'
        }
    ]


@app.route('/')
def index():
    """Serve the dashboard HTML"""
    try:
        # Load data
        orders = load_data()
        summary = load_summary()

        # Use demo data if no real data
        if not orders:
            logger.info("No real data found, using demo data")
            orders = get_demo_data()
            # Calculate demo summary
            valid_orders = [d for d in orders if d.get('order_value_crores', 0) > 0]
            summary = {
                'total_announcements': len(orders),
                'total_value_crores': sum(d['order_value_crores'] for d in valid_orders),
                'average_order_value': sum(d['order_value_crores'] for d in valid_orders) / len(valid_orders) if valid_orders else 0,
                'unique_companies': len(set(d['symbol'] for d in orders)),
                'days': 7
            }

        # Render the dashboard template
        return render_template('dashboard.html',
                             orders=orders,
                             summary=summary,
                             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NSE Order Book Tracker</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; }
            .status { color: #27ae60; font-weight: bold; }
            .error { color: #e74c3c; }
            pre { background: #ecf0f1; padding: 15px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>NSE Order Book Tracker</h1>
            <p class="status">Backend is running!</p>
            <h2>Dashboard not found</h2>
            <p>Please ensure <code>dashboard.html</code> is in the same directory as <code>app.py</code></p>
            <h3>API Endpoints:</h3>
            <ul>
                <li><a href="/api/data">/api/data</a> - Get all order data</li>
                <li><a href="/api/summary">/api/summary</a> - Get summary statistics</li>
                <li><a href="/api/timeline">/api/timeline</a> - Get timeline data</li>
                <li><a href="/api/stats">/api/stats</a> - Get dashboard stats</li>
                <li><a href="/api/export">/api/export</a> - Download Excel</li>
                <li><a href="/api/health">/api/health</a> - Health check</li>
            </ul>
        </div>
    </body>
    </html>
    """)


@app.route('/api/data')
def get_data():
    """Get all orderbook data"""
    try:
        data = load_data()

        # Use demo data if no real data
        if not data:
            logger.info("No real data found, using demo data")
            data = get_demo_data()

        return jsonify({
            'success': True,
            'count': len(data),
            'data': data
        })

    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': get_demo_data()
        }), 200  # Still return 200 with demo data


@app.route('/api/summary')
def get_summary():
    """Get summary statistics"""
    try:
        data = load_data() or get_demo_data()

        # Calculate summary
        valid_orders = [d for d in data if d.get('order_value_crores') and d['order_value_crores'] > 0]

        # Group by company
        company_data = {}
        for order in valid_orders:
            symbol = order['symbol']
            if symbol not in company_data:
                company_data[symbol] = {
                    'symbol': symbol,
                    'company_name': order.get('company_name', symbol),
                    'total_orders': 0,
                    'total_value': 0.0,
                    'orders': []
                }

            company_data[symbol]['total_orders'] += 1
            company_data[symbol]['total_value'] += order['order_value_crores']
            company_data[symbol]['orders'].append({
                'date': order.get('announcement_date'),
                'value': order['order_value_crores'],
                'subject': order.get('subject', '')[:80]
            })

        # Sort by total value
        companies = sorted(
            company_data.values(),
            key=lambda x: x['total_value'],
            reverse=True
        )

        return jsonify({
            'success': True,
            'companies': companies
        })

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/timeline')
def get_timeline():
    """Get timeline data for recent orders"""
    try:
        data = load_data() or get_demo_data()

        # Filter and sort by date
        timeline = [
            {
                'date': d.get('announcement_date'),
                'symbol': d.get('symbol'),
                'company': d.get('company_name'),
                'value': d.get('order_value_crores'),
                'subject': d.get('subject', '')[:100]
            }
            for d in data
            if d.get('order_value_crores')
        ]

        timeline.sort(key=lambda x: x['date'], reverse=True)

        return jsonify({
            'success': True,
            'timeline': timeline[:20]  # Last 20
        })

    except Exception as e:
        logger.error(f"Error generating timeline: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats')
def get_stats():
    """Get overall statistics for dashboard"""
    try:
        data = load_data() or get_demo_data()

        valid_orders = [d for d in data if d.get('order_value_crores') and d['order_value_crores'] > 0]

        stats = {
            'total_announcements': len(data),
            'total_orders': len(valid_orders),
            'total_value': sum(d['order_value_crores'] for d in valid_orders),
            'average_value': sum(d['order_value_crores'] for d in valid_orders) / len(valid_orders) if valid_orders else 0,
            'max_value': max((d['order_value_crores'] for d in valid_orders), default=0),
            'companies': len(set(d['symbol'] for d in data)),
            'last_updated': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Error generating stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export')
def export_excel():
    """Export data to Excel"""
    try:
        data = load_data() or get_demo_data()

        # Create DataFrame
        df = pd.DataFrame(data)

        # Select and reorder columns
        columns = [
            'symbol', 'company_name', 'announcement_date',
            'order_value_crores', 'subject', 'client_name',
            'project_description', 'confidence_score', 'source'
        ]
        existing_cols = [col for col in columns if col in df.columns]
        df = df[existing_cols]

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Order Book', index=False)

        output.seek(0)

        # Generate filename with date
        filename = f"orderbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error exporting Excel: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'NSE Order Book Tracker',
        'timestamp': datetime.now().isoformat(),
        'data_file_exists': DATA_FILE.exists(),
        'html_file_exists': HTML_FILE.exists()
    })


@app.route('/api/pdf/<filename>')
def serve_pdf(filename):
    """Serve PDF files from downloads directory"""
    try:
        pdf_dir = Path('downloads/nse_pdfs')
        pdf_path = pdf_dir / filename

        # Security: Ensure file is within pdf directory (prevent directory traversal)
        if not pdf_path.resolve().is_relative_to(pdf_dir.resolve()):
            logger.warning(f"Attempted directory traversal: {filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file path'
            }), 403

        # Check if file exists
        if not pdf_path.exists():
            logger.warning(f"PDF not found: {filename}")
            return jsonify({
                'success': False,
                'error': 'PDF file not found'
            }), 404

        # Serve the PDF file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=False,  # Display in browser, not download
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error serving PDF {filename}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Trigger data refresh (placeholder for future automation)"""
    return jsonify({
        'success': True,
        'message': 'Manual refresh not yet implemented. Run orchestrator.py to update data.'
    })


@app.route('/api/fetch-data', methods=['POST'])
def fetch_data():
    """
    Fetch fresh data from NSE API for specified date range
    Expects JSON: {"days": 7, "threshold": 500, "enable_telegram": false}
    """
    try:
        # Get parameters from request
        data = request.get_json() or {}
        days = data.get('days', 7)
        threshold = data.get('threshold', 500)
        enable_telegram = data.get('enable_telegram', False)

        # Validate days parameter
        if not isinstance(days, int) or days < 1 or days > 365:
            return jsonify({
                'success': False,
                'error': 'Days must be between 1 and 365'
            }), 400

        logger.info("="*80)
        logger.info(f"API FETCH REQUEST: {days} days, threshold: {threshold} Cr")
        logger.info("="*80)

        # Import orchestrator modules
        try:
            from orchestrator import OrderBookOrchestrator
            logger.info("✓ Orchestrator module imported successfully")
        except ImportError as e:
            logger.error(f"✗ Failed to import orchestrator: {e}")
            return jsonify({
                'success': False,
                'error': 'Orchestrator module not found. Ensure orchestrator.py is in the same directory.'
            }), 500

        # Create orchestrator instance
        try:
            logger.info(f"Creating orchestrator instance (Telegram: {enable_telegram})...")
            orchestrator = OrderBookOrchestrator(
                enable_telegram=enable_telegram,
                value_threshold=threshold
            )
            logger.info("✓ Orchestrator instance created")
        except Exception as e:
            logger.error(f"✗ Failed to create orchestrator: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Failed to initialize orchestrator: {str(e)}'
            }), 500

        # Run the pipeline
        try:
            logger.info(f"Starting orchestrator pipeline for {days} days...")
            logger.info("This may take 10-60 seconds depending on the date range...")

            # Run with explicit parameter name
            orchestrator.run(
                search_term="awarding of order",
                days_back=days
            )

            logger.info("✓ Orchestrator pipeline completed successfully")
        except Exception as e:
            logger.error(f"✗ Orchestrator pipeline failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Pipeline execution failed: {str(e)}'
            }), 500

        # Load the fresh data
        try:
            logger.info("Loading fresh data from output files...")
            fresh_data = load_data()
            fresh_summary = load_summary()

            logger.info(f"✓ Loaded {len(fresh_data)} announcements")
            logger.info(f"✓ Total value: ₹{fresh_summary.get('total_value_crores', 0):.2f} Cr")
            logger.info("="*80)

        except Exception as e:
            logger.error(f"✗ Failed to load data: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Failed to load processed data: {str(e)}'
            }), 500

        return jsonify({
            'success': True,
            'message': f'Successfully fetched {len(fresh_data)} announcements from last {days} days',
            'data': fresh_data,
            'summary': fresh_summary,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'days_fetched': days
        })

    except Exception as e:
        logger.error(f"✗ Unexpected error in fetch_data endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500


if __name__ == '__main__':
    logger.info("="*60)
    logger.info("NSE ORDER BOOK TRACKER - DASHBOARD SERVER")
    logger.info("="*60)
    logger.info(f"Data file: {DATA_FILE} ({'exists' if DATA_FILE.exists() else 'not found'})")
    logger.info(f"HTML file: {HTML_FILE} ({'exists' if HTML_FILE.exists() else 'not found'})")
    logger.info("="*60)
    logger.info("Starting Flask server...")
    logger.info("Dashboard: http://localhost:5000")
    logger.info("API Docs: http://localhost:5000/api/health")
    logger.info("="*60)

    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
