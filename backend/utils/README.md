# Utilities

This directory contains utility functions and helper modules used throughout the astrology application's backend.

## Overview

The utilities module provides common functionality, helper functions, and shared services that support the core calculation and API components. These utilities are designed to be reusable, well-tested, and optimized for their specific purposes.

## Key Components

### 1. Data Access Utilities

A set of functions for accessing and managing data files and resources.

**Functionality:**
- Standardized data file loading and caching
- Path resolution for various data directories
- Data format conversion and normalization
- Asynchronous data loading capabilities
- Memory-efficient data access for large datasets
- Version checking for data files

**Usage Example:**
```python
from backend.utils.data_access import load_json_data, get_data_path

# Load interpretation data
planet_interpretations = load_json_data('interpretations/planets.json')

# Get path to a specific data file
ephemeris_path = get_data_path('astronomical/ephemeris/jpl_2020.dat')
```

### 2. Astronomical Calculations

Helper functions for common astronomical calculations used across modules.

**Functionality:**
- Coordinate system conversions (ecliptic/equatorial/horizontal)
- Time conversions (local/UTC/sidereal/Julian day)
- Angular distance and aspect calculations
- Rise/set time calculations
- Phase calculations (lunar, planetary)
- Equation of time calculations

**Usage Example:**
```python
from backend.utils.astronomical import julian_day, sidereal_time, ecliptic_to_equatorial

# Calculate Julian day for a date
jd = julian_day(2023, 4, 15, 12, 0, 0)

# Calculate local sidereal time
lst = sidereal_time(jd, 77.2090)

# Convert ecliptic coordinates to equatorial
ra, dec = ecliptic_to_equatorial(lon=45.5, lat=0.2, obliquity=23.4366)
```

### 3. Formatting and Display

Utilities for formatting and displaying astrological data.

**Functionality:**
- Format degrees/minutes/seconds
- Generate proper astrological symbols
- Format dates in various astrological notations
- Chart data formatting for different output types
- Localization support for multiple languages
- Unit conversion utilities

**Usage Example:**
```python
from backend.utils.formatting import format_longitude, get_planet_symbol, format_aspect

# Format planetary longitude
formatted_position = format_longitude(128.456789)  # Returns "8°LE30'24""

# Get Unicode symbol for Jupiter
jupiter_symbol = get_planet_symbol('Jupiter')  # Returns "♃"

# Format an aspect
aspect_text = format_aspect('Sun', 'square', 'Saturn', 3.2)  # Returns "Sun □ Saturn (orb 3°12')"
```

### 4. Validation and Error Handling

Functions for input validation and standardized error handling.

**Functionality:**
- Chart data validation
- Location data validation
- Date and time validation
- Astrological parameter boundary checking
- Standardized error types and messages
- Exception handling utilities

**Usage Example:**
```python
from backend.utils.validation import validate_birth_data, is_valid_location

# Validate birth information
is_valid, errors = validate_birth_data(
    year=1990, month=1, day=1, 
    hour=12, minute=0, second=0,
    latitude=28.6139, longitude=77.2090
)

# Check if a location is valid
if not is_valid_location(latitude=91.5, longitude=77.2090):
    print("Invalid location coordinates")
```

### 5. Caching System

Performance optimization through intelligent caching.

**Functionality:**
- In-memory calculation result caching
- Persistent cache for expensive calculations
- Cache invalidation strategies
- Thread-safe caching mechanisms
- Memory usage management
- Cache statistics and monitoring

**Usage Example:**
```python
from backend.utils.caching import cached, clear_cache

# Define a cached function
@cached(ttl=3600)  # Cache for 1 hour
def expensive_calculation(param1, param2):
    # ... perform expensive calculation ...
    return result

# Clear specific cache
clear_cache('planetary_positions')
```

### 6. Logging and Monitoring

Utilities for application logging and performance monitoring.

**Functionality:**
- Standardized logging setup
- Performance timing decorators
- Memory usage tracking
- Critical error alerting
- Calculation accuracy monitoring
- Request/response logging

**Usage Example:**
```python
from backend.utils.logging import get_logger, timing

logger = get_logger(__name__)

# Log an information message
logger.info("Processing chart for user #12345")

# Time a function execution
@timing
def process_chart(chart_data):
    # ... process chart ...
    return result
```

### 7. API Helpers

Utilities specifically designed to support API functionality.

**Functionality:**
- Request parameter validation
- Response formatting
- Rate limiting utilities
- Authentication helpers
- Pagination support
- API version compatibility

**Usage Example:**
```python
from backend.utils.api_helpers import format_response, paginate_results

# Format a standard API response
response = format_response(
    status="success",
    data=chart_data,
    message="Chart calculated successfully"
)

# Paginate query results
paginated_data = paginate_results(
    items=all_predictions,
    page=2,
    items_per_page=10
)
```

### 8. Testing Utilities

Helper functions and fixtures for testing.

**Functionality:**
- Test data generators
- Mock chart data creation
- Assertion utilities for astrological data
- Performance testing helpers
- Test configuration management
- Comparison utilities for floating-point results

**Usage Example:**
```python
from backend.utils.testing import generate_test_chart, assert_positions_equal

# Generate a test chart
test_chart = generate_test_chart(
    year=1990,
    month=1,
    day=1,
    planets=['Sun', 'Moon', 'Mercury']
)

# Compare calculated positions with expected values
assert_positions_equal(
    calculated_positions,
    expected_positions,
    tolerance=0.001  # Allow small floating-point differences
)
```

### 9. Configuration Management

Utilities for managing application configuration.

**Functionality:**
- Configuration loading and validation
- Environment-specific settings
- Secure credential handling
- Dynamic configuration updates
- Configuration schema validation
- Default value management

**Usage Example:**
```python
from backend.utils.config import get_config, update_config

# Get configuration value
ephemeris_path = get_config('paths.ephemeris')

# Update configuration setting
update_config('calculation.precision', 'high')
```

### 10. Integration Utilities

Helper functions for integrating with external services and libraries.

**Functionality:**
- Swiss Ephemeris integration utilities
- API client helpers for external services
- Data conversion for third-party libraries
- Adapter patterns for external calculators
- Webhook handling utilities
- Synchronization helpers

**Usage Example:**
```python
from backend.utils.integration import swisseph_to_internal, call_external_api

# Convert Swiss Ephemeris result to internal format
planet_data = swisseph_to_internal(raw_se_result, planet='Mars')

# Call external timezone API
timezone_info = call_external_api(
    'timezone',
    params={'lat': 28.6139, 'lng': 77.2090}
)
```

## Coding Standards

All utility modules adhere to the following standards:

1. Comprehensive docstrings with parameter and return value documentation
2. Type hints for function parameters and return values
3. Proper error handling and meaningful error messages
4. Unit tests with high coverage
5. Performance considerations for frequently used functions
6. Thread-safety where appropriate

## Usage Guidelines

When using or contributing to utility functions:

1. Avoid duplicating functionality that already exists
2. Place utility functions in the appropriate module
3. Follow the established naming conventions
4. Ensure proper error handling in all utility functions
5. Document any performance considerations or limitations
6. Add unit tests for all new utility functions 