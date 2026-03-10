@echo off
echo Starting CODVOICE - Cloud TTS Platform
echo ======================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Change to codvoice directory
cd /d "%~dp0"

REM Build and start all services
echo Building and starting CODVOICE services...
docker-compose up -d --build

echo.
echo CODVOICE is starting up...
echo.
echo Services:
echo - API Server: http://localhost/api
echo - Admin Dashboard: http://localhost
echo - TTS Engine: Internal (codvoice-tts:8000)
echo.
echo Default API Key: codvoice-default-key-123
echo Admin API Key: codvoice-admin-key-456
echo.
echo Example API Usage:
echo curl -X POST http://localhost/api/tts ^
echo   -H "Content-Type: application/json" ^
echo   -H "Authorization: Bearer codvoice-default-key-123" ^
echo   -d "{\"text\": \"Hello world\", \"voice\": \"en_US-lessac-medium\"}" ^
echo   --output speech.wav
echo.
echo CODVOICE is ready!
echo Visit http://localhost for the admin dashboard
pause