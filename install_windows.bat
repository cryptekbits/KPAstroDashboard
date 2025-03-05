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

:: Check if Python 3.9+ is installed
echo.
echo Checking if Python is installed...
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Installing Python 3.9...
    
    :: Create a temporary directory for the installer
    mkdir %TEMP%\kp_dashboard_setup > nul 2>&1
    cd %TEMP%\kp_dashboard_setup
    
    :: Download Python installer
    echo Downloading Python installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe' -OutFile 'python-installer.exe'"
    
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to download Python installer.
        echo Please install Python 3.9 or later manually from https://www.python.org/downloads/
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
        echo Please install Python 3.9 or later manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    echo Python installed successfully.
) else (
    echo Python is already installed.
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

:: Create desktop shortcut with icon
echo.
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_FILE=%DESKTOP%\KPAstrologyDashboard.lnk
set ICON_PATH=%INSTALL_DIR%\resources\favicon.ico

:: Create VBScript to make the shortcut with icon
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\createShortcut.vbs"
echo sLinkFile = "%SHORTCUT_FILE%" >> "%TEMP%\createShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\createShortcut.vbs"
echo oLink.TargetPath = "cmd.exe" >> "%TEMP%\createShortcut.vbs"
echo oLink.Arguments = "/c cd /d ""%INSTALL_DIR%"" && python main.py" >> "%TEMP%\createShortcut.vbs"
echo oLink.Description = "KP Astrology Dashboard" >> "%TEMP%\createShortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%TEMP%\createShortcut.vbs"
echo oLink.IconLocation = "%ICON_PATH%" >> "%TEMP%\createShortcut.vbs"
echo oLink.Save >> "%TEMP%\createShortcut.vbs"

:: Run the VBScript to create the shortcut
cscript //nologo "%TEMP%\createShortcut.vbs"
del "%TEMP%\createShortcut.vbs"

echo.
echo Installation completed successfully!
echo KP Astrology Dashboard has been installed to: %INSTALL_DIR%
echo You can now run KP Astrology Dashboard from your desktop.
echo.
pause 