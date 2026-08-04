@echo off
rem ============================================================
rem Book Kit - Windows one-shot installer
rem
rem Usage (any of these works):
rem   bin\install-book-kit.bat
rem   .\bin\install-book-kit.bat
rem   bin\install-book-kit.bat C:\downloads\book-kit-0.1.0.zip
rem   bin\install-book-kit.bat C:\downloads\book-kit-0.1.0.zip C:\my-project
rem   bin\install-book-kit.bat                                  (already-unzipped)
rem   bin\install-book-kit.bat C:\my-project                   (already-unzipped)
rem   install-book-kit.bat                                      (PowerShell: needs .\ prefix)
rem
rem Resolves its own location even when double-clicked from Explorer.
rem PowerShell: call as .\bin\install-book-kit.bat ... (current-dir
rem commands are disabled by default; "." prefix opts in).
rem
rem Modes:
rem   1. Already-unzipped: if manifest.json exists next to the bin\ folder,
rem      delegate directly to install.py (no ZIP required).
rem   2. ZIP-required: if no manifest.json, look for a ZIP next to the bat
rem      or in cwd, unzip it, then run install.py inside the unpacked kit.
rem
rem What it does (both modes):
rem   1. Locates Python (py launcher first, then python, then python3)
rem   2. Runs install.py --no-doctor against the target
rem   3. Runs scripts/doctor.py for a preflight report
rem   4. Prints the next-step commands to launch OpenCode
rem
rem Stdlib only. No 7-Zip required (uses PowerShell Expand-Archive).
rem On any error, prints a clear message and PAUSEs so the window stays
rem visible long enough to read (fixes the "flash and close" problem
rem when launched by double-click).
rem ============================================================
setlocal EnableDelayedExpansion

rem ---- 0. Resolve our own location so the script is portable ----
set "SELF_DIR=%~dp0"
pushd "%SELF_DIR%" >nul
set "SELF_DIR=%CD%"
popd >nul

rem ---- 0a. Detect already-unzipped mode ----
rem If manifest.json exists at the kit root (parent of bin\), the kit is
rem already extracted; skip the ZIP flow and delegate to install.py directly.
for %%I in ("%SELF_DIR%\..") do set "KIT_ROOT_DIR=%%~fI"
if exist "%KIT_ROOT_DIR%\manifest.json" if exist "%KIT_ROOT_DIR%\install.py" goto :already_unzipped

rem ---- 1. Resolve arguments (ZIP-required mode) -----------------
set "ZIP_PATH=%~1"
if "%ZIP_PATH%"=="" (
    rem Look for book-kit-*.zip next to this script or in the cwd
    set "ZIP_PATH="
    for %%F in ("%SELF_DIR%\book-kit-*.zip") do (
        if not defined ZIP_PATH set "ZIP_PATH=%%~fF"
    )
    for %%F in ("book-kit-*.zip") do (
        if not defined ZIP_PATH set "ZIP_PATH=%%~fF"
    )
)
if "%ZIP_PATH%"=="" (
    echo [FAIL] No ZIP provided and none found next to this script.
    echo        Either pass a ZIP explicitly:
    echo            bin\install-book-kit.bat C:\downloads\book-kit-0.1.0.zip
    echo        or run from inside an already-unzipped kit
    echo            where the bin\ folder sits next to manifest.json.
    goto :error
)

if not "%~2"=="" (
    set "TARGET=%~2"
) else (
    for %%I in ("%ZIP_PATH%") do set "TARGET=%%~dpnI-unpacked"
)

rem ---- 2. Validate ZIP ---------------------------------------
if not exist "%ZIP_PATH%" (
    echo [FAIL] ZIP not found: %ZIP_PATH%
    goto :error
)
rem Extension check: confirm ".zip" appears anywhere in the path. If a
rem user names their ZIP "kit.zip.bak" we still want them through; the
rem unzip step is what actually validates it.
set "ZIP_DOTPATH=%ZIP_PATH:.zip=ZIPOK%"
if /i "%ZIP_DOTPATH%"=="%ZIP_PATH%" (
    echo [FAIL] %ZIP_PATH% does not have a .zip extension
    goto :error
)

