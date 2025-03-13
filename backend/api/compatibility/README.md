# Compatibility and Matchmaking API

This directory contains API endpoints related to astrological compatibility analysis and marriage matching.

## Endpoints

### POST /matchmaking/basic
Perform basic compatibility analysis.

**Implementation Requirements:**
- Accept birth details for two individuals
- Calculate basic compatibility scores
- Provide overview of relationship compatibility
- Include general compatibility insights
- Support both Vedic and Western compatibility methods

**Integration Points:**
- Core calculation modules for chart generation
- Compatibility scoring algorithms
- Basic interpretation services

### POST /matchmaking/ashtakoota
Perform traditional Ashtakoot (8-fold) matching.

**Implementation Requirements:**
- Accept birth details for two individuals
- Calculate all 8 Kootas (Varna, Vashya, Tara, etc.)
- Provide detailed score for each Koota
- Calculate total Ashtakoot score (out of 36)
- Include traditional interpretation of results

**Integration Points:**
- Ashtakoot calculation modules
- Moon nakshatra and sign position calculations
- Traditional interpretation templates

### POST /matchmaking/dashkoota
Perform extended Dashkoot (10-fold) matching.

**Implementation Requirements:**
- Accept birth details for two individuals
- Calculate all 10 Kootas (including the additional 2)
- Provide detailed score for each Koota
- Calculate total Dashkoot score
- Include extended interpretation of results

**Integration Points:**
- Dashkoot calculation modules
- Extended koota interpretation systems
- Additional matching parameters

### POST /matchmaking/manglik
Analyze Manglik dosha compatibility.

**Implementation Requirements:**
- Accept birth details for two individuals
- Determine Manglik status for both individuals
- Calculate Manglik cancellation factors
- Assess Manglik compatibility
- Provide remedial measures if needed

**Integration Points:**
- Manglik dosha calculation modules
- Manglik cancellation logic
- Remedial measures database

### POST /matchmaking/report
Generate comprehensive matching report.

**Implementation Requirements:**
- Accept birth details for two individuals
- Perform all compatibility calculations
- Generate detailed compatibility analysis
- Include relationship strengths and challenges
- Provide recommendations for harmonious relationship

**Integration Points:**
- All compatibility calculation modules
- Report generation service
- Relationship dynamics interpretation modules

### POST /matchmaking/percentage
Calculate overall compatibility percentage.

**Implementation Requirements:**
- Accept birth details for two individuals
- Perform weighted scoring of various compatibility factors
- Calculate overall compatibility percentage
- Provide brief explanation of score
- Include key strength and challenge areas

**Integration Points:**
- All compatibility calculation modules
- Weighted scoring algorithms
- Simplified interpretation templates

### POST /matchmaking/detailed_report
Generate in-depth relationship analysis.

**Implementation Requirements:**
- Accept birth details for two individuals
- Perform comprehensive compatibility analysis
- Include multiple matching systems (Vedic, Western, etc.)
- Provide detailed analysis of relationship dynamics
- Include long-term compatibility projections

**Integration Points:**
- All compatibility calculation modules
- Chart comparison utilities
- Composite/synastry chart generation
- Report generation service

## Input/Output Formats

Each endpoint should accept JSON input and return JSON responses with consistent structure:

```json
// Example request format
{
  "person1": {
    "datetime": "1990-01-01T12:00:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata",
    "gender": "male"
  },
  "person2": {
    "datetime": "1992-05-15T15:30:00",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "timezone": "Asia/Kolkata",
    "gender": "female"
  },
  "options": {
    "matching_system": "vedic",
    "detailed": true
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
    "processing_time": "0.678s"
  }
}
```

## Error Handling

All endpoints should return appropriate HTTP status codes and error messages:

```json
{
  "status": "error",
  "error": {
    "code": "INCOMPLETE_BIRTH_DATA",
    "message": "Complete birth details are required for both individuals."
  },
  "meta": {
    "version": "1.0"
  }
}
```

## Compatibility Systems Notes

1. Different cultural traditions have different compatibility systems
2. The Ashtakoot system is standard for traditional Hindu marriage matching
3. Western compatibility focuses on aspects between personal planets
4. KP system compatibility has its own unique parameters
5. Gender considerations may be important for traditional matching
6. Modern interpretations should be available alongside traditional ones 