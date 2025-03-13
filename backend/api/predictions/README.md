# Predictions API

This directory contains API endpoints related to astrological predictions and forecasts.

## Endpoints

### POST /predictions/daily/{zodiac_sign}
Generate daily predictions for a specific Sun sign.

**Implementation Requirements:**
- Accept zodiac sign parameter (Aries, Taurus, etc.)
- Generate daily horoscope based on current planetary positions
- Include influences of major transits
- Provide predictions for different life areas
- Support date parameter for predictions on specific days

**Integration Points:**
- Transit calculation modules
- Sign-specific interpretation templates
- Current planetary position data

### POST /predictions/daily/nakshatra
Generate daily predictions based on Moon nakshatra.

**Implementation Requirements:**
- Accept birth details or Moon nakshatra parameter
- Generate daily predictions based on current lunar influences
- Include Moon transit effects on birth nakshatra
- Provide specialized guidance based on lunar day
- Support date parameter for predictions on specific days

**Integration Points:**
- Nakshatra calculation modules
- Lunar transit analysis
- Moon-specific interpretation data

### POST /predictions/custom_daily_prediction/{zodiac_sign}
Generate personalized daily predictions.

**Implementation Requirements:**
- Accept zodiac sign and birth details
- Calculate personalized transit influences
- Generate customized daily prediction based on natal chart
- Include current planetary aspects to natal positions
- Provide timing information for significant events

**Integration Points:**
- Natal chart calculation modules
- Transit-to-natal aspect analysis
- Personalized interpretation engine

### POST /predictions/weekly/{zodiac_sign}
Generate weekly predictions for a specific Sun sign.

**Implementation Requirements:**
- Accept zodiac sign parameter
- Generate weekly forecast based on planetary movements
- Highlight significant days within the week
- Include weekly overview and day-by-day breakdown
- Support start date parameter for specific weeks

**Integration Points:**
- Weekly transit calculation modules
- Sign-specific interpretation templates
- Weekly trend analysis modules

### POST /predictions/monthly/{zodiac_sign}
Generate monthly predictions for a specific Sun sign.

**Implementation Requirements:**
- Accept zodiac sign parameter
- Generate monthly forecast based on planetary movements
- Highlight significant dates and trends
- Include New/Full Moon influences
- Provide predictions for different life areas

**Integration Points:**
- Monthly transit calculation modules
- Lunar phase impact analysis
- Longer-term trend analysis modules

### POST /predictions/chinese_year_forecast
Generate Chinese zodiac yearly forecast.

**Implementation Requirements:**
- Accept birth year or Chinese zodiac sign
- Generate yearly forecast based on Chinese astrology
- Include influences of the current year's animal and element
- Provide predictions for different life areas
- Calculate lucky/unlucky elements, colors, and directions

**Integration Points:**
- Chinese zodiac calculation modules
- Element interaction analysis
- Chinese almanac data

### POST /predictions/yearly
Generate detailed yearly predictions based on Varshaphal.

**Implementation Requirements:**
- Accept birth details
- Calculate solar return (Varshaphal) chart
- Generate comprehensive yearly forecast
- Include major planetary periods and transits
- Provide predictions for different life areas

**Integration Points:**
- Varshaphal calculation modules
- Major transit analysis
- Yearly dasha/planetary period analysis

## Input/Output Formats

Each endpoint should accept JSON input and return JSON responses with consistent structure:

```json
// Example request format
{
  "zodiac_sign": "aries",
  "date": "2023-04-15",
  "options": {
    "include_transits": true,
    "detail_level": "detailed"
  }
}

// Example response format
{
  "status": "success",
  "data": {
    "prediction": "Today is favorable for...",
    "areas": {
      "love": "Venus transiting through...",
      "career": "Mars aspects indicate...",
      "health": "Pay attention to...",
      "finances": "Financial opportunities may..."
    },
    "lucky": {
      "number": 7,
      "color": "Blue",
      "time": "2:00 PM to 4:00 PM"
    }
  },
  "meta": {
    "version": "1.0",
    "date": "2023-04-15",
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
    "code": "INVALID_SIGN",
    "message": "The provided zodiac sign is not valid."
  },
  "meta": {
    "version": "1.0"
  }
}
```

## Prediction System Notes

1. Predictions should balance technical accuracy with accessible language
2. Include disclaimers about prediction limitations and free will
3. Ensure predictions are constructive and avoid excessive negativity
4. Personalized predictions should use multiple chart factors, not just Sun sign
5. Implement proper caching for standard predictions (Sun sign based)
6. Consider cultural sensitivity in prediction language and interpretations
7. Allow for different levels of astrological detail based on user preferences 