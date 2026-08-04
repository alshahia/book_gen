@echo off
rem ============================================================
rem Book Kit - Windows one-shot installer (already unzipped)
rem
rem Use this when you have already extracted book-kit-*.zip and
rem just need to run install.py against the current folder.
rem
rem Usage (any of these works):
rem   install.bat
rem   .\install.bat
rem   install.bat C:\path\to\my-project
rem
rem What it does:
rem   1. Resolves its own location (works from any cwd)
rem   2. Locates Python (py launcher first, then python, then python3)
rem   3. Runs install.py --target . (or the path you pass)
rem   4. Runs scripts/doctor.py for a preflight report
rem   5. Prints the next-step commands to launch OpenCode
rem
rem On any error, PAUSEs so the window stays visible long enough
rem to read (fixes the "flash and close" problem on double-click).
rem ============================================================
setlocal EnableDelayedExpansion

rem ---- 1. Resolve our own location so the script is portable ----
set "SELF_DIR=%~dp0"
pushd "%SELF_DIR%" >nul
set "SELF_DIR=%CD%"
popd >nul

rem ---- 2. Verify install.py is here ----------------------------
if not exist "%SELF_DIR%\install.py" (
    echo [FAIL] install.py not found at %SELF_DIR%
    echo        This batch file must live next to install.py inside the kit.
    goto :error
)

rem ---- 3. Resolve target ---------------------------------------
rem Default to the kit root (this bat's own dir) so the next-step "cd"
rem hint is actionable even though install.py also prints the absolute path.
if not "%~1"=="" (
    set "TARGET=%~1"
) else (
    set "TARGET=%SELF_DIR%"
)

rem ---- 4. Locate Python ----------------------------------------
set "PY="
where py >nul 2>nul && set "PY=py"
if "%PY%"=="" (
    where python >nul 2>nul && set "PY=python"
)
if "%PY%"=="" (
    where python3 >nul 2>nul && set "PY=python3"
)
if "%PY%"=="" (
    echo [FAIL] Python not found in PATH
    echo        install Python 3.8+ from https://python.org
    echo        or run: winget install Python.Python.3.12
    goto :error
)
for /f "tokens=2" %%V in ('"%PY%" --version 2^>^&1') do set "PY_VERSION=%%V"
echo [OK]   Python !PY_VERSION!

rem ---- 5. Run installer ---------------------------------------
echo [step] Running installer (target: !TARGET!)
"%PY%" "%SELF_DIR%\install.py" --target "!TARGET!" --no-doctor
if errorlevel 1 (
    echo [FAIL] installer exited with errors
    goto :error
)

rem ---- 6. Doctor report ----------------------------------------
if exist "%SELF_DIR%\scripts\doctor.py" (
    echo [step] Running doctor preflight
    pushd "!TARGET!" >nul
    "%PY%" "%SELF_DIR%\scripts\doctor.py"
    popd >nul
)

rem ---- 7. Next steps -------------------------------------------
echo.
echo ============================================================
echo Book Kit installed at: !TARGET!
echo.
echo Next steps:
echo   1. cd "!TARGET!"
echo   2. opencode
echo   3. say: "write a book about ^<topic^>"
echo.
echo To uninstall:
echo   "%PY%" "%SELF_DIR%\install.py" --target "!TARGET!" --uninstall
echo ============================================================
echo.
pause
endlocal
exit /b 0

:error
echo.
echo Press any key to close...
pause >nul
endlocal
exit /b 1