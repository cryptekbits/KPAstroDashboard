@echo off
setlocal enabledelayedexpansion

echo KP Astrology Dashboard - Windows Installation Script
echo ===================================================
echo.

:: Set version and GitHub repo information
set VERSION=##VERSION##
set REPO_OWNER=cryptekbits
set REPO_NAME=KPAstroDashboard
set DOWNLOAD_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/archive/refs/tags/v%VERSION%.zip
set INSTALL_DIR=%USERPROFILE%\KPAstrologyDashboard
set REQUIRED_PYTHON_VERSION=3.13.2

echo Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Download the release zip
echo.
echo Downloading KP Astrology Dashboard v%VERSION%...
echo URL: %DOWNLOAD_URL%

powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP%\KPAstrologyDashboard.zip'"

if %ERRORLEVEL% NEQ 0 (
    echo Failed to download the application package.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

:: Extract the zip file
echo.
echo Extracting files...
powershell -Command "Expand-Archive -Path '%TEMP%\KPAstrologyDashboard.zip' -DestinationPath '%TEMP%\KPAstrologyDashboard-extract' -Force"

if %ERRORLEVEL% NEQ 0 (
    echo Failed to extract the application package.
    pause
    exit /b 1
)

:: Move files from the nested directory (GitHub creates a versioned folder)
echo.
echo Moving files to installation directory...
:: Find the extracted folder (it will be KPAstroDashboard-VERSION)
for /d %%G in ("%TEMP%\KPAstrologyDashboard-extract\*") do (
    xcopy "%%G\*" "%INSTALL_DIR%" /E /I /Y
)

:: Delete the temporary files
del "%TEMP%\KPAstrologyDashboard.zip"
rmdir /S /Q "%TEMP%\KPAstrologyDashboard-extract"

:: Change to the installation directory
cd /d "%INSTALL_DIR%"

:: Check if Python is installed and meets the required version
echo.
echo Checking Python installation...
set PYTHON_INSTALLED=false
set PYTHON_NEEDS_UPGRADE=false

python --version > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_INSTALLED=true
    :: Get Python version - handle both Python 2.x (stderr) and Python 3.x (stdout) output formats
    for /f "tokens=*" %%V in ('python --version 2^>^&1') do set PYTHON_VERSION_OUTPUT=%%V
    echo Found: %PYTHON_VERSION_OUTPUT%
    
    :: Extract version number from output (format: "Python X.Y.Z")
    for /f "tokens=2" %%V in ("!PYTHON_VERSION_OUTPUT!") do set CURRENT_PYTHON_VERSION=%%V
    
    :: Check if CURRENT_PYTHON_VERSION is empty
    if "!CURRENT_PYTHON_VERSION!"=="" (
        echo Error: Failed to detect Python version.
        for /f "tokens=*" %%V in ('python --version 2^>^&1') do echo Python output: %%V
        echo Assuming Python version does not meet requirements.
        set PYTHON_NEEDS_UPGRADE=true
    ) else (
        :: Compare versions using PowerShell
        powershell -Command "$current = [version]'!CURRENT_PYTHON_VERSION!'; $required = [version]'%REQUIRED_PYTHON_VERSION%'; if ($current -ge $required) { exit 0 } else { exit 1 }"
        
        if %ERRORLEVEL% EQU 0 (
            echo Python version !CURRENT_PYTHON_VERSION! meets the requirement ^(^>= %REQUIRED_PYTHON_VERSION%^)
        ) else (
            :: If PowerShell comparison fails, try a simple batch comparison as fallback
            echo PowerShell version comparison failed, trying fallback method...
            
            :: Extract major, minor, patch versions
            for /f "tokens=1,2,3 delims=." %%a in ("!CURRENT_PYTHON_VERSION!") do (
                set CURRENT_MAJOR=%%a
                set CURRENT_MINOR=%%b
                set CURRENT_PATCH=%%c
            )
            
            for /f "tokens=1,2,3 delims=." %%a in ("%REQUIRED_PYTHON_VERSION%") do (
                set REQUIRED_MAJOR=%%a
                set REQUIRED_MINOR=%%b
                set REQUIRED_PATCH=%%c
            )
            
            :: Compare major version
            if !CURRENT_MAJOR! GTR !REQUIRED_MAJOR! (
                echo Python version !CURRENT_PYTHON_VERSION! meets the requirement ^(^>= %REQUIRED_PYTHON_VERSION%^)
            ) else if !CURRENT_MAJOR! EQU !REQUIRED_MAJOR! (
                :: Compare minor version
                if !CURRENT_MINOR! GTR !REQUIRED_MINOR! (
                    echo Python version !CURRENT_PYTHON_VERSION! meets the requirement ^(^>= %REQUIRED_PYTHON_VERSION%^)
                ) else if !CURRENT_MINOR! EQU !REQUIRED_MINOR! (
                    :: Compare patch version
                    if !CURRENT_PATCH! GEQ !REQUIRED_PATCH! (
                        echo Python version !CURRENT_PYTHON_VERSION! meets the requirement ^(^>= %REQUIRED_PYTHON_VERSION%^)
                    ) else (
                        echo Python version !CURRENT_PYTHON_VERSION! is older than required version %REQUIRED_PYTHON_VERSION%
                        set PYTHON_NEEDS_UPGRADE=true
                    )
                ) else (
                    echo Python version !CURRENT_PYTHON_VERSION! is older than required version %REQUIRED_PYTHON_VERSION%
                    set PYTHON_NEEDS_UPGRADE=true
                )
            ) else (
                echo Python version !CURRENT_PYTHON_VERSION! is older than required version %REQUIRED_PYTHON_VERSION%
                set PYTHON_NEEDS_UPGRADE=true
            )
        )
    )
)

