@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" drill09.py
) else (
    py drill09.py
)
if errorlevel 1 pause
