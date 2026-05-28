#!/bin/bash

echo "🚀 NSE Order Book Tracker V2 - Quick Run"
echo "========================================="
echo ""

# Default values
DAYS=30
THRESHOLD=500
TELEGRAM=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --days)
            DAYS="$2"
            shift 2
            ;;
        --threshold)
            THRESHOLD="$2"
            shift 2
            ;;
        --telegram)
            TELEGRAM="--telegram"
            shift
            ;;
        --dashboard)
            echo "Starting dashboard..."
            python app.py &
            sleep 2
            open http://localhost:5000 2>/dev/null || echo "Dashboard running at http://localhost:5000"
            exit 0
            ;;
        --help)
            echo "Usage: ./run.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --days N          Scan last N days (default: 30)"
            echo "  --threshold N     Alert threshold in Crores (default: 500)"
            echo "  --telegram        Enable Telegram notifications"
            echo "  --dashboard       Launch dashboard instead of scraping"
            echo "  --help            Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run.sh                           # Basic run (30 days, ₹500 Cr threshold)"
            echo "  ./run.sh --days 7                  # Last 7 days"
            echo "  ./run.sh --threshold 1000          # ₹1000 Cr threshold"
            echo "  ./run.sh --telegram                # With Telegram alerts"
            echo "  ./run.sh --days 7 --telegram       # Combined"
            echo "  ./run.sh --dashboard               # Launch dashboard"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Run './run.sh --help' for usage"
            exit 1
            ;;
    esac
done

echo "Running scraper with:"
echo "  Days: $DAYS"
echo "  Threshold: ₹$THRESHOLD Cr"
echo "  Telegram: ${TELEGRAM:-disabled}"
echo ""

python orchestrator.py --days $DAYS --threshold $THRESHOLD $TELEGRAM

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Scraping complete!"
    echo ""
    echo "View results:"
    echo "  - Check data/json/ for JSON files"
    echo "  - Check data/pdfs/ for downloaded PDFs"
    echo "  - Run './run.sh --dashboard' to view in browser"
else
    echo ""
    echo "❌ Scraping failed (exit code: $EXIT_CODE)"
    echo "Check logs above for errors"
fi
