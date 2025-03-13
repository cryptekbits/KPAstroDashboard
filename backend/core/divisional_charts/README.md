# Divisional Charts Calculation Modules

This directory contains modules for calculating various divisional charts (vargas) used in Vedic astrology.

## Components

### D1 (Rashi/Birth Chart)
The main birth chart showing planetary positions in signs.

**Implementation Requirements:**
- Calculate accurate planetary positions for given date, time, and location
- Support multiple ayanamsha systems (Lahiri, Raman, KP, etc.)
- Determine sign placement for all planets
- Calculate precise degrees within signs
- Handle retrograde planets properly

**Integration Points:**
- Ephemeris calculation modules
- Time and location utilities
- Ayanamsha calculation utilities

### D9 (Navamsa)
The ninth harmonic chart, important for marriage and dharma.

**Implementation Requirements:**
- Calculate Navamsa divisions from D1 chart
- Support multiple calculation methods (Parashara, Lahiri, etc.)
- Determine sign placement in Navamsa
- Calculate precise degrees within Navamsa signs
- Support special Navamsa calculation rules

**Integration Points:**
- D1 chart data
- Division calculation utilities
- Navamsa interpretation modules

### Moon Chart
Chart with Moon as the ascendant.

**Implementation Requirements:**
- Rearrange D1 chart with Moon sign as first house
- Maintain all planetary positions and relationships
- Calculate house cusps from Moon position
- Support different house division systems
- Provide house-sign correspondences

**Integration Points:**
- D1 chart data
- House calculation modules
- Moon position calculation

### Lagna Chalit
Modified birth chart showing planets in houses.

**Implementation Requirements:**
- Use D1 planetary positions
- Calculate house cusps accurately
- Place planets in houses based on their actual degrees
- Handle planets near house cusps correctly
- Support multiple house systems

**Integration Points:**
- D1 chart data
- House cusp calculation modules
- Degree comparison utilities

### Moon Chalit
Modified chart showing planets in houses from Moon.

**Implementation Requirements:**
- Use Moon chart as basis
- Calculate house cusps from Moon
- Place planets in houses based on their actual degrees
- Handle planets near house cusps correctly
- Support multiple house systems

**Integration Points:**
- Moon chart data
- House cusp calculation modules
- Degree comparison utilities

### Other Divisional Charts
Implementation for various other divisional charts (D3, D4, D7, etc.).

**Implementation Requirements:**
- Implement standardized calculation for each divisional chart
- Support traditional and modern calculation methods
- Calculate accurate sign placement in each division
- Determine house relationships in each division
- Support special rules for specific divisional charts

**Implementation Details:**
- D3 (Drekkana): 3rd division, siblings and courage
- D4 (Chaturthamsa): 4th division, property and assets
- D7 (Saptamsa): 7th division, children and progeny
- D10 (Dasamsa): 10th division, career and profession
- D12 (Dwadasamsa): 12th division, parents and ancestry
- D16 (Shodasamsa): 16th division, vehicles and comforts
- D20 (Vimsamsa): 20th division, spiritual practices
- D24 (Chaturvimsamsa): 24th division, education and learning
- D27 (Bhamsa/Nakshatramsa): 27th division, strength and vitality
- D30 (Trimsamsa): 30th division, misfortunes and challenges
- D40 (Khavedamsa): 40th division, auspicious and inauspicious effects
- D45 (Akshavedamsa): 45th division, overall fortune and prosperity
- D60 (Shastiamsa): 60th division, overall karma and specific influences
- Hora Chart: Half-sign divisions related to wealth

**Integration Points:**
- D1 chart data
- Division calculation utilities for each varga
- Sign and degree calculation modules

## Utility Functions

### Division Calculation Utilities
- Calculate division points for any harmonic
- Support special divisional calculations (unequal divisions)
- Handle edge cases at sign boundaries
- Perform degree conversions between divisions

### Varga Analysis Utilities
- Determine strength based on varga positions
- Calculate vargottama (same sign in D1 and D9)
- Analyze multiple varga placements
- Implement Shad-varga, Sapta-varga, and Dasha-varga calculations

### Varga Visualization Utilities
- Format divisional chart data for rendering
- Support different chart display styles
- Generate comparative varga displays
- Prepare data for chart image generation

## Implementation Notes

1. All divisional calculations should be thoroughly tested against verified examples
2. Implement proper error handling for edge cases
3. Optimize performance for multiple chart calculations
4. Support both traditional and modern calculation methods
5. Make calculations configurable for different astrological traditions
6. Document the specific divisional algorithm used for each chart
7. Consider caching strategies for expensive calculations
8. Allow for custom divisional chart calculation methods 