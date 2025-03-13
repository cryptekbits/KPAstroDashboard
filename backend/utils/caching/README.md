# Caching Utilities

This directory contains utility functions for implementing efficient caching throughout the astrology application.

## Purpose

The caching utilities provide a comprehensive framework for optimizing performance through intelligent data and calculation caching. These utilities help reduce redundant calculations, minimize database queries, and speed up response times for frequently accessed data. The caching system is designed to be configurable, memory-efficient, and appropriate for various types of astrological calculations.

## Key Components

### 1. In-Memory Calculation Cache

System for caching computation-intensive results.

**Features:**
- Function result memoization
- Configurable time-to-live (TTL)
- Automatic cache invalidation
- Memory usage limiting
- Multiple cache strategies (LRU, MRU, etc.)
- Thread-safe implementation

### 2. Persistent Cache

Disk-based cache for long-term storage of calculation results.

**Features:**
- File-based result caching
- SQLite-backed cache store
- Cache versioning for invalidation
- Automatic cleanup of expired items
- Size-limited cache with pruning
- Compression for large results

### 3. Cache Key Generation

Utilities for generating consistent cache keys.

**Features:**
- Parameter-based key generation
- Normalization for consistent lookup
- Object and complex data hashing
- Namespace support for key organization
- Prefix management for different cache types
- Collision avoidance strategies

### 4. Cache Invalidation Strategies

Mechanisms for managing cache lifecycle.

**Features:**
- Time-based invalidation
- Dependency tracking for related invalidation
- Event-based cache clearing
- Tag-based invalidation grouping
- Partial cache updates
- Conditional refresh strategies

### 5. Memory Management

System for controlling memory usage of cached data.

**Features:**
- Memory consumption monitoring
- Adaptive cache sizing
- Least-recently-used eviction policies
- Soft and hard size limits
- Memory pressure detection
- Priority-based retention

### 6. Cache Statistics and Monitoring

Tools for analyzing cache performance.

**Features:**
- Hit/miss ratio tracking
- Cache efficiency metrics
- Performance impact assessment
- Cache usage patterns analysis
- Memory consumption reporting
- Optimization suggestions

## Usage Examples

```python
from backend.utils.caching.decorators import cached, cached_property
from backend.utils.caching.key_generators import generate_cache_key
from backend.utils.caching.invalidation import invalidate_cache, invalidate_by_tags
from backend.utils.caching.persistent import disk_cached
from backend.utils.caching.memory import get_cache_stats

# Function with simple caching
@cached(ttl=3600)  # Cache for 1 hour
def expensive_calculation(param1, param2):
    # ... perform expensive calculation ...
    return result

# Object property caching
class ChartAnalysis:
    def __init__(self, chart_data):
        self.chart_data = chart_data
    
    @cached_property
    def aspect_pattern_analysis(self):
        # ... complex analysis that's expensive to compute ...
        return analysis_result

# Custom cache key generation
def custom_planetary_calculation(planet, date, options=None):
    cache_key = generate_cache_key(
        prefix="planetary",
        planet=planet,
        date=date,
        options=options
    )
    
    # Check if result is in cache
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Otherwise calculate and store
    result = perform_calculation(planet, date, options)
    store_in_cache(cache_key, result)
    return result

# Persistent disk caching for very expensive operations
@disk_cached(directory="ephemeris_cache", ttl=86400*30)  # 30 days
def calculate_ephemeris(start_date, end_date, bodies):
    # ... very expensive ephemeris calculation ...
    return large_ephemeris_data

# Invalidate cache for a specific function
invalidate_cache(expensive_calculation, 'param1_value', 'param2_value')

# Tag-based invalidation
invalidate_by_tags(['planet:jupiter', 'calculation:position'])

# Get cache statistics
stats = get_cache_stats()
print(f"Cache hit ratio: {stats.hit_ratio:.2%}")
print(f"Memory usage: {stats.memory_usage_mb:.2f} MB")
```

## Cache Configuration

The caching system can be configured through:

1. Global cache settings in application configuration
2. Cache-specific settings for different data types
3. Function-level cache parameters
4. Dynamic adjustment based on system resources
5. Environment-specific cache configurations
6. Memory usage limits and policies

## Performance Considerations

To maximize caching benefits:

1. Choose appropriate TTL values based on data volatility
2. Use tag-based invalidation for related calculations
3. Monitor memory usage to prevent excessive consumption
4. Balance cache size with cache hit ratio
5. Consider distributed caching for multi-server deployments
6. Implement background refresh for frequently accessed data

## Testing

The caching utilities include comprehensive test coverage:

1. Unit tests for caching logic
2. Performance benchmarks for various cache strategies
3. Memory usage tests for different data volumes
4. Concurrency tests for thread safety
5. Integration tests for cache invalidation chains 