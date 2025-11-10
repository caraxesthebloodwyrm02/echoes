@echo off
REM Echoes Assistant V2 Core - Full Coverage Test Setup
REM This script sets up the environment and runs comprehensive tests

echo 🚀 Echoes Assistant V2 Core - Full Coverage Test Setup
echo ====================================================

REM Check if we're in the right directory
if not exist "assistant_v2_core.py" (
    echo ❌ Error: assistant_v2_core.py not found. Please run from the Echoes project root.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📥 Installing dependencies...
pip install -q fastapi uvicorn requests python-multipart
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Check if OPENAI_API_KEY is set
if "%OPENAI_API_KEY%"=="" (
    echo ⚠️  OPENAI_API_KEY environment variable not set.
    echo    Setting a dummy key for testing purposes...
    set OPENAI_API_KEY=dummy_key_for_testing
    echo 💡 For real API calls, set your actual OpenAI API key.
)

REM Start the API server in background
echo 🌐 Starting Echoes API server...
start "Echoes API Server" cmd /c "call venv\Scripts\activate.bat && uvicorn api.main:app --reload --port 8000 --host 0.0.0.0"

REM Wait for server to start
echo ⏳ Waiting for API server to start...
timeout /t 5 /nobreak > nul

REM Check if server is running
echo 🔍 Checking API health...
curl -s http://localhost:8000/health > nul 2>&1
if errorlevel 1 (
    echo ❌ API server failed to start or is not responding
    echo 💡 Check if port 8000 is available
    pause
    exit /b 1
)

echo ✅ API server is running and healthy

REM Run the full coverage test suite
echo 🧪 Running full coverage test suite...
python full_coverage_test_runner.py --check-api --workers 4

REM Keep window open to see results
echo.
echo 🎯 Test execution completed!
echo 📊 Check the generated test_results_*.json file for detailed results
echo 🔄 API server is still running in the background
echo 💡 To stop the server, close the "Echoes API Server" command window
echo.
pause
