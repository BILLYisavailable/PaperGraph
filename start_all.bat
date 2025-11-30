@echo off
chcp 65001 >nul
echo ====================================
echo PaperGraph - 一键启动所有服务
echo PaperGraph - Start All Services
echo ====================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到Python，请先安装Python 3.9+
    echo [ERROR] Cannot find Python, please install Python 3.9+ first
    pause
    exit /b 1
)

REM 步骤1: 运行setup（如果虚拟环境不存在）
if not exist "venv\" (
    echo ====================================
    echo 步骤 1/4: 设置环境
    echo Step 1/4: Setting up environment
    echo ====================================
    echo.
    call setup.bat
    if errorlevel 1 (
        echo [ERROR] 环境设置失败
        echo [ERROR] Environment setup failed
        pause
        exit /b 1
    )
    echo.
) else (
    echo [OK] 虚拟环境已存在
    echo [OK] Virtual environment already exists
    echo.
)

REM 激活虚拟环境
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] 无法激活虚拟环境
    echo [ERROR] Cannot activate virtual environment
    pause
    exit /b 1
)


echo Step 2/4: Checking Redis service
echo ====================================
echo.
sc query Memurai >nul 2>&1
if errorlevel 1 (

    echo [OK] Redis/Memurai service check completed
    echo.
)


echo Step 3/4: Starting backend services
echo ====================================
echo.


echo Step 4/4: Starting frontend service
echo ====================================
echo.

set FRONTEND_DIR=knowledge_graph_system_v2\knowledge_graph_system_v2

if not exist "%FRONTEND_DIR%" (
    echo [ERROR] 前端目录不存在: %FRONTEND_DIR%
    echo [ERROR] Frontend directory not found: %FRONTEND_DIR%
    pause
    exit /b 1
)


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

echo Press any key to close this window...
pause >nul

