@echo off
REM agents-manager standalone installer shim (Windows)
python "%~dp0install.py" %*
exit /b %errorlevel%
