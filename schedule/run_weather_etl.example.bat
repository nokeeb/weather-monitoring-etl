@echo off
cd /d "C:\Users\YOUR_WINDOWS_USERNAME\Documents\de-projects\weather-monitoring-etl"
"C:\Users\YOUR_WINDOWS_USERNAME\Documents\de-projects\weather-monitoring-etl\.venv\Scripts\python.exe" "scripts\run_pipeline.py" >> "logs\task_scheduler.log" 2>&1
exit /b %ERRORLEVEL%