@echo off
title TRIBE v2 - Quick Start (API Only)
color 0A

echo.
echo  ================================================
echo    TRIBE v2 Persona Predictor - Quick Start
echo  ================================================
echo.

:: Set project directory
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

:: Activate virtual environment
echo [1/2] Activating Python environment...
if not exist "tribev2_env\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Run START.bat to set up first.
    pause
    exit /b 1
)
call tribev2_env\Scripts\activate.bat

:: Check CUDA
python -c "import torch; print(f'CUDA: {\"Available\" if torch.cuda.is_available() else \"Not Available\"}')" 2>nul

:: Start server
echo.
echo [2/2] Starting API Server...
echo.
python -m uvicorn server:app --host 0.0.0.0 --port 8003

:: If server exits, wait for user
pause
