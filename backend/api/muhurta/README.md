# Muhurta API

This directory contains API endpoints related to Muhurta (electional astrology) for determining auspicious timings.

## Endpoints

### POST /muhurta/auspicious
Calculate auspicious timings for various activities.

**Implementation Requirements:**
- Accept date range, location, and activity type
- Calculate auspicious timings based on planetary configurations
- Filter timings based on Panchanga factors
- Consider Nakshatra, Tithi, Yoga, and Karana
- Rank time periods by auspiciousness level

**Integration Points:**
- Panchanga calculation modules
- Activity-specific auspiciousness criteria
- Transit calculation modules
- Timing optimization algorithms

## Activity-Specific Implementations

The auspicious endpoint supports various activity types, each with specialized calculation criteria:

### Marriage Muhurta
- Avoid Panchaka doshas
- Consider Venus and Jupiter positions
- Check for auspicious nakshatras (Rohini, Uttara, etc.)
- Avoid Ritusandhi (junction periods)
- Consider weekday associations

### Travel Muhurta
- Consider Moon position and strength
- Check for favorable Karana and Yoga
- Avoid Rahu Kalam and Yamaganda
- Calculate direction-specific timing factors
- Include journey duration considerations

### Business Muhurta
- Focus on Mercury, Jupiter, and Venus positions
- Consider strength of the 2nd, 9th, and 11th houses
- Check for auspicious yogas for prosperity
- Avoid Bhadra periods for new ventures
- Include Moon-nakshatra relationship

### House Construction Muhurta
- Consider Saturn and Jupiter positions
- Check for favorable Nakshatra for foundation
- Avoid Ritusandhi and Panchaka
- Calculate auspicious direction aspects
- Include special Vastu considerations

### Medical Procedure Muhurta
- Focus on Moon position and aspects
- Consider strength of the 8th house
- Avoid combustion periods for key planets
- Include timing for specific body parts
- Consider recovery period timing

### Education Muhurta
- Focus on Jupiter, Mercury, and Moon
- Consider 5th and 9th house influences
- Calculate auspicious day for beginning studies
- Include suitable hora for specific subjects
- Consider weekday associations with subjects

### Religious Ceremony Muhurta
- Check for auspicious tithis and nakshatras
- Consider benefic planetary hour (hora)
- Avoid malefic yoga combinations
- Include special considerations for deity
- Calculate abhijit muhurta if applicable

## Input/Output Formats

Each endpoint should accept JSON input and return JSON responses with consistent structure:

```json
// Example request format
{
  "activity": "marriage",
  "start_date": "2023-04-01",
  "end_date": "2023-06-30",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timezone": "Asia/Kolkata",
  "options": {
    "minimum_rank": "good",
    "consider_hora": true,
    "avoid_retrograde": true
  }
}

// Example response format
{
  "status": "success",
  "data": {
    "auspicious_timings": [
      {
        "start_time": "2023-04-15T09:30:00+05:30",
        "end_time": "2023-04-15T11:15:00+05:30",
        "rank": "excellent",
        "score": 85,
        "panchanga": {
          "tithi": "Shukla Panchami",
          "nakshatra": "Rohini",
          "yoga": "Siddha",
          "karana": "Bava"
        },
        "factors": {
          "positive": ["Jupiter in strength", "Venus in own sign", "Auspicious Nakshatra"],
          "negative": ["Weak Mars", "8th house aspected"]
        }
      },
      // Additional time periods...
    ]
  },
  "meta": {
    "version": "1.0",
    "processing_time": "0.567s"
  }
}
```

## Error Handling

All endpoints should return appropriate HTTP status codes and error messages:

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_DATE_RANGE",
    "message": "The specified date range is too large. Maximum range is 90 days."
  },
  "meta": {
    "version": "1.0"
  }
}
```

## Muhurta System Notes

1. Electional astrology requires precise astronomical calculations
2. Different activities have different criteria for auspiciousness
3. Rank timings as "excellent", "good", "neutral", "inauspicious"
4. Consider cultural and regional variations in muhurta rules
5. Allow for personal chart considerations when available
6. Support standard exceptions (e.g., emergency procedures don't need muhurta)
7. Include explanations of key auspicious/inauspicious factors 