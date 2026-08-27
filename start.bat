@echo off
:: ==============================================================================
:: Animaker AI Studio - Universal Auto-Launcher (Zero-Config One-Click Start)
:: ==============================================================================
cd /d "%~dp0"
TITLE Animaker AI Studio - Launcher
COLOR 0B

echo.
echo  ======================================================================
echo         🎬 ANIMAKER AI - VIDEO-TO-ANIMATION STUDIO LAUNCHER 🎬
echo  ======================================================================
echo.

:: -----------------------------------------------------------------------------
:: Step 1: Detect Python Environment
:: -----------------------------------------------------------------------------
echo  [1/4] Checking Python Environment...
set PYTHON_CMD=

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)

py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3
    goto :python_found
)

:: Python Not Found Handler
COLOR 0C
echo.
echo  [ERROR] Python is not installed or not added to PATH!
echo.
echo  Please download and install Python 3.10+ from:
echo  https://www.python.org/downloads/
echo.
echo  IMPORTANT: Please check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:python_found
for /f "tokens=*" %%v in ('%PYTHON_CMD% --version 2^>^&1') do echo  [✓] Found %%v

:: -----------------------------------------------------------------------------
:: Step 2: Detect Node.js & npm
:: -----------------------------------------------------------------------------
echo.
echo  [2/4] Checking Node.js Environment...

npm --version >nul 2>&1
if %errorlevel% neq 0 (
    COLOR 0C
    echo.
    echo  [ERROR] Node.js is not installed or not in PATH!
    echo.
    echo  Please download and install Node.js from:
    echo  https://nodejs.org/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('node --version 2^>^&1') do echo  [✓] Found Node.js %%v

:: -----------------------------------------------------------------------------
:: Step 3: Verify .env File
:: -----------------------------------------------------------------------------
echo.
echo  [3/4] Verifying Configuration...

if not exist ".env" (
    if exist ".env.example" (
        echo  [*] Initializing .env from .env.example...
        copy .env.example .env >nul
    ) else (
        echo GEMINI_API_KEY=> .env
        echo REDIS_URL=redis://localhost:6379/0>> .env
    )
    echo  [✓] Configuration file created.
) else (
    echo  [✓] Configuration file found.
)

:: -----------------------------------------------------------------------------
:: Step 4: Prepare Python Virtual Environment and Packages
:: -----------------------------------------------------------------------------
echo.
echo  [4/4] Preparing Backend and Frontend Packages...

if not exist "backend\venv\Scripts\python.exe" (
    echo  [*] Creating Python virtual environment in backend\venv...
    %PYTHON_CMD% -m venv backend\venv
)

if exist "backend\venv\Scripts\python.exe" (
    set VENV_PY=backend\venv\Scripts\python.exe
) else (
    set VENV_PY=%PYTHON_CMD%
)

echo  [*] Checking and installing backend dependencies...
"%VENV_PY%" -m pip install -r backend\requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [!] Retrying pip install...
    "%VENV_PY%" -m pip install -r backend\requirements.txt
)
echo  [✓] Backend dependencies verified.

if not exist "frontend\node_modules" (
    echo  [*] Installing frontend packages (first run only, please wait)...
    cd frontend
    call npm install --silent
    cd ..
    echo  [✓] Frontend packages installed.
) else (
    echo  [✓] Frontend packages verified.
)

:: -----------------------------------------------------------------------------
:: Step 5: Start Services
:: -----------------------------------------------------------------------------
echo.
echo  ======================================================================
echo  🚀 LAUNCHING ANIMAKER AI SERVICES...
echo  ======================================================================
echo.

:: Launch FastAPI Backend
echo  [*] Starting FastAPI Backend on port 8000...
start "Animaker AI - Backend API" cmd /k "title Animaker AI - Backend Server & set PYTHONPATH=. & "%VENV_PY%" -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Launch Next.js Frontend
echo  [*] Starting Next.js Frontend on port 3000...
start "Animaker AI - Frontend Web" cmd /k "title Animaker AI - Frontend Web & cd frontend & npm run dev"


:: Wait 4 seconds for servers to initialize
echo  [*] Waiting for servers to initialize...
timeout /t 4 /nobreak >nul

:: Open Web Browser
echo  [*] Opening Animaker AI Studio in your default browser...
start http://localhost:3000

echo.
echo  ======================================================================
echo  🎉 ALL SERVICES ARE RUNNING!
echo  ======================================================================
echo.
echo   🌐 Web UI Studio      : http://localhost:3000
echo   📚 API Documentation  : http://localhost:8000/docs
echo.
echo   💡 To stop everything, double-click 'stop.bat' or close the windows.
echo  ======================================================================
echo.
pause
