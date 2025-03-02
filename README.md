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
git clone https://github.com/your-username/kp-astrology-dashboard.git
cd kp-astrology-dashboard

# Install dependencies
pip install -r requirements.txt
```

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
- [ ] Calculate important aspects for user-defined timeframes
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
