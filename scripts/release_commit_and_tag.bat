@echo off
setlocal enabledelayedexpansion

:: ------------------------------------------------------------------
:: Configuration
:: ------------------------------------------------------------------
set "log_file=release_log.txt"
set "max_log_size=1048576"  :: 1 MB

:: ------------------------------------------------------------------
:: Helper: timestamp and log rotation
:: ------------------------------------------------------------------
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=!dt:~0,4!"
set "MM=!dt:~4,2!"
set "DD=!dt:~6,2!"
set "HH=!dt:~8,2!"
set "MIN=!dt:~10,2!"
set "timestamp=!YYYY!-!MM!-!DD! !HH!:!MIN!"

if exist "%log_file%" (
    for %%A in ("%log_file%") do set "log_size=%%~zA"
    if !log_size! GTR %max_log_size% (
        ren "%log_file%" "release_log_!YYYY!!MM!!DD!_!HH!!MIN!.txt" >nul 2>&1
    )
)

echo [!timestamp!] Starting release helper >> "%log_file%"

:: ------------------------------------------------------------------
:: Verify Git availability
:: ------------------------------------------------------------------
git --version >nul 2>&1
if errorlevel 1 (
    echo [!timestamp!] Error: Git not found. >> "%log_file%"
    echo Error: Git not found. Install Git and try again.
    exit /b 1
)

:: ------------------------------------------------------------------
:: Back up unhashed/untracked files
:: ------------------------------------------------------------------
set "backup_dir=backup_!YYYY!!MM!!DD!"
echo [!timestamp!] Backing up untracked files to %backup_dir% >> "%log_file%"
if exist "%backup_dir%" (
    echo [!timestamp!] Backup directory already exists; files may be overwritten. >> "%log_file%"
)
mkdir "%backup_dir%" >nul 2>&1
if errorlevel 1 (
    echo [!timestamp!] Error: Unable to create backup directory. >> "%log_file%"
    echo Error: Failed to create backup directory.
    exit /b 1
)

git ls-files --others --exclude-standard > untracked.txt
if not exist untracked.txt (
    echo [!timestamp!] Error: Could not enumerate untracked files. >> "%log_file%"
    echo Error: Unable to list untracked files.
    exit /b 1
)

set "has_untracked=0"
for /f "tokens=*" %%f in (untracked.txt) do (
    set "has_untracked=1"
    if exist "%%f\" (
        robocopy "%%f" "%backup_dir%\%%f" /E /NFL /NDL /NJH /NJS >nul 2>&1
        if errorlevel 8 echo [!timestamp!] Warning: robocopy error copying directory %%f >> "%log_file%"
    ) else (
        set "dest=%backup_dir%\%%f"
        for %%p in ("!dest!") do (
            if not exist "%%~dpp" (
                mkdir "%%~dpp" >nul 2>&1
            )
        )
        copy "%%f" "!dest!" >nul 2>&1
        if errorlevel 1 echo [!timestamp!] Warning: Failed to copy file %%f >> "%log_file%"
    )
)

if "%has_untracked%"=="0" (
    echo [!timestamp!] No untracked files found. >> "%log_file%"
) else (
    echo [!timestamp!] Untracked files backed up. >> "%log_file%"
)

:: ------------------------------------------------------------------
:: Stage documentation (markdown/json)
:: ------------------------------------------------------------------
git add *.md *.json >nul 2>&1
if errorlevel 1 (
    echo [!timestamp!] Error: git add for docs failed. >> "%log_file%"
    echo Error: Failed to add markdown/json files.
    del untracked.txt >nul 2>&1
    exit /b 1
)

echo [!timestamp!] Markdown/JSON files staged. >> "%log_file%"

:: ------------------------------------------------------------------
:: Optional cleanup of remaining untracked content
:: ------------------------------------------------------------------
echo Running interactive git clean (confirm before deleting remaining files)...
git clean -fdx -i

del untracked.txt >nul 2>&1

echo [!timestamp!] Untracked triage complete. >> "%log_file%"

:: ------------------------------------------------------------------
:: Validate command arguments
:: ------------------------------------------------------------------
if "%~1"=="" (
    echo Usage: %~nx0 "commit message" tag_name
    echo [!timestamp!] Error: Commit message not provided. >> "%log_file%"
    exit /b 1
)
if "%~2"=="" (
    echo Error: Tag name required.
    echo [!timestamp!] Error: Tag name missing. >> "%log_file%"
    exit /b 1
)

set "COMMIT_MSG=%~1"
set "TAG_NAME=%~2"

:: ------------------------------------------------------------------
:: Stage, commit, tag, push
:: ------------------------------------------------------------------
set "timestamp=%date% %time%"

git add -A >nul 2>&1
if errorlevel 1 (
    echo [!timestamp!] Error: git add -A failed. >> "%log_file%"
    echo Error: Unable to stage changes.
    exit /b 1
)
echo [!timestamp!] All changes staged. >> "%log_file%"

git commit -m "%COMMIT_MSG%" >nul 2>&1
if errorlevel 1 (
    echo [!timestamp!] Error: git commit failed. >> "%log_file%"
    echo Error: Commit failed.
    exit /b 1
)
echo [!timestamp!] Commit created. >> "%log_file%"

git tag "%TAG_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [!timestamp!] Error: git tag failed. >> "%log_file%"
    echo Error: Tag creation failed.
    exit /b 1
)
echo [!timestamp!] Tag %TAG_NAME% created. >> "%log_file%"

git push origin HEAD --tags >nul 2>&1
if errorlevel 1 (
    echo [!timestamp!] Error: git push failed. >> "%log_file%"
    echo Error: Push to origin failed.
    exit /b 1
)
echo [!timestamp!] Changes pushed to origin with tags. >> "%log_file%"

echo Release complete.
echo [!timestamp!] Release helper completed successfully. >> "%log_file%"

endlocal
exit /b 0

