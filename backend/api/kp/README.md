# KP System API

This directory contains API endpoints related to the Krishnamurti Paddhati (KP) system of astrology.

## Endpoints

### POST /kp/planets
Calculate KP planetary positions and sublords.

**Implementation Requirements:**
- Accept birth details (date, time, location)
- Calculate planetary positions with KP star lord, sub lord, and sub-sub lord
- Include speed, retrogression status, and aspects
- Support multiple ayanamsha systems (KP ayanamsha is default)

**Integration Points:**
- Core KP calculation modules
- Planetary position modules
- KP star and sublord mapping

### POST /kp/cusps
Calculate KP house cusp positions and sublords.

**Implementation Requirements:**
- Accept birth details (date, time, location)
- Calculate house cusps using Placidus system (KP default)
- Determine star lord, sub lord, and sub-sub lord for each cusp
- Include house significators

**Integration Points:**
- Core KP calculation modules
- House cusp calculation modules
- KP significator determination logic

### POST /kp/chart
Generate KP chart data.

**Implementation Requirements:**
- Accept birth details (date, time, location)
- Generate complete KP chart with planets and cusps
- Include all sublord information
- Format data for KP chart visualization

**Integration Points:**
- KP planet and cusp calculation modules
- Chart generation service
- KP-specific data formatting

### POST /kp/significators
Calculate KP significators for houses and planets.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate strong, medium, and weak significators for each house
- Calculate ruling planets for specific houses
- Provide significator strength scores

**Integration Points:**
- KP significator calculation modules
- Sublord relationship mappings
- Chart data from previous calculations

### POST /kp/details
Generate detailed KP analysis.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Provide comprehensive KP analysis of the chart
- Include cuspal interlinks
- Highlight important KP combinations

**Integration Points:**
- All KP calculation modules
- KP analysis algorithms
- Chart data from previous calculations

### POST /kp/dasha
Calculate KP dasha periods.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate dasha periods according to KP principles
- Include sublord influences in dasha interpretation
- Provide timing predictions based on dashas

**Integration Points:**
- KP dasha calculation modules
- Sublord determination
- Time conversion utilities

### POST /kp/transit
Analyze KP transits.

**Implementation Requirements:**
- Accept birth details and transit date
- Calculate transit positions with KP sublords
- Analyze transit influences on natal chart
- Provide timing and prediction based on transit sublords

**Integration Points:**
- KP transit calculation modules
- Natal chart data access
- Transit-natal relationship analysis

## Input/Output Formats

Each endpoint should accept JSON input and return JSON responses with consistent structure:

```json
// Example request format
{
  "datetime": "1990-01-01T12:00:00",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timezone": "Asia/Kolkata",
  "ayanamsha": "kp"
}

// Example response format
{
  "status": "success",
  "data": {
    // Endpoint-specific data
  },
  "meta": {
    "version": "1.0",
    "processing_time": "0.234s"
  }
}
```

## Error Handling

All endpoints should return appropriate HTTP status codes and error messages:

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "Required KP calculation parameters are missing or invalid."
  },
  "meta": {
    "version": "1.0"
  }
}
```

## KP System Notes

1. Always use the KP ayanamsha (Krishnamurti) unless explicitly specified otherwise
2. House cusps should always use the Placidus system for KP calculations
3. Sublord determination is critical for accurate KP predictions
4. The 249-degree sublord table should be implemented with precision
5. Cuspal interlinks are essential for proper KP analysis 