# Astrology Website Backend

This directory contains the backend infrastructure for the astrology website, including API endpoints, core calculation logic, and service utilities.

## Directory Structure

- **api/**: Contains all API endpoint implementations organized by feature
- **core/**: Contains core astrological calculations and algorithms
- **data/**: Contains data models, schemas, and database interactions
- **models/**: Contains business logic models
- **services/**: Contains service layers for authentication, report generation, etc.
- **utils/**: Contains utility functions and helpers
- **docs/**: Contains API documentation and development guides

## Integration with Existing Components

The backend will leverage:
- **flatlib/**: For Sidereal calculations and basic astrological operations
- **astro_engine/**: For core astrological computation

## Environment Setup

See the project root's requirements.txt for dependencies.

## Development Guidelines

1. Keep components modular and focused on specific functionality
2. Maintain clear separation between calculation logic and API endpoints
3. Document all API endpoints with input/output specifications
4. Follow RESTful design principles for API endpoints
5. Implement proper error handling and input validation
6. Use async patterns where appropriate for performance optimization 