@echo off
REM PM2 停止后端服务

echo ========================================
echo PM2 停止后端服务
echo ========================================
echo.

REM 检查 PM2 是否安装
pm2 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PM2 未安装！
    pause
    exit /b 1
)

echo [INFO] 正在停止后端服务...
pm2 stop aigc-backend

if errorlevel 1 (
    echo [WARN] 服务可能未运行
) else (
    echo [SUCCESS] 服务已停止
)

echo.
pause

