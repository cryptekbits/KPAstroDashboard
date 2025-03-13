# Numerology API

This directory contains API endpoints related to numerological calculations and analysis.

## Endpoints

### POST /numerology/table
Generate numerology calculation table.

**Implementation Requirements:**
- Accept birth name and birth date
- Calculate key numerological numbers (Life Path, Expression, etc.)
- Generate numerology grid or table
- Include missing and excess numbers
- Provide core number interpretations

**Integration Points:**
- Numerology calculation modules
- Name analysis utilities
- Numerological interpretation data

### POST /numerology/report
Generate detailed numerology report.

**Implementation Requirements:**
- Accept birth name, birth date, and other personal details
- Calculate comprehensive numerological profile
- Include detailed interpretations of each number
- Provide personality analysis based on numerology
- Generate compatibility insights

**Integration Points:**
- Comprehensive numerology calculation modules
- Report generation service
- Interpretation database

### POST /numerology/fav_time
Calculate favorable time recommendations.

**Implementation Requirements:**
- Accept birth details and numerology profile
- Calculate favorable times for activities based on personal numbers
- Provide daily/weekly/monthly favorable periods
- Include explanations of time significance
- Support time recommendations for specific activities

**Integration Points:**
- Time calculation modules
- Personal number analysis
- Activity-number relationship database

### POST /numerology/place_vastu
Analyze place and Vastu compatibility.

**Implementation Requirements:**
- Accept numerology profile and address/location details
- Calculate place number and compatibility with personal numbers
- Provide Vastu recommendations based on numerological principles
- Include suggestions for space optimization
- Calculate directional influences

**Integration Points:**
- Place number calculation modules
- Vastu-numerology integration modules
- Spatial analysis utilities

### POST /numerology/fasts_report
Generate fasting recommendations based on numerology.

**Implementation Requirements:**
- Accept numerology profile and health goals
- Calculate favorable fasting days
- Recommend fasting approaches based on numbers
- Include dietary suggestions aligned with numbers
- Provide timing for breaking fasts

**Integration Points:**
- Fasting calculation modules
- Health-number relationship data
- Calendar utilities

### POST /numerology/fav_lord
Determine favorable deity or spiritual practice.

**Implementation Requirements:**
- Accept numerology profile
- Calculate deity associations based on birth numbers
- Recommend spiritual practices aligned with numbers
- Include mantras associated with personal numbers
- Provide spiritual guidance based on numerology

**Integration Points:**
- Deity-number association database
- Spiritual practice recommendation modules
- Mantra database

### POST /numerology/fav_mantra
Generate favorable mantras based on numerology.

**Implementation Requirements:**
- Accept numerology profile
- Calculate mantra recommendations based on birth numbers
- Include specific mantras for healing, abundance, etc.
- Provide chanting instructions and timing
- Calculate mantra repetition numbers

**Integration Points:**
- Mantra database
- Numerology-sound relationship modules
- Intention-based recommendation engine

## Input/Output Formats

Each endpoint should accept JSON input and return JSON responses with consistent structure:

```json
// Example request format
{
  "name": "John Smith",
  "birth_date": "1990-01-01",
  "gender": "male",
  "options": {
    "calculation_method": "chaldean",
    "include_master_numbers": true
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
    "code": "INVALID_NAME_FORMAT",
    "message": "The provided name contains invalid characters."
  },
  "meta": {
    "version": "1.0"
  }
}
```

## Numerology System Notes

1. Support both Pythagorean and Chaldean numerology systems
2. Handle master numbers (11, 22, 33) appropriately
3. Consider name change analysis for before/after comparisons
4. Support both Western and Vedic numerology approaches
5. Implement compatibility analysis between multiple individuals
6. Account for cultural variations in name structures and meanings 