@echo off
echo ============================================
echo    VIDEO EDITOR - QUICK START
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
echo.

REM Check if requirements are installed
python -c "import moviepy" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    echo This may take 5-10 minutes on first run...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

echo [2/3] Dependencies OK
echo.

REM Check if .env exists
if not exist .env (
    echo WARNING: No .env file found
    echo The script will use fallback image sources
    echo For better results, create a .env file with API keys
    echo See README.md for instructions
    echo.
    timeout /t 3 >nul
)

echo [3/3] Starting video editor...
echo.
echo ============================================
echo.

python run_editor.py

echo.
echo ============================================
echo Process complete!
echo ============================================
pause
