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
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do set CURRENT_PYTHON_VERSION=%%V
    echo Found Python %CURRENT_PYTHON_VERSION%
    
    :: Compare versions using PowerShell
    powershell -Command "$current = [version]'%CURRENT_PYTHON_VERSION%'; $required = [version]'%REQUIRED_PYTHON_VERSION%'; if ($current -ge $required) { exit 0 } else { exit 1 }"
    
    if %ERRORLEVEL% EQU 0 (
        echo Python version %CURRENT_PYTHON_VERSION% meets the requirement ^(^>= %REQUIRED_PYTHON_VERSION%^)
    ) else (
        echo Python version %CURRENT_PYTHON_VERSION% is older than required version %REQUIRED_PYTHON_VERSION%
        set PYTHON_NEEDS_UPGRADE=true
    )
)

:: Install or upgrade Python if needed
if "%PYTHON_INSTALLED%"=="false" (
    echo Python not found. Installing Python %REQUIRED_PYTHON_VERSION%...
    set INSTALL_PYTHON=true
) else if "%PYTHON_NEEDS_UPGRADE%"=="true" (
    echo Upgrading Python to version %REQUIRED_PYTHON_VERSION%...
    set INSTALL_PYTHON=true
) else (
    set INSTALL_PYTHON=false
)

if "%INSTALL_PYTHON%"=="true" (
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
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

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