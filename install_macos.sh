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
rm "/tmp/KPAstrologyDashboard.zip"
rm -rf "$TEMP_EXTRACT_DIR"

# Change to the installation directory
cd "$INSTALL_DIR"

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if Python 3.9+ is installed
echo
echo "Checking if Python is installed..."
if ! command_exists python3; then
    echo "Python 3 not found. Installing Python 3.9..."
    
    # Check if Homebrew is installed
    if ! command_exists brew; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        if [ $? -ne 0 ]; then
            echo "Failed to install Homebrew."
            echo "Please install Homebrew manually from https://brew.sh"
            echo "Then install Python 3.9 or later using 'brew install python@3.9'"
            exit 1
        fi
        
        # Add Homebrew to PATH for the current session
        eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null)"
    fi
    
    # Install Python 3.9
    echo "Installing Python 3.9 using Homebrew..."
    brew install python@3.9
    
    if [ $? -ne 0 ]; then
        echo "Failed to install Python 3.9."
        echo "Please install Python 3.9 or later manually using 'brew install python@3.9'"
        exit 1
    fi
    
    # Ensure python3 command is available
    if ! command_exists python3; then
        echo "Python 3 installation failed."
        echo "Please install Python 3.9 or later manually."
        exit 1
    fi
    
    echo "Python 3.9 installed successfully."
else
    echo "Python 3 is already installed."
fi

# Install required packages
echo
echo "Installing required packages..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install required packages."
    exit 1
fi

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