@echo off
REM agents-manager installer shim (Windows) — defers to Python
python "%~dp0install.py" %*
exit /b %errorlevel%
