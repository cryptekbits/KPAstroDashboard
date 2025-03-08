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

:: Detect Python command
set "PYTHON_CMD=python"
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    :: Try python3 command
    python3 --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=python3"
    ) else (
        :: Try py command
        py --version >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set "PYTHON_CMD=py"
        ) else (
            echo Python not found. Please install Python and make sure it's in your PATH.
            echo You can download Python from https://www.python.org/downloads/
            pause
            exit /b 1
        )
    )
)

:: Display detected Python version
for /f "tokens=*" %%V in ('!PYTHON_CMD! --version 2^>^&1') do set PYTHON_VERSION_OUTPUT=%%V
echo Using: !PYTHON_VERSION_OUTPUT!
echo.

:: Check for and uninstall existing flatlib
echo Checking for existing flatlib installation...
!PYTHON_CMD! -m pip show flatlib >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Removing existing flatlib installation...
    !PYTHON_CMD! -m pip uninstall -y flatlib
    echo Flatlib removed successfully.
) else (
    echo Flatlib not found.
)

echo Step 1: Installing pyswisseph...
!PYTHON_CMD! -m pip install --upgrade pip

:: Install pyswisseph directly from PyPI
echo Installing pyswisseph from PyPI...
!PYTHON_CMD! -m pip install pyswisseph>=2.10.3.2
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install pyswisseph from PyPI.
    echo This may be due to missing build tools.
    echo Please ensure you have the Microsoft Visual C++ Build Tools installed.
    echo You can download them from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    pause
    exit /b 1
)
echo Pyswisseph installed successfully.

:: Now install other requirements
echo Step 2: Installing other dependencies...
!PYTHON_CMD! -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies from requirements.txt.
    pause
    exit /b 1
)

echo Step 3: Checking Swiss Ephemeris files...
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