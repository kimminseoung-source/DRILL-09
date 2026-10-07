@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" move_character_with_key.py
) else (
    py move_character_with_key.py
)
if errorlevel 1 pause
