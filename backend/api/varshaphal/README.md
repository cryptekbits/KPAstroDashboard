# Varshaphal (Annual Predictions) API

This directory contains API endpoints related to Varshaphal (annual horoscope) calculations and predictions.

## Endpoints

### POST /varshaphal/details
Generate basic Varshaphal details.

**Implementation Requirements:**
- Accept birth details and target year
- Calculate solar return chart
- Determine Muntha, Varsha Lagna, and key points
- Provide overall annual overview
- Include significant dates and periods

**Integration Points:**
- Varshaphal calculation modules
- Solar return chart generation
- Time conversion utilities

### POST /varshaphal/planets
Calculate planetary positions in Varshaphal.

**Implementation Requirements:**
- Accept birth details and target year
- Calculate planetary positions at solar return moment
- Determine planetary strengths and dignities in annual chart
- Analyze planetary aspects and relationships
- Provide detailed interpretation of each planet's influence

**Integration Points:**
- Planetary position calculation modules
- Dignity and strength calculation modules
- Annual chart interpretation utilities

### POST /varshaphal/mudda_dasha
Calculate Mudda dasha periods for the year.

**Implementation Requirements:**
- Accept birth details and target year
- Calculate Mudda dasha periods for the annual chart
- Determine sub-periods if required
- Provide timing of significant events
- Include interpretation of each dasha period

**Integration Points:**
- Mudda dasha calculation modules
- Time division utilities
- Dasha interpretation modules

### POST /varshaphal/year_chart
Generate annual chart data.

**Implementation Requirements:**
- Accept birth details and target year
- Calculate complete annual chart
- Include house positions and strengths
- Determine rising sign and ascendant degree
- Format data for chart visualization

**Integration Points:**
- Varshaphal chart calculation modules
- Chart generation service
- Interpretation modules

### POST /varshaphal/yoga
Identify yogas in the annual chart.

**Implementation Requirements:**
- Accept birth details and target year
- Identify significant yogas in the annual chart
- Analyze yoga strength and timing
- Provide interpretation of each yoga's influence
- Group yogas by category or significance

**Integration Points:**
- Yoga detection modules for annual charts
- Yoga timing and manifestation analysis
- Chart data from previous calculations

### POST /varshaphal/saham_points
Calculate Sahams (special points) for the year.

**Implementation Requirements:**
- Accept birth details and target year
- Calculate important Sahams (Punya, Vidya, etc.)
- Determine house positions of Sahams
- Analyze aspects to Sahams
- Provide interpretation of each Saham's significance

**Integration Points:**
- Saham calculation modules
- House position determination
- Aspect calculation utilities

### POST /varshaphal/panchavargeeya_bala
Calculate five-fold strength in the annual chart.

**Implementation Requirements:**
- Accept birth details and target year
- Calculate Panchavargeeya Bala for planets
- Determine overall planetary strengths
- Identify strongest and weakest planets
- Provide interpretation based on strength values

**Integration Points:**
- Panchavargeeya Bala calculation modules
- Strength interpretation utilities
- Chart data from previous calculations

### POST /varshaphal/harsha_bala
Calculate Harsha Bala in the annual chart.

**Implementation Requirements:**
- Accept birth details and target year
- Calculate Harsha Bala for planets
- Determine overall happiness factors
- Identify sources of joy and satisfaction
- Provide interpretation based on calculation results

**Integration Points:**
- Harsha Bala calculation modules
- Interpretation utilities
- Chart data from previous calculations

### POST /varshaphal/muntha
Analyze Muntha position and effects.

**Implementation Requirements:**
- Accept birth details and target year
- Calculate Muntha position for the year
- Determine house placement of Muntha
- Analyze aspects to Muntha
- Provide detailed interpretation of Muntha's effects

**Integration Points:**
- Muntha calculation modules
- House signification data
- Aspect calculation utilities

## Input/Output Formats

Each endpoint should accept JSON input and return JSON responses with consistent structure:

```json
// Example request format
{
  "birth_details": {
    "datetime": "1990-01-01T12:00:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata"
  },
  "year": 2023,
  "options": {
    "ayanamsha": "lahiri",
    "house_system": "placidus"
  }
}

// Example response format
{
  "status": "success",
  "data": {
    // Endpoint-specific data
  },
  "meta": {
    "version": "1.0",
    "processing_time": "0.789s"
  }
}
```

## Error Handling

All endpoints should return appropriate HTTP status codes and error messages:

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_YEAR",
    "message": "The provided year is outside the supported range."
  },
  "meta": {
    "version": "1.0"
  }
}
```

## Varshaphal System Notes

1. Varshaphal calculations are based on the exact moment of solar return
2. The solar return is when the Sun returns to the same zodiacal position as at birth
3. The Muntha is a special sensitive point specific to annual charts
4. Mudda dasha is a specialized timing system used primarily in annual charts
5. Tajika aspects and yogas are used specifically in annual charts
6. Sahams are special sensitive points calculated for specific life areas 