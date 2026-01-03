@echo off
REM 安装后端服务为 Windows 任务计划程序
REM 需要管理员权限运行

echo ========================================
echo 后端服务自动启动安装脚本
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

set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%start_backend_service.bat
set TASK_NAME=AIGC_Backend_Service
set DESCRIPTION=剧变时代 - AI 视频生成后端服务

echo [INFO] 脚本路径: %SCRIPT_PATH%
echo [INFO] 任务名称: %TASK_NAME%
echo.

REM 删除已存在的任务（如果存在）
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] 发现已存在的任务，正在删除...
    schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
)

REM 创建新任务
echo [INFO] 正在创建任务计划...
schtasks /create /tn "%TASK_NAME%" ^
    /tr "\"%SCRIPT_PATH%\"" ^
    /sc onstart ^
    /ru "SYSTEM" ^
    /rl highest ^
    /f

if errorlevel 1 (
    echo [ERROR] 任务创建失败！
    pause
    exit /b 1
)

echo.
echo [SUCCESS] 任务创建成功！
echo.
echo 任务信息：
echo   - 任务名称: %TASK_NAME%
echo   - 触发条件: 系统启动时
echo   - 运行权限: SYSTEM（最高权限）
echo   - 脚本路径: %SCRIPT_PATH%
echo.
echo 管理命令：
echo   查看任务: schtasks /query /tn "%TASK_NAME%"
echo   运行任务: schtasks /run /tn "%TASK_NAME%"
echo   删除任务: schtasks /delete /tn "%TASK_NAME%" /f
echo.
pause

