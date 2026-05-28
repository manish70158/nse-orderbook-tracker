@echo off
REM NSE/BSE Order Book Tracker - Windows Run Script
REM Quick script to run the daily order checker

echo ================================================
echo 📊 NSE/BSE Order Book Tracker
echo ================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ⚠️  Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo Please create .env file with your Telegram credentials
    pause
    exit /b 1
)

REM Check if .env has placeholder values
findstr /C:"your_telegram_bot_token_here" .env >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  .env file contains placeholder values!
    echo Please edit .env and add your actual Telegram bot token and chat ID
    echo.
    echo Run: notepad .env
    pause
    exit /b 1
)

REM Load environment variables from .env
for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do set %%a

echo ✅ Configuration loaded
echo.

REM Run the daily order checker
echo 🚀 Running daily order checker...
echo ================================================
echo.

cd scripts
python daily_order_checker.py

echo.
echo ================================================
echo ✅ Run completed!
echo.
echo 💡 Tip: Set up GitHub Actions for automatic daily runs
echo    See DEPLOYMENT_GUIDE.md for instructions
echo.
pause
