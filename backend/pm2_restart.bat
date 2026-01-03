@echo off
REM PM2 重启后端服务

echo ========================================
echo PM2 重启后端服务
echo ========================================
echo.

REM 检查 PM2 是否安装
pm2 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PM2 未安装！
    pause
    exit /b 1
)

echo [INFO] 正在重启后端服务...
pm2 restart aigc-backend

if errorlevel 1 (
    echo [ERROR] 重启失败！服务可能未运行
    echo 尝试启动服务: pm2 start ecosystem.config.js
) else (
    echo [SUCCESS] 服务已重启
)

echo.
pause

