# KP Astrology Dashboard - Windows PowerShell Installation Script
Write-Host "KP Astrology Dashboard - Windows Installation Script" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Set version and GitHub repo information
$VERSION = "##VERSION##"
$REPO_OWNER = "cryptekbits"
$REPO_NAME = "KPAstroDashboard"
$DOWNLOAD_URL = "https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/tags/v$VERSION.zip"
$REQUIRED_PYTHON_VERSION = "3.13.2"

# Detect user directories and handle OneDrive case
Write-Host "Detecting user directories..." -ForegroundColor Yellow

# Primary Desktop and Downloads
$DESKTOP_DIR = [System.Environment]::GetFolderPath("Desktop")
$DOWNLOADS_DIR = [System.Environment]::GetFolderPath("UserProfile") + "\Downloads"

Write-Host "Primary Desktop detected at: $DESKTOP_DIR"
Write-Host "Primary Downloads detected at: $DOWNLOADS_DIR"

# Search for OneDrive Desktop
$HAS_ONEDRIVE_DESKTOP = $false
$ONEDRIVE_DESKTOP = "$env:USERPROFILE\OneDrive\Desktop"
if (Test-Path $ONEDRIVE_DESKTOP) {
    Write-Host "OneDrive Desktop detected at: $ONEDRIVE_DESKTOP" -ForegroundColor Green
    $HAS_ONEDRIVE_DESKTOP = $true
}

# Search for OneDrive Downloads
$ONEDRIVE_DOWNLOADS = "$env:USERPROFILE\OneDrive\Downloads"
if (Test-Path $ONEDRIVE_DOWNLOADS) {
    Write-Host "OneDrive Downloads detected at: $ONEDRIVE_DOWNLOADS" -ForegroundColor Green
    $DOWNLOADS_DIR = $ONEDRIVE_DOWNLOADS
    Write-Host "Using OneDrive Downloads as download location" -ForegroundColor Green
}

# Check for other possible Desktop locations
$OTHER_DESKTOPS = @()
$POSSIBLE_DESKTOP_LOCATIONS = @(
    "$env:USERPROFILE\Documents\Desktop",
    "$env:PUBLIC\Desktop",
    "$env:PUBLIC\Public Desktop"
)

foreach ($location in $POSSIBLE_DESKTOP_LOCATIONS) {
    if (Test-Path $location) {
        $OTHER_DESKTOPS += $location
        Write-Host "Additional Desktop found at: $location" -ForegroundColor Green
    }
}

# Set installation directory on primary Desktop (non-OneDrive)
$INSTALL_DIR = "$DESKTOP_DIR\KPAstrologyDashboard"

Write-Host ""
Write-Host "Installation directory: $INSTALL_DIR" -ForegroundColor Cyan
Write-Host "Download directory: $DOWNLOADS_DIR" -ForegroundColor Cyan
Write-Host ""

# Create installation directory if it doesn't exist
if (-not (Test-Path $INSTALL_DIR)) {
    Write-Host "Creating installation directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
    Write-Host "Installation directory created at: $INSTALL_DIR" -ForegroundColor Green
}

