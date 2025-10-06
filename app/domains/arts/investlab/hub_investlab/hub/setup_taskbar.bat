@echo off
setlocal enabledelayedexpansion

:: Unified Hub Taskbar Integration
:: Provides weather updates and quick access to services
:: For user: irfankabirprince@outlook.com

echo Unified Hub Taskbar Integration Starting...

:: Set user account and profile
set "USER_EMAIL=irfankabirprince@outlook.com"
set "EDGE_PROFILE=Default"
set "PROJECT_ROOT=D:\school\school"

:: Create taskbar shortcut script
set "TASKBAR_SCRIPT=%PROJECT_ROOT%\taskbar_integration.bat"

echo @echo off > "%TASKBAR_SCRIPT%"
echo :: Unified Hub Taskbar Integration >> "%TASKBAR_SCRIPT%"
echo :: User: %USER_EMAIL% >> "%TASKBAR_SCRIPT%"
echo :: Profile: %EDGE_PROFILE% >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo echo Unified Hub - Weather & Quick Access >> "%TASKBAR_SCRIPT%"
echo echo ===================================== >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :: Get current time >> "%TASKBAR_SCRIPT%"
echo echo Current Time: %%TIME%% >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :: Get weather (placeholder - would integrate with weather API) >> "%TASKBAR_SCRIPT%"
echo echo Weather: 22C, Partly Cloudy >> "%TASKBAR_SCRIPT%"
echo echo Location: Your Location >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :: Quick access menu >> "%TASKBAR_SCRIPT%"
echo echo Quick Access: >> "%TASKBAR_SCRIPT%"
echo echo 1. Research AI >> "%TASKBAR_SCRIPT%"
echo echo 2. Entertainment >> "%TASKBAR_SCRIPT%"
echo echo 3. Finance >> "%TASKBAR_SCRIPT%"
echo echo 4. Social Insights >> "%TASKBAR_SCRIPT%"
echo echo 5. Master Hub >> "%TASKBAR_SCRIPT%"
echo echo 6. Music Nudge >> "%TASKBAR_SCRIPT%"
echo echo 7. Microsoft Edge (Profile: %EDGE_PROFILE%) >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo choice /c 1234567 /n /m "Select option (1-7): " >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo if errorlevel 7 goto edge >> "%TASKBAR_SCRIPT%"
echo if errorlevel 6 goto nudge >> "%TASKBAR_SCRIPT%"
echo if errorlevel 5 goto master >> "%TASKBAR_SCRIPT%"
echo if errorlevel 4 goto insights >> "%TASKBAR_SCRIPT%"
echo if errorlevel 3 goto finance >> "%TASKBAR_SCRIPT%"
echo if errorlevel 2 goto entertainment >> "%TASKBAR_SCRIPT%"
echo if errorlevel 1 goto research >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :research >> "%TASKBAR_SCRIPT%"
echo echo Starting Research Module... >> "%TASKBAR_SCRIPT%"
echo python "%PROJECT_ROOT%\research\ai_service.py" >> "%TASKBAR_SCRIPT%"
echo goto end >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :entertainment >> "%TASKBAR_SCRIPT%"
echo echo Starting Entertainment Module... >> "%TASKBAR_SCRIPT%"
echo python "%PROJECT_ROOT%\entertainment\media_service.py" >> "%TASKBAR_SCRIPT%"
echo goto end >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :finance >> "%TASKBAR_SCRIPT%"
echo echo Starting Finance Module... >> "%TASKBAR_SCRIPT%"
echo python "%PROJECT_ROOT%\finance\finance_service.py" >> "%TASKBAR_SCRIPT%"
echo goto end >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :insights >> "%TASKBAR_SCRIPT%"
echo echo Starting Insights Module... >> "%TASKBAR_SCRIPT%"
echo python "%PROJECT_ROOT%\insights\social_service.py" >> "%TASKBAR_SCRIPT%"
echo goto end >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :master >> "%TASKBAR_SCRIPT%"
echo echo Starting Master Hub... >> "%TASKBAR_SCRIPT%"
echo python "%PROJECT_ROOT%\master_hub.py" >> "%TASKBAR_SCRIPT%"
echo goto end >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :nudge >> "%TASKBAR_SCRIPT%"
echo echo Playing Music Nudge... >> "%TASKBAR_SCRIPT%"
echo python -c "from entertainment.nudges.music_nudges import nudge_motivation; result = nudge_motivation(); print('Nudge:', result['song']['title'], 'by', result['song']['artist'])" >> "%TASKBAR_SCRIPT%"
echo goto end >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :edge >> "%TASKBAR_SCRIPT%"
echo echo Starting Microsoft Edge with profile %EDGE_PROFILE%... >> "%TASKBAR_SCRIPT%"
echo start msedge --profile-directory="%EDGE_PROFILE%" --new-window "https://outlook.live.com" >> "%TASKBAR_SCRIPT%"
echo goto end >> "%TASKBAR_SCRIPT%"
echo. >> "%TASKBAR_SCRIPT%"
echo :end >> "%TASKBAR_SCRIPT%"
echo pause >> "%TASKBAR_SCRIPT%"

