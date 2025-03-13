# Data Directory

This directory contains various data files and datasets used by the astrology application's backend systems.

## Directory Structure

The data directory is organized into several subdirectories based on data type and purpose:

```
data/
├── astronomical/      # Astronomical data files and ephemeris
├── geographical/      # Geographical data and location databases
├── interpretations/   # Interpretation text and meaning databases
├── remedies/          # Remedial measures databases
├── reference/         # Reference data and lookup tables
└── test/              # Test data sets for validation
```

## Data Categories

### Astronomical Data

The `astronomical` directory contains celestial data needed for accurate astrological calculations:

- **Ephemeris Files**: High-precision planetary position data
- **Fixed Star Data**: Coordinates and properties of fixed stars
- **Asteroid Data**: Position data for major asteroids
- **Lunar Node Data**: North and South node calculations
- **Eclipse Data**: Solar and lunar eclipse information

### Geographical Data

The `geographical` directory contains location-based information:

- **City Database**: Worldwide cities with coordinates and timezones
- **Timezone Data**: Updated timezone definitions and DST rules
- **Country Codes**: ISO country codes and regional information
- **Altitude Data**: Elevation information for locations
- **Coordinates Mapping**: Conversion tables for different coordinate systems

### Interpretation Data

The `interpretations` directory contains text databases for generating astrological interpretations:

- **Planetary Positions**: Interpretations for planets in signs and houses
- **Aspects**: Meanings of various planetary aspects
- **Houses**: House position and rulership interpretations
- **Signs**: Zodiac sign characteristics and traits
- **Combinations**: Interpretations for various planetary combinations
- **Dashas**: Interpretation texts for planetary periods
- **Nakshatras**: Data on lunar mansions and their meanings
- **Yogas**: Definitions and interpretations of planetary yogas

### Remedies Data

The `remedies` directory contains information related to astrological remedies:

- **Gemstones**: Database of gemstones and their planetary associations
- **Mantras**: Collection of mantras for various planets and purposes
- **Rituals**: Details of remedial rituals and procedures
- **Herbs**: Herbal remedies and their astrological correspondences
- **Donation Items**: Lists of donation items for planetary propitiation
- **Timing Data**: Auspicious timing information for remedial measures

### Reference Data

The `reference` directory contains lookup tables and other reference information:

- **Dignity Tables**: Essential and accidental dignity scores
- **Ayanamsa Values**: Different ayanamsa calculation references
- **House Systems**: Parameters for various house division systems
- **Astronomical Constants**: Fixed values used in calculations
- **Compatibility Tables**: Reference data for matchmaking systems
- **Calendar Conversions**: Data for converting between calendar systems

### Test Data

The `test` directory contains datasets specifically for testing and validation:

- **Verified Charts**: Birth charts with verified details for testing
- **Expected Results**: Expected calculation results for validation
- **Edge Cases**: Special case data for testing extreme scenarios
- **Performance Test Data**: Large datasets for performance testing
- **Historical Events**: Correlated events data for predictive testing

## Data Formats

Data in this directory is stored in various formats optimized for their specific use:

- **JSON Files**: For structured data that needs to be human-readable
- **CSV Files**: For tabular data that may be processed by external tools
- **SQLite Databases**: For larger datasets requiring query capabilities
- **Binary Files**: For compact storage of extensive numerical data
- **YAML Files**: For configuration and mapping information

## Data Update Process

Many data files require periodic updates to maintain accuracy:

1. Astronomical ephemeris data updated annually
2. Timezone data updated with DST rule changes
3. Geographical location database updated quarterly
4. Interpretation databases expanded continuously
5. Test data enhanced as new validation scenarios are identified

## Usage Guidelines

When accessing data files from code:

1. Always use relative paths from the application root
2. Implement proper error handling for missing data files
3. Cache frequently accessed data to improve performance
4. Use the provided data access utilities in `backend.utils.data_access`
5. Validate data integrity after updates

## Data Quality Standards

All data files in this directory adhere to the following standards:

1. Source attribution for all external data
2. Version tracking for data file updates
3. Comprehensive documentation of data formats
4. Validation routines for data integrity checking
5. Clear licensing information for third-party data

## Integration with External Data Sources

Some data files are synchronized with or derived from external sources:

- Swiss Ephemeris data for astronomical calculations
- IANA timezone database for timezone information
- GeoNames database for geographical locations
- International Earth Rotation Service data for precision calculations
- NASA JPL ephemeris for high-precision astronomical work

## Data Security and Privacy

Guidelines for handling sensitive data:

1. User chart data must never be stored in this directory
2. Test data must be anonymized if derived from real charts
3. External data sources must be verified for integrity
4. Data backups should follow the project backup schedule
5. Access controls should be implemented for proprietary datasets 