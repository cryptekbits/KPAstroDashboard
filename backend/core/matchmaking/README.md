# Matchmaking Core Component

This directory contains the core calculation components for astrological compatibility and matchmaking.

## Overview

The Matchmaking module implements various systems for analyzing compatibility between individuals based on their birth charts. It incorporates traditional Vedic compatibility methods like Guna Milan (Ashtakoot), Western synastry and composite techniques, as well as specialized matchmaking systems. This module provides comprehensive relationship analysis, scoring, and interpretation capabilities.

## Key Components

### 1. Ashtakoot (Guna Milan) System

Implementation of the traditional 36-point Vedic compatibility system.

**Implementation Requirements:**
- Calculate all 8 Kootas (Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi)
- Implement correct scoring for each Koota
- Calculate total compatibility percentage
- Provide detailed interpretation for each Koota match/mismatch
- Support customizable weightage systems
- Implement special exception rules (Kuja Dosha cancellations, etc.)

### 2. Dasha Compatibility

Analysis of compatibility based on planetary periods (dashas).

**Implementation Requirements:**
- Compare current and upcoming dashas of both individuals
- Identify favorable and challenging dasha combinations
- Calculate temporal compatibility variations
- Implement dasha-based relationship development prediction
- Provide timing for relationship milestones
- Support multiple dasha systems for comparison

### 3. Western Synastry System

Implementation of Western astrological approach to relationship compatibility.

**Implementation Requirements:**
- Calculate all planetary aspects between two charts
- Implement house overlay analysis
- Determine significant interaspects and their interpretations
- Calculate aspect strength and orbs
- Identify challenging and harmonious patterns
- Support comprehensive synastry report generation

### 4. Composite Chart Analysis

Implementation of the composite chart method for relationship analysis.

**Implementation Requirements:**
- Calculate accurate composite chart (midpoint method)
- Implement Davison relationship chart option
- Analyze composite chart planetary placements and aspects
- Calculate composite house interpretations
- Determine relationship strengths and challenges
- Support predictive analysis of relationship development

### 5. Nakshatra Compatibility (Kuja Dosha)

Implementation of nakshatra-based compatibility systems.

**Implementation Requirements:**
- Calculate nakshatra compatibility using 13-point system
- Implement Kuja Dosha (Mangal Dosha) detection
- Determine other dosha interactions between charts
- Calculate nakshatra-based relationship dynamics
- Implement nakshatra lord compatibility
- Support pada (quarter) level compatibility assessment

### 6. Planetary Relationship Analysis

Detailed analysis of how planets in one chart affect the other.

**Implementation Requirements:**
- Calculate mutual reception between charts
- Implement detailed planetary influence analysis
- Determine impact of one's planets on other's houses
- Calculate relationship-specific planetary strength
- Implement comparative benefic/malefic assessment
- Support detailed aspect-based interpretation

### 7. Compatibility Scoring and Reporting

Comprehensive scoring and report generation system.

**Implementation Requirements:**
- Calculate unified compatibility score incorporating multiple systems
- Implement weighted scoring based on relationship type
- Generate detailed compatibility reports
- Provide specific advice for improving relationship dynamics
- Calculate compatibility for different life areas
- Support customizable report formats and detail levels

## Technical Requirements

### Performance Considerations
- Optimize calculations for quick matchmaking analysis
- Implement caching system for partial results
- Use efficient algorithms for aspect and relationship calculations
- Consider parallel processing for batch compatibility matching

### Accuracy & Validation
- Ensure perfect alignment with traditional matchmaking rules
- Validate against known compatible/incompatible examples
- Test against diverse chart combinations
- Implement comprehensive error checking
- Support multiple cultural matchmaking traditions

### Integration Points
- Interface with chart calculation modules
- Integration with remedial measures system
- Connection to report generation services
- API support for frontend visualization of compatibility
- Integration with AI prediction models for relationship outcomes

## Usage Examples

```python
# Example (conceptual): Calculating compatibility between two charts
from backend.core.matchmaking import CompatibilityCalculator
from backend.core.chart import BirthChart

# Create birth chart instances
chart1 = BirthChart(
    datetime="1990-01-01T12:00:00", 
    latitude=28.6139, 
    longitude=77.2090,
    timezone="Asia/Kolkata",
    gender="female",
    name="Person A"
)

chart2 = BirthChart(
    datetime="1988-05-15T15:30:00", 
    latitude=19.0760, 
    longitude=72.8777,
    timezone="Asia/Kolkata",
    gender="male",
    name="Person B"
)

# Initialize the compatibility calculator
compatibility = CompatibilityCalculator(chart1, chart2)

# Get Ashtakoot (Guna Milan) compatibility
ashtakoot = compatibility.calculate_ashtakoot()
print(f"Ashtakoot Score: {ashtakoot.total_score}/36 ({ashtakoot.percentage}%)")
for koota, details in ashtakoot.detailed_scores.items():
    print(f"{koota}: {details.score}/{details.max_score} - {details.interpretation}")

# Get Nakshatra compatibility
nakshatra_comp = compatibility.calculate_nakshatra_compatibility()
print(f"Nakshatra Compatibility: {nakshatra_comp.score}/13")
print(f"Kuja Dosha Status: {nakshatra_comp.kuja_dosha_status}")

# Get Western synastry highlights
synastry = compatibility.calculate_synastry()
print("\nKey Synastry Aspects:")
for aspect in synastry.significant_aspects:
    print(f"{aspect.planet1} {aspect.aspect_type} {aspect.planet2} (Orb: {aspect.orb}°)")
    print(f"Interpretation: {aspect.interpretation}")

# Get composite chart analysis
composite = compatibility.calculate_composite_chart()
print("\nComposite Chart Highlights:")
for highlight in composite.highlights:
    print(f"- {highlight}")

# Get overall compatibility assessment
overall = compatibility.calculate_overall_compatibility()
print(f"\nOverall Compatibility Score: {overall.score}/100")
print(f"Relationship Strengths: {overall.strengths}")
print(f"Relationship Challenges: {overall.challenges}")
print(f"Recommendation: {overall.recommendation}")
```

## Visualization Support

Implementation for generating visual representations of:

1. Ashtakoot compatibility table
2. Synastry aspect grid
3. Composite chart wheel
4. Relationship strength/challenge radar charts
5. Timeline of relationship development

## Testing Strategy

Implement comprehensive testing with:

1. Unit tests for individual compatibility components
2. Integration tests for full compatibility assessment
3. Validation tests against known compatible/incompatible pairs
4. Cultural variation testing for different matchmaking systems
5. Performance benchmarking for optimization

## References

List of authoritative texts for matchmaking:

1. Brihat Parashara Hora Shastra
2. Muhurta Chintamani
3. Narada Samhita
4. Western texts on synastry and composite analysis
5. Research papers on astrological compatibility

## Future Enhancements

1. Machine learning integration for predictive relationship outcomes
2. Expanded psychological compatibility analysis
3. Integration with biorhythm and other complementary systems
4. Multi-person compatibility for family and group dynamics
5. Longitudinal relationship development forecasting 