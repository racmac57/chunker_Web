@echo off
REM Fix All Claude Exports - Conversations, Projects, Users
REM Author: R. A. Carucci
REM Purpose: Fix all JSON files from Claude export for viewer compatibility

echo ============================================================
echo Claude Export Fixer - ALL FILES
echo ============================================================
echo.
echo Processing:
echo   - conversations.json
echo   - projects.json  
echo   - users.json
echo.
echo ============================================================
echo.

cd /d "C:\_chunker"
python fix_all_claude_exports.py

echo.
echo ============================================================
echo.
echo To upload to Claude Chat Viewer:
echo   https://tools.osteele.com/claude-chat-viewer
echo.
echo Use files from:
echo   all_fixed_files folder
echo.
echo ============================================================
echo Press any key to exit...
pause > nul

