@echo off
setlocal enabledelayedexpansion

echo KP Astrology Dashboard - Dependency Installation Script
echo ======================================================
echo.
echo This script will install the pyswisseph library and download required
echo Swiss Ephemeris files for the KP Astrology Dashboard.
echo.

:: Determine the application directory (where this script is located)
set INSTALL_DIR=%~dp0
set INSTALL_DIR=%INSTALL_DIR:~0,-1%

echo Installation directory: %INSTALL_DIR%
echo.

:: Check for and uninstall existing flatlib and pyswisseph
echo Checking for existing flatlib and pyswisseph installations...
python -m pip show flatlib >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Removing existing flatlib installation...
    python -m pip uninstall -y flatlib
    echo Flatlib removed successfully.
) else (
    echo Flatlib not found.
)

python -m pip show pyswisseph >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Removing existing pyswisseph installation...
    python -m pip uninstall -y pyswisseph
    echo Pyswisseph removed successfully.
) else (
    echo Pyswisseph not found.
)

echo Step 1: Installing pyswisseph...
python -m pip install --upgrade pip

:: Try to use local wheels first
echo Checking for local pre-built pyswisseph wheel...
set "PYTHON_VERSION="
for /f "tokens=2" %%i in ('python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"') do (
    set "PYTHON_VERSION=%%i"
)
echo Detected Python version: %PYTHON_VERSION%

:: Map Python version to wheel version
set "CP_VER="
if "!PYTHON_VERSION!"=="3.9" set "CP_VER=cp39-cp39"
if "!PYTHON_VERSION!"=="3.10" set "CP_VER=cp310-cp310"
if "!PYTHON_VERSION!"=="3.11" set "CP_VER=cp311-cp311"
if "!PYTHON_VERSION!"=="3.12" set "CP_VER=cp312-cp312"
if "!PYTHON_VERSION!"=="3.13" set "CP_VER=cp313-cp313"

:: Try to find architecture-appropriate wheel
set "ARCH=win_amd64"
if defined CP_VER (
    set "WHEEL_PATH=%INSTALL_DIR%\wheels\!ARCH!\pyswisseph-2.10.3.2-!CP_VER!-!ARCH!.whl"
    if exist "!WHEEL_PATH!" (
        echo Found local wheel: !WHEEL_PATH!
        python -m pip install "!WHEEL_PATH!" --no-deps
        if %ERRORLEVEL% EQU 0 (
            echo Successfully installed pyswisseph from local wheel.
            goto setup_ephemeris
        ) else (
            echo Failed to install from local wheel.
            echo Please check that the wheel file is not corrupted.
            pause
            exit /b 1
        )
    ) else (
        echo No matching local wheel found for Python !PYTHON_VERSION! on !ARCH!
        echo Expected wheel path: !WHEEL_PATH!
        echo Please ensure the appropriate wheel is available for your system.
        pause
        exit /b 1
    )
) else (
    echo Unsupported Python version: %PYTHON_VERSION%
    echo Please install a supported Python version (3.9-3.13).
    pause
    exit /b 1
)

:setup_ephemeris
echo.
echo Step 2: Setting up Swiss Ephemeris files...
set SWEFILES_DIR=%INSTALL_DIR%\flatlib\resources\swefiles
set SYSTEM_SWEFILES_DIR=C:\sweph\ephe

:: Check if directory exists, create if not
if not exist "%SWEFILES_DIR%" (
    echo Error: Swiss Ephemeris files directory not found at %SWEFILES_DIR%
    echo Please ensure the application is installed correctly.
    goto end_ephemeris
)

:: Required files
set REQUIRED_FILES=seas_18.se1 sepl_18.se1 semo_18.se1 fixstars.cat

:: Check for required files
echo Checking for required ephemeris files...
set "MISSING_FILES=false"
for %%F in (%REQUIRED_FILES%) do (
    if not exist "%SWEFILES_DIR%\%%F" (
        echo Missing: %%F
        set "MISSING_FILES=true"
    ) else (
        echo Found: %%F
    )
)

if "!MISSING_FILES!"=="true" (
    echo.
    echo Some required Swiss Ephemeris files are missing from the source directory.
    echo Please ensure the application package is complete.
    goto end_ephemeris
) else (
    echo All required ephemeris files are present in the application directory.
)

:: Check if system-wide Swiss Ephemeris directory exists
echo.
echo Checking for system-wide Swiss Ephemeris directory...
if not exist "%SYSTEM_SWEFILES_DIR%" (
    echo System-wide Swiss Ephemeris directory not found.
    echo Would you like to create it and copy the ephemeris files? (Y/N)
    echo This will require administrator privileges.
    set /p SYSTEM_CHOICE=Your choice: 
    
    if /i "!SYSTEM_CHOICE!"=="Y" (
        :: Create a temporary admin script
        echo @echo off > "%TEMP%\sweadmin.bat"
        echo echo Creating system-wide Swiss Ephemeris directory... >> "%TEMP%\sweadmin.bat"
        echo if not exist "%SYSTEM_SWEFILES_DIR%" mkdir "%SYSTEM_SWEFILES_DIR%" >> "%TEMP%\sweadmin.bat"
        echo echo Copying ephemeris files... >> "%TEMP%\sweadmin.bat"
        
        for %%F in (%REQUIRED_FILES%) do (
            echo if exist "%SWEFILES_DIR%\%%F" copy /Y "%SWEFILES_DIR%\%%F" "%SYSTEM_SWEFILES_DIR%\%%F" >> "%TEMP%\sweadmin.bat"
        )
        
        echo echo. >> "%TEMP%\sweadmin.bat"
        echo echo System-wide Swiss Ephemeris files setup complete. >> "%TEMP%\sweadmin.bat"
        
        :: Run the script with admin privileges
        echo Requesting administrator privileges...
        powershell -Command "Start-Process -FilePath '%TEMP%\sweadmin.bat' -Verb RunAs -Wait"
        
        :: Clean up
        del "%TEMP%\sweadmin.bat"
    ) else (
        echo Skipping system-wide Swiss Ephemeris setup.
    )
) else (
    echo System-wide Swiss Ephemeris directory already exists.
    echo Would you like to update the ephemeris files? (Y/N)
    set /p UPDATE_CHOICE=Your choice: 
    
    if /i "!UPDATE_CHOICE!"=="Y" (
        :: Create a temporary admin script
        echo @echo off > "%TEMP%\sweadmin.bat"
        echo echo Updating system-wide Swiss Ephemeris files... >> "%TEMP%\sweadmin.bat"
        
        for %%F in (%REQUIRED_FILES%) do (
            echo if exist "%SWEFILES_DIR%\%%F" copy /Y "%SWEFILES_DIR%\%%F" "%SYSTEM_SWEFILES_DIR%\%%F" >> "%TEMP%\sweadmin.bat"
        )
        
        echo echo. >> "%TEMP%\sweadmin.bat"
        echo echo System-wide Swiss Ephemeris files update complete. >> "%TEMP%\sweadmin.bat"
        
        :: Run the script with admin privileges
        echo Requesting administrator privileges...
        powershell -Command "Start-Process -FilePath '%TEMP%\sweadmin.bat' -Verb RunAs -Wait"
        
        :: Clean up
        del "%TEMP%\sweadmin.bat"
    ) else (
        echo Skipping system-wide Swiss Ephemeris update.
    )
)

:end_ephemeris
echo.
echo =====================================================
echo Dependency installation process completed.
echo.
echo If you still experience issues, please visit:
echo https://github.com/cryptekbits/KPAstroDashboard/issues
echo =====================================================
echo.

pause 