@echo off
setlocal EnableDelayedExpansion
title TRIBE Persona Predictor - Setup
color 0E

echo.
echo  ================================================================
echo     TRIBE Persona Predictor - Automated Setup
echo  ================================================================
echo.

:: ============================================================================
:: Ask user for mode preference
:: ============================================================================
echo  Choose installation mode:
echo.
echo     [1] CPU Mode (Recommended - Works on any machine)
echo     [2] GPU Mode (Requires NVIDIA GPU with 10GB+ VRAM)
echo.
set /p MODE_CHOICE="  Enter choice (1 or 2): "

if "%MODE_CHOICE%"=="2" goto :GPU_MODE
if "%MODE_CHOICE%"=="1" goto :CPU_MODE
echo Invalid choice. Defaulting to CPU mode...
timeout /t 1 >nul
goto :CPU_MODE

:: ============================================================================
:: GPU MODE SETUP
:: ============================================================================
:GPU_MODE
echo.
echo  ================================================================
echo     GPU Mode Selected
echo  ================================================================
echo.

:: Check for WSL
echo [1/4] Checking WSL...

wsl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo     WSL not found. Installing WSL...
    echo.
    echo     This requires administrator privileges.
    echo     You may need to restart your computer after installation.
    echo.
    wsl --install
    if %errorlevel% neq 0 (
        echo [ERROR] WSL installation failed.
        echo Falling back to CPU mode...
        timeout /t 2 >nul
        goto :CPU_MODE
    )
    echo.
    echo [IMPORTANT] Please RESTART your computer, then run this script again.
    pause
    exit /b 1
)

echo     [OK] WSL is installed

:: Check for NVIDIA GPU
echo.
echo [2/4] Checking NVIDIA GPU...

nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo     [WARNING] NVIDIA GPU not detected
    echo     GPU mode may not work properly.
    echo.
    set /p CONTINUE="  Continue anyway? (y/n): "
    if /i not "!CONTINUE!"=="y" goto :CPU_MODE
)

:: Setup WSL environment
echo.
echo [3/4] Setting up Python environment in WSL...

:: Create virtual environment in WSL home
wsl -e bash -c "mkdir -p ~/tribev2_env 2>/dev/null || true"
wsl -e bash -c "python3 -m venv ~/tribev2_env 2>/dev/null || echo 'venv may exist'"

echo     Installing PyTorch with CUDA...
wsl -e bash -c "source ~/tribev2_env/bin/activate && pip install --upgrade pip >nul 2>&1 && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 >nul 2>&1 && echo 'PyTorch installed'"

echo     Installing backend dependencies...
wsl -e bash -c "source ~/tribev2_env/bin/activate && pip install fastapi uvicorn python-multipart aiofiles >nul 2>&1 && echo 'Backend deps installed'"

:: Verify GPU access
echo.
echo [4/4] Verifying GPU access...

wsl -e bash -c "source ~/tribev2_env/bin/activate && python -c 'import torch; print(f\"  CUDA: {torch.cuda.is_available()}\"); print(f\"  GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \\"None\\"}\")'" 2>nul

if %errorlevel% neq 0 (
    echo     [WARNING] GPU verification failed. Will use CPU fallback.
)

:: Create WSL startup script
echo.
echo     Creating WSL startup script...

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
echo [SUCCESS] GPU mode configured!
echo.
echo To run:
echo   1. Open WSL terminal
echo   2. Run: bash tribev2_wsl.sh
echo   3. In another terminal: cd frontend ^&^& npm run dev
echo.
echo Or just run START.bat for CPU mode (works without GPU).
echo.
pause
exit /b 0

:: ============================================================================
:: CPU MODE SETUP (DEFAULT)
:: ============================================================================
:CPU_MODE
echo.
echo  ================================================================
echo     CPU Mode Selected
echo  ================================================================
echo.

:: ============================================================================
:: Step 1: Detect Python
:: ============================================================================
echo.
echo [1/4] Checking Python installation...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.10 or higher from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "delims=" %%i in ('python --version 2^>nul') do set PYTHON_VERSION=%%i
echo     Found: %PYTHON_VERSION%

:: ============================================================================
:: Step 2: Create Virtual Environment
:: ============================================================================
echo.
echo [2/4] Setting up Python virtual environment...

if exist "venv" (
    echo     [INFO] Virtual environment already exists
) else (
    echo     Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo     Activating virtual environment...
call venv\Scripts\activate.bat

echo     Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

:: ============================================================================
:: Step 3: Install Python Dependencies
:: ============================================================================
echo.
echo [3/4] Installing Python dependencies...

echo     Installing PyTorch (CPU version)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu >nul 2>&1
if %errorlevel% neq 0 (
    echo     [INFO] Retrying PyTorch installation...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
)

echo     Installing web framework...
pip install fastapi uvicorn python-multipart aiofiles >nul 2>&1
if %errorlevel% neq 0 (
    pip install fastapi uvicorn python-multipart aiofiles
)

echo     [OK] Python dependencies installed

:: ============================================================================
:: Step 4: Setup Frontend
:: ============================================================================
echo.
echo [4/4] Setting up frontend...

if not exist "frontend" (
    echo [ERROR] Frontend folder not found!
    pause
    exit /b 1
)

cd frontend

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Node.js not found!
    echo   Install from: https://nodejs.org/
    echo.
    echo   Skipping frontend setup...
    cd ..
    goto :finalize
)

echo     Installing npm packages...
if exist "package-lock.json" (
    echo     [INFO] Packages already installed
) else (
    call npm install >nul 2>&1
    if %errorlevel% neq 0 (
        echo     Retrying npm install...
        call npm install
    )
)

cd ..

:finalize
:: Create required directories
if not exist "uploads" mkdir uploads
if not exist "cache" mkdir cache

echo.
echo ================================================================
echo     Setup Complete!
echo ================================================================
echo.
echo [SUCCESS] CPU mode is ready!
echo.
echo Next steps:
echo   1. Double-click START.bat to launch
echo   2. Open http://localhost:5173 in your browser
echo.
echo Backend:  http://localhost:8003
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8003/docs
echo.
pause
