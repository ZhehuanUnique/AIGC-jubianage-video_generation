@echo off
REM 后端服务启动脚本（后台运行，自动重启）
REM 用于 Windows 任务计划程序或开机自启动

cd /d "%~dp0"
set PYTHON_PATH=python
set WORK_DIR=%~dp0

REM 检查 Python 是否可用
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未找到，请确保 Python 已安装并添加到 PATH
    pause
    exit /b 1
)

REM 切换到工作目录
cd /d "%WORK_DIR%"

REM 启动 uvicorn 服务器（后台运行）
echo [INFO] 正在启动后端 API 服务...
echo [INFO] 工作目录: %WORK_DIR%
echo [INFO] 服务地址: http://0.0.0.0:8001
echo [INFO] 按 Ctrl+C 停止服务

REM 使用 uvicorn 启动，启用自动重载（开发环境）或生产模式
%PYTHON_PATH% -m uvicorn backend.api:app --host 0.0.0.0 --port 8001

REM 如果服务意外退出，记录日志
if errorlevel 1 (
    echo [ERROR] 服务异常退出，退出码: %errorlevel%
    echo [ERROR] 时间: %date% %time% >> "%WORK_DIR%backend_error.log"
    echo [ERROR] 退出码: %errorlevel% >> "%WORK_DIR%backend_error.log"
    echo. >> "%WORK_DIR%backend_error.log"
)

