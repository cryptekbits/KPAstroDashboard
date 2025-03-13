# Core Astrological Calculations

This directory contains the core calculation logic for various astrological systems and techniques. These components are used by the API endpoints to perform the necessary calculations.

## Components

### Basic Details
- Ayanamsha calculation (multiple systems)
- Sidereal time calculation
- Ascendant (Lagna) and house cusp calculations
- Planetary positions and details (Rasi, Degree, Speed, etc.)
- House systems implementation (Placidus, Koch, Equal, etc.)

### Dasha Calculations
- Vimshottari Dasha (up to 5 levels)
- Yogini Dasha
- Chara Dasha
- Dasha balance calculations

### Ashtakvarga
- Bhinnashtakvarga (individual planet scores)
- Sarvashtakvarga (total scores)
- Ashtakvarga reduction calculations
- Ashtakvarga chart generation

### Shadbala
- Planetary strength calculations
- Bhava Bala calculations
- Ishta/Kashta Phala determination

### Divisional Charts
- D1 (Rashi/Lagna Chart)
- D9 (Navamsa)
- Moon Chart
- Lagna Chalit
- Moon Chalit
- D3 (Drekkana)
- D4 (Chaturthamsa)
- D7 (Saptamsa)
- D8 (Ashtamsa)
- D10 (Dasamsa)
- D12 (Dwadashamsha)
- D16 (Shodasamsa)
- D20 (Vimsamsa)
- D24 (Chaturvimsamsa)
- D27 (Bhamsha/Nakshatramsa)
- D30 (Trimsamsa)
- D40 (Khavedamsa)
- D45 (Akshavedamsa)
- D60 (Shastiamsa)
- Hora Chart

### Yogas
- General yogas based on planetary combinations
- Specific yogas (Gajakesari, Raja Yogas, etc.)
- Panchang yogas
- Kal Sarpa Dosha detection
- Lal Kitab yogas

### KP System
- KP planetary positions
- KP sublord calculations
- KP significator determination
- KP cuspal interlinks

### Lal Kitab
- Lal Kitab planetary positions
- Lal Kitab house effects
- Lal Kitab remedies calculation
- Lal Kitab debts identification

### Matchmaking
- Ashtakoot matching logic
- Dashkoot matching logic
- Manglik dosha analysis
- Overall compatibility calculations

## Integration Notes

1. These modules should leverage the existing `flatlib` and `astro_engine` libraries
2. Each calculation module should be self-contained with clear input/output interfaces
3. Performance optimization is critical for complex calculations
4. Each module should implement proper error handling and validation
5. All calculations should be extensively tested for accuracy
6. Logging should be implemented for debugging purposes 