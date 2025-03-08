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
set REQUIRED_PYTHON_VERSION=3.13.2

:: Detect Desktop and Downloads directories (handle OneDrive case)
echo Detecting user directories...

:: Primary Desktop - try standard location first
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
if not exist "%DESKTOP_DIR%" (
    echo WARNING: Standard Desktop not found at %DESKTOP_DIR%
    
    :: Try alternate locations
    if exist "%USERPROFILE%\OneDrive\Desktop" (
        set "DESKTOP_DIR=%USERPROFILE%\OneDrive\Desktop"
        echo Using OneDrive Desktop as primary: %DESKTOP_DIR%
    ) else if exist "%USERPROFILE%\Documents\Desktop" (
        set "DESKTOP_DIR=%USERPROFILE%\Documents\Desktop"
        echo Using Documents\Desktop as primary: %DESKTOP_DIR%
    ) else (
        echo WARNING: Could not find a valid Desktop directory!
        echo Will default to %USERPROFILE%\Desktop but shortcuts may fail.
        set "DESKTOP_DIR=%USERPROFILE%\Desktop"
    )
) else (
    echo Found standard Desktop at: %DESKTOP_DIR%
)

:: Primary Downloads - try standard location first
set "DOWNLOADS_DIR=%USERPROFILE%\Downloads"
if not exist "%DOWNLOADS_DIR%" (
    echo WARNING: Standard Downloads not found at %DOWNLOADS_DIR%
    
    :: Try alternate locations
    if exist "%USERPROFILE%\OneDrive\Downloads" (
        set "DOWNLOADS_DIR=%USERPROFILE%\OneDrive\Downloads"
        echo Using OneDrive Downloads: %DOWNLOADS_DIR%
    ) else (
        echo WARNING: Could not find a valid Downloads directory!
        echo Will default to %USERPROFILE%\Downloads, downloads may fail.
    )
) else (
    echo Found standard Downloads at: %DOWNLOADS_DIR%
)

:: Check for OneDrive Desktop as secondary location (if primary is not OneDrive)
set "HAS_ONEDRIVE_DESKTOP=false"
set "ONEDRIVE_DESKTOP=%USERPROFILE%\OneDrive\Desktop"
if "%DESKTOP_DIR%" NEQ "%ONEDRIVE_DESKTOP%" (
    if exist "%ONEDRIVE_DESKTOP%" (
        echo Found secondary OneDrive Desktop at: %ONEDRIVE_DESKTOP%
        set "HAS_ONEDRIVE_DESKTOP=true"
    )
)

:: Check for other potential Desktop locations as secondary (if not already primary)
set "OTHER_DESKTOP="
if exist "%USERPROFILE%\Documents\Desktop" (
    if "%DESKTOP_DIR%" NEQ "%USERPROFILE%\Documents\Desktop" (
        set "OTHER_DESKTOP=%USERPROFILE%\Documents\Desktop"
        echo Found additional Desktop at: !OTHER_DESKTOP!
    )
)

:: Set installation directory on primary Desktop
set INSTALL_DIR=%DESKTOP_DIR%\KPAstrologyDashboard

echo Installation directory will be: %INSTALL_DIR%
echo Download directory will be: %DOWNLOADS_DIR%
echo.

