@echo off
REM NSE/BSE Order Book Tracker - Windows Setup Script
REM This script automates the installation and configuration process

echo ================================================
echo 📊 NSE/BSE Order Book Tracker Setup
echo ================================================
echo.

REM Check Python installation
echo 🔍 Step 1: Checking Python installation...
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    echo ✅ Python found
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python3
        echo ✅ Python found
    ) else (
        echo ❌ Python is not installed!
        echo Please install Python 3.8+ from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

%PYTHON_CMD% --version
echo.

REM Create virtual environment
echo 🔧 Step 2: Creating virtual environment...
if exist venv (
    echo ℹ️  Virtual environment already exists. Skipping.
) else (
    %PYTHON_CMD% -m venv venv
    echo ✅ Virtual environment created
)
echo.

REM Activate virtual environment
echo 🔌 Step 3: Activating virtual environment...
call venv\Scripts\activate
echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo 📦 Step 4: Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ Pip upgraded to latest version
echo.

REM Install dependencies
echo 📥 Step 5: Installing dependencies...
echo This may take 2-3 minutes...
pip install -r requirements.txt >nul 2>&1
echo ✅ All dependencies installed
echo.

REM Check if .env file exists
echo ⚙️  Step 6: Configuration setup...
if exist .env (
    echo ℹ️  .env file already exists. Skipping.
) else (
    echo ℹ️  Creating .env template...
    (
        echo # Telegram Bot Configuration
        echo TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
        echo TELEGRAM_CHAT_ID=your_telegram_chat_id_here
    ) > .env
    echo ✅ .env template created
    echo.
    echo ⚠️  IMPORTANT: Edit .env file and add your Telegram credentials
    echo    1. Get bot token from @BotFather on Telegram
    echo    2. Get chat ID from https://api.telegram.org/bot^<TOKEN^>/getUpdates
    echo    3. Edit .env file with your actual values
    echo.
)
echo.

REM Run tests
echo 🧪 Step 7: Running tests...
echo Testing with mock data...
cd scripts
python demo_with_mock_data.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Mock data test passed
) else (
    echo ❌ Mock data test failed. Check the logs.
)
cd ..

echo.
echo ================================================
echo ✅ Setup Complete!
echo ================================================
echo.
echo 📋 Next steps:
echo    1. Edit .env file with your Telegram credentials:
echo       notepad .env
echo.
echo    2. Run the system:
echo       run.bat
echo       OR
echo       cd scripts ^&^& python daily_order_checker.py
echo.
echo    3. View the dashboard:
echo       start dashboard.html
echo.
echo 📚 Documentation:
echo    - Setup guide: SETUP.md
echo    - Main README: README.md
echo    - Telegram setup: TELEGRAM_SETUP_GUIDE.md
echo.
echo 🎉 Happy tracking!
echo.
pause
