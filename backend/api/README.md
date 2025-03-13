# API Endpoints

This directory contains all the API endpoint implementations for the astrology website.

## Endpoints Structure

The API endpoints are organized by feature categories, each in its own subdirectory:

### Birth Details
- `POST /birth_details` - Calculate basic birth details
- `POST /geo_details` - Location and place suggestions
- `POST /timezone` - Timezone calculation and conversion

### Panchang
- `POST /panchang/daily` - Daily panchang details
- `POST /panchang/advanced` - Advanced panchang details
- `POST /panchang/tamil` - Tamil panchang details
- `POST /panchang/monthly` - Monthly panchang calendar
- `POST /panchang/festivals` - Festival calendar
- `POST /panchang/sunrise_sunset` - Sunrise and sunset timings
- `POST /chaughadiya` - Chaughadiya muhurta timings
- `POST /hora` - Hora timings

### Kundli (Birth Chart)
- `POST /kundli/basic` - Basic kundli information
- `POST /kundli/houses` - House details
- `POST /kundli/planets` - Planetary positions and details
- `POST /kundli/vimshottari_dasha` - Vimshottari dasha calculations
- `POST /kundli/current_vdasha_date` - Current dasha for a given date
- `POST /kundli/ashtakvarga` - Ashtakvarga calculations
- `POST /kundli/shadbala` - Shadbala calculations
- `POST /kundli/jaimini_details` - Jaimini astrology details
- `POST /kundli/yogas` - Yoga calculations and analysis
- `POST /kundli/chart/{chart_id}` - Divisional chart data
- `POST /kundli/chart_image/{chart_id}` - Divisional chart image

### KP System
- `POST /kp/planets` - KP planetary positions and sublords
- `POST /kp/cusps` - KP house cusp positions and sublords
- `POST /kp/chart` - KP chart data
- `POST /kp/significators` - KP significator analysis
- `POST /kp/details` - Detailed KP analysis
- `POST /kp/dasha` - KP dasha calculations
- `POST /kp/transit` - KP transit analysis

### Lal Kitab
- `POST /lalkitab/horoscope` - Lal Kitab horoscope
- `POST /lalkitab/reports` - Lal Kitab reports
- `POST /lalkitab/debts` - Lal Kitab debts analysis
- `POST /lalkitab/remedies` - Lal Kitab remedies
- `POST /lalkitab/houses` - Lal Kitab house analysis
- `POST /lalkitab/planets` - Lal Kitab planetary analysis

### Numerology
- `POST /numerology/table` - Numerology calculation table
- `POST /numerology/report` - Numerology detailed report
- `POST /numerology/fav_time` - Favorable time calculations
- `POST /numerology/place_vastu` - Place and vastu analysis
- `POST /numerology/fasts_report` - Fasting recommendations
- `POST /numerology/fav_lord` - Favorable deity
- `POST /numerology/fav_mantra` - Favorable mantras

### Muhurta
- `POST /muhurta/auspicious` - Auspicious timing for various activities

### Predictions
- `POST /predictions/daily/{zodiac_sign}` - Daily sun sign predictions
- `POST /predictions/daily/nakshatra` - Daily nakshatra predictions
- `POST /predictions/custom_daily_prediction/{zodiac_sign}` - Customized daily predictions
- `POST /predictions/weekly/{zodiac_sign}` - Weekly predictions
- `POST /predictions/monthly/{zodiac_sign}` - Monthly predictions
- `POST /predictions/chinese_year_forecast` - Chinese zodiac yearly forecast
- `POST /predictions/yearly` - Yearly predictions (Varshaphal)

### Compatibility and Matchmaking
- `POST /matchmaking/basic` - Basic compatibility analysis
- `POST /matchmaking/ashtakoota` - Ashtakoot matching
- `POST /matchmaking/dashkoota` - Dashkoot matching
- `POST /matchmaking/manglik` - Manglik dosha analysis
- `POST /matchmaking/report` - Comprehensive matching report
- `POST /matchmaking/percentage` - Compatibility percentage
- `POST /matchmaking/detailed_report` - Detailed compatibility report

### Remedies
- `POST /remedies/gemstone` - Gemstone recommendations
- `POST /remedies/rudraksha` - Rudraksha recommendations
- `POST /remedies/puja` - Puja recommendations
- `POST /remedies/mantra` - Mantra recommendations
- `POST /remedies/manglik` - Manglik dosha remedies
- `POST /remedies/kalsarpa` - Kalsarpa dosha remedies
- `POST /remedies/pitra_dosha` - Pitra dosha remedies
- `POST /remedies/sadhesati` - Sadhesati remedies

### Specialized Reports
- `POST /partner_report` - Partnership analysis
- `POST /pitra_dosha_report` - Pitra dosha analysis
- `POST /kalsarpa_details` - Kalsarpa dosha details
- `POST /kalsarpa_remedy` - Kalsarpa dosha remedies
- `POST /ghat_chakra` - Ghat Chakra analysis
- `POST /planet_nature` - Planetary nature analysis
- `POST /papasamyam_details` - Papasamyam analysis
- `POST /planet_ashtak/:planet_name` - Planet-specific Ashtakvarga
- `POST /sarvashtak` - Sarvashtakvarga analysis

### Varshaphal (Annual Predictions)
- `POST /varshaphal/details` - Varshaphal details
- `POST /varshaphal/planets` - Planetary positions in Varshaphal
- `POST /varshaphal/mudda_dasha` - Mudda dasha calculations
- `POST /varshaphal/year_chart` - Annual chart
- `POST /varshaphal/yoga` - Varshaphal yogas
- `POST /varshaphal/saham_points` - Saham points calculation
- `POST /varshaphal/panchavargeeya_bala` - Panchavargeeya Bala in Varshaphal
- `POST /varshaphal/harsha_bala` - Harsha Bala in Varshaphal
- `POST /varshaphal/muntha` - Muntha calculation and analysis

## Implementation Notes

1. Each endpoint should validate input data
2. Responses should follow a consistent JSON structure
3. Error handling should be consistent across all endpoints
4. Authentication middleware should be applied where appropriate
5. Rate limiting should be implemented for public-facing endpoints 