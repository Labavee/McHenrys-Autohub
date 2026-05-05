@echo off
REM Installation Verification Script

setlocal enabledelayedexpansion
title Installation Verification

cls
echo ================================
echo Installation Verification Tool
echo ================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python --version
    echo [PASS] Python is installed
) else (
    echo [FAIL] Python is not installed or not in PATH
    goto error
)

echo.
REM Check pip
echo Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] pip is installed
) else (
    echo [FAIL] pip is not installed
    goto error
)

echo.
REM Check backend requirements
echo Checking backend requirements...
cd backend
if exist requirements.txt (
    echo [PASS] requirements.txt found
) else (
    echo [FAIL] requirements.txt not found
    goto error
)

echo.
REM Check virtual environment
echo Checking virtual environment...
if exist venv (
    echo [PASS] Virtual environment exists
) else (
    echo [INFO] Virtual environment not created yet
)

echo.
REM Check frontend files
cd ..\frontend
echo Checking frontend files...
if exist index.html (
    echo [PASS] index.html found
) else (
    echo [FAIL] index.html not found
    goto error
)

if exist css\styles.css (
    echo [PASS] styles.css found
) else (
    echo [FAIL] styles.css not found
    goto error
)

if exist js\api.js (
    echo [PASS] api.js found
) else (
    echo [FAIL] api.js not found
    goto error
)

echo.
REM Check SQL Server ODBC Driver
echo Checking SQL Server ODBC Driver...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\ODBC\odbcinst.ini" /s | find "ODBC Driver 17 for SQL Server" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] ODBC Driver 17 for SQL Server is installed
) else (
    echo [WARNING] ODBC Driver 17 for SQL Server not found
    echo Please download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
)

echo.
echo ================================
echo Verification Complete!
echo ================================
echo.
echo Next steps:
echo 1. Read README.md for full setup instructions
echo 2. Configure database in .env
echo 3. Run QUICKSTART.bat to start both backend and frontend
echo.
pause
goto end

:error
echo.
echo ================================
echo [ERROR] Verification Failed!
echo ================================
echo.
pause
exit /b 1

:end
