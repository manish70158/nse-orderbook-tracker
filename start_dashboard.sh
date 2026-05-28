#!/bin/bash
# Quick Start Script for NSE Order Book Dashboard

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  NSE ORDER BOOK DASHBOARD - STARTUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

echo "✓ Python 3 detected"

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️  Flask not installed. Installing dependencies..."
    pip3 install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Flask installed"
fi

echo ""
echo "🚀 Starting Flask backend..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Dashboard will open at: http://localhost:5000"
echo "  Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Flask and open browser after 2 seconds
python3 app.py &
FLASK_PID=$!

sleep 2

# Open browser
if command -v open &> /dev/null; then
    echo "🌐 Opening dashboard in browser..."
    open http://localhost:5000
elif command -v xdg-open &> /dev/null; then
    echo "🌐 Opening dashboard in browser..."
    xdg-open http://localhost:5000
fi

# Wait for Flask process
wait $FLASK_PID
