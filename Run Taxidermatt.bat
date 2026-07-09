@echo off
title Taxidermatt

rem Run from this file's folder, wherever it is double-clicked from.
cd /d "%~dp0"

if not exist "venv\Scripts\flask.exe" (
    echo Could not find the virtual environment at venv\Scripts\
    echo Create it with:  python -m venv venv
    echo Then install:    venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

rem Open the browser a few seconds after the server starts warming up.
start "" cmd /c "timeout /t 3 >nul & start "" http://127.0.0.1:5000"

echo Starting Taxidermatt at http://127.0.0.1:5000
echo Close this window or press Ctrl+C to stop the app.
echo.

venv\Scripts\flask.exe --app "src:create_app()" run

rem Keep the window open if Flask exits with an error.
if errorlevel 1 (
    echo.
    echo The app stopped unexpectedly. The error is above.
    pause
)