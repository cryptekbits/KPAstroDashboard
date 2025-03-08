#!/bin/bash

echo "KP Astrology Dashboard - macOS Installation Script"
echo "=================================================="
echo

# Set version and GitHub repo information
VERSION="##VERSION##"
REPO_OWNER="cryptekbits"
REPO_NAME="KPAstroDashboard"
DOWNLOAD_URL="https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/tags/v$VERSION.zip"
INSTALL_DIR="$HOME/KPAstrologyDashboard"
REQUIRED_PYTHON_VERSION="3.13.2"

# Create installation directory
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Download the release zip
echo
echo "Downloading KP Astrology Dashboard v$VERSION..."
echo "URL: $DOWNLOAD_URL"

# Check if curl is available
if command -v curl &> /dev/null; then
    curl -L "$DOWNLOAD_URL" -o "/tmp/KPAstrologyDashboard.zip"
else
    # Fallback to wget if curl is not available
    if command -v wget &> /dev/null; then
        wget -O "/tmp/KPAstrologyDashboard.zip" "$DOWNLOAD_URL"
    else
        echo "Error: Neither curl nor wget is available. Please install either one and try again."
        exit 1
    fi
fi

if [ $? -ne 0 ]; then
    echo "Failed to download the application package."
    echo "Please check your internet connection and try again."
    exit 1
fi

# Extract the zip file to a temporary location
echo
echo "Extracting files..."
TEMP_EXTRACT_DIR="/tmp/KPAstrologyDashboard-extract"
mkdir -p "$TEMP_EXTRACT_DIR"
unzip -o "/tmp/KPAstrologyDashboard.zip" -d "$TEMP_EXTRACT_DIR"

if [ $? -ne 0 ]; then
    echo "Failed to extract the application package."
    exit 1
fi

# Move files from the nested directory (GitHub creates a versioned folder)
echo
echo "Moving files to installation directory..."
# Find the extracted folder (it will be KPAstroDashboard-VERSION)
EXTRACTED_DIR=$(find "$TEMP_EXTRACT_DIR" -maxdepth 1 -type d | grep -v "^$TEMP_EXTRACT_DIR$" | head -n 1)
if [ -n "$EXTRACTED_DIR" ]; then
    cp -R "$EXTRACTED_DIR/"* "$INSTALL_DIR/"
else
    echo "Could not find extracted directory. Installation may be incomplete."
    exit 1
fi

# Delete the temporary files
echo "Cleaning up temporary files..."
rm "/tmp/KPAstrologyDashboard.zip"
rm -rf "$TEMP_EXTRACT_DIR"

# Change to the installation directory
cd "$INSTALL_DIR"

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to compare version numbers
version_compare() {
    # $1 = version1, $2 = version2
    # Returns 0 if version1 >= version2, 1 otherwise
    if [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]; then
        return 0
    else
        return 1
    fi
}

# Check if Python is installed and meets the required version
echo
echo "Checking Python installation..."
PYTHON_INSTALLED=false
PYTHON_NEEDS_UPGRADE=false

if command_exists python3; then
    PYTHON_INSTALLED=true
    CURRENT_PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "Found Python $CURRENT_PYTHON_VERSION"
    
    if version_compare "$CURRENT_PYTHON_VERSION" "$REQUIRED_PYTHON_VERSION"; then
        echo "Python version $CURRENT_PYTHON_VERSION meets the requirement (>= $REQUIRED_PYTHON_VERSION)"
    else
        echo "Python version $CURRENT_PYTHON_VERSION is older than required version $REQUIRED_PYTHON_VERSION"
        PYTHON_NEEDS_UPGRADE=true
    fi
fi

