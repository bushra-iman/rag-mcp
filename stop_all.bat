@echo off
REM =========================================================
REM  Stop all Student Assistant RAG servers started by
REM  run_all.bat (stops the windows bound to 5000/8000/7000)
REM =========================================================
title Student Assistant RAG - Stop servers
echo Stopping RAG API, MCP server and Mock OAuth...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":7000" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Done. Servers stopped.
pause