@echo off
REM PM2 删除后端服务

echo ========================================
echo PM2 删除后端服务
echo ========================================
echo.

REM 检查 PM2 是否安装
pm2 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PM2 未安装！
    pause
    exit /b 1
)

echo [WARN] 这将删除 PM2 中的后端服务进程
echo 按任意键继续，或按 Ctrl+C 取消...
pause >nul

echo.
echo [INFO] 正在删除后端服务...
pm2 delete aigc-backend

if errorlevel 1 (
    echo [WARN] 服务可能不存在
) else (
    echo [SUCCESS] 服务已删除
)

echo.
pause

