@echo off
chcp 65001 >nul
title A-Share MCP Server Manager

:menu
cls
echo ===============================================
echo         A-Share MCP Server Manager
echo ===============================================
echo.
echo Please select an option:
echo.
echo [1] Start Server
echo [2] Stop Server  
echo [3] Check Status
echo [4] View Server Logs (if running)
echo [5] Test Service
echo [0] Exit
echo.

set /p choice="Enter your choice (0-5): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto status
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto test
if "%choice%"=="0" goto exit
goto invalid

:start
echo.
echo [INFO] Starting A-Share MCP Server...
call start.bat
goto menu

:stop
echo.
echo [INFO] Stopping A-Share MCP Server...
call stop_simple.bat
goto menu

:status
echo.
call status.bat
goto menu

:logs
echo.
echo [INFO] Opening browser to view SSE stream...
echo [INFO] Press Ctrl+C in the browser to stop viewing
start http://localhost:8000/sse
pause
goto menu

:test
echo.
echo [INFO] Running service test...
uv run python test_service.py
pause
goto menu

:invalid
echo.
echo [ERROR] Invalid choice. Please enter a number between 0-5.
pause
goto menu

:exit
echo.
echo [INFO] Goodbye!
exit