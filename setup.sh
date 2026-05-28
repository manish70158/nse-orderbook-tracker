#!/bin/bash

# NSE/BSE Order Book Tracker - Automated Setup Script
# This script automates the installation and configuration process

set -e  # Exit on any error

echo "================================================"
echo "📊 NSE/BSE Order Book Tracker Setup"
echo "================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check Python installation
echo "🔍 Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    PYTHON_VERSION=$(python --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python is not installed!"
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi

# Check Python version (must be 3.8+)
PYTHON_VERSION_NUM=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PYTHON_VERSION_NUM < 3.8" | bc -l) )); then
    print_error "Python 3.8+ is required. You have version $PYTHON_VERSION_NUM"
    exit 1
fi

echo ""

# Create virtual environment
echo "🔧 Step 2: Creating virtual environment..."
if [ -d "venv" ]; then
    print_info "Virtual environment already exists. Skipping."
else
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

echo ""

# Activate virtual environment
echo "🔌 Step 3: Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

echo ""

# Upgrade pip
echo "📦 Step 4: Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "Pip upgraded to latest version"

echo ""

# Install dependencies
echo "📥 Step 5: Installing dependencies..."
echo "This may take 2-3 minutes..."
pip install -r requirements.txt > /dev/null 2>&1
print_success "All dependencies installed"

echo ""

# Check if .env file exists
echo "⚙️  Step 6: Configuration setup..."
if [ -f ".env" ]; then
    print_info ".env file already exists. Skipping."
else
    print_info "Creating .env template..."
    cat > .env << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
EOF
    print_success ".env template created"
    echo ""
    print_info "⚠️  IMPORTANT: Edit .env file and add your Telegram credentials"
    echo "   1. Get bot token from @BotFather on Telegram"
    echo "   2. Get chat ID from https://api.telegram.org/bot<TOKEN>/getUpdates"
    echo "   3. Edit .env file with your actual values"
    echo ""
fi

echo ""

# Run tests
echo "🧪 Step 7: Running tests..."
echo "Testing with mock data..."
cd scripts
$PYTHON_CMD demo_with_mock_data.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Mock data test passed"
else
    print_error "Mock data test failed. Check the logs."
fi
cd ..

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with your Telegram credentials:"
echo "      nano .env"
echo ""
echo "   2. Run the system:"
echo "      ./run.sh"
echo "      OR"
echo "      cd scripts && python daily_order_checker.py"
echo ""
echo "   3. View the dashboard:"
echo "      open dashboard.html"
echo ""
echo "📚 Documentation:"
echo "   - Setup guide: SETUP.md"
echo "   - Main README: README.md"
echo "   - Telegram setup: TELEGRAM_SETUP_GUIDE.md"
echo ""
echo "🎉 Happy tracking!"
echo ""
