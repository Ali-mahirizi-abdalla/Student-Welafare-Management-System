@echo off
echo ============================================================
echo    KILLING ALL DJANGO SERVERS
echo ============================================================
echo.

taskkill /F /IM python.exe
if %errorlevel% == 0 (
    echo [OK] All Python/Django servers stopped
) else (
    echo [WARNING] No Python processes were running
)

echo.
echo ============================================================
echo    READY TO START FRESH SERVER
echo ============================================================
echo.
echo Now run this command:
echo python manage.py runserver 127.0.0.1:8000 --skip-checks
echo.
pause
