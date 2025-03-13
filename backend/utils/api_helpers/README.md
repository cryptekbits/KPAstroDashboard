# API Helper Utilities

This directory contains utility functions that facilitate API development, request/response handling, and API-related operations for the astrology application.

## Purpose

The API helper utilities provide consistent patterns and reusable components for building robust, maintainable, and well-documented APIs. These utilities simplify common API tasks, enforce best practices, and ensure consistent response formats across all astrology application endpoints.

## Key Components

### 1. Request Validation and Processing

Utilities for validating and processing incoming API requests.

**Features:**
- Request schema validation
- Parameter type checking and coercion
- Query parameter parsing
- Input sanitization and normalization
- Default value handling
- Required field enforcement

### 2. Response Formatting

Tools for standardized API response formatting.

**Features:**
- Consistent response envelope structure
- Status code standardization
- Error response formatting
- Pagination metadata
- Response compression
- Content negotiation helpers

### 3. Error Handling

Middleware and utilities for consistent API error handling.

**Features:**
- Exception to HTTP status code mapping
- Detailed error messages for debugging
- Production-safe error responses
- Validation error formatting
- Error logging integration
- Retry suggestion helpers

### 4. Authentication and Authorization

Utilities for securing API endpoints.

**Features:**
- Token validation and verification
- Scope and permission checking
- Role-based access control helpers
- API key management
- Rate limiting by authentication context
- Session handling

### 5. Pagination and Filtering

Tools for implementing pagination and filtering in API responses.

**Features:**
- Cursor-based pagination
- Offset/limit pagination
- Page number pagination
- Dynamic filtering support
- Sorting parameter handling
- Result limiting

### 6. Documentation Generators

Utilities for generating and maintaining API documentation.

**Features:**
- OpenAPI (Swagger) specification generation
- Documentation comment processing
- Example request/response generation
- Documentation versioning
- Markdown documentation generation
- Schema visualization

### 7. Versioning Support

Tools for managing API versioning.

**Features:**
- Version header processing
- URL-based version routing
- Version compatibility checking
- Deprecation notice generation
- Feature availability by version
- Version fallback strategies

### 8. Rate Limiting

Utilities for implementing API rate limiting.

**Features:**
- Request rate tracking
- Configurable limit enforcement
- Client identification
- Rate limit headers (X-RateLimit-*)
- Throttling implementation
- Burst allowance

### 9. Caching Integration

Tools for API response caching.

**Features:**
- Cache key generation from requests
- Cache control header management
- Conditional request handling (If-None-Match, ETag)
- Cache invalidation helpers
- Partially cached responses
- Stale-while-revalidate support

## Usage Examples

```python
from backend.utils.api_helpers.validation import validate_request
from backend.utils.api_helpers.response import api_response, paginated_response
from backend.utils.api_helpers.errors import api_error_handler
from backend.utils.api_helpers.auth import require_auth, check_permissions
from backend.utils.api_helpers.pagination import paginate_results
from backend.utils.api_helpers.versioning import api_version
from backend.utils.api_helpers.rate_limit import rate_limited
from backend.utils.api_helpers.caching import cacheable

# Request validation
@validate_request(schema=ChartRequestSchema)
def get_birth_chart(request_data):
    # Request data is already validated
    chart_data = generate_chart(request_data)
    return api_response(chart_data)

# Pagination example
@paginate_results(default_limit=20, max_limit=100)
def list_saved_charts(user_id, pagination_params):
    # pagination_params contains offset/limit or cursor
    total_charts = count_user_charts(user_id)
    charts = fetch_user_charts(user_id, pagination_params)
    
    return paginated_response(
        items=charts,
        total=total_charts,
        pagination_params=pagination_params
    )

# Error handling
@api_error_handler
def calculate_planetary_positions(request_data):
    try:
        # Complex processing that might raise various exceptions
        results = process_request(request_data)
        return api_response(results)
    except InvalidBirthDataError as e:
        # Custom error handling with appropriate HTTP status
        return api_error("invalid_birth_data", str(e), status_code=400)
    except EphemerisDataError as e:
        return api_error("ephemeris_error", str(e), status_code=500)

# Authentication and authorization
@require_auth
@check_permissions(["charts:read", "user:read"])
def get_user_chart(user_id, chart_id):
    # Only authenticated users with proper permissions reach here
    chart = fetch_chart(user_id, chart_id)
    return api_response(chart)

# API versioning
@api_version("1.2")
def get_transits(request_data):
    # Logic for API version 1.2
    transits = calculate_transits_v1_2(request_data)
    return api_response(transits)

# Rate limiting
@rate_limited(limit=10, period=60)  # 10 requests per minute
def generate_detailed_report(request_data):
    # Resource-intensive endpoint with rate limiting
    report = create_detailed_report(request_data)
    return api_response(report)

# Caching
@cacheable(ttl=3600)  # Cache for 1 hour
def get_planetary_positions(date, location):
    # Expensive calculation that's cacheable
    positions = calculate_positions(date, location)
    return api_response(positions)
```

## API Response Structure

The API helper utilities enforce a consistent response structure:

```json
{
  "status": "success",
  "data": {
    // Response data here
  },
  "meta": {
    "version": "1.0",
    "timestamp": "2023-07-15T12:34:56Z",
    "request_id": "req-12345"
  }
}
```

Error response:

```json
{
  "status": "error",
  "error": {
    "code": "invalid_parameters",
    "message": "The birth date is invalid or missing",
    "details": {
      "birth_date": "Must be a valid date in ISO 8601 format"
    }
  },
  "meta": {
    "version": "1.0",
    "timestamp": "2023-07-15T12:34:56Z",
    "request_id": "req-12345"
  }
}
```

Paginated response:

```json
{
  "status": "success",
  "data": [
    // Array of items
  ],
  "meta": {
    "version": "1.0",
    "timestamp": "2023-07-15T12:34:56Z",
    "request_id": "req-12345",
    "pagination": {
      "total": 243,
      "limit": 20,
      "offset": 40,
      "has_more": true,
      "next_cursor": "cursor-value-for-next-page"
    }
  }
}
```

## Best Practices

1. **Consistency:**
   - Use standardized response formats across all endpoints
   - Apply consistent error handling patterns
   - Maintain uniform parameter naming conventions

2. **Validation:**
   - Validate all incoming requests against schemas
   - Provide clear validation error messages
   - Normalize inputs to canonical forms

3. **Security:**
   - Apply appropriate authentication for all endpoints
   - Validate permissions before processing requests
   - Implement rate limiting for resource-intensive endpoints

4. **Performance:**
   - Use caching for appropriate endpoints
   - Implement pagination for list endpoints
   - Allow clients to request only needed fields

5. **Documentation:**
   - Document all API endpoints comprehensively
   - Include example requests and responses
   - Explain error codes and their meanings

## Testing

The API helpers directory includes comprehensive testing utilities:

1. API contract testing tools
2. Request validation test helpers
3. Mock authentication utilities
4. Response structure verification
5. API performance benchmarks 