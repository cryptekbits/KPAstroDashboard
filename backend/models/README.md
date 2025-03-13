# Data Models

This directory contains data models that define the structure of data throughout the application. These models serve as both database schema definitions and API request/response structures.

## Model Types

### User Models (user/)
- User profile and authentication data
- User preferences and settings
- Saved chart data
- Subscription and payment information
- User activity logs

### Chart Models (chart/)
- Birth chart data structures
- Divisional chart structures
- Transit chart structures
- Composite chart structures
- Progression chart structures

## Additional Models

### API Request/Response Models
- Standardized API request formats
- Consistent API response structures
- Error response formats
- Pagination models

### Calculation Result Models
- Dasha calculation results
- Yoga detection results
- Ashtakvarga calculation results
- Compatibility matching results

## Implementation Notes

1. Models should leverage schema validation libraries
2. Implement data transformation methods where needed
3. Include serialization/deserialization methods
4. Document required fields and constraints
5. Add proper type annotations
6. Follow a consistent naming convention
7. Consider using inheritance for related models
8. Add validators for complex model constraints 