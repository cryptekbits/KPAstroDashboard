# <img src="resources/logo.png" width="500">

| Branch   | Version                                                                                | Status                                                                                                                                                                  | Python |
| :------- | :------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----- |
| `master` | ![version](https://img.shields.io/badge/version-1.8.0-green) | [![build](https://github.com/cryptekbits/KPAstroDashboard/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/cryptekbits/KPAstroDashboard/actions/workflows/build.yml) | ![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg) |
| `develop` | ![version](https://img.shields.io/badge/version-1.8.0-green) | [![build](https://github.com/cryptekbits/KPAstroDashboard/actions/workflows/build.yml/badge.svg?branch=develop)](https://github.com/cryptekbits/KPAstroDashboard/actions/workflows/build.yml) | ![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg) |

# KP Astrology Dashboard

A high-precision Krishnamurti Paddhati (KP) astrology calculator with convenient UI and Excel export functionality.

## Overview

This project implements a KP (Krishnamurti Paddhati) Astrology Dashboard that generates accurate horary charts with precise sub-lord divisions. The application was built to address limitations in existing KP astrology platforms that often have poor design, paywalls, or present data in difficult-to-read formats.

The dashboard provides detailed astrological calculations with high precision for personal use and calculations, specifically designed for serious practitioners who need reliable KP Nanchang data.

## Features

- **Horary Chart Generation**: Calculate precise horary charts based on horary numbers and exact ascendant timing
- **Multiple Ayanamsa Support**: Includes various ayanamsa options (Krishnamurti, Lahiri, Raman, Yukteshwar, etc.)
- **Sub-Lord Calculations**: High-precision sub-lord divisions based on KP astrology principles
- **Vedic Horoscope Integration**: Comprehensive Vedic astrological data integrated with KP system
- **Excel Export**: Clean data export to Excel for better readability and analysis
- **Utility Functions**: Conversion utilities for degrees, minutes, seconds, dates and time calculations
- **Swiss Ephemeris Integration**: Uses the Swiss Ephemeris for accurate planetary positions
- **Automatic Updates**: The application checks for updates on startup and can download and install new versions automatically

## Technical Details

The application is built with Python and uses the following key components:

- **Swiss Ephemeris (pyswisseph)**: For accurate planetary calculations
- **Polars**: For efficient data manipulation
- **DateTime & DateUtil**: For precise date-time handling
- **Custom KP Sub-Lord Divisions**: Preloaded from KP_SL_Divisions.csv for accurate subdivision calculations

## Installation

```bash
# Clone the repository
git clone https://github.com/cryptekbits/KPAstroDashboard.git
cd KPAstroDashboard

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Dependencies

The application requires the following key dependencies:

- Python 3.13.2 or higher
- pyswisseph 2.10.3.2 or higher (Swiss Ephemeris library)
- PyQt5 5.15.0 or higher (GUI framework)
- polars-lts-cpu 1.23.0 or higher (Data processing)
- Other dependencies as listed in requirements.txt

## Building from Source

The application can be built into standalone executables for Windows and macOS:

### Windows Build (using py2exe)

```bash
# Install dependencies
pip install -r requirements.txt

# Create a Windows executable
python build_win.py --clean
```

The Windows executable will be created in the `dist` directory and copied to `release_artifacts`.

### macOS Build (using py2app)

```bash
# Install dependencies
pip install -r requirements.txt

# Create a macOS application bundle
python build_mac.py clean py2app
```

The macOS application bundle will be created in the `dist` directory and copied to `release_artifacts`.

### Build Process and Releases

Our build process follows these rules:

1. **Development builds:** The `develop` branch is automatically built when changes are pushed to it, but no release is created.
2. **Production builds:** The `master` branch is only built when a tag is pushed (e.g., `v1.2.0`).
3. **Releases:** GitHub releases are automatically created when:
   - A tag is pushed to the repository
   - A manual build is triggered via GitHub Actions UI (except for develop branch)

To create a release:
```bash
# Tag the commit
git tag v1.2.0
# Push the tag
git push origin v1.2.0
```

This will trigger a build and automatically create a release with Windows and macOS executables.

## Building Windows Executable

To build a Windows executable using PyInstaller, follow these steps:

1. Install PyInstaller and all dependencies:
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. Run the build script:
   ```
   python tools/build_windows_exe.py
   ```

   This will create a standalone executable in the `dist` directory.

3. For a single-file executable, use the `--onefile` option:
   ```
   python tools/build_windows_exe.py --onefile
   ```

4. For debugging build issues, use the `--debug` option:
   ```
   python tools/build_windows_exe.py --debug
   ```

The executable will be created in the `dist` directory with the name `KPAstrologyDashboard-{VERSION}.exe`.

### Automatic Builds

Windows executables are automatically built by GitHub Actions when a new release is created. The executable is included in the GitHub release assets.

To create a new release with the Windows executable:

1. Run the release creation script:
   ```
   python tools/create_release.py
   ```

2. Follow the prompts to create a new release.

3. The GitHub Actions workflow will build the Windows executable and add it to the release.

## Usage

```python
from horary_chart import find_exact_ascendant_time

# Example: Generate a horary chart for the given parameters
year = 2024
month = 2
day = 5
horary_number = 34
latitude, longitude, utc = 11.020085773931049, 76.98319647719487, "+5:30"  # Coimbatore
ayanamsa = "Krishnamurti"

# Get the exact time when ascendant matches the horary number's degree
matched_time, houses_chart, houses_data = find_exact_ascendant_time(
    year, month, day, utc, latitude, longitude, horary_number, ayanamsa
)

# Display the houses data
print(houses_data)
```

## Project Roadmap

- [x] Basic horary chart calculation with precise sub-lord divisions
- [x] Multiple ayanamsa support
- [x] Excel export functionality
- [ ] Build into a deployable web app (Heroku/PythonAnywhere)
- [ ] Add dynamically updating Excel and webapp
- [x] Calculate important aspects for user-defined timeframes
- [ ] Implement Kundli charting as per Lahiri ayanamsa
- [ ] Draw inferences of astrological data for financial markets
- [ ] Find correlations between planets, signs, houses, and Nakshatras with financial data
- [ ] Predict major market moves for commodities, currency, and equities based on correlations

## Dependencies

- polars
- swisseph (pyswisseph)
- prettytable
- python-dateutil
- datetime

## Contribution

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Acknowledgements

- Thanks to Swiss Ephemeris for providing accurate astronomical data
- Thanks to the KP astrology community for documentation on sub-lord divisions

## Building the Application

### Prerequisites

- Python 3.13.2 or higher
- PyQt5
- Required Python packages (see requirements.txt)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Building the Application

```bash
# Build for the current platform
python build.py --clean

# Build for all supported platforms (requires Docker)
python build.py --clean --all-platforms
```

## Cross-Compilation Issues

When cross-compiling the application (especially on Apple Silicon Macs), you might encounter issues with certain dependencies:

### Common Issues:

1. **PyQt5 Installation**: PyQt5 requires Qt libraries to be installed on the system.
2. **Native Extensions**: Packages like `pyswisseph` require a C compiler and appropriate build tools.
3. **Platform-specific Packages**: Some packages like `polars` and `numpy` may have issues when cross-compiled.

### Solutions:

1. **Install Build Tools**: 
   - Windows: Install Microsoft Visual C++ Build Tools
   - macOS: Install Xcode Command Line Tools (`xcode-select --install`)
   - Linux: Install build-essential package (`apt install build-essential`)

2. **Use Docker with Proper Dependencies**: 
   ```bash
   python build.py --clean --target-platform windows --target-arch x64 --alt-win-image
   ```

3. **Build on Native Platforms**: For best results, build each platform's executable on that platform:
   - Windows: Build on a Windows machine
   - Linux: Build on a Linux machine
   - macOS: Build on a Mac

## Latest Version

Current Version: 1.3.0 (Ephemeris Handling & UX Improvements Release)
Build Date: 2025-06-13

## Repository Information

- GitHub Repository: https://github.com/cryptekbits/KPAstroDashboard

## License

[License information here]

## System Requirements

- Windows 10/11 or macOS 12+
- Python 3.13.2 or higher
