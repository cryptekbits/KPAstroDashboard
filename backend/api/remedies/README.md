# Remedies API

This directory contains API endpoints related to astrological remedies and recommendations.

## Endpoints

### POST /remedies/gemstone
Calculate gemstone recommendations.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Analyze planetary strengths and weaknesses
- Recommend appropriate gemstones based on chart analysis
- Provide wearing instructions (finger, metal, timing)
- Include detailed explanation of benefits and precautions

**Integration Points:**
- Planetary strength calculation modules
- Gemstone-planet association database
- Chart analysis modules
- Personalized recommendation engine

### POST /remedies/rudraksha
Recommend appropriate Rudraksha.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Analyze chart for challenges and strengths
- Recommend suitable Rudraksha type(s)
- Provide wearing instructions and mantras
- Include combinations for specific purposes

**Integration Points:**
- Planetary strength calculation modules
- Rudraksha-planet association database
- Dosha identification modules
- Mantra recommendation system

### POST /remedies/puja
Recommend ritual and worship remedies.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Identify challenging planetary periods or placements
- Recommend appropriate pujas and rituals
- Include timing considerations for maximum effectiveness
- Provide detailed procedure and requirements

**Integration Points:**
- Dasha analysis modules
- Transit impact calculation
- Planetary deity association database
- Ritual effectiveness scoring system

### POST /remedies/mantra
Recommend mantra-based remedies.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Identify planets requiring propitiation
- Recommend appropriate mantras with repetition count
- Include pronunciation guides and meaning
- Provide timing and practice instructions

**Integration Points:**
- Planetary weakness identification modules
- Mantra database with audio references
- Personalized mantra prescription logic
- Timing calculation for practice

### POST /remedies/manglik
Generate Manglik dosha remedial measures.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate Manglik dosha presence and severity
- Provide traditional and modern remedial measures
- Include effectiveness rating for each remedy
- Recommend specific sequence of remedies

**Integration Points:**
- Manglik dosha calculation modules
- Mars position and aspect analysis
- Manglik cancellation detection
- Mars-specific remedy database

### POST /remedies/kalsarpa
Generate Kalsarpa dosha remedial measures.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate Kalsarpa or Partial Kalsarpa presence
- Identify specific type of Kalsarpa yoga
- Recommend tailored remedial measures
- Include severity assessment and priority order

**Integration Points:**
- Kalsarpa yoga detection modules
- Rahu-Ketu axis analysis
- Kalsarpa type-specific remedy database
- Yoga severity calculation

### POST /remedies/pitra_dosha
Generate Pitra (ancestral) dosha remedial measures.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Analyze chart for Pitra dosha indicators
- Recommend specific remedial measures
- Provide Shraddha and ritual details
- Include timing recommendations

**Integration Points:**
- Pitra dosha identification modules
- Moon-Saturn-Rahu relationship analysis
- 9th house and lord analysis
- Ancestor-related remedy database

### POST /remedies/sadhesati
Generate Sadhesati remedial measures.

**Implementation Requirements:**
- Accept birth details or reference to existing chart
- Calculate Saturn transit status relative to Moon
- Identify current Sadhesati phase if applicable
- Recommend phase-specific remedial measures
- Include timing and duration of remedies

**Integration Points:**
- Saturn transit calculation
- Moon position analysis
- Sadhesati phase identification
- Saturn-specific remedy database

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
    "remedy_level": "moderate",
    "include_alternatives": true,
    "consider_practicality": true
  }
}

// Example response format
{
  "status": "success",
  "data": {
    "remedies": [
      {
        "type": "Primary",
        "name": "Yellow Sapphire (Pukhraj)",
        "description": "Gemstone for Jupiter strengthening",
        "procedure": "Wear a 3-5 carat natural yellow sapphire set in gold on the index finger",
        "timing": "Thursday morning during Jupiter hora",
        "effectiveness": "High",
        "benefits": [
          "Strengthens weak Jupiter",
          "Enhances wisdom and academic success",
          "Improves financial prosperity"
        ],
        "precautions": [
          "Must be natural and flawless",
          "Should be energized before wearing",
          "Not recommended if Jupiter is debilitated or combust"
        ]
      },
      // Additional remedies...
    ]
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
    "code": "INCOMPLETE_CHART_DATA",
    "message": "Unable to calculate remedies without complete birth information."
  },
  "meta": {
    "version": "1.0"
  }
}
```

## Remedy System Notes

1. Recommendations should be personalized based on individual chart factors
2. Include traditional and modern alternatives where appropriate
3. Consider severity of the issue when recommending remedies
4. Provide scientific rationale where available along with traditional explanation
5. Include disclaimers about consulting qualified practitioners for serious issues
6. Remedies should be culturally sensitive and practical for implementation
7. Prioritize remedies that address root causes rather than symptoms 