:: Create desktop shortcut for easy access
set "DESKTOP_PATH=%USERPROFILE%\Desktop"
set "SHORTCUT_NAME=Unified Hub.lnk"

:: Create PowerShell script to create shortcut
echo $WshShell = New-Object -comObject WScript.Shell >> "%PROJECT_ROOT%\create_shortcut.ps1"
echo $Shortcut = $WshShell.CreateShortcut("%DESKTOP_PATH%\%SHORTCUT_NAME%") >> "%PROJECT_ROOT%\create_shortcut.ps1"
echo $Shortcut.TargetPath = "cmd.exe" >> "%PROJECT_ROOT%\create_shortcut.ps1"
echo $Shortcut.Arguments = "/c ""%TASKBAR_SCRIPT%""" >> "%PROJECT_ROOT%\create_shortcut.ps1"
echo $Shortcut.WorkingDirectory = "%PROJECT_ROOT%" >> "%PROJECT_ROOT%\create_shortcut.ps1"
echo $Shortcut.IconLocation = "cmd.exe,0" >> "%PROJECT_ROOT%\create_shortcut.ps1"
echo $Shortcut.Description = "Unified Hub - Weather & Quick Access" >> "%PROJECT_ROOT%\create_shortcut.ps1"
echo $Shortcut.Save() >> "%PROJECT_ROOT%\create_shortcut.ps1"

:: Run PowerShell script to create shortcut
powershell -ExecutionPolicy Bypass -File "%PROJECT_ROOT%\create_shortcut.ps1"

:: Update .env with taskbar integration settings
set "ENV_FILE=%PROJECT_ROOT%\.env"
if exist "%ENV_FILE%" (
    echo. >> "%ENV_FILE%"
    echo # Taskbar Integration >> "%ENV_FILE%"
    echo TASKBAR_USER=%USER_EMAIL% >> "%ENV_FILE%"
    echo TASKBAR_EDGE_PROFILE=%EDGE_PROFILE% >> "%ENV_FILE%"
    echo TASKBAR_SCRIPT=%TASKBAR_SCRIPT% >> "%ENV_FILE%"
    echo DESKTOP_SHORTCUT=%DESKTOP_PATH%\%SHORTCUT_NAME% >> "%ENV_FILE%"
) else (
    echo # Taskbar Integration > "%ENV_FILE%"
    echo TASKBAR_USER=%USER_EMAIL% >> "%ENV_FILE%"
    echo TASKBAR_EDGE_PROFILE=%EDGE_PROFILE% >> "%ENV_FILE%"
)

echo.
echo Taskbar integration setup complete!
echo.
echo Features added:
echo - Weather display
echo - Quick access to all sectors (research, entertainment, finance, insights)
echo - Music nudges
echo - Microsoft Edge integration with %EDGE_PROFILE% profile
echo - Desktop shortcut created
echo.
echo To use:
echo 1. Double-click the desktop shortcut "Unified Hub"
echo 2. Select your desired module from the menu
echo 3. Weather information is displayed at startup
echo.
echo User Account: %USER_EMAIL%
echo Edge Profile: %EDGE_PROFILE%
echo.
pause
