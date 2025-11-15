@echo off
setlocal EnableDelayedExpansion

REM Get the directory where this batch file is located
set "BATCH_DIR=%~dp0"
set "BATCH_DIR=!BATCH_DIR:~0,-1!"

REM Set script path - use batch file's directory
set "SCRIPT=!BATCH_DIR!\Chunker_MoveOptimized.ps1"

REM Debug output
echo [Batch] Launching PowerShell script:
echo !SCRIPT!
echo.

REM Check if script exists
if not exist "!SCRIPT!" (
    echo Error: PowerShell script not found at !SCRIPT!
    echo Batch file directory: !BATCH_DIR!
    pause
    exit /b 1
)

REM Run PowerShell script with all arguments
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -File "!SCRIPT!" %*

REM Capture exit code (ERRORLEVEL must be checked immediately)
set EXITCODE=%ERRORLEVEL%

REM Always pause so user can see output
echo.
echo [Batch] Script completed with exit code: %EXITCODE%
if %EXITCODE% NEQ 0 (
    echo.
    echo PowerShell reported an error. Review any messages above.
)
pause

REM Exit with the captured code (before endlocal clears it)
set "EXIT=%EXITCODE%"
endlocal
exit /b %EXIT%

