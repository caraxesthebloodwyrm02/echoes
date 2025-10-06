@echo off 
:: Unified Hub Command Aliases 
doskey hub=python "D:\school\school\hub_cli.py" $1 
doskey research=python "D:\school\school\research\ai_service.py" 
doskey entertainment=python "D:\school\school\entertainment\media_service.py" 
doskey finance=python "D:\school\school\finance\finance_service.py" 
doskey insights=python "D:\school\school\insights\social_service.py" 
doskey master=python "D:\school\school\master_hub.py" 
doskey nudge=python -c "from entertainment.nudges.music_nudges import nudge_motivation; result = nudge_motivation(); print('Nudge:', result['song']['title'], 'by', result['song']['artist'])" 
doskey weather=python -c "print('Weather: 22C, Partly Cloudy')" 
doskey edge=start msedge --profile-directory=\"Default\" --new-window \"https://outlook.live.com\" 
