@echo off

title ShaunMariaOS Web

cd /d "%~dp0"

echo.
echo ========================================
echo        Starting ShaunMariaOS...
echo ========================================
echo.

".venv\Scripts\python.exe" -m uvicorn web.app:app --host 127.0.0.1 --port 8000

pause