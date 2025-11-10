@echo off
REM Twitter Bearer Token Setup Script
REM This script helps you set your Twitter Bearer Token as an environment variable

echo ========================================
echo Twitter Bearer Token Setup
echo ========================================
echo.
echo This script will help you set your Twitter Bearer Token.
echo The token will be stored as a system environment variable.
echo.
echo IMPORTANT SECURITY NOTES:
echo - Never share your Bearer Token with anyone
echo - Keep it secure and rotate regularly
echo - This token provides read access to Twitter API v2
echo.

set /p BEARER_TOKEN="Enter your Twitter Bearer Token: "

if "%BEARER_TOKEN%"=="" (
    echo ❌ No token entered. Setup cancelled.
    pause
    exit /b 1
)

echo.
echo Setting TWITTER_BEARER_TOKEN environment variable...
setx TWITTER_BEARER_TOKEN "%BEARER_TOKEN%" /M

if %ERRORLEVEL% EQU 0 (
    echo ✅ Twitter Bearer Token set successfully!
    echo.
    echo The token has been saved as a system environment variable.
    echo You may need to restart your command prompt or IDE for changes to take effect.
    echo.
    echo To verify, run: python check_twitter_credentials.py
) else (
    echo ❌ Failed to set the environment variable.
    echo Please try running this script as Administrator.
)

echo.
pause
