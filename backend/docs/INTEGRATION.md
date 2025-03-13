# Integration Guide: flatlib and astro_engine

This document provides guidelines for integrating with the existing `flatlib` and `astro_engine` libraries in the astrology website backend.

## Overview

The backend leverages two primary libraries for astronomical and astrological calculations:

1. **flatlib**: Provides Sidereal calculations and basic astronomical operations
2. **astro_engine**: Implements core astrological computation algorithms

## flatlib Integration

### Library Structure

The `flatlib` library provides the following key components:

- **flatlib.datetime**: Date and time handling for astrological calculations
- **flatlib.geopos**: Geographic position handling
- **flatlib.chart**: Chart generation and analysis
- **flatlib.object**: Base objects for astrological entities
- **flatlib.aspects**: Aspect calculations between planets
- **flatlib.dignities**: Planetary dignity calculations
- **flatlib.ephem**: Ephemeris data and calculations
- **flatlib.predictives**: Predictive technique implementations

### Usage Examples

```python
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

# Create date, time and location
date = Datetime('2023-01-01', '12:00', '+05:30')
pos = GeoPos(28.6139, 77.2090)

# Calculate chart
chart = Chart(date, pos)

# Access planets
sun = chart.getObject(const.SUN)
moon = chart.getObject(const.MOON)

# Access houses
asc = chart.getAngle(const.ASC)
house1 = chart.getHouse(1)

# Get aspects
aspects = chart.aspects()
```

### Extension Guidelines

When extending or integrating with `flatlib`:

1. Use composition over inheritance where possible
2. Respect the existing flatlib API conventions
3. Maintain the separation between astronomical and astrological concerns
4. Handle exceptions appropriately
5. Document any deviations from standard flatlib behavior

## astro_engine Integration

### Library Structure

The `astro_engine` library provides these main components:

- **astro_engine.core**: Core calculation engine
- **astro_engine.utils**: Utility functions
- **astro_engine.data**: Data models and reference data
- **astro_engine.horary**: Horary astrology calculations

### Usage Examples

```python
from astro_engine.core import calculate_chart
from astro_engine.core import calculate_divisional_chart
from astro_engine.utils import get_nakshatra, get_ayanamsha

# Calculate ayanamsha
ayanamsha = get_ayanamsha('lahiri', date)

# Calculate a chart
chart = calculate_chart(date, lat, lng, ayanamsha='lahiri')

# Access chart data
ascendant = chart['ascendant']
planets = chart['planets']

# Calculate divisional chart
d9_chart = calculate_divisional_chart(chart, 9)  # Navamsa
```

### Extension Guidelines

When extending or integrating with `astro_engine`:

1. Use the provided factory methods rather than instantiating internal classes directly
2. Respect the input/output contracts of functions
3. Prefer using the highest-level APIs available
4. Add appropriate error handling for edge cases
5. Document dependencies on specific `astro_engine` features

## Integration Architecture

### Layer Approach

When building the backend, follow this layered approach to integration:

1. **Core Calculation Layer**: Direct interface with `flatlib` and `astro_engine`
2. **Domain Logic Layer**: Implements astrological systems and interpretations 
3. **Service Layer**: Orchestrates calculations and transforms results
4. **API Layer**: Exposes functionality through well-defined endpoints

### Integration Patterns

Use these patterns for effective integration:

1. **Adapter Pattern**: Create adapters to normalize interfaces between libraries
2. **Facade Pattern**: Provide simplified interfaces to complex functionality
3. **Strategy Pattern**: Allow swapping calculation methods when needed
4. **Factory Pattern**: Create objects without exposing creation logic

## Best Practices

1. **Caching**: Cache expensive calculations, especially planetary positions
2. **Error Handling**: Implement comprehensive error handling for calculation edge cases
3. **Validation**: Validate all inputs before passing to calculation libraries
4. **Testing**: Create tests that verify correct integration with the libraries
5. **Documentation**: Document assumptions and dependencies clearly
6. **Version Compatibility**: Document the compatible versions of each library

## Common Integration Challenges

1. **Different Ayanamsha Systems**: Ensure consistent ayanamsha usage across libraries
2. **House System Differences**: Be explicit about which house system is being used
3. **Degree Precision**: Handle degree precision consistently (avoid floating point issues)
4. **Time Zone Handling**: Ensure proper timezone conversion and UTC consistency
5. **Location Precision**: Handle geographic coordinates with appropriate precision

## Performance Considerations

1. **Ephemeris Calculations**: Planet position calculations are expensive - cache results
2. **Multiple Chart Calculations**: Reuse intermediate results when calculating multiple charts
3. **Divisional Chart Optimization**: Calculate only required divisional charts
4. **Parallel Processing**: Consider parallel processing for independent calculations
5. **Memory Management**: Be mindful of memory usage with large calculation sets 