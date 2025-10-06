@echo off
echo Setting up streamlined PATH configurations for Unified Hub...
echo.

:: Add Python and Scripts to PATH
set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311"
set "PYTHON_SCRIPTS=%PYTHON_PATH%\Scripts"

:: Add project directories to PATH
set "PROJECT_ROOT=D:\school\school"
set "RESEARCH_PATH=%PROJECT_ROOT%\research"
set "ENTERTAINMENT_PATH=%PROJECT_ROOT%\entertainment"
set "INSIGHTS_PATH=%PROJECT_ROOT%\insights"
set "FINANCE_PATH=%PROJECT_ROOT%\finance"
set "CONTENT_PATH=%PROJECT_ROOT%\content"
set "MEDIA_PATH=%PROJECT_ROOT%\media"
set "BRAINSTORMING_PATH=%PROJECT_ROOT%\brainstorming"

:: Create batch file for PATH management
echo @echo off > "%PROJECT_ROOT%\path_manager.bat"
echo :: Unified Hub Path Manager >> "%PROJECT_ROOT%\path_manager.bat"
echo set "PROJECT_ROOT=%PROJECT_ROOT%" >> "%PROJECT_ROOT%\path_manager.bat"
echo set "PATH=%PYTHON_PATH%;%PYTHON_SCRIPTS%;%PROJECT_ROOT%;%RESEARCH_PATH%;%ENTERTAINMENT_PATH%;%INSIGHTS_PATH%;%FINANCE_PATH%;%CONTENT_PATH%;%MEDIA_PATH%;%BRAINSTORMING_PATH%;%%PATH%%" >> "%PROJECT_ROOT%\path_manager.bat"
echo echo PATH configured for Unified Hub >> "%PROJECT_ROOT%\path_manager.bat"
echo echo Current PATH: %%PATH%% >> "%PROJECT_ROOT%\path_manager.bat"

:: Set permanent PATH using setx (requires admin)
echo Setting permanent PATH...
setx PATH "%PYTHON_PATH%;%PYTHON_SCRIPTS%;%PROJECT_ROOT%;%RESEARCH_PATH%;%ENTERTAINMENT_PATH%;%INSIGHTS_PATH%;%FINANCE_PATH%;%CONTENT_PATH%;%MEDIA_PATH%;%BRAINSTORMING_PATH%;%PATH%"

:: Create environment variables for easy access
setx UNIFIED_HUB_PATH "%PROJECT_ROOT%"
setx UNIFIED_HUB_RESEARCH "%RESEARCH_PATH%"
setx UNIFIED_HUB_ENTERTAINMENT "%ENTERTAINMENT_PATH%"
setx UNIFIED_HUB_INSIGHTS "%INSIGHTS_PATH%"
setx UNIFIED_HUB_FINANCE "%FINANCE_PATH%"
setx UNIFIED_HUB_CONTENT "%CONTENT_PATH%"
setx UNIFIED_HUB_MEDIA "%MEDIA_PATH%"
setx UNIFIED_HUB_BRAINSTORMING "%BRAINSTORMING_PATH%"

:: Create aliases for quick access
echo Creating command aliases...
echo @echo off > "%PROJECT_ROOT%\hub_commands.bat"
echo :: Unified Hub Command Aliases >> "%PROJECT_ROOT%\hub_commands.bat"
echo doskey hub=python "%PROJECT_ROOT%\hub_cli.py" $1 >> "%PROJECT_ROOT%\hub_commands.bat"
echo doskey research=python "%PROJECT_ROOT%\research\ai_service.py" >> "%PROJECT_ROOT%\hub_commands.bat"
echo doskey entertainment=python "%PROJECT_ROOT%\entertainment\media_service.py" >> "%PROJECT_ROOT%\hub_commands.bat"
echo doskey finance=python "%PROJECT_ROOT%\finance\finance_service.py" >> "%PROJECT_ROOT%\hub_commands.bat"
echo doskey insights=python "%PROJECT_ROOT%\insights\social_service.py" >> "%PROJECT_ROOT%\hub_commands.bat"
echo doskey master=python "%PROJECT_ROOT%\master_hub.py" >> "%PROJECT_ROOT%\hub_commands.bat"
echo doskey nudge=python -c "from entertainment.nudges.music_nudges import nudge_motivation; result = nudge_motivation(); print('Nudge:', result['song']['title'], 'by', result['song']['artist'])" >> "%PROJECT_ROOT%\hub_commands.bat"
echo doskey weather=python -c "print('Weather: 22C, Partly Cloudy')" >> "%PROJECT_ROOT%\hub_commands.bat"
echo doskey edge=start msedge --profile-directory=\"Default\" --new-window \"https://outlook.live.com\" >> "%PROJECT_ROOT%\hub_commands.bat"

echo.
echo PATH configuration completed!
echo.
echo To use the unified hub:
echo 1. Restart your terminal/command prompt
echo 2. Run: hub [command] (research, entertainment, finance, insights, master)
echo 3. Or use individual commands: research, entertainment, finance, insights
echo 4. Music nudges: nudge
echo 5. Weather: weather
echo 6. Microsoft Edge: edge
echo.
echo Environment variables set:
echo - UNIFIED_HUB_PATH=%PROJECT_ROOT%
echo - UNIFIED_HUB_RESEARCH=%RESEARCH_PATH%
echo - UNIFIED_HUB_ENTERTAINMENT=%ENTERTAINMENT_PATH%
echo - UNIFIED_HUB_INSIGHTS=%INSIGHTS_PATH%
echo - UNIFIED_HUB_FINANCE=%FINANCE_PATH%
echo - UNIFIED_HUB_CONTENT=%CONTENT_PATH%
echo - UNIFIED_HUB_MEDIA=%MEDIA_PATH%
echo - UNIFIED_HUB_BRAINSTORMING=%BRAINSTORMING_PATH%
echo.
echo Next step: Run setup_taskbar.bat for Windows taskbar integration
echo.
pause
