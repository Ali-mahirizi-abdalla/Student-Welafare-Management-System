# Stop all running Django servers
Write-Host "Stopping all Django servers..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*manage.py*runserver*"
} | ForEach-Object {
    Write-Host "Stopping process $($_.Id)..." -ForegroundColor Red
    Stop-Process -Id $_.Id -Force
}

Start-Sleep -Seconds 2

# Clear Python cache
Write-Host "`nClearing Python cache..." -ForegroundColor Yellow
if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }
if (Test-Path "hms\__pycache__") { Remove-Item -Recurse -Force "hms\__pycache__" }
if (Test-Path "swms\__pycache__") { Remove-Item -Recurse -Force "swms\__pycache__" }

Write-Host "`nAll servers stopped and cache cleared!" -ForegroundColor Green
Write-Host "`nNow run:" -ForegroundColor Cyan
Write-Host "python manage.py runserver 127.0.0.1:8000 --skip-checks" -ForegroundColor White
