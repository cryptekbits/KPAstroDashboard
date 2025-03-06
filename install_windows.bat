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

:: First try to install pyswisseph from pre-built wheels
echo Installing pyswisseph from pre-built wheels...
python -m pip install --only-binary=:all: pyswisseph==2.10.3.post2 --no-deps

if %ERRORLEVEL% NEQ 0 (
    echo Pre-built wheel for pyswisseph not available for your system.
    echo Attempting to use alternative installation methods...
    
    :: Try pip wheel from unofficial wheel repository (many libraries have pre-built wheels here)
    echo Trying unofficial wheel repository...
    python -m pip install pyswisseph==2.10.3.post2 --no-deps --index-url https://www.lfd.uci.edu/~gohlke/pythonlibs/ || (
        echo Unofficial wheel repository failed.
        
        :: Try conda-forge if conda is available
        where conda >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            echo Trying conda-forge...
            conda install -y -c conda-forge pyswisseph || (
                echo Conda-forge installation failed.
                
                :: Show failure message with instructions
                echo.
                echo ===================================================================
                echo WARNING: Could not install pyswisseph automatically.
                echo.
                echo The application may not work correctly without this package.
                echo.
                echo To install manually, you will need to:
                echo 1. Install Visual Studio Build Tools 2022 with C++ development tools
                echo 2. Run: pip install pyswisseph==2.10.3.post2
                echo ===================================================================
                echo.
            )
        ) else (
            :: Show failure message with instructions
            echo.
            echo ===================================================================
            echo WARNING: Could not install pyswisseph automatically.
            echo.
            echo The application may not work correctly without this package.
            echo.
            echo To install manually, you will need to:
            echo 1. Install Visual Studio Build Tools 2022 with C++ development tools
            echo 2. Run: pip install pyswisseph==2.10.3.post2
            echo ===================================================================
            echo.
        )
    )
) else (
    echo Successfully installed pyswisseph from pre-built wheel.
)

:: Install the rest of the packages
echo Installing remaining packages...
python -m pip install -r requirements.txt --no-deps  
python -m pip install -e .

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

:: Now ensure Swiss Ephemeris files are downloaded and in the right place
echo.
echo Setting up Swiss Ephemeris files...
set SWEFILES_DIR=%INSTALL_DIR%\flatlib\resources\swefiles

:: Check if directory exists, create if not
if not exist "%SWEFILES_DIR%" mkdir "%SWEFILES_DIR%"

:: Check for required files
set "MISSING_FILES=false"
for %%F in (seas_18.se1 sepl_18.se1 semo_18.se1 fixstars.cat) do (
    if not exist "%SWEFILES_DIR%\%%F" (
        set "MISSING_FILES=true"
    )
)

:: Download files if missing
if "%MISSING_FILES%"=="true" (
    echo Swiss Ephemeris files are missing, downloading them...
    for %%F in (seas_18.se1 sepl_18.se1 semo_18.se1 fixstars.cat) do (
        if not exist "%SWEFILES_DIR%\%%F" (
            echo Downloading %%F...
            powershell -Command "Invoke-WebRequest -Uri 'https://github.com/aloistr/swisseph/raw/master/ephe/%%F' -OutFile '%SWEFILES_DIR%\%%F'"
            
            if %ERRORLEVEL% NEQ 0 (
                echo Failed to download %%F, will try alternative source...
                powershell -Command "Invoke-WebRequest -Uri 'https://github.com/flatangle/flatlib/raw/master/flatlib/resources/swefiles/%%F' -OutFile '%SWEFILES_DIR%\%%F'"
            )
        )
    )
) else (
    echo Swiss Ephemeris files are already present.
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