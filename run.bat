@echo off
setlocal

title NTC Darta-Chalan Digitization System

echo ============================================================================
echo   [NTC] NEPAL TELECOM CORPORATION
echo   Darta-Chalan Digitization System (Runner)
echo ============================================================================

:: Locate Python command
set PYTHON_CMD=python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python is not installed or not in PATH!
        echo Please install Python 3.10+ and add it to your system PATH.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
)

:: Check if local virtual environment exists and activate if present
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment: venv
    call "venv\Scripts\activate.bat"
    set PYTHON_CMD=python
)
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment: .venv
    call ".venv\Scripts\activate.bat"
    set PYTHON_CMD=python
)

:: Run the universal runner file
%PYTHON_CMD% run_app.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [INFO] Application exited with code %ERRORLEVEL%.
)
