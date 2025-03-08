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

:: Check if the application is already installed
set APP_INSTALLED=false
if exist "%INSTALL_DIR%\main.py" (
    set APP_INSTALLED=true
    echo.
    echo KP Astrology Dashboard is already installed at:
    echo %INSTALL_DIR%
    echo.
    echo What would you like to do?
    echo 1. Update existing installation (preserves user configuration)
    echo 2. Perform a clean reinstall (removes all files and settings)
    echo 3. Exit without changes
    echo.
    
    set /p INSTALL_CHOICE=Your choice (1-3): 
    
    if "!INSTALL_CHOICE!"=="3" (
        echo Installation cancelled by user.
        pause
        exit /b 0
    )
    
    if "!INSTALL_CHOICE!"=="2" (
        echo.
        echo Performing clean reinstall...
        echo Removing existing installation...
        
        :: Backup config.json if it exists
        if exist "%INSTALL_DIR%\config.json" (
            echo Backing up user configuration...
            copy "%INSTALL_DIR%\config.json" "%TEMP%\kp_dashboard_config_backup.json" >nul
            echo Configuration backed up to: %TEMP%\kp_dashboard_config_backup.json
        )
        
        :: Remove existing installation
        rmdir /S /Q "%INSTALL_DIR%"
        mkdir "%INSTALL_DIR%"
    )
    
    if "!INSTALL_CHOICE!"=="1" (
        echo.
        echo Updating existing installation...
        echo Important files and user settings will be preserved.
        
        :: Create a temporary directory for update files
        set "UPDATE_TEMP=%TEMP%\kp_dashboard_update"
        if exist "!UPDATE_TEMP!" rmdir /S /Q "!UPDATE_TEMP!"
        mkdir "!UPDATE_TEMP!"
    )
) else (
    :: Create installation directory if it doesn't exist
    if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
)

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

:: Set up extraction based on whether we're doing an update or reinstall
if "!INSTALL_CHOICE!"=="1" (
    :: For update, extract to temporary location first
    set "TEMP_EXTRACT_DIR=!UPDATE_TEMP!\extract"
) else (
    :: For clean install or new install, use standard temp location
    set "TEMP_EXTRACT_DIR=%TEMP%\KPAstrologyDashboard-extract"
)

:: Clean previous extraction directory if it exists
if exist "!TEMP_EXTRACT_DIR!" (
    echo Cleaning previous temporary extraction directory...
    rmdir /S /Q "!TEMP_EXTRACT_DIR!"
)

:: Extract using PowerShell
echo.
echo Extracting files...
powershell -Command "& { $ErrorActionPreference = 'Stop'; try { Write-Host 'Extracting archive...' -ForegroundColor Cyan; Expand-Archive -Path '%LOCAL_ZIP_FILE%' -DestinationPath '!TEMP_EXTRACT_DIR!' -Force; Write-Host 'Extraction successful.' -ForegroundColor Green; } catch { Write-Host ('Extraction error: ' + $_.Exception.Message) -ForegroundColor Red; exit 1; } }"

if %ERRORLEVEL% NEQ 0 (
    echo Failed to extract the application package.
    pause
    exit /b 1
)

