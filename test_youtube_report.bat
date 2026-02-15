@echo off
REM YouTube ROI Report Generator - Test Script
REM Tests the backend components

echo ========================================
echo YouTube ROI Report Generator - Test
echo ========================================
echo.

REM Change to backend directory
cd /d "%~dp0backend"

echo [1/4] Testing Firestore connection...
python -c "from app.core.firestore_client import firestore_client; import asyncio; result = asyncio.run(firestore_client.get_collection_stats('roi_metrics')); print(result)"
if errorlevel 1 (
    echo FAILED: Firestore connection
    echo Check Firebase credentials in .env file
    pause
    exit /b 1
)
echo SUCCESS: Firestore connected
echo.

echo [2/4] Testing YouTube AI Agent...
python -m app.services.youtube_report.youtube_ai_agent
if errorlevel 1 (
    echo FAILED: YouTube AI Agent
    echo Check Google AI API key in .env file
    pause
    exit /b 1
)
echo SUCCESS: YouTube AI Agent working
echo.

echo [3/4] Testing YouTube PDF Generator...
python -m app.services.youtube_report.youtube_pdf_generator
if errorlevel 1 (
    echo FAILED: YouTube PDF Generator
    echo Check xhtml2pdf installation: pip install xhtml2pdf
    pause
    exit /b 1
)
echo SUCCESS: YouTube PDF Generator working
echo.

echo [4/4] Testing API Server (quick check)...
echo Starting server for 5 seconds...
start /b uvicorn main:app --host 127.0.0.1 --port 8000
timeout /t 5 /nobreak > nul
curl -s http://localhost:8000/api/v1/youtube-report/preview > nul
if errorlevel 1 (
    echo FAILED: API Server
    echo Could not connect to server
) else (
    echo SUCCESS: API Server responding
)
taskkill /f /im python.exe > nul 2>&1
echo.

echo ========================================
echo All tests completed!
echo ========================================
echo.
echo Next steps:
echo 1. Add sample data: python populate_youtube_data.py 50
echo 2. Start backend: uvicorn main:app --reload
echo 3. Start frontend: cd ../frontend ^&^& npm run dev
echo 4. Visit: http://localhost:3000/youtube-report
echo.
pause