:: Install or upgrade Python if needed
if "!PYTHON_INSTALLED!"=="false" (
    echo Python not found. Installing Python %REQUIRED_PYTHON_VERSION%...
    set INSTALL_PYTHON=true
) else if "!PYTHON_NEEDS_UPGRADE!"=="true" (
    echo Upgrading Python to version %REQUIRED_PYTHON_VERSION%...
    set INSTALL_PYTHON=true
) else (
    set INSTALL_PYTHON=false
)

if "!INSTALL_PYTHON!"=="true" (
    :: Create a temporary directory for the installer
    mkdir %TEMP%\kp_dashboard_setup > nul 2>&1
    cd %TEMP%\kp_dashboard_setup
    
    :: Download Python installer
    echo Downloading Python installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/%REQUIRED_PYTHON_VERSION%/python-%REQUIRED_PYTHON_VERSION%-amd64.exe' -OutFile 'python-installer.exe'"
    
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to download Python installer.
        echo Please install Python %REQUIRED_PYTHON_VERSION% or later manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    :: Install Python with pip and add to PATH
    echo Installing Python...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Clean up
    del python-installer.exe
    cd /d "%INSTALL_DIR%"
    
    :: Verify installation
    echo Verifying Python installation...
    python --version > nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install Python automatically.
        echo Please install Python %REQUIRED_PYTHON_VERSION% or later manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do set INSTALLED_PYTHON_VERSION=%%V
    echo Python %INSTALLED_PYTHON_VERSION% installed successfully.
) else (
    echo Python %CURRENT_PYTHON_VERSION% is already installed and meets requirements.
)

:: Install required packages
echo.
echo Installing required packages...
python -m pip install --upgrade pip

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

:: Install pyswisseph from wheels
echo Installing pyswisseph from wheels directory...
:: Detect Python version
for /f "tokens=2" %%i in ('python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"') do (
    set "PYTHON_VERSION=%%i"
)
echo Detected Python version: !PYTHON_VERSION!

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

:: Now install requirements
echo Installing required packages from requirements.txt...
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

:: Setup Swiss Ephemeris files
echo.
echo Setting up Swiss Ephemeris files...
set SWEFILES_DIR=%INSTALL_DIR%\flatlib\resources\swefiles
set SYSTEM_SWEFILES_DIR=C:\sweph\ephe

:: Check if directory exists
if not exist "%SWEFILES_DIR%" (
    echo Error: Swiss Ephemeris files directory not found at %SWEFILES_DIR%
    echo Please ensure the application is installed correctly.
    goto skip_ephemeris
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
    goto skip_ephemeris
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

:skip_ephemeris

:: Create desktop shortcut
echo.
echo Creating desktop shortcut...
set DESKTOP_DIR=%USERPROFILE%\Desktop
set APP_DIR=%INSTALL_DIR%
set SHORTCUT=%DESKTOP_DIR%\KPAstrologyDashboard.lnk
set ICON_PATH=%APP_DIR%\resources\favicon.ico

:: Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '%APP_DIR%\main.py'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.IconLocation = '%ICON_PATH%'; $Shortcut.Save()"

echo.
echo Installation completed successfully!
echo KP Astrology Dashboard has been installed to: %INSTALL_DIR%
echo You can now run KP Astrology Dashboard from your desktop.
echo.

pause 