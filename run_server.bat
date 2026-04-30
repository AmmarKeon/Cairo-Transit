@echo off
echo ========================================
echo   Cairo Transit - Running
echo ========================================
echo.
echo Backend running at: http://localhost:8000
echo Frontend:         http://localhost:5173
echo.
echo DO NOT close this window while testing!
echo.
echo Testing...
python -c "from backend.main import test_route; print(test_route('F2', '3'))"
echo.
echo If you see path data above, the backend works!
echo.
echo Press Ctrl+C to stop or close this window.
pause