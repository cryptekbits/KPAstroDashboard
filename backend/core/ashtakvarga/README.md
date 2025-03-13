# Ashtakvarga Core Component

This directory contains the core calculation components for Ashtakvarga system in Vedic astrology.

## Overview

Ashtakvarga is an important predictive tool in Vedic astrology that assesses the strength and contributions of planets across all houses of a birth chart. It consists of 8 Varga charts (7 for planets and 1 combined). This module implements the calculation, analysis, and interpretation of Ashtakvarga.

## Key Components

### 1. Bindu (Point) Calculator

The Bindu Calculator determines the benefic points (Bindus) for each planet in each house according to classical rules.

**Implementation Requirements:**
- Calculate Sarvashtakvarga (combined) bindu counts for all houses
- Determine individual planet bindus in each house (Prastarashtakvarga)
- Implement classical rules for bindu contribution of each planet
- Support for benefic and malefic bindu calculation

### 2. Kaksha Vibhaga (Subdivision) System

Implementation of the subdivision of Ashtakvarga bindus within signs.

**Implementation Requirements:**
- Calculate 30 sub-divisions within each sign
- Determine exact degree-level bindu distribution
- Support for micro-analysis of planetary positions within bindu zones
- Map bindus to specific degrees for transit timing

### 3. Trikona Shodhana (Trine Reduction)

Implementation of the reduction process for triplicities.

**Implementation Requirements:**
- Perform reduction of bindus in trines (same element signs)
- Calculate reduced values according to classical methods
- Implement the full reduction sequence
- Provide interpretive data for reduced values

### 4. Ekadhipatya Shodhana (Lordship Reduction)

Implementation of the reduction process for houses ruled by the same planet.

**Implementation Requirements:**
- Identify signs with the same planetary ruler
- Apply reduction rules for planets with dual lordship
- Calculate reduced values of bindus
- Preserve both raw and reduced bindu counts

### 5. Transit Analysis System

Tools for analyzing planetary transits through the lens of Ashtakvarga.

**Implementation Requirements:**
- Calculate favorable transit periods using Ashtakvarga
- Implement Gochara (transit) strength assessment
- Determine peak bindu zones for each planet
- Generate timing predictions based on bindu density

### 6. Sodhya Pindas (Final Assessment)

The final reduction and assessment system that leads to Sodhya Pindas.

**Implementation Requirements:**
- Calculate final reduced bindu totals
- Implement all steps of the traditional reduction process
- Generate Sodhya Pindas and their interpretations
- Calculate overall chart strength based on final pindas

### 7. Ashtakvarga Interpretation Engine

System for interpreting the meaning and effects of Ashtakvarga calculations.

**Implementation Requirements:**
- Detailed analysis of house strength based on bindu counts
- Assessment of planetary strength through bindu analysis
- Prediction system based on transit through high/low bindu areas
- Recommendation engine based on Ashtakvarga analysis

## Technical Requirements

### Performance Considerations
- Optimize calculations for speed, especially for multiple chart analysis
- Implement caching system for intermediate calculation results
- Use efficient algorithms for reduction processes
- Consider parallel processing for bindu calculations

### Accuracy & Validation
- Ensure perfect alignment with classical Ashtakvarga calculation rules
- Implement comprehensive testing against reference charts
- Validate results against known classical examples
- Ensure consistent results across different chart formats and systems

### Integration Points
- Interface with core planetary calculation modules
- Integration with transit calculation system
- Connection to Dasha (planetary period) analysis
- API support for frontend visualization of Ashtakvarga charts

## Usage Examples

```python
# Example (conceptual): Calculating Ashtakvarga for a chart
from backend.core.ashtakvarga import AshtakvargaCalculator
from backend.core.chart import BirthChart

# Create a birth chart instance
chart = BirthChart(datetime="1990-01-01T12:00:00", latitude=28.6139, 
                  longitude=77.2090, timezone="Asia/Kolkata")

# Initialize the Ashtakvarga calculator
ashtakvarga = AshtakvargaCalculator(chart)

# Get Sarvashtakvarga (total bindus for all planets)
sarva = ashtakvarga.get_sarvashtakvarga()
print(f"Sarvashtakvarga bindus: {sarva.bindu_counts}")

# Get individual planet's Ashtakvarga
jupiter_ashtakvarga = ashtakvarga.get_planet_ashtakvarga("Jupiter")
print(f"Jupiter's beneficial houses: {jupiter_ashtakvarga.get_strong_houses()}")

# Calculate transit favorability for a planet
transit_date = "2023-01-01"
jupiter_transit_score = ashtakvarga.calculate_transit_score("Jupiter", transit_date)
print(f"Jupiter transit score on {transit_date}: {jupiter_transit_score}/8")

# Get recommendations for favorable periods
favorable_periods = ashtakvarga.get_favorable_transit_periods("Sun", 
                                        start_date="2023-01-01", 
                                        end_date="2023-12-31",
                                        minimum_score=5)
for period in favorable_periods:
    print(f"Favorable Sun transit: {period.start} to {period.end}")
```

## Visualization Support

Implementation for generating visual representations of:

1. Prastarashtakvarga (individual planet bindus) as 12x7 grid
2. Sarvashtakvarga (combined bindus) as circular or linear chart
3. Kaksha Vibhaga (degree-level bindus) as detailed sign maps
4. Reduction process visualization
5. Transit analysis overlay on Ashtakvarga

## Testing Strategy

Implement comprehensive testing with:

1. Unit tests for each calculation step in isolation
2. Integration tests for full reduction sequence
3. Validation tests against known charts with published Ashtakvarga values
4. Performance benchmarking for optimization
5. Edge case testing for unusual planetary configurations

## References

List of authoritative texts for Ashtakvarga calculations:

1. Brihat Parashara Hora Shastra
2. Jataka Parijata
3. Sarvartha Chintamani
4. Phaladeepika
5. Brihat Jataka

## Future Enhancements

1. Advanced transit timing based on degree-level Kaksha Vibhaga
2. Integration with Shadbala for comprehensive strength assessment
3. Expanded interpretation database for house-specific Ashtakvarga readings
4. Machine learning analysis of correlation between Ashtakvarga and life events
5. Comparative Ashtakvarga analysis for relationship compatibility 