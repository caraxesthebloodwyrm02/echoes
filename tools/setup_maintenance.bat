@echo off
REM Echoes Project Maintenance Setup
REM Run this script to set up scheduled maintenance

echo === Echoes Project Scheduled Maintenance Setup ===
echo.

set SCRIPT_DIR=%~dp0
set MAINTENANCE_SCRIPT=%SCRIPT_DIR%scheduled_maintenance.ps1
set SETUP_SCRIPT=%SCRIPT_DIR%setup_maintenance_task.ps1

echo Available options:
echo   1. Setup daily maintenance (recommended)
echo   2. Setup weekly maintenance
echo   3. Run maintenance now (test)
echo   4. Run maintenance dry-run (safe test)
echo   5. Uninstall scheduled task
echo.

set /p choice="Choose option (1-5): "

if "%choice%"=="1" (
    echo Setting up daily maintenance...
    powershell -ExecutionPolicy Bypass -File "%SETUP_SCRIPT%" -Schedule Daily
) else if "%choice%"=="2" (
    echo Setting up weekly maintenance...
    powershell -ExecutionPolicy Bypass -File "%SETUP_SCRIPT%" -Schedule Weekly
) else if "%choice%"=="3" (
    echo Running maintenance now...
    powershell -ExecutionPolicy Bypass -File "%SETUP_SCRIPT%" -RunNow
) else if "%choice%"=="4" (
    echo Running maintenance dry-run...
    powershell -ExecutionPolicy Bypass -File "%MAINTENANCE_SCRIPT%" -DryRun -Verbose
) else if "%choice%"=="5" (
    echo Uninstalling scheduled task...
    powershell -ExecutionPolicy Bypass -File "%SETUP_SCRIPT%" -Uninstall
) else (
    echo Invalid choice. Exiting.
    pause
    exit /b 1
)

echo.
echo Maintenance setup complete!
echo.
echo To view scheduled tasks: taskschd.msc
echo To run manually: .\scheduled_maintenance.ps1 -Verbose
echo.
pause
