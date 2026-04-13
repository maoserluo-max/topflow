@echo off
chcp 65001 >nul
color 0A
title TikTok Demo - Python 3.14

set "PYTHON_EXE=C:\Users\maose\AppData\Local\Python\pythoncore-3.14-64\python.exe"

echo.
echo ============================================
echo    TikTok Data Crawler Demo Launcher
echo    Python Version: 3.14.3
echo ============================================
echo.

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at:
    echo   %PYTHON_EXE%
    echo.
    echo Please check the path or reinstall Python.
    pause
    exit /b 1
)

echo [OK] Python found: %PYTHON_EXE%
"%PYTHON_EXE%" --version
echo.

cd /d "%~dp0"
echo [INFO] Starting demo...
echo.

"%PYTHON_EXE%" -X utf8 demo.py

echo.
pause
