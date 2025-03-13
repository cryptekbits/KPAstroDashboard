# Yogas Core Component

This directory contains the core calculation components for identifying and analyzing Yogas (planetary combinations) in Vedic astrology.

## Overview

Yogas are specific combinations of planets, houses, and signs that result in particular effects in an individual's life. This module provides calculation capabilities for detecting, analyzing, and interpreting various yogas present in a birth chart.

## Key Components

### 1. Yoga Detection Engine

The yoga detection engine systematically scans a horoscope to identify the presence of various yogas based on planetary positions, aspects, and house placements.

**Implementation Requirements:**
- High-performance algorithm for checking multiple yoga conditions simultaneously
- Support for customizable yoga definition rules
- Ability to detect partial and complete yoga formations
- Strength assessment for each identified yoga

### 2. Yoga Categories

#### Dhana (Wealth) Yogas
- Implementations for Lakshmi Yoga, Chandra-Mangala Yoga, Gajakesari Yoga, etc.
- Algorithms to assess the strength and potential financial impact of these yogas
- Timing analysis for when wealth yogas will activate

#### Raj (Power) Yogas
- Implementations for Pancha Mahapurusha Yogas (Ruchaka, Bhadra, Hamsa, Malavya, Sasa)
- Calculations for Raja Yoga formations from lords of Kendra and Trikona houses
- Algorithms for Neechabhanga Raja Yoga and other power-conferring combinations

#### Dharma-Karma Yogas
- Implementations for yogas related to spirituality, career, and life purpose
- Calculations for combinations like Sanyasa Yoga, Amala Yoga, etc.
- Analysis of dharma-related house lordships and connections

#### Dosha (Problematic) Yogas
- Implementations for Kemadruma Yoga, Daridra Yoga, Dainya Yoga, etc.
- Calculators for Graha Yuddha (planetary war) and its effects
- Algorithms for assessing the severity of challenging yogas

#### Special & Rare Yogas
- Implementations for Mahabhagya Yoga, Adhi Yoga, Vasumati Yoga, etc.
- Detection of complex and multi-planetary combinations
- Assessment of strength and life-area impact

### 3. Yoga Strength Calculator

The yoga strength calculator evaluates each identified yoga for its potency based on:

**Implementation Requirements:**
- Analysis of planet strength (Shadbala) contributing to the yoga
- Assessment of house positions and lordships involved
- Evaluation of aspect strength and conjunctions
- Accounting for cancellation factors or enhancement factors

### 4. Yoga Timing Analysis

This component predicts when yogas will manifest their effects through:

**Implementation Requirements:**
- Integration with Dasha (planetary period) system
- Transit activation points calculation
- Progressions and time-based triggers
- Peak activation period determination

### 5. Yoga Interpretation Engine

This component provides detailed meaning and effects of detected yogas:

**Implementation Requirements:**
- Detailed description database for each yoga
- Life area impact assessment
- Personalized interpretation based on chart context
- Recommendation generation based on yoga analysis

## Technical Requirements

### Performance Considerations
- Optimize for high-throughput processing of multiple charts
- Implement caching for frequently accessed yoga definitions
- Use efficient algorithms for planetary relationship detection
- Consider parallel processing for simultaneous yoga detection

### Accuracy & Validation
- Comprehensive test suite with known yoga examples
- Validation against classical astrological texts
- Peer review with astrological experts
- Error margin assessment for borderline yoga formations

### Integration Points
- Interface with core planetary calculation modules
- Integration with house and sign determination modules
- Connection to interpretation and report generation services
- API support for frontend yoga visualization

## Usage Examples

```python
# Example (conceptual): Detecting Raja Yogas in a chart
from backend.core.yogas.raj_yogas import RajaYogaDetector
from backend.core.chart import BirthChart

# Create a birth chart instance
chart = BirthChart(datetime="1990-01-01T12:00:00", latitude=28.6139, 
                  longitude=77.2090, timezone="Asia/Kolkata")

# Initialize the Raja Yoga detector
raja_yoga_detector = RajaYogaDetector(chart)

# Get all Raja Yogas present in the chart
raja_yogas = raja_yoga_detector.get_all_raja_yogas()

# Get strength assessment for each Raja Yoga
for yoga in raja_yogas:
    print(f"Yoga: {yoga.name}")
    print(f"Strength: {yoga.strength}/10")
    print(f"Primary activation period: {yoga.primary_activation_period}")
    print(f"Contributing planets: {yoga.contributing_planets}")
    print(f"Life areas affected: {yoga.life_areas}")
```

## Testing Strategy

Implement comprehensive testing with:

1. Unit tests for individual yoga detection algorithms
2. Integration tests for yoga strength assessment
3. Validation tests using charts with known yoga formations
4. Benchmark tests for performance optimization
5. Edge case testing for rare and complex yoga formations

## References

List of authoritative texts for yoga definitions:

1. Brihat Parashara Hora Shastra
2. Phaladeepika
3. Saravali
4. Jataka Parijata
5. Brihat Jataka

## Future Enhancements

1. Machine learning integration for pattern recognition of unclassified yogas
2. Statistical analysis of yoga manifestation in large chart datasets
3. Correlation studies between yoga presence and life events
4. API for community contribution to yoga definitions
5. Advanced visualization tools for yoga formation patterns 