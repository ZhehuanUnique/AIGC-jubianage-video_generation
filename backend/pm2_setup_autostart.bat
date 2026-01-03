@echo off
REM PM2 设置开机自启动

echo ========================================
echo PM2 开机自启动设置
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

REM 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo [WARN] 需要管理员权限来设置开机自启动
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    echo 或者手动运行以下命令:
    echo   pm2 save
    echo   pm2 startup
    echo.
    pause
    exit /b 1
)

echo [INFO] 保存当前 PM2 进程列表...
pm2 save

if errorlevel 1 (
    echo [ERROR] 保存失败！请确保服务已启动
    echo 运行: pm2 start ecosystem.config.js
    pause
    exit /b 1
)

echo.
echo [INFO] 生成开机自启动脚本...
pm2 startup

if errorlevel 1 (
    echo [ERROR] 生成启动脚本失败！
    pause
    exit /b 1
)

echo.
echo [SUCCESS] 开机自启动已设置！
echo.
echo PM2 会在系统启动时自动恢复所有保存的进程
echo.
echo 管理命令:
echo   查看状态: pm2 status
echo   查看日志: pm2 logs aigc-backend
echo   停止服务: pm2 stop aigc-backend
echo   重启服务: pm2 restart aigc-backend
echo.
pause