:: Create installation directory if it doesn't exist
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Check if zip file already exists from a previous download
set LOCAL_ZIP_FILE=%DOWNLOADS_DIR%\KPAstrologyDashboard-%VERSION%.zip
if exist "%LOCAL_ZIP_FILE%" (
    echo.
    echo Previously downloaded KP Astrology Dashboard v%VERSION% found.
    echo Location: %LOCAL_ZIP_FILE%
    echo Skipping download phase.
) else (
    :: Download the release zip with progress indicator
    echo.
    echo Downloading KP Astrology Dashboard v%VERSION%...
    echo URL: %DOWNLOAD_URL%
    
    :: Fixed PowerShell script for download with progress
    powershell -Command "& { $ProgressPreference = 'Continue'; $wc = New-Object System.Net.WebClient; $wc.Headers.Add('User-Agent', 'KPAstroDashboard Installer'); $dest = '%LOCAL_ZIP_FILE%'; $start = Get-Date; $totalSize = 0; $wc.DownloadFile('%DOWNLOAD_URL%', $dest); if (Test-Path $dest) { $fileInfo = Get-Item $dest; Write-Host ('Downloaded {0:N2} MB in {1:N2} seconds.' -f ($fileInfo.Length/1MB), ((Get-Date) - $start).TotalSeconds) -ForegroundColor Green; } else { Write-Host 'Download failed!' -ForegroundColor Red; exit 1 } }"

    if %ERRORLEVEL% NEQ 0 (
        echo Failed to download the application package.
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
    
    echo Download saved to: %LOCAL_ZIP_FILE%
)

:: Verify the downloaded file exists and has content
if not exist "%LOCAL_ZIP_FILE%" (
    echo ERROR: Download file not found: %LOCAL_ZIP_FILE%
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

:: Get file size to verify download
for %%I in ("%LOCAL_ZIP_FILE%") do set FILE_SIZE=%%~zI
if %FILE_SIZE% EQU 0 (
    echo ERROR: Downloaded file is empty. Download may have failed.
    echo Please delete %LOCAL_ZIP_FILE% and run this installer again.
    pause
    exit /b 1
)

:: Check if files were already extracted to the destination
if exist "%INSTALL_DIR%\main.py" (
    echo.
    echo Application files already exist in destination folder.
    echo Would you like to re-extract the files? (Y/N)
    set /p EXTRACT_CHOICE=Your choice: 
    
    if /i not "!EXTRACT_CHOICE!"=="Y" goto skip_extraction
)

:: Extract the zip file
echo.
echo Extracting files...
:: Check if temp extraction dir already exists and contains files
set "TEMP_EXTRACT_DIR=%TEMP%\KPAstrologyDashboard-extract"
if exist "%TEMP_EXTRACT_DIR%" (
    echo Cleaning previous temporary extraction directory...
    rmdir /S /Q "%TEMP_EXTRACT_DIR%"
)

:: Extract using PowerShell with simplified error handling
powershell -Command "& { $ErrorActionPreference = 'Stop'; try { Write-Host 'Extracting archive...' -ForegroundColor Cyan; Expand-Archive -Path '%LOCAL_ZIP_FILE%' -DestinationPath '%TEMP_EXTRACT_DIR%' -Force; Write-Host 'Extraction successful.' -ForegroundColor Green; } catch { Write-Host ('Extraction error: ' + $_.Exception.Message) -ForegroundColor Red; exit 1; } }"

if %ERRORLEVEL% NEQ 0 (
    echo Failed to extract the application package.
    pause
    exit /b 1
)

:: Move files from the nested directory (GitHub creates a versioned folder)
echo.
echo Moving files to installation directory...
:: Find the extracted folder (it will be KPAstroDashboard-VERSION)
for /d %%G in ("%TEMP_EXTRACT_DIR%\*") do (
    echo Copying from: %%G
    xcopy "%%G\*" "%INSTALL_DIR%" /E /I /Y
)

:: Check if requirements.txt exists, create it if not
if not exist "%INSTALL_DIR%\requirements.txt" (
    echo Creating requirements.txt file...
    (
        echo streamlit==1.38.0
        echo pandas==2.1.4
        echo numpy==1.26.4
        echo python-dateutil==2.8.2
        echo matplotlib==3.8.2
        echo pytz==2024.1
        echo pyephem==4.1.5
        echo scipy==1.12.0
        echo pyswisseph==2.10.3.2
    ) > "%INSTALL_DIR%\requirements.txt"
    echo Created requirements.txt file.
)

:: Clean up temp extraction directory
rmdir /S /Q "%TEMP_EXTRACT_DIR%"

:skip_extraction

:: Change to the installation directory
cd /d "%INSTALL_DIR%"

:: Check if Python is installed and meets the required version
echo.
echo Checking Python installation...
set PYTHON_INSTALLED=false
set PYTHON_NEEDS_UPGRADE=false

:: Try different Python commands to detect installation
:: First try python command
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_INSTALLED=true
    set PYTHON_CMD=python
) else (
    :: Try python3 command
    python3 --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_INSTALLED=true
        set PYTHON_CMD=python3
    ) else (
        :: Try py command
        py --version >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set PYTHON_INSTALLED=true
            set PYTHON_CMD=py
        )
    )
)

