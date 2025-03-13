# Panchang API

This directory contains API endpoints related to Panchang (Hindu almanac) calculations.

## Endpoints

### POST /panchang/daily
Calculate daily Panchang details.

**Implementation Requirements:**
- Accept date and location parameters
- Calculate Tithi, Nakshatra, Yoga, Karana
- Calculate Sunrise, Sunset, Moonrise, Moonset
- Include auspicious and inauspicious timings

**Integration Points:**
- Core Panchang calculation modules
- Geolocation utilities
- Time utilities for sunrise/sunset calculations

### POST /panchang/advanced
Calculate advanced Panchang details.

**Implementation Requirements:**
- Accept date and location parameters
- Include all daily Panchang elements
- Add additional elements like Rahu Kalam, Gulika, etc.
- Calculate planetary positions and transits

**Integration Points:**
- Core Panchang calculation modules
- Planetary position calculation modules
- Muhurta calculation modules

### POST /panchang/tamil
Calculate Tamil Panchang details.

**Implementation Requirements:**
- Accept date and location parameters
- Calculate Tamil calendar-specific elements
- Include Tamil month, year, and special days
- Add Tamil festival information if applicable

**Integration Points:**
- Tamil calendar conversion utilities
- Core Panchang calculation modules
- Festival database

### POST /panchang/monthly
Generate monthly Panchang calendar.

**Implementation Requirements:**
- Accept month, year, and location parameters
- Generate daily Panchang for each day of the month
- Include major festival and observance information
- Format data in calendar-friendly structure

**Integration Points:**
- Daily Panchang calculation modules
- Festival database
- Calendar formatting utilities

### POST /panchang/festivals
Calculate festival dates.

**Implementation Requirements:**
- Accept year and optional location parameters
- Calculate major Hindu festival dates
- Include festival details and significance
- Group festivals by month or season

**Integration Points:**
- Festival calculation modules
- Calendar conversion utilities
- Tithi calculation modules

### POST /panchang/sunrise_sunset
Calculate sunrise, sunset, and related timings.

**Implementation Requirements:**
- Accept date and location parameters
- Calculate sunrise, sunset, civil/nautical/astronomical twilight
- Include daylight duration
- Provide solar position information

**Integration Points:**
- Astronomical calculation modules
- Geolocation utilities
- Time utilities

### POST /chaughadiya
Calculate Chaughadiya muhurta timings.

**Implementation Requirements:**
- Accept date and location parameters
- Calculate the 8 Chaughadiya periods for day and night
- Include quality/nature of each period
- Provide start and end times in local timezone

**Integration Points:**
- Sunrise/sunset calculation modules
- Muhurta calculation utilities
- Time division modules

### POST /hora
Calculate Hora (planetary hour) timings.

**Implementation Requirements:**
- Accept date and location parameters
- Calculate the planetary hours for day and night
- Map hours to ruling planets
- Provide start and end times in local timezone

**Integration Points:**
- Sunrise/sunset calculation modules
- Day of week determination
- Planetary ruler assignment logic

## Input/Output Formats

Each endpoint should accept JSON input and return JSON responses with consistent structure:

```json
// Example request format
{
  "date": "2023-04-15",
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
    "code": "INVALID_DATE",
    "message": "The provided date is outside the supported range."
  },
  "meta": {
    "version": "1.0"
  }
}
``` 