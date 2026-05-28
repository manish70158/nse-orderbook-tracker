#!/bin/bash

echo "🚀 NSE Order Book Tracker V2 - Setup Script"
echo "=============================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "❌ Python 3 is required"; exit 1; }
echo "✅ Python 3 found"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt || { echo "❌ Failed to install dependencies"; exit 1; }
echo "✅ Python packages installed"
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium || { echo "❌ Failed to install Playwright"; exit 1; }
echo "✅ Playwright chromium installed"
echo ""

# Install Playwright system dependencies (Linux/CI)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing Playwright system dependencies..."
    playwright install-deps || echo "⚠️  Could not install system deps (may need sudo)"
fi

# Create output directories
echo "Creating output directories..."
mkdir -p data/pdfs
mkdir -p data/json
mkdir -p screenshots
echo "✅ Directories created"
echo ""

# Run tests
echo "Running tests..."
python tests/test_pdf_parser.py
TEST_RESULT=$?
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ Tests passed (91.7% accuracy expected)"
else
    echo "⚠️  Some tests may have failed - check output above"
fi
echo ""

echo "=============================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. (Optional) Set up Telegram:"
echo "   cat docs/TELEGRAM_SETUP_GUIDE.md"
echo "   export TELEGRAM_BOT_TOKEN='your-token'"
echo "   export TELEGRAM_CHAT_ID='your-chat-id'"
echo ""
echo "2. Run the scraper:"
echo "   python orchestrator.py --days 7"
echo ""
echo "3. Launch dashboard:"
echo "   python app.py"
echo "   open http://localhost:5000"
echo ""
echo "Happy tracking! 📊"
