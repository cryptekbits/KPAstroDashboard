# Reports API

This directory contains API endpoints related to generating comprehensive astrological reports.

## Endpoints

### POST /reports/birth_chart
Generate a comprehensive birth chart report.

**Implementation Requirements:**
- Accept birth details (date, time, location)
- Generate detailed natal chart analysis
- Include planetary positions and aspects
- Calculate house positions and sign placements
- Provide detailed personality analysis
- Include strengths and challenges based on chart

**Integration Points:**
- Core chart calculation modules
- Planetary position modules
- House and sign determination modules
- Interpretation database for chart factors

### POST /reports/transit
Generate a transit report for a specified time period.

**Implementation Requirements:**
- Accept birth details and transit period
- Calculate current transits relative to natal chart
- Identify significant transit events and aspects
- Provide interpretation for each transit
- Include timing for peak transit effects
- Organize transits by life area impact

**Integration Points:**
- Transit calculation modules
- Aspect identification system
- Time period analysis algorithms
- Predictive interpretation database

### POST /reports/solar_return
Generate annual solar return report.

**Implementation Requirements:**
- Accept birth details and year for analysis
- Calculate precise solar return chart
- Compare solar return chart to natal chart
- Provide yearly outlook based on solar return
- Highlight key themes and potential developments
- Include timing details for important periods

**Integration Points:**
- Solar return calculation modules
- Chart comparison utilities
- Yearly forecast interpretation database
- Timing analysis modules

### POST /reports/compatibility
Generate relationship compatibility report.

**Implementation Requirements:**
- Accept birth details for two individuals
- Calculate synastry aspects and interactions
- Analyze composite chart if requested
- Assess overall compatibility score
- Provide detailed analysis of relationship dynamics
- Include strengths and potential challenges

**Integration Points:**
- Synastry calculation modules
- Composite chart generators
- Compatibility scoring algorithms
- Relationship interpretation database

### POST /reports/dasha_prediction
Generate dasha-based prediction report.

**Implementation Requirements:**
- Accept birth details
- Calculate current and upcoming dasha periods
- Provide detailed interpretation of current dasha
- Include antardasha and pratyantardasha analysis
- Highlight significant life events based on dashas
- Offer timing predictions for major transitions

**Integration Points:**
- Dasha calculation modules
- Life event prediction engine
- Personalized interpretation system
- Timing analysis algorithms

### POST /reports/yearly_prediction
Generate yearly prediction report.

**Implementation Requirements:**
- Accept birth details and year for analysis
- Include analysis of Varshaphal (annual chart)
- Calculate transits for the year
- Analyze dasha influences during the year
- Provide month-by-month breakdown of influences
- Highlight key periods of opportunity or challenge

**Integration Points:**
- Varshaphal calculation modules
- Transit timing system
- Dasha impact assessment
- Yearly prediction interpretation database

### POST /reports/yogas
Generate report on yogas (planetary combinations) in chart.

**Implementation Requirements:**
- Accept birth details
- Identify all significant yogas in the chart
- Calculate strength and activation timing for each yoga
- Provide detailed interpretation of each yoga's effect
- Include remedies for challenging yogas if requested
- Organize yogas by life area impact

**Integration Points:**
- Yoga detection engine
- Yoga strength assessment modules
- Yoga timing analysis system
- Remedial measures recommendation engine

### POST /reports/special_charts
Generate special chart analysis reports (Navamsa, D10, etc.).

**Implementation Requirements:**
- Accept birth details and divisional chart type(s)
- Generate specified divisional charts
- Provide detailed analysis of requested charts
- Include specialized interpretations for each chart type
- Highlight significant patterns across divisional charts
- Compare divisional charts to main chart

**Integration Points:**
- Divisional chart calculation modules
- Chart comparison utilities
- Specialized divisional chart interpretation database
- Pattern recognition algorithms

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
  "options": {
    "report_format": "detailed",
    "include_remedies": true,
    "language": "en"
  }
}

// Example response format
{
  "status": "success",
  "data": {
    "title": "Birth Chart Analysis for John Doe",
    "summary": "This chart reveals a strong emphasis on communication and intellectual pursuits...",
    "sections": [
      {
        "title": "Planetary Positions",
        "content": [
          {
            "planet": "Sun",
            "sign": "Capricorn",
            "house": 5,
            "degrees": "16°42'",
            "analysis": "The Sun in Capricorn in the 5th house indicates..."
          },
          // Additional planets...
        ]
      },
      {
        "title": "Houses and Signs",
        "content": [
          {
            "house": 1,
            "sign": "Leo",
            "lord": "Sun",
            "analysis": "Leo rising gives a confident and charismatic persona..."
          },
          // Additional houses...
        ]
      },
      // Additional report sections...
    ]
  },
  "meta": {
    "version": "1.0",
    "generation_date": "2023-04-15T08:30:45",
    "processing_time": "1.234s"
  }
}
```

## Error Handling

All endpoints should return appropriate HTTP status codes and error messages:

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_BIRTH_DATA",
    "message": "Unable to generate report with the provided birth information."
  },
  "meta": {
    "version": "1.0"
  }
}
```

## Report System Notes

1. Reports should support various detail levels (basic, standard, detailed)
2. Include options for different formatting styles (narrative, bullet points, etc.)
3. Support multiple languages with appropriate translation systems
4. Provide both traditional and modern astrological interpretations
5. Include visualization data for chart diagrams when requested
6. Implement caching for computationally intensive report components
7. Support customizable report templates for different user preferences 