:: Move files based on installation type
echo.
if "!INSTALL_CHOICE!"=="1" (
    echo Updating files in installation directory...
    
    :: Identify the GitHub extracted folder (it will be KPAstroDashboard-VERSION)
    for /d %%G in ("!TEMP_EXTRACT_DIR!\*") do (
        set "SOURCE_DIR=%%G"
    )
    
    :: Backup important user files
    echo Backing up user configuration...
    if exist "%INSTALL_DIR%\config.json" (
        copy "%INSTALL_DIR%\config.json" "!UPDATE_TEMP!\config.json.bak" >nul
    )
    
    :: Files to preserve during update
    set "PRESERVE_FILES=config.json kp_astrology.log app_startup.log"
    
    :: Copy new files, skipping the preserved files
    echo Copying new application files...
    for /f "delims=" %%F in ('dir /b /a-d "!SOURCE_DIR!\*"') do (
        set "SKIP_FILE=false"
        for %%P in (%PRESERVE_FILES%) do (
            if "%%F"=="%%P" set "SKIP_FILE=true"
        )
        
        if "!SKIP_FILE!"=="false" (
            copy "!SOURCE_DIR!\%%F" "%INSTALL_DIR%\" >nul
        )
    )
    
    :: Copy directories
    for /f "delims=" %%D in ('dir /b /ad "!SOURCE_DIR!\*"') do (
        :: Skip logs directory
        if not "%%D"=="logs" (
            if exist "%INSTALL_DIR%\%%D" (
                rmdir /S /Q "%INSTALL_DIR%\%%D"
            )
            xcopy "!SOURCE_DIR!\%%D" "%INSTALL_DIR%\%%D\" /E /I /Y >nul
        )
    )
    
    echo Update completed successfully.
) else (
    :: Regular installation - copy all files from the extracted folder
    echo Moving files to installation directory...
    :: Find the extracted folder (it will be KPAstroDashboard-VERSION)
    for /d %%G in ("!TEMP_EXTRACT_DIR!\*") do (
        echo Copying from: %%G
        xcopy "%%G\*" "%INSTALL_DIR%" /E /I /Y
    )
    
    :: Restore config.json if doing a clean reinstall and a backup exists
    if "!INSTALL_CHOICE!"=="2" if exist "%TEMP%\kp_dashboard_config_backup.json" (
        echo Restoring user configuration...
        copy "%TEMP%\kp_dashboard_config_backup.json" "%INSTALL_DIR%\config.json" >nul
        echo Configuration restored.
    )
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

:: Clean up temp extraction directories
if "!INSTALL_CHOICE!"=="1" (
    rmdir /S /Q "!UPDATE_TEMP!"
) else (
    rmdir /S /Q "!TEMP_EXTRACT_DIR!"
)

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

:: Setup Swiss Ephemeris files - test functionality first
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

:: Create a quick Python test script to verify Swiss Ephemeris functionality
echo.
echo Creating Swiss Ephemeris test script...
set TEST_SCRIPT=%INSTALL_DIR%\test_swisseph.py

:: Create the test script
echo import os > "%TEST_SCRIPT%"
echo import sys >> "%TEST_SCRIPT%"
echo. >> "%TEST_SCRIPT%"
echo def test_swisseph_functionality(): >> "%TEST_SCRIPT%"
echo     """Test if Swiss Ephemeris works correctly""" >> "%TEST_SCRIPT%"
echo     try: >> "%TEST_SCRIPT%"
echo         import swisseph >> "%TEST_SCRIPT%"
echo         import flatlib >> "%TEST_SCRIPT%"
echo         from flatlib.ephem import setPath >> "%TEST_SCRIPT%"
echo. >> "%TEST_SCRIPT%"
echo         # Use only built-in path for swefiles >> "%TEST_SCRIPT%"
echo         app_dir = os.path.dirname(os.path.abspath(__file__)) >> "%TEST_SCRIPT%"
echo         swefiles_path = os.path.join(app_dir, 'flatlib', 'resources', 'swefiles') >> "%TEST_SCRIPT%"
echo. >> "%TEST_SCRIPT%"
echo         # Normalize path for Windows >> "%TEST_SCRIPT%"
echo         normalized_path = swefiles_path.replace('\\', '/') >> "%TEST_SCRIPT%"
echo. >> "%TEST_SCRIPT%"
echo         # Set path >> "%TEST_SCRIPT%"
echo         setPath(normalized_path) >> "%TEST_SCRIPT%"
echo. >> "%TEST_SCRIPT%"
echo         # Test calculation >> "%TEST_SCRIPT%"
echo         test_jd = 2459000.5  # A random Julian date >> "%TEST_SCRIPT%"
echo         test_result = swisseph.calc_ut(test_jd, 0, 2)  # Calculate Sun position >> "%TEST_SCRIPT%"
echo. >> "%TEST_SCRIPT%"
echo         print(f"SwissEph test successful: {test_result}") >> "%TEST_SCRIPT%"
echo         return True >> "%TEST_SCRIPT%"
echo     except Exception as e: >> "%TEST_SCRIPT%"
echo         print(f"SwissEph test failed: {str(e)}") >> "%TEST_SCRIPT%"
echo         return False >> "%TEST_SCRIPT%"
echo. >> "%TEST_SCRIPT%"
echo if __name__ == "__main__": >> "%TEST_SCRIPT%"
echo     success = test_swisseph_functionality() >> "%TEST_SCRIPT%"
echo     sys.exit(0 if success else 1) >> "%TEST_SCRIPT%"

:: Run the test script
echo.
echo Running Swiss Ephemeris test...
%PYTHON_CMD% "%TEST_SCRIPT%"
set SWISSEPH_TEST_RESULT=%ERRORLEVEL%

:: Only proceed with system-wide setup if the test failed
if %SWISSEPH_TEST_RESULT% NEQ 0 (
    echo.
    echo Swiss Ephemeris test failed. Checking system-wide configuration...
    
    :: Check if system-wide Swiss Ephemeris directory exists
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
        :: Check if files exist in the system directory
        set "SYSTEM_MISSING_FILES=false"
        for %%F in (%REQUIRED_FILES%) do (
            if not exist "%SYSTEM_SWEFILES_DIR%\%%F" (
                set "SYSTEM_MISSING_FILES=true"
                goto check_missing_done
            )
        )
        
        :check_missing_done
        if "!SYSTEM_MISSING_FILES!"=="true" (
            echo System-wide Swiss Ephemeris directory exists but some files are missing.
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
        ) else (
            echo System-wide Swiss Ephemeris directory exists with all required files.
            echo No actions needed.
        )
    )
    
    :: Run the test script again to verify
    echo.
    echo Running Swiss Ephemeris test again after system-wide setup...
    %PYTHON_CMD% "%TEST_SCRIPT%"
    set RETEST_RESULT=%ERRORLEVEL%
    
    if !RETEST_RESULT! EQU 0 (
        echo Swiss Ephemeris now working correctly!
    ) else (
        echo Warning: Swiss Ephemeris still not working correctly. You may encounter issues with the application.
    )
) else (
    echo Swiss Ephemeris test successful! No system-wide setup needed.
)

:: Clean up the test script
del "%TEST_SCRIPT%"

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