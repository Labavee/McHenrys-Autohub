@echo off
REM Car Sales and Servicing Portal - Quick Start for Windows

title Car Sales and Servicing Portal - Setup
color 0A

echo ================================
echo Car Sales and Servicing Portal
echo Quick Start Setup (Windows)
echo ================================

REM Backend Setup
echo.
echo Setting up Backend...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo [SUCCESS] Backend setup complete!
echo To start backend: python run.py

REM Frontend Setup
echo.
echo Setting up Frontend...
cd ..\frontend

echo.
echo [SUCCESS] Frontend setup complete!
echo To start frontend: python -m http.server 8000

REM Summary
echo.
echo ================================
echo [SUCCESS] Setup Complete!
echo ================================
echo.
echo Next Steps:
echo 1. Open two Command Prompt windows
echo 2. Window 1: cd backend ^&^& python run.py
echo 3. Window 2: cd frontend ^&^& python -m http.server 8000
echo 4. Open browser: http://localhost:8000
echo.
echo Database Setup:
echo - See DATABASE_SETUP.md for SQL Server configuration
echo - Update .env with your database credentials
echo.
echo Documentation:
echo - See README.md for full documentation
echo - See API_TESTING.md for API testing guide
echo.
pause
