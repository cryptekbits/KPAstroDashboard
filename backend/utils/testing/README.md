# Testing Utilities

This directory contains utility functions, fixtures, and helpers to facilitate testing throughout the astrology application.

## Purpose

The testing utilities provide a comprehensive framework for writing reliable, maintainable, and efficient tests across the application. These utilities help standardize testing approaches, reduce boilerplate code, simulate complex scenarios, and ensure thorough test coverage of astrological calculations and APIs.

## Key Components

### 1. Test Data Generators

Utilities for generating test data for astrological components.

**Features:**
- Birth chart data generators
- Planetary position simulators
- Transit pattern generators
- Aspect configuration creators
- Random birth data generators
- Edge case data providers

### 2. Test Fixtures

Reusable test fixtures for common testing scenarios.

**Features:**
- Pre-calculated chart fixtures
- Ephemeris data fixtures
- Mock API response fixtures
- Database fixtures
- Authentication fixtures
- User profile fixtures

### 3. Mock Services

Tools for mocking external services and dependencies.

**Features:**
- Ephemeris calculation mocks
- Time zone service mocks
- External API mocks
- Database mocks
- File system mocks
- Authentication service mocks

### 4. Assertion Helpers

Custom assertion functions for astrological calculations.

**Features:**
- Planetary position assertions
- Chart comparison utilities
- Aspect verification helpers
- Numerical precision adjustments
- Tolerance-based equality checks
- Output format validators

### 5. Performance Testing Tools

Utilities for measuring and verifying performance.

**Features:**
- Execution time benchmarks
- Memory usage profiling
- Scalability test helpers
- Load test generators
- Performance regression detectors
- Comparative benchmarking

### 6. API Testing Utilities

Tools for testing API endpoints.

**Features:**
- Request builders
- Response validators
- Authentication helpers
- Parameterized API testing
- API sequence testing
- Contract validation

### 7. Test Result Analyzers

Tools for analyzing and reporting test results.

**Features:**
- Coverage analyzers
- Test result comparisons
- Visual difference highlighters
- Test report generators
- Failure pattern analyzers
- Historical comparison tools

### 8. Integration Test Helpers

Utilities for integration testing across components.

**Features:**
- Component interaction simulators
- Workflow test helpers
- System boundary monitors
- Transaction trackers
- Cross-component validators
- End-to-end test orchestrators

## Usage Examples

```python
from backend.utils.testing.fixtures import chart_fixture, ephemeris_fixture
from backend.utils.testing.generators import generate_birth_data, generate_transit_data
from backend.utils.testing.mocks import mock_ephemeris_service, mock_timezone_api
from backend.utils.testing.assertions import assert_planet_positions, assert_aspects
from backend.utils.testing.performance import benchmark, assert_performance
from backend.utils.testing.api import api_test_client, validate_response
from backend.utils.testing.integration import workflow_test

# Using test fixtures
def test_chart_calculation():
    # Get a pre-defined chart fixture
    test_chart = chart_fixture("basic_chart")
    
    # Run the calculation
    result = calculate_chart(test_chart.input_data)
    
    # Assert the results match expected values
    assert_planet_positions(result.planets, test_chart.expected_planets, tolerance=0.01)
    assert_aspects(result.aspects, test_chart.expected_aspects)

# Using test data generators
def test_random_charts():
    # Generate 10 random birth charts
    for _ in range(10):
        birth_data = generate_birth_data(
            year_range=(1950, 2020),
            locations=["urban", "international"]
        )
        
        # Test the calculation with this random data
        result = calculate_chart(birth_data)
        
        # Basic validation of the result structure
        assert result.planets is not None
        assert len(result.aspects) > 0
        assert result.houses is not None

# Using mock services
@mock_ephemeris_service
@mock_timezone_api
def test_chart_with_mocked_services():
    # Services are mocked, so calculations will use controlled test data
    result = calculate_chart({
        "date": "2000-01-01T12:00:00Z",
        "latitude": 40.7128,
        "longitude": -74.0060
    })
    
    # Verify the calculation used the mock data
    assert result.meta.data_source == "mock_ephemeris"

# Performance testing
@benchmark
def test_calculation_performance():
    # Standard test data
    test_data = generate_birth_data()
    
    # Run with performance monitoring
    with assert_performance(max_time=0.5, max_memory_mb=50):
        result = calculate_chart(test_data)
        calculate_divisional_charts(result)
        generate_detailed_report(result)

# API testing
def test_chart_api_endpoint():
    # Get a test client with authentication
    client = api_test_client(auth_level="user")
    
    # Test data
    test_data = generate_birth_data()
    
    # Call the API
    response = client.post("/api/charts", json=test_data)
    
    # Validate the response
    validate_response(
        response,
        expected_status=201,
        schema=ChartResponseSchema,
        content_checks=[
            lambda r: len(r["data"]["planets"]) == 10,
            lambda r: r["meta"]["calculation_source"] is not None
        ]
    )

# Integration testing
@workflow_test
def test_chart_creation_workflow():
    # Test the entire workflow from chart creation to report generation
    workflow = workflow_test("chart_to_report")
    
    # Step 1: Create a chart
    chart_id = workflow.execute_step(
        "create_chart",
        input_data=generate_birth_data()
    )
    
    # Step 2: Generate a basic report
    report_id = workflow.execute_step(
        "generate_basic_report",
        chart_id=chart_id
    )
    
    # Step 3: Verify the report was saved
    report_data = workflow.execute_step(
        "fetch_report",
        report_id=report_id
    )
    
    # Validate the end result
    assert report_data["chart_id"] == chart_id
    assert len(report_data["sections"]) >= 5
    assert workflow.step_durations["generate_basic_report"] < 2.0  # Should take < 2s
```

## Testing Best Practices

### 1. Test Organization

- Group tests by functional area
- Use descriptive test names
- Separate unit, integration, and performance tests
- Organize fixtures by domain
- Maintain clean test isolation

### 2. Test Coverage

- Aim for comprehensive coverage of calculation logic
- Test edge cases thoroughly
- Include negative testing scenarios
- Verify all API contracts
- Test configuration variations

### 3. Performance Testing

- Establish baseline performance expectations
- Test with realistic data volumes
- Include stress tests for critical paths
- Monitor memory usage
- Test cache effectiveness

### 4. Test Data Management

- Use deterministic test data where possible
- Separate test data from test logic
- Version control large test datasets
- Document test data origins and assumptions
- Provide tools to refresh test data

### 5. Mocking Strategy

- Mock external dependencies consistently
- Document mock behavior
- Make mocks configurable
- Test with both mocks and real integrations
- Verify mock fidelity to real systems

## Test Execution

The testing utilities support multiple test execution modes:

1. **Fast mode:** Quick tests for development cycles
2. **Standard mode:** Complete test suite for CI/CD pipelines
3. **Extended mode:** In-depth tests including performance and stress testing
4. **Integration mode:** Tests with real external dependencies
5. **Coverage mode:** Tests instrumented for coverage analysis

## Testing Environment Setup

Utilities for setting up testing environments:

1. Test database initialization
2. Ephemeris data preparation
3. Configuration overrides for testing
4. Test user creation
5. Test data seeding

## Common Testing Patterns

The utilities support common testing patterns:

1. **Given-When-Then:** For behavior-driven tests
2. **Arrange-Act-Assert:** For unit testing
3. **Setup-Exercise-Verify-Teardown:** For complex tests
4. **Test Parameterization:** For coverage of multiple scenarios
5. **Test Fixtures:** For reusable test components 