# Install or upgrade Python if needed
if [ "$PYTHON_INSTALLED" = false ] || [ "$PYTHON_NEEDS_UPGRADE" = true ]; then
    echo "Installing/Upgrading Python to version $REQUIRED_PYTHON_VERSION..."
    
    # Check if Homebrew is installed
    if ! command_exists brew; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        if [ $? -ne 0 ]; then
            echo "Failed to install Homebrew."
            echo "Please install Homebrew manually from https://brew.sh"
            echo "Then install Python $REQUIRED_PYTHON_VERSION using 'brew install python@3.13'"
            exit 1
        fi
        
        # Add Homebrew to PATH for the current session
        eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null)"
    fi
    
    # Install/upgrade Python
    echo "Installing/Upgrading Python $REQUIRED_PYTHON_VERSION using Homebrew..."
    brew update
    brew install python@3.13
    
    if [ $? -ne 0 ]; then
        echo "Failed to install Python $REQUIRED_PYTHON_VERSION."
        echo "Please install Python $REQUIRED_PYTHON_VERSION or later manually using 'brew install python@3.13'"
        exit 1
    fi
    
    # Ensure python3 command is available
    if ! command_exists python3; then
        echo "Python 3 installation failed."
        echo "Please install Python $REQUIRED_PYTHON_VERSION or later manually."
        exit 1
    fi
    
    # Verify the installed version
    INSTALLED_PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "Python $INSTALLED_PYTHON_VERSION installed successfully."
else
    echo "Python $CURRENT_PYTHON_VERSION is already installed and meets requirements."
fi

# Install required packages
echo
echo "Installing required packages..."
python3 -m pip install --upgrade pip

# Check for and uninstall existing flatlib
echo "Checking for existing flatlib installation..."
python3 -m pip show flatlib 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Removing existing flatlib installation..."
    python3 -m pip uninstall -y flatlib
    echo "Flatlib removed successfully."
else
    echo "Flatlib not found."
fi

# Install pyswisseph directly from PyPI
echo "Installing pyswisseph from PyPI..."
python3 -m pip install pyswisseph>=2.10.3.2
if [ $? -ne 0 ]; then
    echo "Failed to install pyswisseph from PyPI."
    echo "This may be due to missing build tools."
    echo "Please ensure you have Xcode Command Line Tools installed."
    echo "You can install them by running: xcode-select --install"
    exit 1
fi
echo "Pyswisseph installed successfully."

# Now install requirements
echo "Installing required packages from requirements.txt..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install required packages."
    exit 1
fi

# Setup Swiss Ephemeris files - use test script to check if they work correctly first
echo
echo "Testing Swiss Ephemeris functionality..."
SWEFILES_DIR="$INSTALL_DIR/flatlib/resources/swefiles"
SYSTEM_SWEFILES_DIR="/usr/local/share/sweph/ephe"

# Check if source directory exists
if [ ! -d "$SWEFILES_DIR" ]; then
    echo "Error: Swiss Ephemeris files directory not found at $SWEFILES_DIR"
    echo "Please ensure the application is installed correctly."
    exit 1
fi

# Required files
REQUIRED_FILES=("seas_18.se1" "sepl_18.se1" "semo_18.se1" "fixstars.cat")

# Check for required files
echo "Checking for required ephemeris files..."
MISSING_FILES=false

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$SWEFILES_DIR/$file" ]; then
        echo "Missing: $file"
        MISSING_FILES=true
    else
        echo "Found: $file"
    fi
done

# Handle missing files
if [ "$MISSING_FILES" = true ]; then
    echo
    echo "Some required Swiss Ephemeris files are missing from the source directory."
    echo "Please ensure the application package is complete."
    exit 1
else
    echo "All required ephemeris files are present in the application directory."
fi

# Create a quick Python test script to verify Swiss Ephemeris functionality
cat > "$INSTALL_DIR/test_swisseph.py" << 'EOL'
import os
import sys

