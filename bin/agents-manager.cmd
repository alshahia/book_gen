@echo off
REM agents-manager CLI shim (Windows) — defers to Python
python "%~dp0agents-manager.py" %*
exit /b %errorlevel%
