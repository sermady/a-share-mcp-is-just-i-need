@echo off
chcp 65001 >nul
title Stop A-Share MCP Server

echo ===============================================
echo        Stop A-Share MCP HTTP Server
echo ===============================================
echo.

REM 直接根据端口号查找并终止进程（最可靠的方法）
echo [INFO] Searching for processes using port 8000...

REM 查找占用8000端口的进程并终止
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    if not "%%a"=="0" (
        echo [INFO] Found process using port 8000: PID %%a
        taskkill /f /pid %%a >nul 2>&1
        if errorlevel 1 (
            echo [WARNING] Failed to kill process %%a
        ) else (
            echo [SUCCESS] Successfully stopped process %%a
        )
    )
)

REM 等待一秒让进程完全结束
timeout /t 1 /nobreak >nul

REM 检查端口 8000 是否还被占用
echo [INFO] Checking if port 8000 is still in use...
netstat -ano | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Port 8000 is now free
) else (
    echo [WARNING] Port 8000 may still be in use
    echo [INFO] You may need to manually kill the process or restart your computer
    echo.
    echo Active connections on port 8000:
    netstat -ano | findstr ":8000"
)

echo.
echo [INFO] Stop operation completed
echo.
pause