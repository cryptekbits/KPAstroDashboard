# Basic Details Core Component

This directory contains the core calculation components for fundamental astrological calculations and chart generation.

## Overview

The Basic Details module handles the foundational calculations necessary for all astrological analysis, including planetary positions, house systems, aspects, and essential chart details. This module serves as the basis upon which all other astrological calculations and interpretations are built.

## Key Components

### 1. Planetary Position Calculator

Accurate calculation of planetary positions for any given time and location.

**Implementation Requirements:**
- Calculate precise longitude, latitude, and declination for all planets
- Support high-precision ephemeris data (Swiss Ephemeris integration)
- Calculate retrograde status and speed
- Determine zodiacal positions with precise degrees, minutes, and seconds
- Support both tropical and sidereal zodiacs with various ayanamsa options
- Calculate planetary stations (direct/retrograde transition points)

### 2. House System Calculator

Implementation of various house systems for horoscope division.

**Implementation Requirements:**
- Support all major house systems (Placidus, Koch, Equal, Whole Sign, Porphyry, Regiomontanus, Campanus, etc.)
- Calculate precise house cusps and degrees
- Determine planetary house placements
- Support specialized Vedic house systems
- Calculate house strengths and significance
- Provide house lordship determination

### 3. Aspect Calculator

Calculation of planetary aspects and aspect patterns.

**Implementation Requirements:**
- Calculate all standard aspects (conjunction, opposition, trine, square, sextile)
- Support minor aspects (semi-sextile, quincunx, etc.)
- Determine aspect orbs and exact/applying/separating status
- Calculate aspect strengths and significances
- Identify major aspect patterns (Grand Trine, T-Square, etc.)
- Support specialized Vedic aspect systems

### 4. Ascendant and Angular Points

Calculation of the Ascendant and other key chart points.

**Implementation Requirements:**
- Calculate precise Ascendant degree
- Determine Midheaven (MC), Descendant, and Imum Coeli (IC)
- Calculate additional points like Vertex, East Point, etc.
- Support various calculation methods for special points
- Calculate rising sign characteristics
- Determine Lagna Lord details

### 5. Lunar Calculation System

Specialized calculations for lunar factors.

**Implementation Requirements:**
- Calculate precise Moon position with nodal relationship
- Determine Nakshatra (lunar mansion) and pada (quarter)
- Calculate Tithi (lunar day) and Paksha (lunar phase)
- Determine Karana (half of lunar day)
- Calculate lunar Yogas (combinations)
- Support lunar-based timing systems

### 6. Chart Rectification Utilities

Tools to assist in birth time rectification.

**Implementation Requirements:**
- Calculate sensitive points for different birth times
- Implement event-based rectification algorithms
- Provide timing analysis for life events
- Support various rectification techniques
- Calculate probabilities for candidate birth times
- Implement reverse-engineering from known life events

### 7. Core Sign and Element Analysis

Basic analysis of zodiac signs and elements in a chart.

**Implementation Requirements:**
- Calculate distribution of planets across signs and elements
- Determine dominant signs, elements, modalities, and polarities
- Calculate elemental balances and imbalances
- Provide basic sign placement interpretations
- Determine planetary dignity and debility states
- Calculate dispositorship chains and mutual receptions

## Technical Requirements

### Performance Considerations
- Optimize astronomical calculations for speed and accuracy
- Implement caching system for ephemeris data
- Use efficient algorithms for coordinate system conversions
- Consider parallel processing for batch chart calculations

### Accuracy & Validation
- Ensure high precision in all astronomical calculations
- Validate against established ephemeris data
- Test against known chart examples
- Implement comprehensive error handling for edge cases
- Support leap seconds and calendar anomalies

### Integration Points
- Interface with Astro-Engine for astronomical calculations
- Provide foundation for all other module calculations
- Export standardized chart data structures
- Support various input and output formats
- Integration with time zone and location databases

## Usage Examples

```python
# Example (conceptual): Calculating basic chart details
from backend.core.basic_details import ChartCalculator
from datetime import datetime

# Initialize chart calculator with birth details
chart = ChartCalculator(
    datetime=datetime(1990, 1, 1, 12, 0, 0),
    latitude=28.6139,
    longitude=77.2090,
    timezone="Asia/Kolkata",
    house_system="Placidus",
    ayanamsa="Lahiri"
)

# Get planetary positions
planets = chart.get_planet_positions()
for planet, data in planets.items():
    print(f"{planet}: {data.sign} {data.degrees}° (Retrograde: {data.is_retrograde})")

# Get house cusps
houses = chart.get_house_cusps()
for house_num, details in houses.items():
    print(f"House {house_num}: {details.sign} {details.degrees}°")

# Get angular points
angles = chart.get_angular_points()
print(f"Ascendant: {angles.ascendant.sign} {angles.ascendant.degrees}°")
print(f"Midheaven: {angles.midheaven.sign} {angles.midheaven.degrees}°")

# Get aspects
aspects = chart.get_aspects()
for aspect in aspects:
    print(f"{aspect.planet1} {aspect.aspect_type} {aspect.planet2} (Orb: {aspect.orb}°)")

# Get lunar details
lunar = chart.get_lunar_details()
print(f"Nakshatra: {lunar.nakshatra} (Pada {lunar.pada})")
print(f"Tithi: {lunar.tithi}")
```

## Visualization Support

Implementation for generating visual representations of:

1. Birth chart wheels in various formats
2. Planetary position tables
3. Aspect grids and tables
4. Element and modality distributions
5. House system comparisons

## Testing Strategy

Implement comprehensive testing with:

1. Unit tests for individual calculation components
2. Integration tests for complete chart generation
3. Validation tests against published charts and ephemeris
4. Edge case testing for unusual chart configurations
5. Performance benchmarking for calculation optimization

## References

List of authoritative texts and resources:

1. Astronomical Algorithms by Jean Meeus
2. Swiss Ephemeris documentation
3. Brihat Parashara Hora Shastra
4. Standard astrological calculation references
5. IAU standards for astronomical calculations

## Future Enhancements

1. Integration with machine learning for pattern recognition
2. Support for exotic coordinate systems and house methods
3. Advanced rectification algorithms using multiple event correlations
4. Support for real-time astronomical data feeds
5. Enhanced astronomical phenomena detection (eclipses, occultations, etc.) 