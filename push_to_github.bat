@echo off
:: ==============================================================================
:: Animaker AI Studio - Push to GitHub Repository Helper
:: ==============================================================================
cd /d "%~dp0"
TITLE Push Animaker AI to GitHub
COLOR 0B

echo.
echo  ======================================================================
echo         🚀 PUSH ANIMAKER AI TO GITHUB REPOSITORY 🚀
echo  ======================================================================
echo.
echo  Target Repository: https://github.com/paipai1999/pai-ai-animation-video.git
echo.

:: Detect Git executable
set "GIT_CMD=git"
git --version >nul 2>&1
if %errorlevel% equ 0 goto :git_found

if exist "C:\Program Files\Git\cmd\git.exe" (
    set "GIT_CMD=C:\Program Files\Git\cmd\git.exe"
    goto :git_found
)

if exist "C:\Program Files\Git\bin\git.exe" (
    set "GIT_CMD=C:\Program Files\Git\bin\git.exe"
    goto :git_found
)

if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" (
    set "GIT_CMD=%LOCALAPPDATA%\Programs\Git\cmd\git.exe"
    goto :git_found
)

echo  [ERROR] Git was not found in PATH or standard installation directories.
echo  Please restart your computer or command prompt.
pause
exit /b 1

:git_found
echo  [✓] Git detected successfully:
"%GIT_CMD%" --version
echo.

echo  [1/4] Initializing Git repository...
if not exist ".git" (
    "%GIT_CMD%" init
    "%GIT_CMD%" branch -M main
)

echo  [2/4] Setting remote origin to paipai1999/pai-ai-animation-video...
"%GIT_CMD%" remote remove origin >nul 2>&1
"%GIT_CMD%" remote add origin https://github.com/paipai1999/pai-ai-animation-video.git

echo  [3/4] Staging and committing all project files...
"%GIT_CMD%" add .
"%GIT_CMD%" commit -m "Initial release: Animaker AI Video-to-Animation Remake Studio with Google Colab GPU support"

echo  [4/4] Pushing to GitHub (main branch)...
"%GIT_CMD%" push -u origin main

if %errorlevel% equ 0 (
    COLOR 0A
    echo.
    echo  ======================================================================
    echo  🎉 SUCCESS: Project pushed to GitHub successfully!
    echo  👉 View repository: https://github.com/paipai1999/pai-ai-animation-video
    echo  ======================================================================
) else (
    COLOR 0E
    echo.
    echo  [NOTE] If GitHub authentication window appears, please sign in to complete push.
)

echo.
pause
