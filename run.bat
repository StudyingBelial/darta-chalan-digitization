@echo off
setlocal

:: Ensure execution from the repository directory
cd /d "%~dp0"

title NTC Darta-Chalan Digitization System (Docker)

:: Check if Python is installed; if so, delegate to run_app.py for the full interactive runner
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python run_app.py %*
    goto :end
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py run_app.py %*
    goto :end
)

:: If Python is not installed, directly invoke Docker Compose
echo [INFO] Python not found in system PATH. Directing to Docker Compose...
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Neither Python nor Docker is installed or in system PATH!
    echo Please install Docker Desktop: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting containers via Docker Compose...
docker compose up --build %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [NOTE] If Docker failed to start, please ensure Docker Desktop is open and running.
)

:end
set "EXIT_CODE=%ERRORLEVEL%"
if %EXIT_CODE% NEQ 0 (
    echo.
    echo Process exited with code %EXIT_CODE%.
    pause
)
