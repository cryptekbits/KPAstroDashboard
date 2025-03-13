# Formatting Utilities

This directory contains utility functions for formatting and displaying astrological data and symbols.

## Purpose

The formatting utilities provide standardized methods for formatting astrological data like planetary positions, aspects, dates, and symbols for display. These utilities ensure consistent presentation of information across the application and support various output formats, including plain text, HTML, and graphical renderings.

## Key Components

### 1. Coordinate and Angle Formatters

Functions for formatting astronomical coordinates and angles.

**Features:**
- Degrees, minutes, seconds (DMS) formatting
- Zodiacal position formatting (sign + degrees)
- Declination and right ascension formatting
- Custom precision control
- Support for various unit systems
- Localized direction indicators (N/S/E/W)

### 2. Astrological Symbol Generation

Utilities for generating proper astrological symbols.

**Features:**
- Planet symbol generation (Unicode and HTML)
- Zodiac sign symbol generation
- Aspect symbol generation
- House number formatting
- Node and special point symbols
- Customizable symbol styles

### 3. Date and Time Formatting

Specialized date and time formatting for astrological contexts.

**Features:**
- Formatted Julian date display
- Astrological era formatting
- Planetary hour display
- Timezone-aware formatting
- Lunar phase date formatting
- Dasha period formatting

### 4. Chart Data Formatting

Structured formatting of chart data for various output requirements.

**Features:**
- Tabular position data formatting
- Aspect grid generation
- Chart data JSON serialization
- Report section formatting
- Chart summary generation
- Multi-language support for interpretations

### 5. Localization Support

Internationalization and localization utilities for astrological terminology.

**Features:**
- Translation of astrological terms
- Cultural variant support for astrological systems
- Number formatting per locale
- RTL/LTR text handling
- Honorific and formal/informal variants
- Locale-specific date formats

### 6. Unit Conversion

Utilities for converting between different units and notation systems.

**Features:**
- Decimal degrees to DMS conversion
- Hours/minutes/seconds to decimal hours
- Calendar system conversions
- Ancient unit conversion helpers
- Coordinate system notation converters
- Time unit conversions

## Usage Examples

```python
from backend.utils.formatting.angles import format_longitude, format_dms
from backend.utils.formatting.symbols import get_planet_symbol, get_sign_symbol
from backend.utils.formatting.dates import format_julian_day
from backend.utils.formatting.charts import format_position_table
from backend.utils.formatting.localize import translate_term

# Format a zodiacal longitude
position = format_longitude(128.456789)  # Returns "8°♌30′24″" or "8°Leo30′24″"

# Format an angle in degrees, minutes, seconds
dms = format_dms(67.8912, precision=0)  # Returns "67°53′28″"

# Get Unicode symbol for Jupiter
jupiter_symbol = get_planet_symbol("Jupiter")  # Returns "♃"

# Get HTML entity for Leo
leo_html = get_sign_symbol("Leo", format="html")  # Returns "&leo;"

# Format a Julian day as a calendar date
calendar_date = format_julian_day(2459318.5)  # Returns "2021-Apr-15"

# Generate a formatted table of planetary positions
table_html = format_position_table(
    planet_positions,
    format="html",
    include_minutes=True
)

# Translate an astrological term to Spanish
term_es = translate_term("Ascendant", locale="es_ES")  # Returns "Ascendente"
```

## Style Guidelines

The formatting utilities follow these style guidelines:

1. Consistent symbol and terminology usage throughout the application
2. Flexible formatting options with sensible defaults
3. Support for both technical and user-friendly output styles
4. Compliance with astrological notation standards
5. Accessibility considerations for all formatted output
6. Clear documentation of formatting patterns and options

## Customization

The formatting utilities support customization through:

1. Configurable precision for numerical displays
2. Multiple output format options (text, HTML, Unicode, etc.)
3. Style variation support (traditional/modern notation)
4. Custom templates for complex formatting
5. User preference incorporation
6. Cultural and regional variant support

## Testing

The formatting utilities include comprehensive test coverage:

1. Unit tests for each formatting function
2. Validation of symbol rendering across platforms
3. Localization testing for multiple languages
4. Edge case testing for unusual values
5. Visual regression testing for graphical outputs 