if "!PYTHON_INSTALLED!"=="true" (
    :: Get Python version - handle both Python 2.x (stderr) and Python 3.x (stdout) output formats
    for /f "tokens=*" %%V in ('!PYTHON_CMD! --version 2^>^&1') do set PYTHON_VERSION_OUTPUT=%%V
    echo Found: !PYTHON_VERSION_OUTPUT!
    
    :: Extract version number from output (format: "Python X.Y.Z")
    for /f "tokens=2" %%V in ("!PYTHON_VERSION_OUTPUT!") do set CURRENT_PYTHON_VERSION=%%V
    
    :: Check if CURRENT_PYTHON_VERSION is empty
    if "!CURRENT_PYTHON_VERSION!"=="" (
        echo Error: Failed to detect Python version.
        for /f "tokens=*" %%V in ('!PYTHON_CMD! --version 2^>^&1') do echo Python output: %%V
        echo Assuming Python version does not meet requirements.
        set PYTHON_NEEDS_UPGRADE=true
    ) else (
        :: Compare versions using PowerShell
        powershell -Command "$current = [version]'!CURRENT_PYTHON_VERSION!'; $required = [version]'%REQUIRED_PYTHON_VERSION%'; if ($current -ge $required) { exit 0 } else { exit 1 }"
        
        if %ERRORLEVEL% EQU 0 (
            echo Python version !CURRENT_PYTHON_VERSION! meets the requirement ^(^>= %REQUIRED_PYTHON_VERSION%^)
        ) else (
            echo Python version !CURRENT_PYTHON_VERSION! is older than required version %REQUIRED_PYTHON_VERSION%
            set PYTHON_NEEDS_UPGRADE=true
        )
    )
)

:: Install or upgrade Python if needed
if "!PYTHON_INSTALLED!"=="false" (
    echo Python not found. You need to install Python %REQUIRED_PYTHON_VERSION%...
    set INSTALL_PYTHON=true
) else if "!PYTHON_NEEDS_UPGRADE!"=="true" (
    echo You need to upgrade Python to version %REQUIRED_PYTHON_VERSION%...
    set INSTALL_PYTHON=true
) else (
    set INSTALL_PYTHON=false
)

