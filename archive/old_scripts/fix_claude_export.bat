@echo off
REM Fix Claude Export - Run Python script to repair validation errors
REM Author: R. A. Carucci

echo ============================================================
echo Claude Export Validator and Fixer
echo ============================================================
echo.

cd /d "C:\_chunker"
python fix_claude_export.py

echo.
echo ============================================================
echo Press any key to exit...
pause > nul

