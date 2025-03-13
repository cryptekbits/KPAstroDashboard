# Data Access Utilities

This directory contains utility functions for accessing and managing data files and resources used throughout the astrology application.

## Purpose

The data access utilities provide a standardized, efficient, and reliable way to load, cache, and manage various data files needed for astrological calculations and interpretations. These utilities abstract away the file system operations and provide a consistent API for accessing data regardless of format or location.

## Key Components

### 1. Data File Loaders

Functions for loading data from various file formats.

**Features:**
- JSON file loading with schema validation
- CSV parsing with appropriate data typing
- YAML configuration loading
- Binary data file handling
- SQLite database access

### 2. Path Resolution

Utilities for resolving file paths across different environments.

**Features:**
- Cross-platform path resolution
- Resource locators for packaged data
- Environment-aware path selection
- Data directory structure navigation
- File existence validation

### 3. Data Caching

Smart caching system for frequently accessed data.

**Features:**
- Memory-efficient data caching
- LRU (Least Recently Used) cache implementation
- Thread-safe cache access
- Configurable expiration policies
- Automatic cache invalidation when data files change

### 4. Asynchronous Data Loading

Support for non-blocking data loading operations.

**Features:**
- Async file reading operations
- Background data loading
- Progress monitoring for large dataset loading
- Cancellable loading operations
- Concurrent file access management

### 5. Format Conversion

Utilities for converting between different data formats.

**Features:**
- CSV to JSON conversion
- Table to hierarchical data transformation
- Ephemeris data format normalization
- Character encoding handling
- Data structure transformation

## Usage Examples

```python
from backend.utils.data_access.loaders import load_json, load_csv
from backend.utils.data_access.paths import get_data_path, ensure_dir_exists
from backend.utils.data_access.cache import cached_data

# Load JSON data with automatic caching
planet_data = load_json('reference/planets.json')

# Resolve path to a data file
ephemeris_path = get_data_path('astronomical/ephemeris/jpl_2020.dat')

# Load CSV data with column typing
city_database = load_csv(
    'geographical/cities.csv',
    types={
        'latitude': float,
        'longitude': float,
        'population': int,
        'timezone': str
    }
)

# Access data with explicit caching
@cached_data(ttl=3600)
def get_large_dataset(dataset_name):
    # Complex loading logic here
    return dataset

# Create directory if it doesn't exist
user_data_dir = get_data_path('user_data')
ensure_dir_exists(user_data_dir)
```

## Error Handling

The data access utilities implement a consistent error handling approach:

1. File not found errors include clear path information and suggestions
2. Format errors provide details about the specific parsing problem
3. All exceptions are derived from a base `DataAccessError`
4. Optional fallback mechanisms for critical data
5. Detailed logging of access errors for troubleshooting

## Performance Considerations

To ensure efficient data access:

1. Implement appropriate caching strategies based on data size and access patterns
2. Use memory mapping for large files when appropriate
3. Implement lazy loading for large datasets
4. Monitor file access patterns to optimize caching strategies
5. Provide mechanisms to preload frequently accessed data during startup

## Testing

The data access utilities include comprehensive test coverage:

1. Unit tests for each loading function
2. Mock file system for testing path resolution
3. Performance tests for caching mechanisms
4. Edge case tests for corrupted or missing data
5. Concurrency tests for thread safety 