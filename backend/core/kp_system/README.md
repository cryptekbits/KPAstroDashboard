# KP System Core Component

This directory contains the core calculation components for Krishnamurti Paddhati (KP System) of Vedic astrology.

## Overview

Krishnamurti Paddhati, often referred to as the KP System, is a modern approach to Vedic astrology developed by K.S. Krishnamurti. It combines traditional Vedic astrology with Western techniques, emphasizing the use of sub-lords, stellar positions, and the 249 sub-sub divisions of the zodiac. This module implements the specialized calculations, analysis, and predictive techniques of the KP System.

## Key Components

### 1. KP Ayanamsa and Coordinates

Implementation of the specific ayanamsa and coordinate system used in KP.

**Implementation Requirements:**
- Calculate precise KP ayanamsa (Krishnamurti ayanamsa)
- Implement KP-specific zodiacal calculations
- Convert between standard astronomical coordinates and KP positions
- Support accurate planetary longitude calculations per KP standards
- Calculate precise cuspal positions according to KP system
- Implement advanced KP ephemeris integration

### 2. Sub-Lord Calculator

Implementation of the comprehensive sub-lord system that forms the foundation of KP.

**Implementation Requirements:**
- Calculate precise position of planets in KP star and sub divisions
- Determine Nakshatra (constellation), sub, and sub-sub lords for all planets
- Calculate cuspal sub-lords for all house cusps
- Implement the 249-point sub-division system
- Calculate lordship strengths and relationships
- Support various sub-division levels for detailed analysis

### 3. Stellar-Based Ruling Periods

Implementation of the specialized dasha systems used in KP.

**Implementation Requirements:**
- Calculate KP-specific vimshottari dasha sequence
- Determine current and future stellar ruling periods
- Calculate sub and sub-sub periods with precise timing
- Implement KP-specific timing prediction algorithms
- Calculate significator periods and important transits
- Support customizable ruling period settings

### 4. Significator System

Implementation of the significator determination system unique to KP.

**Implementation Requirements:**
- Calculate house significators (primary, secondary, and tertiary)
- Determine planet significators for various life areas
- Implement ruling planets determination algorithm
- Calculate strength of significators for predictive work
- Determine positive and negative significator influences
- Support compound significator assessment

### 5. KP Aspects and Relationships

Implementation of the specialized aspect system used in KP.

**Implementation Requirements:**
- Calculate conjunctions based on KP star-based approach
- Determine stellar aspects between planets
- Implement KP-specific aspect strength calculation
- Calculate sublord relationship influences
- Support both traditional and KP-specific aspect analysis
- Implement aspect strength and influence calculation

### 6. Predictive Algorithms

Implementation of KP's precise predictive techniques.

**Implementation Requirements:**
- Calculate event timing using ruling planets and transits
- Implement the "ruling planets" predictive technique
- Determine favorable and unfavorable periods
- Calculate results of sublord positions during transits
- Implement sublord-based predictive algorithms
- Support directional (cusp-based) predictive calculations

### 7. KP Horary System

Implementation of KP's specialized horary (prashna) system.

**Implementation Requirements:**
- Calculate horary chart based on KP number selection
- Implement ruling planet determination for query time
- Calculate significators for specific question types
- Determine answer potentials based on sublord positions
- Implement timing predictions for horary questions
- Support various question categories and interpretation frameworks

## Technical Requirements

### Performance Considerations
- Optimize sub-lord calculations for speed
- Implement caching system for frequently accessed calculations
- Use efficient algorithms for 249-point subdivisions
- Consider parallel processing for complex significator calculations

### Accuracy & Validation
- Ensure perfect alignment with KP calculation methods
- Validate against published KP examples
- Test against charts with known predictions
- Implement comprehensive error checking
- Ensure precision to the required decimal places for subdivisions

### Integration Points
- Interface with basic astronomical calculation modules
- Integration with custom KP ephemeris data
- Connection to interpretation and prediction systems
- API support for frontend visualization of KP charts
- Integration with transit calculation modules

## Usage Examples

```python
# Example (conceptual): Calculating KP details for a chart
from backend.core.kp_system import KPCalculator
from backend.core.chart import BirthChart

# Create a birth chart instance
chart = BirthChart(datetime="1990-01-01T12:00:00", latitude=28.6139, 
                  longitude=77.2090, timezone="Asia/Kolkata")

# Initialize the KP calculator
kp = KPCalculator(chart)

# Get star and sublord positions for planets
planet_positions = kp.get_planet_stellar_positions()
for planet, data in planet_positions.items():
    print(f"{planet}: Star: {data.star}, Sublord: {data.sublord}, Sub-sublord: {data.sub_sublord}")

# Get cusp sublords
cusp_sublords = kp.get_cusp_sublords()
for cusp, sublord in cusp_sublords.items():
    print(f"Cusp {cusp}: Sublord: {sublord}")

# Get significators for a specific house
house = 7  # Relationships
significators = kp.get_house_significators(house)
print(f"House {house} Significators:")
print(f"Primary: {significators.primary}")
print(f"Secondary: {significators.secondary}")
print(f"Tertiary: {significators.tertiary}")

# Predict timing for a specific event
event_type = "marriage"
timing = kp.predict_event_timing(event_type)
print(f"Predicted timing for {event_type}: {timing.start_date} to {timing.end_date}")
print(f"Peak period: {timing.peak_date}")
print(f"Ruling planets: {timing.ruling_planets}")
```

## Visualization Support

Implementation for generating visual representations of:

1. KP chart with star and sublord positions
2. Significator tables for houses and planets
3. Ruling planet diagrams
4. Sub-division tables and maps
5. Predictive timeline visualizations

## Testing Strategy

Implement comprehensive testing with:

1. Unit tests for sub-lord and star position calculations
2. Integration tests for significator determination
3. Validation tests against published KP chart examples
4. Event prediction testing with historical data
5. Performance benchmarking for optimization

## References

List of authoritative texts for KP system:

1. K.S. Krishnamurti's original works
2. Advanced Predictive Techniques of Krishnamurti Paddhati
3. KP Reader series
4. KP Stellar Astrology publications
5. KP & Astrology periodicals

## Future Enhancements

1. Integration with machine learning for significator pattern recognition
2. Enhanced event timing prediction with multi-factor analysis
3. Comprehensive KP horary module with expanded question types
4. Advanced sublord relationship analysis for compatibility
5. Research module for testing and refining KP principles with large datasets 