@echo off
setlocal enabledelayedexpansion

:: Ensure execution from the repository directory
cd /d "%~dp0"

title NTC Darta-Chalan - Environment Setup

echo ============================================================================
echo   [NTC] NEPAL TELECOM CORPORATION
echo   Darta-Chalan Digitization System — Environment Setup
echo ============================================================================
echo.

:: 1. Verify Docker installation
echo [1/5] Checking Docker installation...
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed or not in system PATH!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    echo Once installed, restart your terminal and run setup.bat again.
    echo.
    pause
    exit /b 1
)
echo       * Docker CLI found.

:: 2. Verify Docker daemon is active
echo.
echo [2/5] Checking Docker Desktop status...
docker info >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Docker daemon is not running!
    echo Please start the "Docker Desktop" application on your computer.
    echo Wait until Docker Desktop shows "Engine running", then press any key.
    pause
    docker info >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Docker Desktop is still not running. Please launch it and retry.
        pause
        exit /b 1
    )
)
echo       * Docker Engine is running and responsive.

:: 3. Setup .env configuration
echo.
echo [3/5] Checking environment configuration (.env)...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo       * Created .env from template (.env.example).
    ) else (
        echo [WARN] .env.example not found. Creating minimal default .env...
        (
            echo PROJECT_NAME="Nepal Telecom Darta-Chalan Digitization System"
            echo PORT=8000
            echo FRONTEND_PORT=3000
            echo POSTGRES_DB=darta_chalan_db
            echo POSTGRES_USER=ntc_admin
            echo POSTGRES_PASSWORD=ntc_secure_password_2081
            echo POSTGRES_PORT=5432
            echo DATABASE_URL=postgresql+psycopg2://ntc_admin:ntc_secure_password_2081@db:5432/darta_chalan_db
        ) > .env
        echo       * Minimal .env initialized.
    )
) else (
    echo       * .env configuration verified.
)

:: 4. Ensure local storage directories exist
echo.
echo [4/5] Ensuring storage directory structure...
if not exist "storage\uploads\darta" mkdir "storage\uploads\darta"
if not exist "storage\uploads\chalan" mkdir "storage\uploads\chalan"
if not exist "storage\uploads\inbound" mkdir "storage\uploads\inbound"
if not exist "storage\logs" mkdir "storage\logs"
if not exist "storage\uploads\.gitkeep" type nul > "storage\uploads\.gitkeep"
if not exist "storage\logs\.gitkeep" type nul > "storage\logs\.gitkeep"
echo       * Storage folders verified.

:: Clean up obsolete SQLite db if present
if exist "digitization.db" (
    del /f /q "digitization.db" >nul 2>nul
    echo       * Cleaned up legacy SQLite file (system uses PostgreSQL).
)

:: 5. Configure Windows Firewall (optional / best-effort)
echo.
echo [5/5] Configuring Windows Firewall for LAN accessibility...
netsh advfirewall firewall show rule name="NTC Darta-Chalan Web Ports (3000, 8000)" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    netsh advfirewall firewall add rule name="NTC Darta-Chalan Web Ports (3000, 8000)" dir=in action=allow protocol=TCP localport=3000,8000 >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo       * Added firewall rule for Web Ports (3000, 8000).
    ) else (
        echo       * [Note] Could not add firewall rule automatically (requires Run as Administrator).
        echo                If other computers cannot connect, allow ports 3000 and 8000 in Windows Firewall.
    )
) else (
    echo       * Firewall rule already present.
)

netsh advfirewall firewall show rule name="NTC Darta-Chalan SMTP Intake (1025)" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    netsh advfirewall firewall add rule name="NTC Darta-Chalan SMTP Intake (1025)" dir=in action=allow protocol=TCP localport=1025 >nul 2>nul
)

echo.
echo ============================================================================
echo   [SUCCESS] Environment setup completed successfully!
echo.
echo   To launch the server exclusively in Docker, simply run:
echo     run.bat
echo   or:
echo     python run_app.py
echo ============================================================================
echo.
pause