rem ---- 3. Locate Python --------------------------------------
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

rem ---- 4. Unzip via PowerShell -------------------------------
if exist "%TARGET%" (
    if /i "%TARGET%"=="%CD%" (
        echo [FAIL] Target equals current dir; refusing to overwrite a live project.
        echo        Pass a target folder as the second arg.
        goto :error
    )
    echo [WARN] Target folder exists: %TARGET%
    set /p "OVERWRITE=Overwrite? (y/N) "
    if /i not "!OVERWRITE!"=="y" (
        echo aborted.
        goto :error
    )
)
echo [step] Unzipping %ZIP_PATH% -^> %TARGET%
rem PowerShell 5.1 doesn't auto-join caret-continued -Command strings,
rem so put the entire script on one line.
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Expand-Archive -LiteralPath '%ZIP_PATH%' -DestinationPath '%TARGET%' -Force } catch { Write-Error $_.Exception.Message; exit 1 }"
if errorlevel 1 (
    echo [FAIL] unzip failed
    goto :error
)

rem ---- 5. Locate kit root inside the unpacked folder --------
rem New layout wraps kit files in a "book-kit/" subdir.
rem Older zips may put install.py at the unzip root.
set "KIT_DIR="
if exist "%TARGET%\book-kit\install.py" set "KIT_DIR=%TARGET%\book-kit"
if "!KIT_DIR!"=="" (
    if exist "%TARGET%\install.py" set "KIT_DIR=%TARGET%"
)
if "!KIT_DIR!"=="" (
    echo [FAIL] install.py not found inside %TARGET%
    echo        ZIP layout unexpected - extract manually and run install.py
    goto :error
)

rem ---- 6. Run installer --------------------------------------
echo [step] Running installer (target: %TARGET%)
"%PY%" "!KIT_DIR!\install.py" --target "%TARGET%" --no-doctor
if errorlevel 1 (
    echo [FAIL] installer exited with errors
    goto :error
)

rem ---- 7. Doctor report -------------------------------------
if exist "!KIT_DIR!\scripts\doctor.py" (
    echo [step] Running doctor preflight
    "%PY%" "!KIT_DIR!\scripts\doctor.py"
)

rem ---- 8. Next steps ----------------------------------------
echo.
echo ============================================================
echo Book Kit installed at: %TARGET%
echo.
echo Next steps:
echo   1. cd "%TARGET%"
echo   2. opencode
echo   3. say: "write a book about ^<topic^>"
echo.
echo To uninstall:
echo   "%PY%" "%TARGET%\install.py" --target "%TARGET%" --uninstall
echo ============================================================
echo.
pause
endlocal
exit /b 0

:already_unzipped
echo [mode] already-unzipped detected at %KIT_ROOT_DIR%; running install.py directly

rem Optional target override (first arg). Defaults to the kit root.
if not "%~1"=="" (
    set "TARGET=%~1"
) else (
    set "TARGET=%KIT_ROOT_DIR%"
)

rem Python locator (same chain as the ZIP flow).
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

rem Run installer.
echo [step] Running installer (target: !TARGET!)
"%PY%" "%KIT_ROOT_DIR%\install.py" --target "!TARGET!" --no-doctor
if errorlevel 1 (
    echo [FAIL] installer exited with errors
    goto :error
)

rem Doctor report.
if exist "%KIT_ROOT_DIR%\scripts\doctor.py" (
    echo [step] Running doctor preflight
    pushd "!TARGET!" >nul
    "%PY%" "%KIT_ROOT_DIR%\scripts\doctor.py"
    popd >nul
)

rem Next steps.
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
echo   "%PY%" "%KIT_ROOT_DIR%\install.py" --target "!TARGET!" --uninstall
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