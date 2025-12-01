@echo off

echo ====================================
echo PaperGraph - Environment Setup
echo ====================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot find Python, please install Python 3.9+ first
    pause
    exit /b 1
)
echo [OK] Python is already installed

if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment successfully created
) else (
    echo [OK] Virtual environment already exists
)

call venv\Scripts\activate.bat

echo Updating pip...
python -m pip install --upgrade pip

echo Installing requirements...
pip install -r requirements.txt

if not exist "logs\" mkdir logs
if not exist "exports\" mkdir exports
echo [OK] Directory successfully created

if not exist ".env" (
    echo [WARNING] Cannot find .env file
    echo Please create .env file and configure database connection information
    echo Please refer to the configuration instructions in README.md
)

echo ====================================
echo Environment setup succeed£¡
echo ====================================
echo Next£º
echo 1. Configure .env file
echo 2. Run python scripts/init_database.py to initialize database
echo 3. Run python scripts/load_sample_data.py to load sample data
echo 4. Run start_server.bat to start server
pause