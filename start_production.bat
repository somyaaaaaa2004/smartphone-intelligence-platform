@echo off
REM Production startup script for Smartphone Intelligence Platform API (Windows)
REM This script starts the API using Gunicorn with production settings

echo Starting Smartphone Intelligence Platform API...

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure your settings.
    exit /b 1
)

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Warning: Virtual environment not activated.
    echo It's recommended to use a virtual environment in production.
    set /p CONTINUE="Continue anyway? (y/N): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

REM Check if gunicorn is installed
where gunicorn >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: gunicorn not found!
    echo Please install dependencies: pip install -r requirements.txt
    exit /b 1
)

REM Set defaults if not set
if "%PORT%"=="" set PORT=8000
if "%ENVIRONMENT%"=="" set ENVIRONMENT=production
if "%API_HOST%"=="" set API_HOST=0.0.0.0

echo Configuration:
echo   Port: %PORT%
echo   Host: %API_HOST%
echo   Environment: %ENVIRONMENT%

REM Start Gunicorn
echo Starting Gunicorn server...
gunicorn backend.main:app -c gunicorn.conf.py
