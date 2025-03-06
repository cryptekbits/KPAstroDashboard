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

echo Step 1: Installing pyswisseph...
python -m pip install --upgrade pip

:: First try to install pyswisseph from pre-built wheels
echo Attempting to install pyswisseph from pre-built wheels...
python -m pip install --only-binary=:all: pyswisseph==2.10.3.post2

if %ERRORLEVEL% NEQ 0 (
    echo Pre-built wheel for pyswisseph not available for your system.
    echo.
    echo Would you like to:
    echo 1. Try alternative installation methods
    echo 2. Try to install using pip (requires Visual Studio Build Tools)
    echo 3. Skip installation of pyswisseph
    echo.
    
    set /p CHOICE=Enter your choice (1, 2, or 3): 
    
    if "!CHOICE!"=="1" (
        echo Trying unofficial wheel repository...
        python -m pip install pyswisseph==2.10.3.post2 --no-deps --index-url https://www.lfd.uci.edu/~gohlke/pythonlibs/
        
        if %ERRORLEVEL% NEQ 0 (
            echo Unofficial wheel repository failed.
            
            :: Try conda-forge if conda is available
            where conda >nul 2>nul
            if %ERRORLEVEL% EQU 0 (
                echo Trying conda-forge...
                conda install -y -c conda-forge pyswisseph
                
                if %ERRORLEVEL% NEQ 0 (
                    echo Conda-forge installation failed.
                    echo.
                    echo Failed to install pyswisseph using alternative methods.
                    echo.
                    echo To install manually, you will need to:
                    echo 1. Install Visual Studio Build Tools 2022 with C++ development tools
                    echo 2. Run: pip install pyswisseph==2.10.3.post2
                    echo.
                ) else (
                    echo Successfully installed pyswisseph using conda-forge.
                )
            ) else (
                echo Conda not found. Cannot try conda-forge.
                echo.
                echo Failed to install pyswisseph using alternative methods.
                echo.
                echo To install manually, you will need to:
                echo 1. Install Visual Studio Build Tools 2022 with C++ development tools
                echo 2. Run: pip install pyswisseph==2.10.3.post2
                echo.
            )
        ) else (
            echo Successfully installed pyswisseph from unofficial wheel repository.
        )
    ) else if "!CHOICE!"=="2" (
        echo Trying to install with pip (this may fail if you don't have Visual Studio Build Tools)...
        python -m pip install pyswisseph==2.10.3.post2
        
        if %ERRORLEVEL% NEQ 0 (
            echo.
            echo Failed to install pyswisseph.
            echo.
            echo To install manually, you will need to:
            echo 1. Install Visual Studio Build Tools 2022 with C++ development tools
            echo 2. Run: pip install pyswisseph==2.10.3.post2
            echo.
        ) else (
            echo Successfully installed pyswisseph.
        )
    ) else (
        echo Skipping pyswisseph installation.
    )
) else (
    echo Successfully installed pyswisseph.
)

echo.
echo Step 2: Setting up Swiss Ephemeris files...
set SWEFILES_DIR=%INSTALL_DIR%\flatlib\resources\swefiles

:: Check if directory exists, create if not
if not exist "%SWEFILES_DIR%" (
    echo Creating directory for ephemeris files...
    mkdir "%SWEFILES_DIR%"
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

:: Download files if missing
if "%MISSING_FILES%"=="true" (
    echo.
    echo Some ephemeris files are missing. Would you like to download them now? (Y/N)
    set /p DOWNLOAD_CHOICE=Your choice: 
    
    if /i "!DOWNLOAD_CHOICE!"=="Y" (
        echo Downloading missing ephemeris files...
        
        for %%F in (%REQUIRED_FILES%) do (
            if not exist "%SWEFILES_DIR%\%%F" (
                echo Downloading %%F...
                
                :: Try from official GitHub repo first
                powershell -Command "Invoke-WebRequest -Uri 'https://github.com/aloistr/swisseph/raw/master/ephe/%%F' -OutFile '%SWEFILES_DIR%\%%F'"
                
                if %ERRORLEVEL% NEQ 0 (
                    echo Failed from primary source, trying alternative...
                    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/flatangle/flatlib/raw/master/flatlib/resources/swefiles/%%F' -OutFile '%SWEFILES_DIR%\%%F'"
                    
                    if %ERRORLEVEL% NEQ 0 (
                        echo Failed to download %%F from all sources.
                    ) else (
                        echo Downloaded %%F successfully from alternative source.
                    )
                ) else (
                    echo Downloaded %%F successfully.
                )
            )
        )
        
        echo.
        echo Verifying downloaded files...
        set "STILL_MISSING=false"
        for %%F in (%REQUIRED_FILES%) do (
            if not exist "%SWEFILES_DIR%\%%F" (
                echo Still missing: %%F
                set "STILL_MISSING=true"
            ) else (
                echo Verified: %%F
            )
        )
        
        if "%STILL_MISSING%"=="true" (
            echo.
            echo WARNING: Some files could not be downloaded. 
            echo The application may not work correctly.
        ) else (
            echo.
            echo All ephemeris files were successfully downloaded.
        )
    ) else (
        echo Skipping ephemeris file download.
    )
) else (
    echo All required ephemeris files are already present.
)

echo.
echo =====================================================
echo Dependency installation process completed.
echo.
echo If you still experience issues, please visit:
echo https://github.com/cryptekbits/KPAstroDashboard/issues
echo =====================================================
echo.

pause 