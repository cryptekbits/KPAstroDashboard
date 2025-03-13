# Dasha Calculation Modules

This directory contains modules for calculating various dasha (planetary period) systems used in Vedic astrology.

## Components

### Vimshottari Dasha
The most commonly used dasha system, based on the Moon's nakshatra at birth.

**Implementation Requirements:**
- Calculate Mahadasha periods (main planetary periods)
- Calculate Antardasha periods (sub-periods)
- Calculate Pratyantardasha (sub-sub-periods)
- Calculate Sookshma and Prana dashas (4th and 5th levels)
- Calculate dasha balance at birth
- Determine current running dasha for any given date
- Handle edge cases properly (e.g., retrograde planets, etc.)

**Integration Points:**
- Moon nakshatra calculation
- Date/time utilities for period calculations
- Chart data access for planetary positions

### Yogini Dasha
An 8-year cycle dasha system related to the 8 goddesses.

**Implementation Requirements:**
- Calculate Yogini dasha periods based on Moon nakshatra
- Calculate sub-periods
- Determine current running Yogini dasha
- Calculate dasha balance at birth

**Integration Points:**
- Moon nakshatra calculation
- Date/time utilities for period calculations
- Chart data access for natal positions

### Chara Dasha
A dasha system based on movable (chara) signs.

**Implementation Requirements:**
- Calculate Chara dasha periods
- Calculate sub-periods
- Determine current running Chara dasha
- Calculate dasha balance at birth
- Handle special calculation rules

**Integration Points:**
- Rashi (sign) calculations
- Date/time utilities for period calculations
- Chart data access for house and sign positions

## Utility Functions

### Dasha Balance Calculations
- Calculate remaining dasha at birth
- Convert dasha balance to years, months, and days
- Handle edge cases in dasha transitions

### Dasha Prediction Utilities
- Categorize dashas by benefic/malefic influence
- Provide dasha significance based on chart factors
- Calculate peak periods within dashas

### Dasha Conversion Utilities
- Convert between different date formats
- Calculate exact transition moments
- Handle timezone considerations in dasha calculations

## Implementation Notes

1. All dasha calculations should be thoroughly tested against verified examples
2. Performance optimization is critical for multi-level dasha calculations
3. Implement proper error handling for edge cases
4. Ensure accurate date/time calculations across time zones
5. Consider caching strategies for expensive calculations
6. Provide detailed documentation for each dasha system
7. Include examples and test cases for verification
8. Allow for different ayanamsha systems as input parameters 