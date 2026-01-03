@echo off
REM 卸载后端服务任务计划

echo ========================================
echo 后端服务自动启动卸载脚本
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 需要管理员权限！
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

set TASK_NAME=AIGC_Backend_Service

echo [INFO] 正在删除任务: %TASK_NAME%

schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [INFO] 任务不存在，无需删除
) else (
    schtasks /delete /tn "%TASK_NAME%" /f
    if errorlevel 1 (
        echo [ERROR] 删除失败！
    ) else (
        echo [SUCCESS] 任务已删除
    )
)

echo.
pause

