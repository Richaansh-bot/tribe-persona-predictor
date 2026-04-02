# Quick reference for starting TRIBE v2 Persona Predictor

## Option 1: Double-Click Start (Easiest)

### For Full Setup (Backend + Frontend):
```
Double-click: START.bat
```

### For API Only (Backend only):
```
Double-click: START-QUICK.bat
```

## Option 2: Manual Start

### 1. Start Backend API
```bash
cd C:\Users\giris\persona-predictor
tribev2_env\Scripts\activate
python -m uvicorn server:app --host 0.0.0.0 --port 8003
```

### 2. Start Frontend (in new terminal)
```bash
cd C:\Users\giris\persona-predictor\frontend
npm run dev
```

## Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8003
- **API Documentation**: http://localhost:8003/docs

## GPU/CUDA Information

- If you have an NVIDIA GPU with CUDA, TRIBE v2 mode will be available
- Without GPU, the system uses Fast Mode (enhanced CPU analysis)

## Troubleshooting

### Virtual environment not found
Run `START.bat` once - it will create the environment.

### Port already in use
```bash
# Find and kill process on port 8003
netstat -ano | findstr :8003
# Then kill the PID shown
taskkill /PID <PID> /F
```

### Dependencies missing
```bash
tribev2_env\Scripts\pip install -r requirements-api.txt
```
