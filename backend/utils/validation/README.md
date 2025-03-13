# Validation and Error Handling Utilities

This directory contains utility functions for input validation and standardized error handling throughout the astrology application.

## Purpose

The validation utilities provide systematic approaches to validate user inputs, configuration values, and calculation parameters. They ensure that data meets required formats, ranges, and constraints before processing, helping to prevent runtime errors and unexpected behavior. Additionally, these utilities establish standardized error handling patterns for consistent messaging and graceful failure handling.

## Key Components

### 1. Birth Data Validation

Functions for validating astrological birth data inputs.

**Features:**
- Date and time validation with calendar system awareness
- Geographic coordinate validation
- Timezone validation and verification
- Birth data completeness checking
- Cross-field validation rules
- Missing data assessment for rectification cases

### 2. Location Data Validation

Utilities for validating and normalizing location information.

**Features:**
- Coordinate range and format validation
- Geocoding result validation
- Timezone consistency checking
- Location name validation
- Elevation data validation
- Historical location name validation

### 3. Astrological Parameter Validation

Specialized validation for astrological calculation parameters.

**Features:**
- House system validation
- Ayanamsa parameter validation
- Planet set validation
- Aspect set and orb validation
- Chart calculation option validation
- Algorithm selection validation

### 4. API Input Validation

Framework for validating API request data.

**Features:**
- Request schema validation
- Parameter type checking
- Required field validation
- Cross-parameter consistency checking
- Rate limit and quota validation
- Input sanitization

### 5. Standardized Error Types

Comprehensive error type system for consistent error handling.

**Features:**
- Hierarchical error class system
- Domain-specific error subclasses
- Error code standardization
- Internationalized error messages
- Error context enrichment
- HTTP status code mapping

### 6. Exception Handling Utilities

Helper functions for consistent exception management.

**Features:**
- Try-except wrappers with standardized logging
- Error aggregation utilities
- Default value handling
- Exception chaining helpers
- Retry mechanisms for transient errors
- Graceful degradation support

## Usage Examples

```python
from backend.utils.validation.birth_data import validate_birth_data, is_valid_date
from backend.utils.validation.location import validate_coordinates, is_valid_timezone
from backend.utils.validation.astrological import validate_house_system
from backend.utils.validation.error_types import InputValidationError, CalculationError
from backend.utils.validation.error_handling import handle_calculation_errors

# Validate birth information
is_valid, errors = validate_birth_data(
    year=1990, month=1, day=1,
    hour=12, minute=0, second=0,
    latitude=28.6139, longitude=77.2090,
    timezone="Asia/Kolkata"
)

if not is_valid:
    for error in errors:
        print(f"Error: {error.message} (Code: {error.code})")

# Check if individual elements are valid
if not is_valid_date(year=2100, month=2, day=29):
    print("Invalid date - February 29, 2100 does not exist")

# Validate coordinates
try:
    validated_coords = validate_coordinates(latitude=91.5, longitude=77.2090)
except InputValidationError as e:
    print(f"Coordinate validation failed: {e}")

# Validate astrological parameters
try:
    validate_house_system("InvalidSystem")
except ValueError as e:
    print(f"House system validation failed: {e}")

# Use error handling decorator
@handle_calculation_errors(default_return=None, log_level="WARNING")
def calculate_sensitive_point(chart_data):
    # Calculation logic that might raise exceptions
    if some_error_condition:
        raise CalculationError("Failed to calculate point")
    return result
```

## Validation Principles

The validation utilities adhere to these principles:

1. Fail early and explicitly - catch errors at input time
2. Provide clear, actionable error messages
3. Validate at the appropriate level (field, object, cross-field)
4. Support both strict and lenient validation modes where appropriate
5. Maintain a clear separation between validation and business logic
6. Ensure validation itself fails gracefully

## Error Handling Guidelines

Consistent error handling patterns include:

1. Using specialized error types for different error categories
2. Including error codes for programmatic handling
3. Providing user-friendly error messages
4. Capturing and preserving context for debugging
5. Appropriate logging at error boundaries
6. Maintaining security by avoiding sensitive data in error messages

## Testing

The validation utilities include comprehensive test coverage:

1. Unit tests for each validation function
2. Edge case testing with invalid inputs
3. Locale-specific validation testing
4. Performance testing for validation overhead
5. Integration tests for error propagation patterns 