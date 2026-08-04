@echo off
rem Book Kit CLI wrapper (Windows cmd).
rem Delegates to install.py for install/upgrade/uninstall; otherwise prints help.
setlocal
set HERE=%~dp0..
set PY=python
where py >nul 2>nul && set PY=py
"%PY%" "%HERE%\install.py" %*
endlocal