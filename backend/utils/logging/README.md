# Logging and Monitoring Utilities

This directory contains utility functions for comprehensive logging, monitoring, and observability throughout the astrology application.

## Purpose

The logging and monitoring utilities provide a robust framework for tracking application behavior, performance metrics, user activity, and system health. These utilities help developers identify issues, optimize performance, understand user patterns, and ensure the reliability of the astrology application in production environments.

## Key Components

### 1. Structured Logging System

Comprehensive logging framework with contextual information.

**Features:**
- JSON-formatted logs for machine readability
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Contextual enrichment with request IDs, user info, etc.
- Component-based loggers for targeted debugging
- Correlation IDs for tracking requests across services
- Log rotation and retention policies

### 2. Performance Monitoring

Tools for tracking and analyzing application performance.

**Features:**
- Function execution timing
- Database query performance tracking
- External API call monitoring
- Memory usage profiling
- CPU utilization tracking
- Bottleneck identification

### 3. Error Tracking and Reporting

System for capturing, aggregating, and analyzing errors.

**Features:**
- Exception capturing with full stack traces
- Error categorization and prioritization
- Notification system for critical errors
- Deduplication of similar errors
- Error frequency tracking
- Error context capture

### 4. Health Checks and Diagnostics

Utilities for monitoring system health.

**Features:**
- Component health status checks
- Dependency availability monitoring
- System resource monitoring
- Readiness and liveness probes
- Self-healing recommendations
- Degraded mode detection

### 5. User Activity Tracking

Anonymized analytics for understanding application usage.

**Features:**
- API endpoint usage statistics
- Feature popularity metrics
- Performance experience tracking
- User journey analysis
- Error impact assessment
- Geographic usage patterns

### 6. Alerting System

Tools for proactive notification of system issues.

**Features:**
- Threshold-based alerts
- Anomaly detection
- Alert routing and escalation
- Alert grouping and correlation
- Alert severity classification
- Notification channel integration (email, SMS, etc.)

### 7. Metrics Collection

Utilities for gathering and exposing application metrics.

**Features:**
- Prometheus-compatible metrics
- Custom business metrics
- System resource metrics
- Performance counter tracking
- Histogram and summary statistics
- Metrics aggregation

## Usage Examples

```python
from backend.utils.logging.logger import get_logger
from backend.utils.logging.performance import timing_decorator, track_memory
from backend.utils.logging.metrics import increment_counter, observe_value
from backend.utils.logging.health import register_health_check
from backend.utils.logging.errors import capture_exception

# Get a component-specific logger
logger = get_logger("chart_generation")

# Log messages at various levels
def process_chart_request(chart_data, user_id):
    logger.info("Processing chart request", extra={"user_id": user_id})
    try:
        # Business logic
        if not validate_chart_data(chart_data):
            logger.warning("Invalid chart data received", extra={
                "user_id": user_id,
                "data_issues": get_validation_errors(chart_data)
            })
            return {"error": "Invalid chart data"}
            
        # More processing...
        logger.debug("Chart data validation passed", extra={"chart_type": chart_data.get("type")})
        
    except Exception as e:
        logger.error("Error generating chart", exc_info=True, extra={
            "user_id": user_id,
            "chart_type": chart_data.get("type")
        })
        capture_exception(e, context={"chart_data": chart_data, "user_id": user_id})
        raise

# Performance monitoring
@timing_decorator(name="planetary_positions_calculation")
def calculate_planetary_positions(birth_data):
    # Expensive calculations...
    with track_memory() as memory_usage:
        result = perform_calculations(birth_data)
    
    logger.debug("Memory usage for calculation", extra={
        "peak_memory_mb": memory_usage.peak,
        "duration_ms": memory_usage.duration
    })
    
    # Increment metrics
    increment_counter("calculations_performed", labels={"type": "planetary_positions"})
    observe_value("calculation_time_ms", memory_usage.duration)
    
    return result

# Register health checks
@register_health_check(name="ephemeris_data_access")
def check_ephemeris_data():
    try:
        # Verify ephemeris data is accessible
        test_result = test_ephemeris_access()
        return {"status": "healthy", "message": "Ephemeris data accessible"}
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Ephemeris data inaccessible: {str(e)}",
            "details": {"exception": type(e).__name__}
        }
```

## Configuration

The logging and monitoring system can be configured through:

1. Environment-specific settings
2. Log level controls per component
3. Sampling rates for high-volume logs
4. Metrics collection intervals
5. Health check frequency
6. Retention policies for logs and metrics
7. Integration settings for external monitoring tools

## Integration with External Systems

The utilities support integration with:

1. **Log Aggregation Systems:**
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Graylog
   - Loki

2. **Metrics Systems:**
   - Prometheus
   - Grafana
   - DataDog
   - New Relic

3. **Error Tracking:**
   - Sentry
   - Rollbar
   - Bugsnag

4. **APM (Application Performance Monitoring):**
   - Elastic APM
   - Datadog APM
   - New Relic APM

## Best Practices

1. **Structured Logging:**
   - Use structured logs with consistent fields
   - Include contextual information in every log
   - Log at appropriate levels
   - Avoid sensitive information in logs

2. **Performance Monitoring:**
   - Monitor both average and percentile metrics
   - Set appropriate baselines and thresholds
   - Focus on user-impacting metrics
   - Track trends over time

3. **Error Handling:**
   - Capture exceptions with sufficient context
   - Categorize errors by severity and impact
   - Implement appropriate retry mechanisms
   - Document error codes and solutions

4. **Health Monitoring:**
   - Monitor all critical dependencies
   - Implement both deep and shallow health checks
   - Design for graceful degradation
   - Test failure scenarios

## Privacy and Compliance

The logging utilities are designed with privacy in mind:

1. Personal Identifiable Information (PII) is automatically redacted
2. Sensitive astrological data is anonymized when logged
3. Data retention policies comply with relevant regulations
4. Consent mechanisms for user activity tracking
5. Audit logs for sensitive operations 