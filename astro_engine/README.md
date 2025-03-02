# Astro Engine

A Python module for Vedic and KP (Krishnamurti Paddhati) astrology calculations.

## Overview

Astro Engine provides tools and utilities for astrological calculations, including:

- Vedic horoscope data generation and analysis
- Horary chart calculations
- Astrological utilities for time and angle conversions

## Structure

The module is organized into the following components:

- `core.py`: Contains the main `VedicHoroscopeData` class for generating and analyzing Vedic horoscope data
- `horary.py`: Functions for horary chart calculations according to the KP system
- `utils.py`: Utility functions for working with astrological data
- `data/`: Directory containing data files used by the module

## Usage

```python
from astro_engine import VedicHoroscopeData, dms_to_decdeg
from astro_engine.horary import find_exact_ascendant_time, get_horary_ascendant_degree

# Create a VedicHoroscopeData object
vhd = VedicHoroscopeData(
    year=2023, month=5, day=15, 
    hour=12, minute=30, second=0, 
    utc="+5:30", 
    latitude=28.6139, longitude=77.2090, 
    ayanamsa="Krishnamurti", 
    house_system="Placidus"
)

# Generate a chart
chart = vhd.generate_chart()

# Get planets data
planets_data = vhd.get_planets_data_from_chart(chart)

# Get houses data
houses_data = vhd.get_houses_data_from_chart(chart)

# Get consolidated chart data
chart_data = vhd.get_consolidated_chart_data(planets_data, houses_data)

# Calculate planetary aspects
aspects = vhd.get_planetary_aspects(chart)

# Find exact ascendant time for a horary number
matched_time, houses_chart, houses_data = find_exact_ascendant_time(
    year=2023, month=5, day=15, 
    utc_offset="+5:30", 
    lat=28.6139, lon=77.2090, 
    horary_number=34, 
    ayanamsa="Krishnamurti"
)
```

## Dependencies

- flatlib
- polars
- swisseph
- dateutil

## License

This module is part of the KP Dashboard project. 