@echo off
echo ====================================
echo YouTube ROI Data Population Tool
echo ====================================
echo.

set /p USER_EMAIL="Enter user email (press Enter for limjl0130@gmail.com): "
if "%USER_EMAIL%"=="" set USER_EMAIL=limjl0130@gmail.com

set /p NUM_VIDEOS="Enter number of videos to generate (press Enter for 15): "
if "%NUM_VIDEOS%"=="" set NUM_VIDEOS=15

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Generating %NUM_VIDEOS% videos for %USER_EMAIL%...
python -c "from populate_roi_data import generate_mock_youtube_videos; generate_mock_youtube_videos('%USER_EMAIL%', %NUM_VIDEOS%)"

echo.
echo ====================================
echo Done! Data has been populated.
echo You can now view it at http://localhost:3000/roi
echo ====================================
pause
