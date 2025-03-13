# Lal Kitab API

This directory contains API endpoints related to Lal Kitab (Red Book) astrology system.

## Endpoints

### POST /lalkitab/horoscope
Generate Lal Kitab horoscope.

**Implementation Requirements:**
- Accept birth details (date, time, location)
- Calculate planetary positions according to Lal Kitab principles
- Determine house placements using Lal Kitab rules
- Return complete Lal Kitab chart data

**Integration Points:**
- Core Lal Kitab calculation modules
- Chart generation service for visual representation
- Lal Kitab house and planet relationship data

### POST /lalkitab/reports
Generate Lal Kitab detailed reports.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Generate detailed analysis of each planetary position
- Include karmic debts and planetary relationships
- Provide overall life analysis based on Lal Kitab principles

**Integration Points:**
- Lal Kitab interpretation modules
- Report generation service
- Lal Kitab house and planet signification data

### POST /lalkitab/debts
Analyze Lal Kitab karmic debts.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate the presence of ancestral debts
- Determine nature and severity of each debt
- Provide detailed explanation of debt origins and effects

**Integration Points:**
- Lal Kitab debt calculation modules
- Debt analysis and interpretation utilities
- Chart data from previous calculations

### POST /lalkitab/remedies
Generate Lal Kitab remedial measures.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate appropriate remedies for planetary afflictions
- Include remedies for karmic debts if present
- Prioritize remedies by importance and effectiveness

**Integration Points:**
- Lal Kitab remedy determination modules
- Planetary affliction analysis
- Debt calculation modules

### POST /lalkitab/houses
Analyze Lal Kitab house details.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Provide detailed analysis of each house
- Include effects of planets in each house
- Determine house strength and significance

**Integration Points:**
- Lal Kitab house analysis modules
- House-planet relationship data
- Chart data from previous calculations

### POST /lalkitab/planets
Analyze Lal Kitab planetary details.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Provide detailed analysis of each planet
- Include planet-house relationships
- Determine planetary strength and significance

**Integration Points:**
- Lal Kitab planetary analysis modules
- Planet-house relationship data
- Chart data from previous calculations

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
    "processing_time": "0.345s"
  }
}
```

## Error Handling

All endpoints should return appropriate HTTP status codes and error messages:

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_CHART_DATA",
    "message": "Unable to generate Lal Kitab chart with the provided data."
  },
  "meta": {
    "version": "1.0"
  }
}
```

## Lal Kitab System Notes

1. Lal Kitab uses a fixed zodiac rather than a tropical or sidereal zodiac
2. Planetary positions are determined by sign only, not by degree
3. Rahu and Ketu have special significance in Lal Kitab
4. Houses are numbered 1-12 starting from Aries (unlike traditional Vedic astrology)
5. Remedies are a central focus of the Lal Kitab system 