@echo off
setlocal EnableDelayedExpansion
title TRIBE Persona Predictor - GPU Setup (WSL)
color 0E

echo.
echo  ================================================================
echo     TRIBE Persona Predictor - GPU Setup (WSL)
echo  ================================================================
echo.

:: ============================================================================
:: Prerequisites Check
:: ============================================================================

:: Check for WSL
echo [1/5] Checking WSL...

wsl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] WSL not found!
    echo.
    echo Please install WSL first:
    echo   1. Open PowerShell as Administrator
    echo   2. Run: wsl --install
    echo   3. Restart your computer
    echo.
    pause
    exit /b 1
)
echo     [OK] WSL is installed

:: Check for NVIDIA GPU
echo.
echo [2/5] Checking NVIDIA GPU...

nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] NVIDIA GPU not detected via nvidia-smi
    echo          GPU mode may not work properly.
) else (
    echo     [OK] NVIDIA GPU detected
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
)

:: ============================================================================
:: WSL Setup
:: ============================================================================
echo.
echo [3/5] Setting up Python environment in WSL...

:: Create virtual environment in WSL home
wsl -e bash -c "python3 -m venv ~/tribev2_env 2>/dev/null || echo 'venv may already exist'"

echo     Installing PyTorch with CUDA...
wsl -e bash -c "source ~/tribev2_env/bin/activate && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118" >nul 2>&1

echo     Installing backend dependencies...
wsl -e bash -c "source ~/tribev2_env/bin/activate && pip install fastapi uvicorn python-multipart aiofiles" >nul 2>&1

echo.
echo [4/5] Verifying GPU access...

:: Test GPU access
wsl -e bash -c "source ~/tribev2_env/bin/activate && python -c 'import torch; print(f\"CUDA: {torch.cuda.is_available()}\"); print(f\"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}\")'" >nul 2>&1

if %errorlevel% neq 0 (
    echo [WARNING] GPU not accessible in WSL
    echo          GPU mode may fall back to CPU.
)

:: ============================================================================
:: Final Steps
:: ============================================================================
echo.
echo [5/5] Creating startup scripts...

:: Update WSL startup script
(
echo #!/bin/bash
echo source ~/tribev2_env/bin/activate
echo cd /mnt/c/Users/Anirudh%%20Bhanot/Downloads/Richansh/tribe-persona-predictor
echo exec python -m uvicorn server:app --host 0.0.0.0 --port 8003
) > tribev2_wsl.sh

echo.
echo ================================================================
echo     GPU Setup Complete!
echo ================================================================
echo.
echo To run with GPU mode:
echo   1. Open WSL terminal
echo   2. Run: bash tribev2_wsl.sh
echo   3. Start frontend separately: npm run dev (in frontend folder)
echo.
echo Or use START.bat for CPU mode (works without GPU).
echo.
pause
