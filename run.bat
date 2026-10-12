@echo off
setlocal

title NTC Darta-Chalan Digitization System

echo ============================================================================
echo   [NTC] NEPAL TELECOM CORPORATION
echo   Darta-Chalan Digitization System (Runner)
echo ============================================================================

:: 1. Locate system Python executable
set "PYTHON_CMD=python"
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python is not installed or not in system PATH!
        echo Please install Python 3.10+ from python.org and add it to PATH.
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=py"
    )
)

:: 2. Create virtual environment if it does not exist
if not exist "venv\Scripts\activate.bat" (
    echo [SETUP] Python virtual environment 'venv' not found.
    echo [SETUP] Creating virtual environment 'venv'...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment 'venv'.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment 'venv' created.
)

:: 3. Activate virtual environment
echo [INFO] Activating virtual environment: venv
call "venv\Scripts\activate.bat"
set "PYTHON_CMD=python"

:: 4. Verify and install Python requirements
echo [INFO] Checking Python dependencies...
python -c "import fastapi, uvicorn, sqlalchemy, pydantic, alembic" >nul 2>nul
if errorlevel 1 (
    echo [SETUP] Installing required packages from requirements.txt...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install Python dependencies from requirements.txt!
        pause
        exit /b 1
    )
    echo [SUCCESS] Python dependencies installed successfully.
) else (
    echo [INFO] Python dependencies are up-to-date.
)

:: 5. Handle positional port argument (e.g. "run.bat 9000")
set "EXTRA_ARGS=%*"
if not "%~1"=="" (
    echo %~1| findstr /r "^[0-9][0-9]*$" >nul
    if not errorlevel 1 (
        set "EXTRA_ARGS=--port %~1 %2 %3 %4 %5"
    )
)

:: 6. Launch the universal application host
echo [INFO] Launching application runner...
%PYTHON_CMD% run_app.py %EXTRA_ARGS%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [INFO] Application exited with code %ERRORLEVEL%.
)