def test_swisseph_functionality():
    """Test if Swiss Ephemeris works correctly"""
    try:
        import swisseph
        import flatlib
        from flatlib.ephem import setPath
        
        # Use only built-in path for swefiles
        app_dir = os.path.dirname(os.path.abspath(__file__))
        swefiles_path = os.path.join(app_dir, 'flatlib', 'resources', 'swefiles')
        
        # Normalize path for Windows
        normalized_path = swefiles_path.replace('\\', '/')
        
        # Set path
        setPath(normalized_path)
        
        # Test calculation
        test_jd = 2459000.5  # A random Julian date
        test_result = swisseph.calc_ut(test_jd, 0, 2)  # Calculate Sun position
        
        print(f"SwissEph test successful: {test_result}")
        return True
    except Exception as e:
        print(f"SwissEph test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_swisseph_functionality()
    sys.exit(0 if success else 1)
EOL

# Make test script executable
chmod +x "$INSTALL_DIR/test_swisseph.py"

# Run the test script
echo "Running Swiss Ephemeris test..."
python3 "$INSTALL_DIR/test_swisseph.py"
SWISSEPH_TEST_RESULT=$?

# Only proceed with system-wide setup if the test failed
if [ $SWISSEPH_TEST_RESULT -ne 0 ]; then
    echo
    echo "Swiss Ephemeris test failed. Checking system-wide configuration..."
    
    # Check if system-wide Swiss Ephemeris directory exists
    if [ ! -d "$SYSTEM_SWEFILES_DIR" ]; then
        echo "System-wide Swiss Ephemeris directory not found."
        echo "Would you like to create it and copy the ephemeris files? (Y/N)"
        echo "This will require administrator privileges."
        read -p "Your choice: " SYSTEM_CHOICE
        
        if [[ "$SYSTEM_CHOICE" =~ ^[Yy]$ ]]; then
            # Create a temporary script for admin privileges
            ADMIN_SCRIPT="/tmp/sweadmin.sh"
            
            echo "#!/bin/bash" > "$ADMIN_SCRIPT"
            echo "echo Creating system-wide Swiss Ephemeris directory..." >> "$ADMIN_SCRIPT"
            echo "mkdir -p \"$SYSTEM_SWEFILES_DIR\"" >> "$ADMIN_SCRIPT"
            echo "echo Copying ephemeris files..." >> "$ADMIN_SCRIPT"
            
            for file in "${REQUIRED_FILES[@]}"; do
                echo "if [ -f \"$SWEFILES_DIR/$file\" ]; then cp \"$SWEFILES_DIR/$file\" \"$SYSTEM_SWEFILES_DIR/$file\"; fi" >> "$ADMIN_SCRIPT"
            done
            
            echo "echo" >> "$ADMIN_SCRIPT"
            echo "echo System-wide Swiss Ephemeris files setup complete." >> "$ADMIN_SCRIPT"
            echo "chmod -R 755 \"$SYSTEM_SWEFILES_DIR\"" >> "$ADMIN_SCRIPT"
            
            # Make the script executable
            chmod +x "$ADMIN_SCRIPT"
            
            # Run with sudo
            echo "Requesting administrator privileges..."
            sudo "$ADMIN_SCRIPT"
            
            # Clean up
            rm "$ADMIN_SCRIPT"
        else
            echo "Skipping system-wide Swiss Ephemeris setup."
        fi
    else
        # Check if files exist in the system directory
        SYSTEM_MISSING_FILES=false
        for file in "${REQUIRED_FILES[@]}"; do
            if [ ! -f "$SYSTEM_SWEFILES_DIR/$file" ]; then
                SYSTEM_MISSING_FILES=true
                break
            fi
        done
        
        if [ "$SYSTEM_MISSING_FILES" = true ]; then
            echo "System-wide Swiss Ephemeris directory exists but some files are missing."
            echo "Would you like to update the ephemeris files? (Y/N)"
            read -p "Your choice: " UPDATE_CHOICE
            
            if [[ "$UPDATE_CHOICE" =~ ^[Yy]$ ]]; then
                # Create a temporary script for admin privileges
                ADMIN_SCRIPT="/tmp/sweadmin.sh"
                
                echo "#!/bin/bash" > "$ADMIN_SCRIPT"
                echo "echo Updating system-wide Swiss Ephemeris files..." >> "$ADMIN_SCRIPT"
                
                for file in "${REQUIRED_FILES[@]}"; do
                    echo "if [ -f \"$SWEFILES_DIR/$file\" ]; then cp \"$SWEFILES_DIR/$file\" \"$SYSTEM_SWEFILES_DIR/$file\"; fi" >> "$ADMIN_SCRIPT"
                done
                
                echo "echo" >> "$ADMIN_SCRIPT"
                echo "echo System-wide Swiss Ephemeris files update complete." >> "$ADMIN_SCRIPT"
                echo "chmod -R 755 \"$SYSTEM_SWEFILES_DIR\"" >> "$ADMIN_SCRIPT"
                
                # Make the script executable
                chmod +x "$ADMIN_SCRIPT"
                
                # Run with sudo
                echo "Requesting administrator privileges..."
                sudo "$ADMIN_SCRIPT"
                
                # Clean up
                rm "$ADMIN_SCRIPT"
            else
                echo "Skipping system-wide Swiss Ephemeris update."
            fi
        else
            echo "System-wide Swiss Ephemeris directory exists with all required files."
            echo "No actions needed."
        fi
    fi
    
    # Run the test script again to verify
    echo
    echo "Running Swiss Ephemeris test again after system-wide setup..."
    python3 "$INSTALL_DIR/test_swisseph.py"
    RETEST_RESULT=$?
    
    if [ $RETEST_RESULT -eq 0 ]; then
        echo "Swiss Ephemeris now working correctly!"
    else
        echo "Warning: Swiss Ephemeris still not working correctly. You may encounter issues with the application."
    fi
else
    echo "Swiss Ephemeris test successful! No system-wide setup needed."
fi

# Clean up the test script
rm "$INSTALL_DIR/test_swisseph.py"

# Create desktop shortcut with icon
echo
echo "Creating desktop shortcut..."
DESKTOP_DIR="$HOME/Desktop"
APP_DIR="$INSTALL_DIR"
SHORTCUT="$DESKTOP_DIR/KPAstrologyDashboard.command"
ICON_PATH="$APP_DIR/resources/favicon.ico"

# Create executable shell script with reference to the icon
cat > "$SHORTCUT" << EOL
#!/bin/bash
# KP Astrology Dashboard Launcher
# Icon: $ICON_PATH
cd "$APP_DIR"
python3 main.py
EOL

# Make it executable
chmod +x "$SHORTCUT"

# Try to set custom icon if possible
if command_exists sips && command_exists iconutil; then
    echo "Setting up custom icon for the shortcut..."
    ICON_DIR="/tmp/KPAstrologyIcon.iconset"
    mkdir -p "$ICON_DIR"
    
    # Convert ico to png if needed
    if [[ "$ICON_PATH" == *.ico ]]; then
        if command_exists convert; then
            convert "$ICON_PATH" "/tmp/app_icon.png"
            ICON_PATH="/tmp/app_icon.png"
        else
            echo "ImageMagick not found, skipping icon conversion."
        fi
    fi
    
    # Only proceed if we have a png
    if [[ -f "$ICON_PATH" && "$ICON_PATH" == *.png ]]; then
        # Create iconset
        sips -z 16 16 "$ICON_PATH" --out "${ICON_DIR}/icon_16x16.png" &>/dev/null
        sips -z 32 32 "$ICON_PATH" --out "${ICON_DIR}/icon_32x32.png" &>/dev/null
        sips -z 128 128 "$ICON_PATH" --out "${ICON_DIR}/icon_128x128.png" &>/dev/null
        sips -z 256 256 "$ICON_PATH" --out "${ICON_DIR}/icon_256x256.png" &>/dev/null
        sips -z 512 512 "$ICON_PATH" --out "${ICON_DIR}/icon_512x512.png" &>/dev/null
        
        # Convert iconset to icns
        iconutil -c icns "$ICON_DIR" -o "/tmp/AppIcon.icns"
        
        # Use AppleScript to set the custom icon
        if [ -f "/tmp/AppIcon.icns" ]; then
            osascript << EOF
tell application "Finder"
    set file_path to POSIX file "$SHORTCUT" as alias
    set icon_path to POSIX file "/tmp/AppIcon.icns" as alias
    set icon of file_path to icon of icon_path
end tell
EOF
            # Clean up
            rm -rf "$ICON_DIR" "/tmp/AppIcon.icns" "/tmp/app_icon.png" 2>/dev/null
        fi
    fi
fi

echo
echo "Installation completed successfully!"
echo "KP Astrology Dashboard has been installed to: $INSTALL_DIR"
echo "You can now run KP Astrology Dashboard from your desktop."
echo 