#!/bin/bash

# NSE/BSE Order Book Tracker - Run Script
# Quick script to run the daily order checker

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "================================================"
echo "📊 NSE/BSE Order Book Tracker"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found!${NC}"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists and has values
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo "Please create .env file with your Telegram credentials"
    exit 1
fi

# Check if .env has placeholder values
if grep -q "your_telegram_bot_token_here" .env; then
    echo -e "${YELLOW}⚠️  .env file contains placeholder values!${NC}"
    echo "Please edit .env and add your actual Telegram bot token and chat ID"
    echo ""
    echo "Run: nano .env"
    exit 1
fi

# Load environment variables from .env
export $(cat .env | grep -v '^#' | xargs)

echo -e "${GREEN}✅ Configuration loaded${NC}"
echo ""

# Run the daily order checker
echo "🚀 Running daily order checker..."
echo "================================================"
echo ""

cd scripts
python daily_order_checker.py

echo ""
echo "================================================"
echo "✅ Run completed!"
echo ""
echo "💡 Tip: Set up GitHub Actions for automatic daily runs"
echo "   See DEPLOYMENT_GUIDE.md for instructions"
echo ""
