@echo off
chcp 65001 >nul
title A-Share MCP Server Status

echo ===============================================
echo       A-Share MCP Server Status Check
echo ===============================================
echo.

echo [INFO] Checking server status on port 8000...
echo.

REM 检查端口 8000 是否被占用
netstat -ano | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo [STATUS] Server is NOT running
    echo [INFO] Port 8000 is free
) else (
    echo [STATUS] Server is RUNNING
    echo [INFO] Active connections on port 8000:
    netstat -ano | findstr ":8000"
    echo.
    
    REM 尝试测试服务响应
    echo [INFO] Testing server response...
    curl -s --max-time 3 http://localhost:8000/sse >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Server is running but may not be responding properly
    ) else (
        echo [SUCCESS] Server is responding normally
        echo [INFO] Service URL: http://localhost:8000
        echo [INFO] SSE Endpoint: http://localhost:8000/sse
    )
)

echo.
pause