@echo off
cd /d "%~dp0"
TITLE Animaker AI Studio - Docker Launcher
COLOR 0A

echo ================================================================
echo        🐳 ANIMAKER AI - DOCKER COMPOSE LAUNCHER 🐳
echo ================================================================
echo.

docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running or not installed!
    echo Please make sure Docker Desktop is open and running.
    pause
    exit /b
)

echo [*] Starting Redis, Backend & Celery Worker via Docker Compose...
docker compose up --build -d

echo [*] Launching Frontend Web...
start "Animaker AI - Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo [✓] Animaker AI is running in Docker!
echo Open http://localhost:3000 in your browser.
pause
