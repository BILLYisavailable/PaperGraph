@echo off
chcp 65001 >nul
echo ====================================
echo PaperGraph - Start All Services
echo ====================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot find Python, please install Python 3.9+ first
    pause
    exit /b 1
)

if not exist "venv\" (
    echo ====================================
    echo Step 1/4: Setting up environment
    echo ====================================
    echo.
    call setup.bat
    if errorlevel 1 (
        echo [ERROR] Environment setup failed
        pause
        exit /b 1
    )
    echo.
) else (
    echo [OK] Virtual environment already exists
    echo.
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Cannot activate virtual environment
    pause
    exit /b 1
)

echo ====================================
echo Step 2/4: Checking Redis service
echo ====================================
echo.
sc query Memurai >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Memurai service is not running, please start it manually
    echo Run command: net start Memurai
    echo.
) else (
    echo [OK] Redis/Memurai service check completed
    echo.
)

echo ====================================
echo Step 3/4: Starting backend services
echo ====================================
echo.

echo [INFO] Starting FastAPI server...
start "PaperGraph - FastAPI Server" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && echo ==================================== && echo FastAPI Server && echo ==================================== && echo Visit http://localhost:8000/docs for API documentation && echo Press Ctrl+C to stop server && echo. && python -m app.main"

timeout /t 3 /nobreak >nul

echo [INFO] Starting Celery Worker...
start "PaperGraph - Celery Worker" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && set CELERY_BROKER_URL=redis://localhost:6379/1 && set CELERY_RESULT_BACKEND=redis://localhost:6379/2 && echo ==================================== && echo Celery Worker && echo ==================================== && echo Press Ctrl+C to stop worker && echo. && celery -A app.tasks.celery_app worker --loglevel=info --pool=solo"

timeout /t 2 /nobreak >nul

echo ====================================
echo Step 4/4: Starting frontend service
echo ====================================
echo.

set FRONTEND_DIR=knowledge_graph_system_v2\knowledge_graph_system_v2

if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found: %FRONTEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo [INFO] Frontend dependencies not found, installing...
    cd /d "%FRONTEND_DIR%"
    call npm install
    if errorlevel 1 (
        echo [ERROR] Frontend dependencies installation failed
        pause
        exit /b 1
    )
    cd /d %~dp0
    echo [OK] Frontend dependencies installed
    echo.
)

echo [INFO] Starting frontend service...
start "PaperGraph - Frontend Server" cmd /k "cd /d %~dp0\%FRONTEND_DIR% && echo ==================================== && echo Frontend Server && echo ==================================== && echo Visit http://localhost:3000 in your browser && echo Press Ctrl+C to stop server && echo. && npm run serve"

echo.
echo ====================================
echo All services started!
echo ====================================
echo.
echo The following windows have been opened:
echo.
echo 1. FastAPI Server - http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo    Background task processing
echo.
echo 3. Frontend Server - http://localhost:3000
echo    Frontend UI: http://localhost:3000
echo.
echo ====================================
echo Tip: Close the corresponding window to stop the service
echo ====================================
echo.
echo Press any key to close this window...
pause >nul

