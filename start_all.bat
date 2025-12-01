@echo off
chcp 65001 >nul
echo ====================================
<<<<<<< HEAD
=======
echo PaperGraph - 一键启动所有服务
>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
echo PaperGraph - Start All Services
echo ====================================
echo.

<<<<<<< HEAD
python --version >nul 2>&1
if errorlevel 1 (
=======
REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到Python，请先安装Python 3.9+
>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
    echo [ERROR] Cannot find Python, please install Python 3.9+ first
    pause
    exit /b 1
)

<<<<<<< HEAD
if not exist "venv\" (
    echo ====================================
=======
REM 步骤1: 运行setup（如果虚拟环境不存在）
if not exist "venv\" (
    echo ====================================
    echo 步骤 1/4: 设置环境
>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
    echo Step 1/4: Setting up environment
    echo ====================================
    echo.
    call setup.bat
    if errorlevel 1 (
<<<<<<< HEAD
=======
        echo [ERROR] 环境设置失败
>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
        echo [ERROR] Environment setup failed
        pause
        exit /b 1
    )
    echo.
) else (
<<<<<<< HEAD
=======
    echo [OK] 虚拟环境已存在
>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
    echo [OK] Virtual environment already exists
    echo.
)

<<<<<<< HEAD
call venv\Scripts\activate.bat
if errorlevel 1 (
=======
REM 激活虚拟环境
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] 无法激活虚拟环境
>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
    echo [ERROR] Cannot activate virtual environment
    pause
    exit /b 1
)

<<<<<<< HEAD
echo ====================================
=======

>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
echo Step 2/4: Checking Redis service
echo ====================================
echo.
sc query Memurai >nul 2>&1
if errorlevel 1 (
<<<<<<< HEAD
    echo [WARNING] Memurai service is not running, please start it manually
    echo Run command: net start Memurai
    echo.
) else (
=======

>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
    echo [OK] Redis/Memurai service check completed
    echo.
)

<<<<<<< HEAD
echo ====================================
=======

>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
echo Step 3/4: Starting backend services
echo ====================================
echo.

<<<<<<< HEAD
echo [INFO] Starting FastAPI server...
start "PaperGraph - FastAPI Server" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && echo ==================================== && echo FastAPI Server && echo ==================================== && echo Visit http://localhost:8000/docs for API documentation && echo Press Ctrl+C to stop server && echo. && python -m app.main"

timeout /t 3 /nobreak >nul

echo [INFO] Starting Celery Worker...
start "PaperGraph - Celery Worker" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && set CELERY_BROKER_URL=redis://localhost:6379/1 && set CELERY_RESULT_BACKEND=redis://localhost:6379/2 && echo ==================================== && echo Celery Worker && echo ==================================== && echo Press Ctrl+C to stop worker && echo. && celery -A app.tasks.celery_app worker --loglevel=info --pool=solo"

timeout /t 2 /nobreak >nul

echo ====================================
=======

>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
echo Step 4/4: Starting frontend service
echo ====================================
echo.

set FRONTEND_DIR=knowledge_graph_system_v2\knowledge_graph_system_v2

if not exist "%FRONTEND_DIR%" (
<<<<<<< HEAD
=======
    echo [ERROR] 前端目录不存在: %FRONTEND_DIR%
>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
    echo [ERROR] Frontend directory not found: %FRONTEND_DIR%
    pause
    exit /b 1
)

<<<<<<< HEAD
if not exist "%FRONTEND_DIR%\node_modules" (
=======

>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
    echo [INFO] Frontend dependencies not found, installing...
    cd /d "%FRONTEND_DIR%"
    call npm install
    if errorlevel 1 (
<<<<<<< HEAD
=======

>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
        echo [ERROR] Frontend dependencies installation failed
        pause
        exit /b 1
    )
    cd /d %~dp0
<<<<<<< HEAD
=======

>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
    echo [OK] Frontend dependencies installed
    echo.
)

<<<<<<< HEAD
=======

>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
echo [INFO] Starting frontend service...
start "PaperGraph - Frontend Server" cmd /k "cd /d %~dp0\%FRONTEND_DIR% && echo ==================================== && echo Frontend Server && echo ==================================== && echo Visit http://localhost:3000 in your browser && echo Press Ctrl+C to stop server && echo. && npm run serve"

echo.
echo ====================================
<<<<<<< HEAD
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
=======

>>>>>>> 1323288fd3d48c4c20eb59d7158432c9aacf479e
echo Press any key to close this window...
pause >nul

