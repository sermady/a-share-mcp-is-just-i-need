@echo off
chcp 65001 >nul
title A-Share MCP Server

echo ===============================================
echo           A-Share MCP HTTP Server
echo ===============================================
echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.12+ and try again
    pause
    exit /b 1
)

REM 检查 uv 是否可用
uv --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] uv package manager is not installed
    echo Please install uv and try again
    pause
    exit /b 1
)

echo [INFO] Starting A-Share MCP Server...
echo [INFO] Service URL: http://localhost:8000
echo [INFO] SSE Endpoint: http://localhost:8000/sse
echo.

REM 启动服务器
uv run python http_server_minimal.py

echo.
echo [INFO] Server stopped
pause