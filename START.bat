@echo off
title TRIBE v2 Persona Predictor
color 0A

echo.
echo  ================================================
echo    TRIBE v2 Persona Predictor - Startup
echo  ================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.11+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Set project directory
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

:: Check if virtual environment exists
if not exist "tribev2_env\Scripts\python.exe" (
    echo [WARNING] Virtual environment not found at tribev2_env
    echo Creating new virtual environment...
    python -m venv tribev2_env
    echo [OK] Virtual environment created
)

:: Activate virtual environment
echo [1/3] Activating Python environment...
call tribev2_env\Scripts\activate.bat

:: Check CUDA availability
echo.
echo [INFO] Checking GPU/CUDA availability...
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')" 2>nul
if errorlevel 1 (
    echo [INFO] Running in CPU mode
) else (
    python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>nul
    if not errorlevel 1 (
        echo [OK] GPU detected! TRIBE v2 mode available
    ) else (
        echo [INFO] No GPU found - using Fast Mode
    )
)

:: Install dependencies if needed
echo.
echo [2/3] Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements-api.txt
)

:: Start the backend server
echo.
echo [3/3] Starting Backend API Server...
echo    API: http://localhost:8003
echo    Docs: http://localhost:8003/docs
echo.
start "TRIBE Backend" cmd /k "python -m uvicorn server:app --host 0.0.0.0 --port 8003"

:: Wait for server to start
timeout /t 3 /nobreak >nul

:: Start the frontend dev server
echo.
echo Starting Frontend Dev Server...
cd frontend
start "TRIBE Frontend" cmd /k "npm run dev"

:: Wait for frontend to start
timeout /t 5 /nobreak >nul

:: Open browser
echo.
echo ================================================
echo    All services started!
echo ================================================
echo.
echo    Backend API: http://localhost:8003
echo    Frontend:    http://localhost:5173
echo.
echo    Press any key to open browser...
pause >nul

start http://localhost:5173

echo.
echo [OK] Servers are running in background windows
echo    Close those windows to stop the servers
echo.
pause
