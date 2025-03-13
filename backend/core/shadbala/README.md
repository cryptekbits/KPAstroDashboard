# Shadbala Core Component

This directory contains the core calculation components for Shadbala (six-fold planetary strength) in Vedic astrology.

## Overview

Shadbala is a comprehensive system for assessing the strength of planets in a birth chart. It consists of six different types of strength calculations that are combined to determine the overall functional capability of each planet. This module implements the calculation, analysis, and interpretation of Shadbala according to classical texts.

## Key Components

### 1. Sthana Bala (Positional Strength)

Calculation of a planet's strength based on its position in the chart.

**Implementation Requirements:**
- Calculate Uchcha Bala (exaltation strength)
- Determine Saptavargaja Bala (strength in seven divisional charts)
- Implement Ojha-Yugma Bala (odd-even sign strength)
- Calculate Kendradi Bala (angular house strength)
- Compute Drekkana Bala (decanate strength)
- Implement algorithm for total Sthana Bala calculation

### 2. Dig Bala (Directional Strength)

Calculation of a planet's strength based on its placement in directional houses.

**Implementation Requirements:**
- Implement classical directional strength assignments for all planets
- Calculate accurate Dig Bala values based on house placement
- Support partial strength calculations for planets in transition zones
- Implement maximum Dig Bala reference values

### 3. Kala Bala (Temporal Strength)

Calculation of a planet's strength based on time factors.

**Implementation Requirements:**
- Calculate Natonnata Bala (ascension/declension strength)
- Implement Paksha Bala (lunar phase strength)
- Calculate Tribhaga Bala (three-segments-of-day strength)
- Determine Abda Bala (annual strength)
- Calculate Masa Bala (monthly strength)
- Implement Vara Bala (weekday strength)
- Calculate Hora Bala (planetary hour strength)
- Determine Ayana Bala (solstice strength)
- Implement Yuddha Bala (planetary war strength)
- Calculate total Kala Bala per classical formulas

### 4. Cheshta Bala (Motional Strength)

Calculation of a planet's strength based on its motion.

**Implementation Requirements:**
- Calculate strength based on retrograde, direct, or stationary motion
- Implement velocity-based strength calculations
- Determine phase-based strength components
- Calculate accurate Cheshta Bala values according to classical rules
- Support special Cheshta Bala rules for Sun and Moon

### 5. Naisargika Bala (Natural Strength)

Calculation of a planet's innate strength independent of its position.

**Implementation Requirements:**
- Implement fixed natural strength values assigned to each planet
- Support customizable natural strength assignments

### 6. Drig Bala (Aspectual Strength)

Calculation of a planet's strength based on aspects received and cast.

**Implementation Requirements:**
- Calculate beneficial aspect strength from each planet
- Determine malefic aspect strength from each planet
- Implement classical aspect calculation rules
- Calculate total Drig Bala according to classical formulas
- Support partial and full aspect strength calculations

### 7. Ishta and Kashta Phala (Beneficial and Malefic Effects)

System for calculating the beneficial and malefic potentials of planets.

**Implementation Requirements:**
- Calculate Ishta Phala (beneficial effect) for each planet
- Determine Kashta Phala (malefic effect) for each planet
- Implement classical formulas for effect calculations
- Provide interpretations for the Ishta-Kashta ratio

### 8. Total Shadbala and Minimum Requirements

The final calculation system for total planetary strength.

**Implementation Requirements:**
- Calculate final Shadbala total values for each planet
- Determine Shadbala in Rupas (traditional units)
- Compare to minimum required strengths by planet
- Calculate relative strength percentages
- Provide deficiency/excess analysis for each planet

## Technical Requirements

### Performance Considerations
- Optimize calculations for speed due to mathematical complexity
- Implement caching system for intermediate calculation results
- Use efficient algorithms for astronomical calculations
- Consider parallel processing for planet-by-planet calculations

### Accuracy & Validation
- Ensure perfect alignment with classical Shadbala calculation rules
- Validate against known examples from classical texts
- Implement comprehensive testing against reference charts
- Ensure precision in decimal calculations

### Integration Points
- Interface with core planetary calculation modules
- Integration with Astro-Engine for accurate astronomical parameters
- Connection to interpretation and recommendation systems
- API support for frontend visualization of Shadbala results

## Usage Examples

```python
# Example (conceptual): Calculating Shadbala for a chart
from backend.core.shadbala import ShadbalaCalculator
from backend.core.chart import BirthChart

# Create a birth chart instance
chart = BirthChart(datetime="1990-01-01T12:00:00", latitude=28.6139, 
                  longitude=77.2090, timezone="Asia/Kolkata")

# Initialize the Shadbala calculator
shadbala = ShadbalaCalculator(chart)

# Get complete Shadbala for all planets
complete_shadbala = shadbala.calculate_complete_shadbala()

# Get Shadbala for a specific planet
jupiter_shadbala = shadbala.get_planet_shadbala("Jupiter")
print(f"Jupiter's total Shadbala: {jupiter_shadbala.total_shadbala} Rupas")
print(f"Minimum required: {jupiter_shadbala.minimum_required} Rupas")
print(f"Strength ratio: {jupiter_shadbala.strength_ratio}")

# Get specific bala component
jupiter_dig_bala = shadbala.get_specific_bala("Jupiter", "dig_bala")
print(f"Jupiter's Dig Bala: {jupiter_dig_bala} Virupas")

# Get strongest and weakest planets
strongest_planet = shadbala.get_strongest_planet()
weakest_planet = shadbala.get_weakest_planet()
print(f"Strongest planet: {strongest_planet.name} with {strongest_planet.total_shadbala} Rupas")
print(f"Weakest planet: {weakest_planet.name} with {weakest_planet.total_shadbala} Rupas")

# Get Ishta and Kashta Phala
ishta_phala = shadbala.get_ishta_phala("Saturn")
kashta_phala = shadbala.get_kashta_phala("Saturn")
print(f"Saturn's beneficial effect (Ishta Phala): {ishta_phala}")
print(f"Saturn's malefic effect (Kashta Phala): {kashta_phala}")
```

## Visualization Support

Implementation for generating visual representations of:

1. Complete Shadbala chart with all six strength components
2. Comparative strength analysis across planets
3. Strength vs. minimum required visualization
4. Ishta-Kashta ratio charts
5. Individual Bala component breakdown visuals

## Testing Strategy

Implement comprehensive testing with:

1. Unit tests for each strength component calculation
2. Integration tests for complete Shadbala calculation
3. Validation tests against published reference calculations
4. Edge case testing for unusual planetary configurations
5. Performance benchmarking for optimization

## References

List of authoritative texts for Shadbala calculations:

1. Brihat Parashara Hora Shastra
2. Jataka Parijata
3. Sarvartha Chintamani
4. Phaladeepika
5. Brihat Jataka

## Future Enhancements

1. Integration with Ashtakvarga for comprehensive planet assessment
2. Machine learning correlation studies between Shadbala and planetary effects
3. Dynamic analysis of changing strength during planetary transits
4. Alternative strength calculation methods from other classical sources
5. Advanced remedial recommendations based on Shadbala deficiencies 