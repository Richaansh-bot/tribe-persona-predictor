# PowerShell Script - For Windows 10/11

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  TRIBE v2 Persona Predictor - Startup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check for virtual environment
$VenvPath = Join-Path $ScriptDir "tribev2_env"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run START.bat first to set up the environment." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/4] Activating Python environment..." -ForegroundColor Green
& "$VenvPath\Scripts\Activate.ps1" | Out-Null

Write-Host "[2/4] Checking GPU/CUDA..." -ForegroundColor Green
$CUDA = & python -c "import torch; print('Available' if torch.cuda.is_available() else 'Not Available')" 2>$null
Write-Host "       CUDA: $CUDA" -ForegroundColor Gray

Write-Host "[3/4] Checking dependencies..." -ForegroundColor Green
$FastAPI = & pip show fastapi 2>$null
if (-not $FastAPI) {
    Write-Host "       Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements-api.txt | Out-Null
}

Write-Host "[4/4] Starting API Server..." -ForegroundColor Green
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Server running at: http://localhost:8003" -ForegroundColor Green
Write-Host "  API Docs at: http://localhost:8003/docs" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
& python -m uvicorn server:app --host 0.0.0.0 --port 8003

# Keep window open after exit
Write-Host ""
Read-Host "Server stopped. Press Enter to exit"
