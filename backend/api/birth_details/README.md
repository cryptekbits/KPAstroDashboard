# Birth Details API

This directory contains API endpoints related to birth details and location information.

## Endpoints

### POST /birth_details
Calculate and return basic birth details based on input parameters.

**Implementation Requirements:**
- Accept birth date, time, and location data
- Validate inputs for completeness and accuracy
- Calculate relevant astrological parameters
- Return formatted birth details

**Integration Points:**
- Core calculation modules for astrological calculations
- Geolocation utilities for handling location data
- Time utilities for handling date/time conversions

### POST /geo_details
Provide location suggestions and details based on partial input.

**Implementation Requirements:**
- Accept partial location name or coordinates
- Return matching location suggestions with complete data
- Include coordinates, timezone, and other relevant details
- Implement proper error handling for location not found

**Integration Points:**
- External geocoding service or database
- Location data caching for performance
- Coordinate validation utilities

### POST /timezone
Calculate timezone information for a given location and date.

**Implementation Requirements:**
- Accept location coordinates and optional date
- Determine the correct timezone for the given parameters
- Handle DST transitions correctly
- Return timezone name, offset, and relevant details

**Integration Points:**
- Timezone database or API
- Time utilities for DST calculations
- Location validation utilities

## Input/Output Formats

Each endpoint should accept JSON input and return JSON responses with consistent structure:

```json
// Example request format
{
  "datetime": "1990-01-01T12:00:00",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timezone": "Asia/Kolkata"
}

// Example response format
{
  "status": "success",
  "data": {
    // Endpoint-specific data
  },
  "meta": {
    "version": "1.0",
    "processing_time": "0.123s"
  }
}
```

## Error Handling

All endpoints should return appropriate HTTP status codes and error messages:

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_LOCATION",
    "message": "The provided location coordinates are invalid."
  },
  "meta": {
    "version": "1.0"
  }
}
``` 