if "!INSTALL_PYTHON!"=="true" (
    :: Download Python installer to user's Downloads folder
    set PYTHON_INSTALLER_PATH=%DOWNLOADS_DIR%\python-%REQUIRED_PYTHON_VERSION%-installer.exe
    
    :: Check if installer already exists
    if exist "!PYTHON_INSTALLER_PATH!" (
        echo Python installer already exists at: !PYTHON_INSTALLER_PATH!
    ) else (
        echo Downloading Python installer to your Downloads folder...
        
        :: Determine architecture - check for ARM64
        set "ARCH=amd64"
        wmic OS get OSArchitecture | findstr /i "ARM64" > nul
        if %ERRORLEVEL% EQU 0 (
            set "ARCH=arm64"
            echo Detected ARM64 architecture
        )
        
        :: Download installer with progress
        set PYTHON_DOWNLOAD_URL=https://www.python.org/ftp/python/%REQUIRED_PYTHON_VERSION%/python-%REQUIRED_PYTHON_VERSION%-%ARCH%.exe
        echo Download URL: !PYTHON_DOWNLOAD_URL!
        
        powershell -Command "& { $ProgressPreference = 'Continue'; $wc = New-Object System.Net.WebClient; $dest = '!PYTHON_INSTALLER_PATH!'; $start = Get-Date; $wc.DownloadFile('!PYTHON_DOWNLOAD_URL!', $dest); if (Test-Path $dest) { $fileInfo = Get-Item $dest; Write-Host ('Downloaded {0:N2} MB in {1:N2} seconds.' -f ($fileInfo.Length/1MB), ((Get-Date) - $start).TotalSeconds) -ForegroundColor Green; } else { Write-Host 'Download failed!' -ForegroundColor Red; exit 1 } }"
    )
    
    :: Open the folder containing the Python installer
    echo.
    echo Please install Python %REQUIRED_PYTHON_VERSION% by running the installer.
    echo Opening the download location for you...
    explorer.exe /select,"%PYTHON_INSTALLER_PATH%"
    echo.
    echo IMPORTANT: During installation, make sure to check:
    echo - "Add Python to PATH"
    echo - "Install for all users" (recommended)
    echo.
    echo After installing Python, please come back to this window and press any key to continue.
    pause
    
    :: Verify installation
    echo Verifying Python installation...
    python --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
    ) else (
        python3 --version >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set PYTHON_CMD=python3
        ) else (
            py --version >nul 2>&1
            if %ERRORLEVEL% EQU 0 (
                set PYTHON_CMD=py
            ) else (
                echo Failed to find Python after installation.
                echo Please make sure Python was installed correctly and "Add Python to PATH" was selected.
                echo You may need to restart your computer for PATH changes to take effect.
                echo.
                echo Do you want to continue anyway? (Y/N)
                set /p CONTINUE_CHOICE=Your choice: 
                if /i not "!CONTINUE_CHOICE!"=="Y" (
                    exit /b 1
                )
                set PYTHON_CMD=python
            )
        )
    )
    
    for /f "tokens=2" %%V in ('!PYTHON_CMD! --version 2^>^&1') do set INSTALLED_PYTHON_VERSION=%%V
    echo Python !INSTALLED_PYTHON_VERSION! detected.
) else (
    echo Python %CURRENT_PYTHON_VERSION% is already installed and meets requirements.
)

:: Install required packages
echo.
echo Installing required packages...
%PYTHON_CMD% -m pip install --upgrade pip

:: Check for and uninstall existing flatlib
echo Checking for existing flatlib installation...
%PYTHON_CMD% -m pip show flatlib 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Removing existing flatlib installation...
    %PYTHON_CMD% -m pip uninstall -y flatlib
    echo Flatlib removed successfully.
) else (
    echo Flatlib not found.
)

:: Install pyswisseph directly from PyPI
echo Installing pyswisseph from PyPI...
%PYTHON_CMD% -m pip install pyswisseph>=2.10.3.2
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install pyswisseph from PyPI.
    echo This may be due to missing build tools.
    echo Please ensure you have the Microsoft Visual C++ Build Tools installed.
    echo You can download them from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    pause
    exit /b 1
)
echo Pyswisseph installed successfully.

:: Install other dependencies
echo Installing other dependencies...

:: Install required packages
echo.
echo Installing required packages...
%PYTHON_CMD% -m pip install -r requirements.txt

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

:: Create desktop shortcuts on all detected Desktop locations
echo.
echo Creating desktop shortcuts...
set APP_DIR=%INSTALL_DIR%
set ICON_PATH=%APP_DIR%\resources\favicon.ico

:: Check if resources and icon exist
if not exist "%APP_DIR%\resources" (
    echo WARNING: Resources folder not found at %APP_DIR%\resources
    mkdir "%APP_DIR%\resources" 2>nul
    echo Created resources directory.
)

