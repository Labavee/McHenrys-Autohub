@echo off
REM Car Sales and Servicing Portal - Windows Start Guide

setlocal enabledelayedexpansion
mode con: cols=100 lines=30
title Car Sales and Servicing Portal - Installation Guide

cls
color 0B

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                                           ║
echo ║        🚗  CAR SALES AND SERVICING PORTAL - INSTALLATION GUIDE (WINDOWS)  🚗              ║
echo ║                                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════════════════════╝
echo.
echo This guide will help you set up the complete Car Sales and Servicing Portal system.
echo.

echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo STEP 1: VERIFY SYSTEM REQUIREMENTS
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo.
echo ✓ Check that you have the following installed:
echo   • Python 3.8 or higher
echo   • SQL Server 2019 or SQL Server Express
echo   • ODBC Driver 17 for SQL Server
echo.
echo To check Python:
echo   Command Prompt: python --version
echo.
echo Recommended download links:
echo   • Python: https://www.python.org/downloads/
echo   • SQL Server Express: https://www.microsoft.com/en-us/sql-server/sql-server-editions-express
echo   • ODBC Driver: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
echo.
pause

cls
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo STEP 2: AUTOMATED SETUP (RECOMMENDED)
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo.
echo ✓ Double-click QUICKSTART.bat to automatically:
echo   1. Create virtual environment
echo   2. Install dependencies
echo   3. Guide you through final steps
echo.
echo Location: QUICKSTART.bat (in project root)
echo.
pause

cls
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo STEP 3: MANUAL SETUP (IF NEEDED)
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo.
echo 3.1 Open Command Prompt and navigate to project root
echo     cd "path\to\Car Sales and Servicing Portal website"
echo.
echo 3.2 Setup Backend:
echo     cd backend
echo     python -m venv venv
echo     venv\Scripts\activate
echo     pip install -r requirements.txt
echo.
echo 3.3 Configure Database:
echo     • Create SQL Server database (see DATABASE_SETUP.md)
echo     • Update .env file with credentials
echo.
echo 3.4 Start Backend:
echo     python run.py
echo     Backend will run at http://localhost:5000
echo.
echo 3.5 Start Frontend (new Command Prompt):
echo     cd frontend
echo     python -m http.server 8000
echo     Frontend will run at http://localhost:8000
echo.
pause

cls
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo STEP 4: DATABASE CONFIGURATION
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo.
echo Follow these steps to configure your database:
echo.
echo 1. Open SQL Server Management Studio
echo.
echo 2. Create new database:
echo    • Right-click Databases ^> New Database
echo    • Name: CarPortalDB
echo    • Click OK
echo.
echo 3. Edit backend\.env file:
echo    • Open backend\.env in a text editor
echo    • Update DATABASE_URL with your credentials
echo    • Replace "YourPassword" with your SQL Server password
echo.
echo 4. Example connection string:
echo    mssql+pyodbc:///?odbc_connect=DRIVER={ODBC Driver 17 for SQL Server};
echo    SERVER=localhost;DATABASE=CarPortalDB;UID=sa;PWD=YourPassword
echo.
echo See DATABASE_SETUP.md for more details.
echo.
pause

cls
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo STEP 5: RUNNING THE APPLICATION
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo.
echo Once setup is complete:
echo.
echo 1. Open two Command Prompt windows
echo.
echo 2. Window 1 - Start Backend:
echo    cd backend
echo    python run.py
echo    • Wait for "Running on http://localhost:5000"
echo.
echo 3. Window 2 - Start Frontend:
echo    cd frontend
echo    python -m http.server 8000
echo    • Backend should show "Serving HTTP on..."
echo.
echo 4. Open your browser:
echo    http://localhost:8000
echo.
pause

cls
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo STEP 6: TESTING THE APPLICATION
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo.
echo 1. Register a new account:
echo    • Click "Register" on home page
echo    • Fill in the form
echo    • Click "Register"
echo.
echo 2. Login with your new account:
echo    • Click "Login"
echo    • Enter credentials
echo    • Click "Login"
echo.
echo 3. Explore features:
echo    • Browse Vehicles
echo    • Dashboard
echo    • Schedule Bookings
echo    • View Invoices
echo.
echo 4. Admin access (if you have admin account):
echo    • Admin dashboard shows system stats
echo    • Manage users, vehicles, bookings, invoices
echo.
pause

cls
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo STEP 7: DOCUMENTATION
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo.
echo Read these files for more information:
echo.
echo • INDEX.md - Quick navigation guide
echo • README.md - Complete documentation
echo • PROJECT_SUMMARY.md - Feature overview
echo • API_TESTING.md - API testing examples
echo • DEVELOPMENT_GUIDE.md - Development guidelines
echo • DATABASE_SETUP.md - Database configuration
echo.
pause

cls
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo STEP 8: TROUBLESHOOTING
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo.
echo Common Issues:
echo.
echo Issue: "Python not found"
echo Solution: Install Python from https://www.python.org/downloads/
echo.
echo Issue: "Database connection failed"
echo Solution: 
echo   • Verify SQL Server is running
echo   • Check connection string in .env
echo   • Ensure ODBC driver is installed
echo.
echo Issue: "CORS errors in browser"
echo Solution:
echo   • Ensure backend is running on port 5000
echo   • Ensure frontend is running on port 8000
echo   • Clear browser cache
echo.
echo Issue: "Token expired/401 Unauthorized"
echo Solution:
echo   • Logout and login again
echo   • Clear browser cookies
echo.
echo For more help, see:
echo • README.md - Troubleshooting section
echo • DEVELOPMENT_GUIDE.md - For development issues
echo.
pause

cls
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo STEP 9: QUICK COMMANDS REFERENCE
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo.
echo Start Backend:
echo   cd backend
echo   python run.py
echo.
echo Start Frontend:
echo   cd frontend
echo   python -m http.server 8000
echo.
echo Open Application:
echo   http://localhost:8000
echo.
echo API Documentation:
echo   http://localhost:5000 (when running)
echo.
echo Stop Services:
echo   Ctrl + C in Command Prompt windows
echo.
pause

cls
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo SETUP COMPLETE!
echo ═══════════════════════════════════════════════════════════════════════════════════════════
echo.
echo You're ready to use the Car Sales and Servicing Portal!
echo.
echo Next steps:
echo 1. Run QUICKSTART.bat for automated setup
echo 2. Open http://localhost:8000
echo 3. Create a test account
echo 4. Explore the application
echo.
echo ✓ Happy coding!
echo.
pause
