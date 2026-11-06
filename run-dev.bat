@echo off
title MediaFlow Launcher
echo ===================================================
echo           Starting MediaFlow Development Stack
echo ===================================================

echo [1/2] Starting Backend (FastAPI on Port 8000)...
start "MediaFlow Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting Frontend (Next.js on Port 3000)...
start "MediaFlow Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ===================================================
echo MediaFlow is launching!
echo App URL:     http://localhost:3000
echo Backend API: http://127.0.0.1:8000/docs
echo ===================================================
timeout /t 5
start http://localhost:3000

