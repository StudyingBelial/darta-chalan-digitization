@echo off
setlocal enabledelayedexpansion

title NTC Darta-Chalan - Interactive Deployment Launcher

echo ============================================================================
echo   [NTC] NEPAL TELECOM CORPORATION
echo   Darta-Chalan Digitization System — Deployment Launcher
echo ============================================================================
echo.

:: Read current settings from .env if present
set "CURR_HOST=0.0.0.0"
set "CURR_PORT=8000"
if exist ".env" (
    for /f "tokens=1,2 delims==" %%A in (.env) do (
        if "%%A"=="HOST" set "CURR_HOST=%%B"
        if "%%A"=="APP_HOST" set "CURR_HOST=%%B"
        if "%%A"=="PORT" set "CURR_PORT=%%B"
        if "%%A"=="APP_PORT" set "CURR_PORT=%%B"
    )
)

echo Current configuration from .env:
echo   * Host Address : !CURR_HOST!
echo   * Port Number  : !CURR_PORT!
echo.
echo Choose deployment mode:
echo   [1] Unified Application Runner (Direct Python / Bare-Metal)  [Recommended]
echo   [2] Background Containers (Docker Compose)
echo.
set /p DEPLOY_CHOICE="Select mode [1 or 2, default: 1]: "
if "!DEPLOY_CHOICE!"=="" set "DEPLOY_CHOICE=1"

if "!DEPLOY_CHOICE!"=="2" (
    echo.
    echo ============================================================================
    echo   Launching via Docker Compose in the background...
    echo ============================================================================
    docker compose up -d --build
    echo.
    echo Containers launched!
    echo   * Web Portal URL : http://localhost:3000 (or http://^<YOUR_SERVER_IP^>:3000)
    echo   * REST API Docs  : http://localhost:8000/docs
    echo   * Check logs with: docker compose logs -f
    echo ============================================================================
    pause
    exit /b 0
)

echo.
echo Choose network accessibility:
echo   [1] Remote ^& Local (0.0.0.0) — allows other PCs/phones on LAN/Remote to connect [Default]
echo   [2] Localhost Only (127.0.0.1) — restricted to this computer only
echo.
set /p NET_CHOICE="Select access [1 or 2, default: 1]: "
set "CHOSEN_HOST=0.0.0.0"
if "!NET_CHOICE!"=="2" set "CHOSEN_HOST=127.0.0.1"

echo.
set /p CHOSEN_PORT="Enter Port number [default: !CURR_PORT!]: "
if "!CHOSEN_PORT!"=="" set "CHOSEN_PORT=!CURR_PORT!"

echo.
echo ============================================================================
echo Starting application on Host: !CHOSEN_HOST! | Port: !CHOSEN_PORT!
echo ============================================================================

call run.bat --host !CHOSEN_HOST! --port !CHOSEN_PORT!
