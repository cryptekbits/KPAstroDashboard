# Kundli (Birth Chart) API

This directory contains API endpoints related to birth chart (Kundli) calculations and analysis.

## Endpoints

### POST /kundli/basic
Generate basic Kundli (birth chart) information.

**Implementation Requirements:**
- Accept birth details (date, time, location)
- Calculate ascendant, planetary positions, and basic chart details
- Return formatted Kundli data
- Support multiple ayanamsha systems (Lahiri, Raman, etc.)

**Integration Points:**
- Core calculation modules for planetary positions
- Chart generation service for visual representation
- Ayanamsha calculation utilities

### POST /kundli/houses
Calculate detailed house information for a birth chart.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate house cusps using specified house system
- Determine house lords and occupants
- Provide detailed house strength and significance information

**Integration Points:**
- Core house calculation modules
- Dignities calculation for house lords
- House signification database

### POST /kundli/planets
Calculate detailed planetary information for a birth chart.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate planetary positions with detailed attributes
- Include nakshatra, pada, dignity, aspect information
- Calculate planetary relationships (friend, enemy, neutral)

**Integration Points:**
- Core planetary calculation modules
- Nakshatra calculation utilities
- Dignities and aspects calculation modules

### POST /kundli/vimshottari_dasha
Calculate Vimshottari Dasha periods.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate Mahadasha, Antardasha, Pratyantardasha (up to 5 levels)
- Calculate dasha balance
- Provide start and end dates for each period

**Integration Points:**
- Core dasha calculation modules
- Time conversion utilities for date formatting
- Nakshatra calculation for dasha lord determination

### POST /kundli/current_vdasha_date
Calculate current running dasha for a specific date.

**Implementation Requirements:**
- Accept birth details and target date
- Calculate the current dasha hierarchy running on the specified date
- Return formatted dasha information with remaining duration

**Integration Points:**
- Vimshottari dasha calculation module
- Date comparison utilities

### POST /kundli/ashtakvarga
Calculate Ashtakvarga points for a birth chart.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate Bhinnashtakvarga for each planet
- Calculate Sarvashtakvarga (combined points)
- Perform reduction calculations if required

**Integration Points:**
- Core Ashtakvarga calculation modules
- Chart data access for planetary positions
- Visualization service for Ashtakvarga charts

### POST /kundli/shadbala
Calculate Shadbala (six-fold strength) for planets.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate all Shadbala components
- Calculate Bhava Bala
- Calculate Ishta/Kashta Phala

**Integration Points:**
- Core Shadbala calculation modules
- Dignities calculation modules
- Chart data access for planetary positions

### POST /kundli/jaimini_details
Calculate Jaimini astrology details.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate Karakas (Atma, Amatya, etc.)
- Calculate Pada Lagna and other Jaimini-specific points
- Calculate Jaimini aspects and relationships

**Integration Points:**
- Jaimini calculation modules
- Chart data access for planetary positions

### POST /kundli/yogas
Identify and analyze yogas in a birth chart.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Detect presence of various yogas
- Provide yoga strength and significance
- Group yogas by category (Raja, Dhana, etc.)

**Integration Points:**
- Yoga detection modules
- Planetary position and aspect calculations
- Yoga effects database

### POST /kundli/chart/{chart_id}
Generate divisional chart data.

**Implementation Requirements:**
- Accept birth details and divisional chart type (D1, D9, etc.)
- Calculate specified divisional chart
- Return chart data in structured format
- Support standard and special calculation methods

**Integration Points:**
- Divisional chart calculation modules
- Chart data transformation utilities
- Chart ID validation

### POST /kundli/chart_image/{chart_id}
Generate visual representation of a chart.

**Implementation Requirements:**
- Accept chart data or reference and chart style parameters
- Generate chart image in specified format (SVG, PNG)
- Support multiple chart styles (North Indian, South Indian, etc.)
- Allow customization of chart appearance

**Integration Points:**
- Chart generation service
- Image format conversion utilities
- Chart style templates

## Input/Output Formats

Each endpoint should accept JSON input and return JSON responses with consistent structure:

```json
// Example request format
{
  "datetime": "1990-01-01T12:00:00",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timezone": "Asia/Kolkata",
  "ayanamsha": "lahiri"
}

// Example response format
{
  "status": "success",
  "data": {
    // Endpoint-specific data
  },
  "meta": {
    "version": "1.0",
    "processing_time": "0.456s"
  }
}
```

## Error Handling

All endpoints should return appropriate HTTP status codes and error messages:

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_CHART_ID",
    "message": "The provided chart ID is not valid or supported."
  },
  "meta": {
    "version": "1.0"
  }
}
``` 