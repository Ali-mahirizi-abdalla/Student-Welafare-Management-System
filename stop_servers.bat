@echo off
echo Stopping all Django servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *manage.py*" 2>nul
if %errorlevel% == 0 (
    echo All Django servers stopped successfully
) else (
    echo No Django servers were running
)

echo.
echo Clearing Python cache...
if exist __pycache__ rmdir /s /q __pycache__
if exist hms\__pycache__ rmdir /s /q hms\__pycache__
if exist swms\__pycache__ rmdir /s /q swms\__pycache__

echo.
echo Done! Now run:
echo python manage.py runserver 127.0.0.1:8000 --skip-checks
pause
