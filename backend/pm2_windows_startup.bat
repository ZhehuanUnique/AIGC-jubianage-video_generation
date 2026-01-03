@echo off
REM PM2 Windows 开机自启动脚本
REM 此脚本会被任务计划程序调用

cd /d "%~dp0"
pm2 resurrect