if not exist "%ICON_PATH%" (
    echo WARNING: Favicon not found at %ICON_PATH%
    echo Using default Windows icon instead.
    set "ICON_PATH=%SystemRoot%\System32\shell32.dll,0"
)

:: Create shortcut on primary Desktop
set SHORTCUT=%DESKTOP_DIR%\KPAstrologyDashboard.lnk
if exist "%DESKTOP_DIR%" (
    echo Creating shortcut at: %SHORTCUT%
    powershell -Command "& { try { $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '!PYTHON_CMD!'; $Shortcut.Arguments = '%APP_DIR%\main.py'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.IconLocation = '%ICON_PATH%'; $Shortcut.Save(); Write-Host 'Primary desktop shortcut created successfully.' -ForegroundColor Green; } catch { Write-Host ('Error creating shortcut: ' + $_.Exception.Message) -ForegroundColor Red; } }"
) else (
    echo WARNING: Primary Desktop not found at %DESKTOP_DIR%. Skipping shortcut creation.
)

:: Create shortcut on OneDrive Desktop if it exists
if "!HAS_ONEDRIVE_DESKTOP!"=="true" (
    if exist "%ONEDRIVE_DESKTOP%" (
        set ONEDRIVE_SHORTCUT=%ONEDRIVE_DESKTOP%\KPAstrologyDashboard.lnk
        echo Creating shortcut at: !ONEDRIVE_SHORTCUT!
        powershell -Command "& { try { $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('!ONEDRIVE_SHORTCUT!'); $Shortcut.TargetPath = '!PYTHON_CMD!'; $Shortcut.Arguments = '%APP_DIR%\main.py'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.IconLocation = '%ICON_PATH%'; $Shortcut.Save(); Write-Host 'OneDrive desktop shortcut created successfully.' -ForegroundColor Green; } catch { Write-Host ('Error creating OneDrive shortcut: ' + $_.Exception.Message) -ForegroundColor Red; } }"
        
        :: Also create a shortcut to the application folder on OneDrive Desktop
        set FOLDER_SHORTCUT=!ONEDRIVE_DESKTOP!\KPAstrologyDashboard-Folder.lnk
        echo Creating folder shortcut at: !FOLDER_SHORTCUT!
        powershell -Command "& { try { $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('!FOLDER_SHORTCUT!'); $Shortcut.TargetPath = '%APP_DIR%'; $Shortcut.Save(); Write-Host 'Folder shortcut created successfully.' -ForegroundColor Green; } catch { Write-Host ('Error creating folder shortcut: ' + $_.Exception.Message) -ForegroundColor Red; } }"
    ) else (
        echo WARNING: OneDrive Desktop was detected earlier but not found at %ONEDRIVE_DESKTOP%. Skipping OneDrive shortcut creation.
    )
)

:: Create shortcut on other Desktop location if detected
if not "!OTHER_DESKTOP!"=="" (
    if exist "!OTHER_DESKTOP!" (
        set OTHER_SHORTCUT=!OTHER_DESKTOP!\KPAstrologyDashboard.lnk
        echo Creating shortcut at: !OTHER_SHORTCUT!
        powershell -Command "& { try { $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('!OTHER_SHORTCUT!'); $Shortcut.TargetPath = '!PYTHON_CMD!'; $Shortcut.Arguments = '%APP_DIR%\main.py'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.IconLocation = '%ICON_PATH%'; $Shortcut.Save(); Write-Host 'Additional desktop shortcut created successfully.' -ForegroundColor Green; } catch { Write-Host ('Error creating additional shortcut: ' + $_.Exception.Message) -ForegroundColor Red; } }"
    ) else (
        echo WARNING: Additional Desktop was detected earlier but not found at !OTHER_DESKTOP!. Skipping additional shortcut creation.
    )
)

echo.
echo Installation completed successfully!
echo KP Astrology Dashboard has been installed to: %INSTALL_DIR%
echo You can now run KP Astrology Dashboard from your desktop.
echo.

pause 