# Astrology Website Project Instructions

This document serves as a comprehensive guide for implementing and maintaining the astrology website project. It outlines the key components, architecture, development approach, and best practices to be followed.

## Project Overview

This project implements a comprehensive astrology website with multiple calculation systems (Vedic, KP, Lal Kitab, etc.), API endpoints, and report generation capabilities. It leverages existing libraries (`flatlib` and `astro_engine`) for core astrological calculations.

## Key Components

1. **Backend API**: RESTful API endpoints organized by feature categories
2. **Core Calculations**: Astrological calculation modules for various systems
3. **Services**: Authentication, report generation, and chart rendering
4. **Data Models**: Structured data representations for the application
5. **Utilities**: Helper functions for common operations

## Technology Stack

- **Python**: Primary programming language
- **FastAPI/Flask**: Web framework for API implementation
- **flatlib**: Library for Sidereal calculations
- **astro_engine**: Custom library for astrological calculations
- **pyswisseph**: Swiss Ephemeris wrapper for astronomical calculations
- **pandas/polars**: Data manipulation libraries
- **SQLAlchemy**: ORM for database interactions (if required)
- **Pydantic**: Data validation and settings management
- **JWT**: Token-based authentication
- **Pillow/Cairo**: Image generation for charts
- **WeasyPrint/ReportLab**: PDF generation for reports

## Development Approach

### Modular Architecture

Follow a modular approach with clear separation of concerns:

1. **API Layer**: Handles HTTP requests/responses, input validation, and route management
2. **Service Layer**: Orchestrates operations and implements business logic
3. **Core Layer**: Implements astrological calculations and algorithms
4. **Data Layer**: Manages data persistence and retrieval
5. **Utility Layer**: Provides helper functions and common operations

### Component Sizing Guidelines

1. Each module should have a single, well-defined responsibility
2. Keep files under 500 lines where possible
3. Break complex calculations into smaller, testable functions
4. Use composition over inheritance for reusability
5. Aim for components that are easy to understand and debug in isolation

### Performance Considerations

1. Implement caching for expensive calculations
2. Use memoization for repetitive operations
3. Consider asynchronous processing for long-running calculations
4. Profile code regularly to identify bottlenecks
5. Optimize critical paths while maintaining readability

## Integration Guidelines

### Integrating with flatlib

The `flatlib` library provides essential functionality for Sidereal calculations:

1. Use `flatlib` for basic astronomical calculations
2. Extend `flatlib` classes only when necessary
3. Ensure compatibility with the existing `flatlib` API
4. Document any modifications or extensions to `flatlib`

### Integrating with astro_engine

The `astro_engine` handles core astrological computations:

1. Use `astro_engine` for complex astrological calculations
2. Maintain consistency with `astro_engine` conventions
3. Extend functionality through composition rather than modification
4. Document dependencies on `astro_engine` components

## Error Handling and Validation

1. Validate all input data at the API level
2. Implement comprehensive error handling throughout the codebase
3. Return meaningful error messages with appropriate HTTP status codes
4. Log errors with sufficient context for debugging
5. Handle edge cases explicitly (e.g., invalid birth data, calculation errors)

## Documentation Standards

1. Document all public APIs with input/output specifications
2. Include examples for complex operations
3. Maintain up-to-date architecture documentation
4. Document assumptions and limitations clearly
5. Use type annotations throughout the codebase

## Testing Strategy

1. Implement unit tests for all calculation modules
2. Add integration tests for API endpoints
3. Include validation tests with known example data
4. Test edge cases explicitly
5. Measure and maintain code coverage

## Memory & Context Management

The project uses several Model Control Primitives (MCPs) to improve performance and reduce hallucinations:

1. **PersistentMemory**: Stores key calculation results for reuse
2. **ContextManager**: Manages conversation context to optimize token usage
3. **EntityGraph**: Maintains relationships between astrological entities

## Component Decomposition Guidelines

When implementing complex features:

1. Break down the feature into atomic components
2. Ensure each component fits within chat context limits (approximately 4K tokens)
3. Design clean interfaces between components
4. Document integration points clearly
5. Create tests for individual components before integration

## Progress Tracking

Track implementation progress using:

1. GitHub issues for feature tasks
2. Pull requests for code reviews
3. Milestone tracking for feature completeness
4. Documentation updates with each feature addition

## Versioning and API Stability

1. Follow semantic versioning for releases
2. Maintain backward compatibility where possible
3. Document breaking changes clearly
4. Provide migration guides for major version updates

## Deployment Considerations

1. Create comprehensive environment documentation
2. Document all external dependencies
3. Provide containerization options (Docker)
4. Include monitoring recommendations
5. Document scaling considerations for high-traffic scenarios 