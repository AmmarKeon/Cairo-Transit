@echo off
echo ========================================
echo   Cairo Transit - Full Stack
echo ========================================
echo.

cd /d "%~dp0.."

echo Killing old backend on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo.
echo [1] Starting Backend (port 8000)...
cd backend
start "Backend" cmd /c "python main.py"

echo [2] Waiting...
timeout /t 3 /nobreak >nul

echo [3] Starting Frontend (port 5173)...
cd ..\frontend
start "Frontend" cmd /c "npm run dev"

echo.
echo ========================================
echo   Ready!
echo ========================================
echo.
echo Backend:   http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
