# Configuration Management Utilities

This directory contains utility functions and tools for managing application configuration across various environments and deployment scenarios for the astrology application.

## Purpose

The configuration management utilities provide a robust, flexible, and secure way to manage configuration settings throughout the application lifecycle. These utilities ensure consistent configuration access, environment-specific settings, secure credential management, and runtime configuration updates for the astrology application.

## Key Components

### 1. Configuration Loading and Access

Utilities for loading and accessing configuration data.

**Features:**
- Hierarchical configuration structure
- Environment-specific overrides
- Default value fallbacks
- Configuration validation
- Type conversion and coercion
- Dot-notation access patterns

### 2. Environment Management

Tools for environment detection and management.

**Features:**
- Environment detection (dev, test, staging, prod)
- Environment-specific configuration loading
- Local development environment support
- CI/CD environment support
- Cloud environment detection
- Container environment handling

### 3. Secure Credentials Management

Utilities for securely managing sensitive configuration.

**Features:**
- Secret key management
- Integration with secret stores (AWS Secrets Manager, HashiCorp Vault, etc.)
- Credential rotation support
- Masked logging of sensitive values
- Encryption/decryption of sensitive settings
- Access control for sensitive configuration

### 4. Dynamic Configuration

Tools for runtime configuration updates.

**Features:**
- Hot reloading of configuration
- Feature flags management
- A/B testing configuration
- User-specific configuration overrides
- Remote configuration updates
- Configuration change notifications

### 5. Configuration Validation

Utilities for validating configuration correctness.

**Features:**
- Schema-based configuration validation
- Configuration dependency checking
- Required setting verification
- Type checking and conversion
- Range and constraint validation
- Semantic validation rules

### 6. Service Configuration

Tools for configuring external services and dependencies.

**Features:**
- Database connection configuration
- External API endpoint management
- Caching service configuration
- Email service setup
- Storage service configuration
- Third-party service credentials

### 7. Application Profiling

Utilities for managing application profiles.

**Features:**
- Performance profiles (low/medium/high resource usage)
- Feature enablement profiles
- Regional profiles for localization
- Deployment target profiles
- Data access profiles
- Logging and monitoring profiles

### 8. Configuration Documentation

Tools for documenting configuration options.

**Features:**
- Configuration option documentation generation
- Sample configuration files
- Configuration option discovery
- Default value documentation
- Deprecated option warnings
- Configuration migration guides

## Usage Examples

```python
from backend.utils.config.loader import get_config, ConfigurationError
from backend.utils.config.environment import is_production, get_environment
from backend.utils.config.secrets import get_secret
from backend.utils.config.dynamic import feature_enabled, get_feature_flag
from backend.utils.config.validation import validate_config

# Basic configuration access
def initialize_database():
    # Get database configuration section
    db_config = get_config("database")
    
    # Access with fallback values
    host = db_config.get("host", "localhost")
    port = db_config.get_int("port", 5432)
    use_ssl = db_config.get_bool("use_ssl", True)
    
    # Connect using configuration
    connection = create_db_connection(
        host=host,
        port=port,
        database=db_config["database_name"],  # Required value, will raise if missing
        username=db_config["username"],
        password=get_secret("database_password"),  # Securely access sensitive data
        use_ssl=use_ssl
    )
    
    return connection

# Environment-specific configuration
def configure_logging():
    env = get_environment()
    
    log_config = get_config("logging")
    
    if is_production():
        # Production uses structured JSON logging
        initialize_json_logging(
            level=log_config.get("level", "INFO"),
            output=log_config.get("output", "stdout"),
            include_correlation_id=True
        )
    else:
        # Development uses more human-readable logging
        initialize_development_logging(
            level=log_config.get("level", "DEBUG"),
            include_line_numbers=True,
            colorized=True
        )

# Feature flag usage
def calculate_chart(birth_data, options=None):
    # Check if experimental features are enabled
    if feature_enabled("use_improved_calculation_algorithm"):
        return calculate_with_improved_algorithm(birth_data, options)
    else:
        return calculate_with_standard_algorithm(birth_data, options)

# Dynamic configuration for A/B testing
def get_report_generator(user_id):
    # Get A/B test configuration for the user
    report_version = get_feature_flag("report_version", user_id, default="A")
    
    if report_version == "B":
        return new_report_generator
    else:
        return standard_report_generator

# Configuration validation
def validate_application_config():
    try:
        # Validate entire configuration
        validate_config(get_config())
        return True
    except ConfigurationError as e:
        log_error(f"Configuration validation failed: {e}")
        return False

# Service configuration
def initialize_external_services():
    # Get all external service configurations
    services_config = get_config("external_services")
    
    # Initialize each configured service
    for service_name, service_config in services_config.items():
        if service_config.get_bool("enabled", False):
            initialize_service(
                service_name,
                endpoint=service_config["endpoint"],
                api_key=get_secret(f"{service_name}_api_key"),
                timeout=service_config.get_int("timeout_seconds", 30),
                retry_count=service_config.get_int("retry_count", 3)
            )
```

## Configuration Structure

The configuration system uses a hierarchical structure with the following levels:

```
config/
├── default.yaml           # Default values for all environments
├── development.yaml       # Development environment overrides
├── test.yaml              # Test environment overrides
├── staging.yaml           # Staging environment overrides 
├── production.yaml        # Production environment overrides
├── local.yaml             # Local developer overrides (git-ignored)
└── schema.yaml            # Configuration schema validation rules
```

## Configuration Sources

The configuration system supports multiple sources with the following precedence (highest to lowest):

1. **Environment Variables:** Highest precedence, useful for containerized deployments
2. **Command Line Arguments:** For runtime overrides
3. **Local Configuration:** For developer-specific settings (git-ignored)
4. **Environment-Specific Configuration:** Based on detected environment
5. **Default Configuration:** Base settings for all environments

## Security Considerations

1. **Secret Management:**
   - Sensitive values are never stored in plain text configuration
   - Secrets are retrieved from secure stores at runtime
   - Encryption is used for any persisted sensitive values

2. **Access Control:**
   - Configuration access is logged for sensitive settings
   - Role-based access control for configuration management
   - Auditing of configuration changes

3. **Validation:**
   - Schema validation prevents misconfiguration
   - Type checking prevents injection attacks
   - Configuration is validated before application startup

## Best Practices

1. **Naming Conventions:**
   - Use lowercase snake_case for configuration keys
   - Use descriptive, specific names
   - Group related configuration under namespaces

2. **Documentation:**
   - Document all configuration options
   - Include valid value ranges and constraints
   - Document dependencies between settings

3. **Defaults:**
   - Provide sensible defaults for most settings
   - Make critical settings required (no default)
   - Document the reasoning behind default values

4. **Validation:**
   - Validate configuration early in application startup
   - Include both structural and semantic validation
   - Fail explicitly for invalid configuration

5. **Testing:**
   - Test application with different configuration combinations
   - Include configuration validation in CI/CD pipelines
   - Test handling of missing or invalid configuration 