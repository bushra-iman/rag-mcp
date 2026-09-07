@echo off
REM =========================================================
REM  Student Assistant RAG API - One-click launcher
REM  Starts all 3 servers in separate windows:
REM    1. RAG API         -> http://localhost:5000
REM    2. MCP server      -> http://localhost:8000/mcp
REM    3. Mock OAuth      -> http://localhost:7000
REM
REM  Ports can be changed in .env (PORT / MCP_PORT / OAUTH_PORT)
REM =========================================================
title Student Assistant RAG - Launcher
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
    echo ERROR: virtual environment not found.
    echo Run this first:  python -m venv venv
    echo Then install deps:  venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo ============================================================
echo  Student Assistant RAG API - starting all servers...
echo ============================================================
echo.

echo [1/3] Starting RAG API on port 5000 ...
start "RAG API (5000)" cmd /k venv\Scripts\python.exe app.py

echo [2/3] Starting MCP server on port 8000 ...
start "MCP Server (8000)" cmd /k venv\Scripts\python.exe mcp_server.py

echo [3/3] Starting Mock OAuth server on port 7000 ...
start "Mock OAuth (7000)" cmd /k venv\Scripts\python.exe mock_oauth_server.py

echo.
echo All servers launched in separate windows.
echo Close those windows, or run  stop_all.bat  to stop them.
echo.
pause