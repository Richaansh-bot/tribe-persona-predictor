@echo off
setlocal EnableDelayedExpansion
title TRIBE Persona Predictor
color 0A

echo.
echo  ================================================================
echo     TRIBE Persona Predictor - Starting
echo  ================================================================
echo.

:: Set project directory
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

:: ============================================================================
:: Step 1: Check Python
:: ============================================================================
echo [1/3] Checking Python...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please run SETUP.bat first to install dependencies.
    pause
    exit /b 1
)

:: ============================================================================
:: Step 2: Activate Virtual Environment or System Python
:: ============================================================================
echo [2/3] Setting up Python environment...

if exist "venv\Scripts\activate.bat" (
    echo     Using virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo     Using system Python...
)

:: ============================================================================
:: Step 3: Start Backend
:: ============================================================================
echo [3/3] Starting servers...
echo.

:: Start backend in new window
start "TRIBE Backend" cmd /k "python -m uvicorn server:app --host 0.0.0.0 --port 8003 --reload"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend
cd frontend
start "TRIBE Frontend" cmd /k "npm run dev"
cd ..

:: Wait for frontend
timeout /t 3 /nobreak >nul

:: Open browser
start http://localhost:5173

:: ============================================================================
:: Done
:: ============================================================================
echo.
echo ================================================================
echo     All services started!
echo ================================================================
echo.
echo     Frontend:    http://localhost:5173
echo     Backend:     http://localhost:8003
echo     API Docs:    http://localhost:8003/docs
echo.
echo     Close this window to stop the servers.
echo.
echo ================================================================
echo.

:: Close this window after a delay
timeout /t 5 /nobreak >nul
exit
