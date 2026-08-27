@echo off
cd /d "%~dp0"
TITLE Animaker AI Studio - Stopper
COLOR 0C

echo.
echo  ======================================================================
echo         🛑 STOPPING ANIMAKER AI STUDIO SERVICES 🛑
echo  ======================================================================
echo.

echo  [*] Stopping Backend Server (Uvicorn / Python)...
taskkill /F /FI "WINDOWTITLE eq Animaker AI - Backend*" >nul 2>&1
taskkill /F /IM uvicorn.exe >nul 2>&1

echo  [*] Stopping Frontend Web (Next.js / Node)...
taskkill /F /FI "WINDOWTITLE eq Animaker AI - Frontend*" >nul 2>&1

echo.
echo  [✓] All Animaker AI Studio services have been stopped successfully!
echo  ======================================================================
echo.
timeout /t 2 >nul
