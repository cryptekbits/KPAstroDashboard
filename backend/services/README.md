# Backend Services

This directory contains service layer implementations for the astrology website. Services are responsible for orchestrating complex operations that may involve multiple core components.

## Service Components

### Authentication (auth/)
- User authentication and authorization
- JWT token generation and validation
- Role-based access control
- Session management
- Password reset and account recovery

### PDF Generation (pdf_generation/)
- Astrology report generation in PDF format
- PDF template management
- Dynamic content population
- Image embedding in reports
- Localization of report content

### Chart Generation (chart_generation/)
- Astrological chart image rendering
- SVG and PNG output formats
- Customizable chart styles and themes
- North and South Indian chart formats
- KP chart styles
- Interactive chart elements

### Data Processing (data_processing/)
- Data transformation and normalization
- Calculation result formatting
- Historical data analysis
- Prediction models
- Data caching strategies

## Implementation Notes

1. Services should be designed with a clean interface for API layers to consume
2. Implement proper error handling and provide meaningful error messages
3. Services should be stateless where possible
4. Implement appropriate logging and monitoring 
5. Use dependency injection to access core calculation modules
6. Consider implementing circuit breakers for external dependencies
7. Add metrics collection for performance monitoring 