# Astronomical Calculation Utilities

This directory contains utility functions for astronomical calculations used throughout the astrology application.

## Purpose

The astronomical utilities provide essential functions for planetary calculations, coordinate transformations, time conversions, and other astronomical operations needed for accurate astrological computations. These utilities form the mathematical foundation for the astrological calculations performed by the application.

## Key Components

### 1. Coordinate System Transformations

Functions for converting between different astronomical coordinate systems.

**Features:**
- Ecliptic to equatorial coordinate conversion
- Equatorial to horizontal coordinate conversion
- Geocentric to topocentric transformations
- Precession calculations
- Nutation corrections
- Proper motion handling

### 2. Time Conversion Utilities

Comprehensive time handling for astronomical calculations.

**Features:**
- Julian day calculation and conversion
- Local/UTC/Sidereal time conversions
- Delta T computation
- Ephemeris time conversion
- Time zone handling for observations
- Day/night determination

### 3. Angular Calculations

Utilities for working with astronomical angles and relationships.

**Features:**
- Angular distance between celestial objects
- Angular velocity calculations
- Aspect determination and orb calculation
- Phase angle computation
- Eclipse calculation helpers
- Planetary station determination (retrograde/direct)

### 4. Rising, Setting, and Transit Calculation

Functions for determining visibility and transit times.

**Features:**
- Rise and set time calculation
- Transit (culmination) time computation
- Heliacal rising and setting
- Visibility condition determination
- Twilight period calculation
- Day length computation

### 5. Planetary Position Helpers

Support functions for planetary position calculations.

**Features:**
- Phase calculation for Moon and planets
- Planetary speed determination
- Planetary station point calculation
- Parallax corrections
- Light-time corrections
- Aberration corrections

### 6. Astronomical Phenomena

Utilities for calculating special astronomical events.

**Features:**
- Solstice and equinox calculation
- Eclipse prediction helpers
- Planetary conjunction and opposition timing
- Lunar phase calculation
- Planetary ingress calculation
- Astronomical event finding

## Usage Examples

```python
from backend.utils.astronomical.coordinates import ecliptic_to_equatorial, equatorial_to_horizontal
from backend.utils.astronomical.time import julian_day, sidereal_time
from backend.utils.astronomical.angles import angular_distance, is_aspect_applying
from backend.utils.astronomical.visibility import calculate_rise_set

# Convert coordinates
ra, dec = ecliptic_to_equatorial(longitude=45.5, latitude=0.2, obliquity=23.4366)

# Calculate Julian day
jd = julian_day(year=2023, month=4, day=15, hour=12, minute=0, second=0)

# Calculate local sidereal time
lst = sidereal_time(jd=jd, longitude=77.2090)

# Calculate angular distance between two celestial points
dist = angular_distance(
    ra1=2.57, dec1=23.45,
    ra2=3.62, dec2=22.31
)

# Determine if an aspect is applying or separating
is_applying = is_aspect_applying(
    planet1_speed=0.98,
    planet2_speed=-0.12,
    aspect_angle=90.0,
    current_angle=87.5
)

# Calculate rise and set times for the Sun
rise_time, set_time = calculate_rise_set(
    jd=jd,
    body="Sun",
    latitude=28.6139,
    longitude=77.2090
)
```

## Mathematical Precision

The astronomical utilities prioritize computational accuracy:

1. Use double-precision floating point for all calculations
2. Implement proper handling of edge cases (poles, date line, etc.)
3. Apply appropriate corrections (aberration, nutation, etc.) where needed
4. Follow IAU standards for astronomical calculations
5. Validate against established astronomical references
6. Document precision limitations where applicable

## Performance Considerations

To ensure efficient computation:

1. Implement caching for expensive calculations
2. Use approximation methods where appropriate based on required precision
3. Optimize critical mathematical operations
4. Avoid redundant coordinate transformations
5. Implement batch calculation capabilities for multiple positions

## Testing

The astronomical utilities include comprehensive test coverage:

1. Unit tests comparing results against established ephemeris data
2. Validation against published astronomical algorithms
3. Edge case testing (polar regions, date line, etc.)
4. Precision testing for critical calculations
5. Regression tests for historically verified positions 