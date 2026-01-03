@echo off
REM PM2 启动后端服务脚本

echo ========================================
echo PM2 后端服务管理
echo ========================================
echo.

REM 检查 PM2 是否安装
pm2 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PM2 未安装！
    echo.
    echo 请先安装 PM2:
    echo   npm install -g pm2
    echo.
    pause
    exit /b 1
)

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 创建日志目录
if not exist "logs" mkdir logs

echo [INFO] 正在启动后端服务...
pm2 start ecosystem.config.cjs

if errorlevel 1 (
    echo [ERROR] 启动失败！
    pause
    exit /b 1
)

echo.
echo [SUCCESS] 服务已启动！
echo.
echo 常用命令:
echo   查看状态: pm2 status
echo   查看日志: pm2 logs aigc-backend
echo   停止服务: pm2 stop aigc-backend
echo   重启服务: pm2 restart aigc-backend
echo   删除服务: pm2 delete aigc-backend
echo   保存配置: pm2 save
echo   设置开机自启: pm2 startup
echo.
pause

