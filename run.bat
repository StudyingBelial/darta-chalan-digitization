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

:: Check if first argument is a plain port number (e.g. "run.bat 9000")
set "EXTRA_ARGS=%*"
if not "%~1"=="" (
    echo %~1| findstr /r "^[0-9][0-9]*$" >nul
    if not errorlevel 1 (
        set "EXTRA_ARGS=--port %~1 %2 %3 %4 %5"
    )
)

:: Run the universal runner file
%PYTHON_CMD% run_app.py %EXTRA_ARGS%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [INFO] Application exited with code %ERRORLEVEL%.
)