# Check if zip file already exists from a previous download
$LOCAL_ZIP_FILE = "$DOWNLOADS_DIR\KPAstrologyDashboard-$VERSION.zip"
if (Test-Path $LOCAL_ZIP_FILE) {
    Write-Host "Previously downloaded KP Astrology Dashboard v$VERSION found." -ForegroundColor Green
    Write-Host "Location: $LOCAL_ZIP_FILE" -ForegroundColor Green
    Write-Host "Skipping download phase." -ForegroundColor Green
} else {
    # Download the release zip with progress indicator
    Write-Host "Downloading KP Astrology Dashboard v$VERSION..." -ForegroundColor Yellow
    Write-Host "URL: $DOWNLOAD_URL" -ForegroundColor Yellow
    
    try {
        $ProgressPreference = 'Continue'
        $wc = New-Object System.Net.WebClient
        $wc.Headers.Add("User-Agent", "KPAstroDashboard Installer")
        
        # Register download progress event
        $start = Get-Date
        
        $ProgressEvent = Register-ObjectEvent -InputObject $wc -EventName DownloadProgressChanged -Action {
            $percent = $EventArgs.ProgressPercentage
            $currBytes = $EventArgs.BytesReceived
            $totalBytes = $EventArgs.TotalBytesToReceive
            $elapsed = ((Get-Date) - $start).TotalSeconds
            $speed = if ($elapsed -gt 0) { $currBytes / $elapsed / 1MB } else { 0 }
            $remaining = if ($speed -gt 0) { ($totalBytes - $currBytes) / ($speed * 1MB) } else { 0 }
            
            Write-Progress -Activity "Downloading KP Astrology Dashboard" `
                -Status "$([Math]::Round($percent))% Complete" `
                -CurrentOperation "$([Math]::Round($currBytes/1MB, 2)) MB of $([Math]::Round($totalBytes/1MB, 2)) MB - $([Math]::Round($speed, 2)) MB/s - ETA: $([Math]::Round($remaining)) seconds" `
                -PercentComplete $percent
        }
        
        $CompletedEvent = Register-ObjectEvent -InputObject $wc -EventName DownloadFileCompleted -Action {
            Write-Host "Download completed!" -ForegroundColor Green
            Write-Progress -Activity "Downloading KP Astrology Dashboard" -Completed
        }
        
        # Start async download
        $wc.DownloadFileAsync($DOWNLOAD_URL, $LOCAL_ZIP_FILE)
        
        # Wait for download to complete
        while ($wc.IsBusy) { Start-Sleep -Milliseconds 100 }
        
        # Clean up events
        Unregister-Event -SourceIdentifier $ProgressEvent.Name
        Unregister-Event -SourceIdentifier $CompletedEvent.Name
        
        if (Test-Path $LOCAL_ZIP_FILE) {
            $fileSize = (Get-Item $LOCAL_ZIP_FILE).Length / 1MB
            $downloadTime = ((Get-Date) - $start).TotalSeconds
            Write-Host "Downloaded $([Math]::Round($fileSize, 2)) MB in $([Math]::Round($downloadTime, 2)) seconds." -ForegroundColor Green
        } else {
            Write-Host "Download failed!" -ForegroundColor Red
            exit 1
        }
    }
    catch {
        Write-Host "Failed to download the application package." -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        Write-Host "Please check your internet connection and try again."
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check if files were already extracted to the destination
if (Test-Path "$INSTALL_DIR\main.py") {
    Write-Host "Application files already exist in destination folder." -ForegroundColor Yellow
    $extractChoice = Read-Host "Would you like to re-extract the files? (Y/N)"
    
    if ($extractChoice -ne "Y" -and $extractChoice -ne "y") {
        Write-Host "Skipping extraction phase." -ForegroundColor Green
        $skipExtraction = $true
    }
}

if (-not $skipExtraction) {
    # Extract the zip file
    Write-Host ""
    Write-Host "Extracting files..." -ForegroundColor Yellow
    
    # Check if temp extraction dir already exists and contains files
    $TEMP_EXTRACT_DIR = "$env:TEMP\KPAstrologyDashboard-extract"
    if (Test-Path $TEMP_EXTRACT_DIR) {
        Write-Host "Cleaning previous temporary extraction directory..." -ForegroundColor Yellow
        Remove-Item -Path $TEMP_EXTRACT_DIR -Recurse -Force
    }
    
    # Extract using PowerShell with progress indicator
    try {
        Write-Host "Extracting archive..." -ForegroundColor Yellow
        $ProgressPreference = 'Continue'
        Expand-Archive -Path $LOCAL_ZIP_FILE -DestinationPath $TEMP_EXTRACT_DIR -Force
        
        # Find the extracted directory
        $extractedDir = Get-ChildItem -Path $TEMP_EXTRACT_DIR -Directory | Select-Object -First 1
        
        if ($extractedDir) {
            Write-Host "Moving files to installation directory..." -ForegroundColor Yellow
            
            # Copy files with progress
            $files = Get-ChildItem -Path $extractedDir.FullName -Recurse
            $fileCount = $files.Count
            $i = 0
            
            foreach ($file in $files) {
                $i++
                $percent = [int]($i / $fileCount * 100)
                $relativePath = $file.FullName.Substring($extractedDir.FullName.Length)
                $destPath = Join-Path -Path $INSTALL_DIR -ChildPath $relativePath
                
                Write-Progress -Activity "Copying Files" -Status "$percent% Complete" -PercentComplete $percent -CurrentOperation $relativePath
                
                if ($file -is [System.IO.DirectoryInfo]) {
                    if (-not (Test-Path $destPath)) {
                        New-Item -ItemType Directory -Path $destPath -Force | Out-Null
                    }
                } else {
                    Copy-Item -Path $file.FullName -Destination $destPath -Force
                }
            }
            
            Write-Progress -Activity "Copying Files" -Completed
            Write-Host "Files copied successfully." -ForegroundColor Green
        } else {
            Write-Host "Error: Could not find extracted directory." -ForegroundColor Red
            exit 1
        }
        
        # Clean up temp extraction directory
        Remove-Item -Path $TEMP_EXTRACT_DIR -Recurse -Force
        Write-Host "Temporary extraction directory cleaned up." -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to extract the application package." -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check if Python is installed and meets the required version
Write-Host ""
Write-Host "Checking Python installation..." -ForegroundColor Yellow

$pythonInstalled = $false
$pythonCommand = $null
$currentPythonVersion = $null

# Try different Python commands to detect installation
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    try {
        $pythonOutput = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonInstalled = $true
            $pythonCommand = $cmd
            
            # Extract version number from output (format: "Python X.Y.Z")
            if ($pythonOutput -match "Python (\d+\.\d+\.\d+)") {
                $currentPythonVersion = $matches[1]
                Write-Host "Found: Python $currentPythonVersion using command '$pythonCommand'" -ForegroundColor Green
                break
            }
        }
    }
    catch {
        # Command not found, continue to next
        continue
    }
}

$needsPythonInstall = $false

if (-not $pythonInstalled) {
    Write-Host "Python not found. You need to install Python $REQUIRED_PYTHON_VERSION..." -ForegroundColor Yellow
    $needsPythonInstall = $true
} else {
    # Compare versions
    $currentVersion = [Version]$currentPythonVersion
    $requiredVersion = [Version]$REQUIRED_PYTHON_VERSION
    
    if ($currentVersion -lt $requiredVersion) {
        Write-Host "Python version $currentPythonVersion is older than required version $REQUIRED_PYTHON_VERSION" -ForegroundColor Yellow
        Write-Host "You need to upgrade Python..." -ForegroundColor Yellow
        $needsPythonInstall = $true
    } else {
        Write-Host "Python version $currentPythonVersion meets the requirement (>= $REQUIRED_PYTHON_VERSION)" -ForegroundColor Green
    }
}

if ($needsPythonInstall) {
    # Download Python installer to user's Downloads folder
    $arch = "amd64"
    
    # Detect ARM64 architecture
    $isArm64 = $false
    try {
        $osInfo = Get-WmiObject -Class Win32_OperatingSystem
        if ($osInfo.OSArchitecture -like "*ARM64*") {
            $arch = "arm64"
            $isArm64 = $true
            Write-Host "Detected ARM64 architecture" -ForegroundColor Yellow
        } else {
            Write-Host "Detected AMD64 architecture" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Could not detect system architecture, defaulting to AMD64" -ForegroundColor Yellow
    }
    
    $PYTHON_INSTALLER_PATH = "$DOWNLOADS_DIR\python-$REQUIRED_PYTHON_VERSION-$arch.exe"
    
    # Check if installer already exists
    if (Test-Path $PYTHON_INSTALLER_PATH) {
        Write-Host "Python installer already exists at: $PYTHON_INSTALLER_PATH" -ForegroundColor Green
    } else {
        Write-Host "Downloading Python installer to your Downloads folder..." -ForegroundColor Yellow
        
        $PYTHON_DOWNLOAD_URL = "https://www.python.org/ftp/python/$REQUIRED_PYTHON_VERSION/python-$REQUIRED_PYTHON_VERSION-$arch.exe"
        Write-Host "Download URL: $PYTHON_DOWNLOAD_URL" -ForegroundColor Yellow
        
        try {
            $ProgressPreference = 'Continue'
            $wc = New-Object System.Net.WebClient
            
            # Register download progress event
            $start = Get-Date
            
            $ProgressEvent = Register-ObjectEvent -InputObject $wc -EventName DownloadProgressChanged -Action {
                $percent = $EventArgs.ProgressPercentage
                $currBytes = $EventArgs.BytesReceived
                $totalBytes = $EventArgs.TotalBytesToReceive
                $elapsed = ((Get-Date) - $start).TotalSeconds
                $speed = if ($elapsed -gt 0) { $currBytes / $elapsed / 1MB } else { 0 }
                $remaining = if ($speed -gt 0) { ($totalBytes - $currBytes) / ($speed * 1MB) } else { 0 }
                
                Write-Progress -Activity "Downloading Python Installer" `
                    -Status "$([Math]::Round($percent))% Complete" `
                    -CurrentOperation "$([Math]::Round($currBytes/1MB, 2)) MB of $([Math]::Round($totalBytes/1MB, 2)) MB - $([Math]::Round($speed, 2)) MB/s - ETA: $([Math]::Round($remaining)) seconds" `
                    -PercentComplete $percent
            }
            
            $CompletedEvent = Register-ObjectEvent -InputObject $wc -EventName DownloadFileCompleted -Action {
                Write-Host "Download completed!" -ForegroundColor Green
                Write-Progress -Activity "Downloading Python Installer" -Completed
            }
            
            # Start async download
            $wc.DownloadFileAsync($PYTHON_DOWNLOAD_URL, $PYTHON_INSTALLER_PATH)
            
            # Wait for download to complete
            while ($wc.IsBusy) { Start-Sleep -Milliseconds 100 }
            
            # Clean up events
            Unregister-Event -SourceIdentifier $ProgressEvent.Name
            Unregister-Event -SourceIdentifier $CompletedEvent.Name
            
            if (Test-Path $PYTHON_INSTALLER_PATH) {
                $fileSize = (Get-Item $PYTHON_INSTALLER_PATH).Length / 1MB
                $downloadTime = ((Get-Date) - $start).TotalSeconds
                Write-Host "Downloaded $([Math]::Round($fileSize, 2)) MB in $([Math]::Round($downloadTime, 2)) seconds." -ForegroundColor Green
            } else {
                Write-Host "Download failed!" -ForegroundColor Red
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
        catch {
            Write-Host "Failed to download Python installer." -ForegroundColor Red
            Write-Host "Error: $_" -ForegroundColor Red
            Write-Host "Please install Python $REQUIRED_PYTHON_VERSION or later manually from https://www.python.org/downloads/"
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    
    # Open the folder containing the Python installer
    Write-Host ""
    Write-Host "Please install Python $REQUIRED_PYTHON_VERSION by running the installer." -ForegroundColor Yellow
    Write-Host "Opening the download location for you..." -ForegroundColor Yellow
    
    Start-Process "explorer.exe" -ArgumentList "/select,`"$PYTHON_INSTALLER_PATH`""
    
    Write-Host ""
    Write-Host "IMPORTANT: During installation, make sure to check:" -ForegroundColor Yellow
    Write-Host "- 'Add Python to PATH'" -ForegroundColor Cyan
    Write-Host "- 'Install for all users' (recommended)" -ForegroundColor Cyan
    Write-Host ""
    
    Read-Host "After installing Python, press Enter to continue"
    
    # Verify installation
    Write-Host "Verifying Python installation..." -ForegroundColor Yellow
    
    $pythonInstalled = $false
    foreach ($cmd in $pythonCommands) {
        try {
            $pythonOutput = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $pythonInstalled = $true
                $pythonCommand = $cmd
                
                # Extract version number from output (format: "Python X.Y.Z")
                if ($pythonOutput -match "Python (\d+\.\d+\.\d+)") {
                    $currentPythonVersion = $matches[1]
                    Write-Host "Detected: Python $currentPythonVersion using command '$pythonCommand'" -ForegroundColor Green
                    break
                }
            }
        }
        catch {
            # Command not found, continue to next
            continue
        }
    }
    
    if (-not $pythonInstalled) {
        Write-Host "Failed to find Python after installation." -ForegroundColor Red
        Write-Host "Please make sure Python was installed correctly and 'Add Python to PATH' was selected." -ForegroundColor Red
        Write-Host "You may need to restart your computer for PATH changes to take effect." -ForegroundColor Yellow
        
        $continueAnyway = Read-Host "Do you want to continue anyway? (Y/N)"
        if ($continueAnyway -ne "Y" -and $continueAnyway -ne "y") {
            exit 1
        }
        
        # Default to python as command if not found but user wants to continue
        $pythonCommand = "python"
    }
} else {
    Write-Host "Python $currentPythonVersion is already installed and meets requirements." -ForegroundColor Green
}

# Install required packages
Write-Host ""
Write-Host "Installing required packages..." -ForegroundColor Yellow

try {
    # Upgrade pip
    Write-Host "Upgrading pip..." -ForegroundColor Yellow
    & $pythonCommand -m pip install --upgrade pip
    
    # Check for and uninstall existing flatlib
    Write-Host "Checking for existing flatlib installation..." -ForegroundColor Yellow
    
    $hasFlatlib = $false
    
    try {
        & $pythonCommand -m pip show flatlib | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $hasFlatlib = $true
            Write-Host "Removing existing flatlib installation..." -ForegroundColor Yellow
            & $pythonCommand -m pip uninstall -y flatlib
            Write-Host "Flatlib removed successfully." -ForegroundColor Green
        } else {
            Write-Host "Flatlib not found." -ForegroundColor Green
        }
    }
    catch {
        Write-Host "Flatlib not found." -ForegroundColor Green
    }
    
    # Install pyswisseph directly from PyPI
    Write-Host "Installing pyswisseph from PyPI..." -ForegroundColor Yellow
    & $pythonCommand -m pip install pyswisseph>=2.10.3.2
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install pyswisseph from PyPI." -ForegroundColor Red
        Write-Host "This may be due to missing build tools." -ForegroundColor Red
        Write-Host "Please ensure you have the Microsoft Visual C++ Build Tools installed." -ForegroundColor Red
        Write-Host "You can download them from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Pyswisseph installed successfully." -ForegroundColor Green
    
    # Now install requirements
    Write-Host "Installing required packages from requirements.txt..." -ForegroundColor Yellow
    & $pythonCommand -m pip install -r "$INSTALL_DIR\requirements.txt"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully installed required packages." -ForegroundColor Green
    } else {
        Write-Host "Failed to install required packages." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}
catch {
    Write-Host "An error occurred during package installation." -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Setup Swiss Ephemeris files
Write-Host ""
Write-Host "Setting up Swiss Ephemeris files..." -ForegroundColor Yellow

$SWEFILES_DIR = "$INSTALL_DIR\flatlib\resources\swefiles"
$SYSTEM_SWEFILES_DIR = "C:\sweph\ephe"

# Check if directory exists
if (-not (Test-Path $SWEFILES_DIR)) {
    Write-Host "Error: Swiss Ephemeris files directory not found at $SWEFILES_DIR" -ForegroundColor Red
    Write-Host "Please ensure the application is installed correctly." -ForegroundColor Red
} else {
    # Required files
    $REQUIRED_FILES = @("seas_18.se1", "sepl_18.se1", "semo_18.se1", "fixstars.cat")
    
    # Check for required files
    Write-Host "Checking for required ephemeris files..." -ForegroundColor Yellow
    $missingFiles = $false
    
    foreach ($file in $REQUIRED_FILES) {
        if (-not (Test-Path "$SWEFILES_DIR\$file")) {
            Write-Host "Missing: $file" -ForegroundColor Red
            $missingFiles = $true
        } else {
            Write-Host "Found: $file" -ForegroundColor Green
        }
    }
    
    if ($missingFiles) {
        Write-Host "Some required Swiss Ephemeris files are missing from the source directory." -ForegroundColor Red
        Write-Host "Please ensure the application package is complete." -ForegroundColor Red
    } else {
        Write-Host "All required ephemeris files are present in the application directory." -ForegroundColor Green
        
        # Check if system-wide Swiss Ephemeris directory exists
        Write-Host ""
        Write-Host "Checking for system-wide Swiss Ephemeris directory..." -ForegroundColor Yellow
        
        if (-not (Test-Path $SYSTEM_SWEFILES_DIR)) {
            Write-Host "System-wide Swiss Ephemeris directory not found." -ForegroundColor Yellow
            $systemChoice = Read-Host "Would you like to create it and copy the ephemeris files? (Y/N) This will require administrator privileges"
            
            if ($systemChoice -eq "Y" -or $systemChoice -eq "y") {
                $scriptBlock = {
                    param($SYSTEM_SWEFILES_DIR, $SWEFILES_DIR, $REQUIRED_FILES)
                    
                    # Create directory if it doesn't exist
                    if (-not (Test-Path $SYSTEM_SWEFILES_DIR)) {
                        Write-Host "Creating system-wide Swiss Ephemeris directory..." -ForegroundColor Yellow
                        New-Item -ItemType Directory -Path $SYSTEM_SWEFILES_DIR -Force | Out-Null
                    }
                    
                    # Copy files
                    Write-Host "Copying ephemeris files..." -ForegroundColor Yellow
                    foreach ($file in $REQUIRED_FILES) {
                        if (Test-Path "$SWEFILES_DIR\$file") {
                            Copy-Item -Path "$SWEFILES_DIR\$file" -Destination "$SYSTEM_SWEFILES_DIR\$file" -Force
                            Write-Host "Copied: $file" -ForegroundColor Green
                        } else {
                            Write-Host "Skipped: $file (not found in source)" -ForegroundColor Yellow
                        }
                    }
                    
                    Write-Host "System-wide Swiss Ephemeris files setup complete." -ForegroundColor Green
                }
                
                # Run as administrator
                Write-Host "Requesting administrator privileges..." -ForegroundColor Yellow
                
                $encodedCommand = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes(
                    "&{$scriptBlock} -SYSTEM_SWEFILES_DIR '$SYSTEM_SWEFILES_DIR' -SWEFILES_DIR '$SWEFILES_DIR' -REQUIRED_FILES @('$($REQUIRED_FILES -join "','")') | Write-Output"
                ))
                
                Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile", "-EncodedCommand", $encodedCommand -Verb RunAs -Wait
            } else {
                Write-Host "Skipping system-wide Swiss Ephemeris setup." -ForegroundColor Yellow
            }
        } else {
            Write-Host "System-wide Swiss Ephemeris directory already exists." -ForegroundColor Green
            $updateChoice = Read-Host "Would you like to update the ephemeris files? (Y/N) This will require administrator privileges"
            
            if ($updateChoice -eq "Y" -or $updateChoice -eq "y") {
                $scriptBlock = {
                    param($SYSTEM_SWEFILES_DIR, $SWEFILES_DIR, $REQUIRED_FILES)
                    
                    # Copy files
                    Write-Host "Updating system-wide Swiss Ephemeris files..." -ForegroundColor Yellow
                    foreach ($file in $REQUIRED_FILES) {
                        if (Test-Path "$SWEFILES_DIR\$file") {
                            Copy-Item -Path "$SWEFILES_DIR\$file" -Destination "$SYSTEM_SWEFILES_DIR\$file" -Force
                            Write-Host "Updated: $file" -ForegroundColor Green
                        } else {
                            Write-Host "Skipped: $file (not found in source)" -ForegroundColor Yellow
                        }
                    }
                    
                    Write-Host "System-wide Swiss Ephemeris files update complete." -ForegroundColor Green
                }
                
                # Run as administrator
                Write-Host "Requesting administrator privileges..." -ForegroundColor Yellow
                
                $encodedCommand = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes(
                    "&{$scriptBlock} -SYSTEM_SWEFILES_DIR '$SYSTEM_SWEFILES_DIR' -SWEFILES_DIR '$SWEFILES_DIR' -REQUIRED_FILES @('$($REQUIRED_FILES -join "','")') | Write-Output"
                ))
                
                Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile", "-EncodedCommand", $encodedCommand -Verb RunAs -Wait
            } else {
                Write-Host "Skipping system-wide Swiss Ephemeris update." -ForegroundColor Yellow
            }
        }
    }
}

# Create desktop shortcuts on all detected Desktop locations
Write-Host ""
Write-Host "Creating desktop shortcuts..." -ForegroundColor Yellow

$APP_DIR = $INSTALL_DIR
$ICON_PATH = "$APP_DIR\resources\favicon.ico"

# Create shortcut on primary Desktop
$SHORTCUT = "$DESKTOP_DIR\KPAstrologyDashboard.lnk"
Write-Host "Creating shortcut at: $SHORTCUT" -ForegroundColor Yellow

try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($SHORTCUT)
    $Shortcut.TargetPath = $pythonCommand
    $Shortcut.Arguments = "$APP_DIR\main.py"
    $Shortcut.WorkingDirectory = $APP_DIR
    $Shortcut.IconLocation = $ICON_PATH
    $Shortcut.Save()
    Write-Host "Shortcut created successfully." -ForegroundColor Green
}
catch {
    Write-Host "Failed to create shortcut at $SHORTCUT" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

# Create shortcut on OneDrive Desktop if it exists
if ($HAS_ONEDRIVE_DESKTOP) {
    $ONEDRIVE_SHORTCUT = "$ONEDRIVE_DESKTOP\KPAstrologyDashboard.lnk"
    Write-Host "Creating shortcut at: $ONEDRIVE_SHORTCUT" -ForegroundColor Yellow
    
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($ONEDRIVE_SHORTCUT)
        $Shortcut.TargetPath = $pythonCommand
        $Shortcut.Arguments = "$APP_DIR\main.py"
        $Shortcut.WorkingDirectory = $APP_DIR
        $Shortcut.IconLocation = $ICON_PATH
        $Shortcut.Save()
        Write-Host "OneDrive Desktop shortcut created successfully." -ForegroundColor Green
        
        # Also create a shortcut to the application folder on OneDrive Desktop
        $FOLDER_SHORTCUT = "$ONEDRIVE_DESKTOP\KPAstrologyDashboard-Folder.lnk"
        Write-Host "Creating folder shortcut at: $FOLDER_SHORTCUT" -ForegroundColor Yellow
        
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($FOLDER_SHORTCUT)
        $Shortcut.TargetPath = $APP_DIR
        $Shortcut.Save()
        Write-Host "Folder shortcut created successfully." -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to create OneDrive shortcut" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

# Create shortcuts on other Desktop locations if detected
foreach ($otherDesktop in $OTHER_DESKTOPS) {
    $OTHER_SHORTCUT = "$otherDesktop\KPAstrologyDashboard.lnk"
    Write-Host "Creating shortcut at: $OTHER_SHORTCUT" -ForegroundColor Yellow
    
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($OTHER_SHORTCUT)
        $Shortcut.TargetPath = $pythonCommand
        $Shortcut.Arguments = "$APP_DIR\main.py"
        $Shortcut.WorkingDirectory = $APP_DIR
        $Shortcut.IconLocation = $ICON_PATH
        $Shortcut.Save()
        Write-Host "Additional Desktop shortcut created successfully." -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to create shortcut at $OTHER_SHORTCUT" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "KP Astrology Dashboard has been installed to: $INSTALL_DIR" -ForegroundColor Green
Write-Host "You can now run KP Astrology Dashboard from your desktop." -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit" 