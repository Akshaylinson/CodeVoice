@echo off
echo CODVOICE Troubleshooting Build
echo ===============================

echo Step 1: Cleaning Docker system...
docker system df
docker builder prune -f
docker image prune -f

echo.
echo Step 2: Building services one by one...

echo Building backend...
docker build -t codvoice-backend ./backend
if errorlevel 1 (
    echo Backend build failed!
    pause
    exit /b 1
)

echo Building TTS engine...
docker build -t codvoice-tts ./tts-engine
if errorlevel 1 (
    echo TTS engine build failed!
    pause
    exit /b 1
)

echo Building worker...
docker build -t codvoice-worker ./worker
if errorlevel 1 (
    echo Worker build failed!
    pause
    exit /b 1
)

echo.
echo Step 3: Starting core services...
docker-compose -f docker-compose.simple.yml up -d

echo.
echo Core services started. Check status:
docker-compose -f docker-compose.simple.yml ps

echo.
echo Test API:
echo curl http://localhost:8000/health
pause