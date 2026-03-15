@echo off
title Life Manager - Setup and Launch
color 0A

echo ============================================================
echo           Ultimate Daily Life Manager - Launcher
echo ============================================================
echo.

REM ── Check Python ────────────────────────────────────────────────
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.10 or newer from:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, check the box
    echo   "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM ── Show Python version ────────────────────────────────────────
echo [OK] Python found:
python --version
echo.

REM ── Install / upgrade dependencies ─────────────────────────────
echo [..] Installing dependencies (this may take a minute the first time)...
python -m pip install --upgrade pip >nul 2>nul
python -m pip install -r "%~dp0requirements.txt"
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies.
    echo Try running:  python -m pip install flet
    pause
    exit /b 1
)
echo [OK] Dependencies installed.
echo.

REM ── Check Ollama (non-blocking) ────────────────────────────────
echo [..] Checking if Ollama is running...
curl -s http://localhost:11434/api/tags >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!!] Ollama is NOT running. AI features will be unavailable.
    echo      To enable AI, install Ollama from https://ollama.com
    echo      Then run:  ollama pull llama3.2
    echo.
) else (
    echo [OK] Ollama is running.
    echo.
)

REM ── Launch the app ─────────────────────────────────────────────
echo ============================================================
echo   Starting Life Manager...
echo   (Close this window to stop the application)
echo ============================================================
echo.
cd /d "%~dp0"
python main.py
pause
