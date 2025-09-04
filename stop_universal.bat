@echo off
chcp 65001 >nul
title Stop A-Share MCP Server

echo ===============================================
echo        Stop A-Share MCP HTTP Server
echo ===============================================
echo.

echo [INFO] Stopping A-Share MCP Server on port 8000...

REM 方法1: 根据端口号直接终止进程（最可靠）
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

REM 再次检查端口状态
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [SUCCESS] Port 8000 is now free - Server stopped successfully
) else (
    echo.
    echo [WARNING] Port 8000 may still be in use
    echo [INFO] Trying alternative method...
    
    REM 方法2: 强制终止所有Python进程（备选方案）
    echo [INFO] Force stopping all Python processes...
    taskkill /f /im python.exe >nul 2>&1
    
    timeout /t 2 /nobreak >nul
    
    netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
    if errorlevel 1 (
        echo [SUCCESS] Port 8000 is now free after force stop
    ) else (
        echo [ERROR] Failed to stop server. Please manually close the Python process
        echo Active connections on port 8000:
        netstat -ano | findstr ":8000"
    )
)

echo.
pause