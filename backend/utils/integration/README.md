# Integration Utilities

This directory contains utility functions and tools for integrating the astrology application with external systems, libraries, and services.

## Purpose

The integration utilities provide standardized interfaces, adapters, and connectors for interacting with external systems, ensuring clean integration boundaries, error handling, and compatibility with third-party services and libraries used throughout the astrology application.

## Key Components

### 1. External Library Adapters

Adapters for third-party astrological calculation libraries.

**Features:**
- Swiss Ephemeris adapter
- FlatLib adapter
- Astro Engine compatibility layer
- Jyotish library integration
- Version compatibility management
- Consistent interface across libraries

### 2. API Client Utilities

Tools for interacting with external APIs.

**Features:**
- HTTP client abstraction
- Request/response formatting
- Authentication management
- Rate limiting handling
- Error handling and retries
- API version negotiation

### 3. Data Source Connectors

Connectors for external data sources.

**Features:**
- Astronomical data providers
- Timezone database integration
- Geocoding service integration
- Weather data integration
- Calendar system connectors
- Historical event databases

### 4. Notification Service Integration

Utilities for integrated notification services.

**Features:**
- Email service integration
- SMS notification integration
- Push notification services
- Webhook event dispatching
- In-app notification delivery
- Message templating

### 5. Payment Processing Integration

Tools for payment service integration.

**Features:**
- Payment gateway adapters
- Subscription management
- Invoice generation
- Payment verification
- Refund processing
- Pricing tier management

### 6. Authentication Provider Integration

Utilities for external authentication services.

**Features:**
- OAuth provider integration
- Social login adapters
- SAML integration
- JWT token handling
- Two-factor authentication
- Single sign-on support

### 7. Storage System Integration

Tools for external storage systems.

**Features:**
- Cloud storage adapters (S3, GCS, etc.)
- CDN integration
- File system abstraction
- Backup service integration
- Media asset management
- Storage migration utilities

### 8. Analytics and Tracking Integration

Utilities for analytics and tracking services.

**Features:**
- Analytics service clients
- Event tracking standardization
- User journey tracking
- Conversion tracking
- Custom metrics reporting
- Privacy-compliant data collection

## Usage Examples

```python
from backend.utils.integration.ephemeris import SwissEphemerisAdapter, FlatLibAdapter
from backend.utils.integration.api_clients import GeocodingClient, TimezoneClient
from backend.utils.integration.notifications import EmailService, PushNotifier
from backend.utils.integration.payment import PaymentProcessor, SubscriptionManager
from backend.utils.integration.auth import OAuthProvider, SocialLoginManager
from backend.utils.integration.storage import CloudStorage, AssetManager
from backend.utils.integration.analytics import AnalyticsTracker, EventLogger

# Using ephemeris library adapters
def calculate_planet_positions(birth_data, calculation_options):
    # Select the appropriate adapter based on configuration or availability
    adapter = SwissEphemerisAdapter() if use_swiss_eph() else FlatLibAdapter()
    
    # Use a consistent interface regardless of underlying library
    planet_positions = adapter.calculate_planet_positions(
        date=birth_data["date"],
        latitude=birth_data["latitude"],
        longitude=birth_data["longitude"],
        options=calculation_options
    )
    
    return planet_positions

# Using API clients
async def enrich_location_data(location_query):
    # Geocode the location
    geocoding_client = GeocodingClient()
    location_data = await geocoding_client.geocode(location_query)
    
    if not location_data:
        raise ValueError(f"Could not geocode location: {location_query}")
    
    # Get timezone for the coordinates
    timezone_client = TimezoneClient()
    timezone_data = await timezone_client.get_timezone(
        latitude=location_data["latitude"],
        longitude=location_data["longitude"]
    )
    
    # Combine and return enriched data
    return {
        **location_data,
        "timezone": timezone_data["timezone_id"],
        "utc_offset": timezone_data["utc_offset"]
    }

# Using notification services
def send_chart_notification(user, chart_data):
    # Initialize notification services
    email = EmailService()
    push = PushNotifier()
    
    # Prepare notification content
    notification = {
        "subject": "Your Astrological Chart is Ready",
        "message": f"Your {chart_data['chart_type']} chart has been generated and is ready to view.",
        "deep_link": f"/charts/{chart_data['chart_id']}"
    }
    
    # Send through multiple channels
    email.send(
        recipient=user.email,
        template="chart_ready",
        context={"user": user, "chart": chart_data}
    )
    
    if user.push_enabled:
        push.send_notification(
            user_id=user.id,
            title=notification["subject"],
            body=notification["message"],
            data={"deep_link": notification["deep_link"]}
        )

# Using payment processing
async def process_subscription(user, plan_id, payment_method):
    # Initialize payment processor
    payment = PaymentProcessor()
    subscriptions = SubscriptionManager()
    
    try:
        # Process the payment
        payment_result = await payment.create_payment(
            amount=get_plan_price(plan_id),
            currency="USD",
            payment_method=payment_method,
            description=f"Astrology subscription: {get_plan_name(plan_id)}"
        )
        
        # Create subscription if payment successful
        if payment_result["status"] == "succeeded":
            subscription = await subscriptions.create_subscription(
                user_id=user.id,
                plan_id=plan_id,
                payment_id=payment_result["id"],
                start_date=get_current_date(),
                auto_renew=True
            )
            
            return {
                "success": True,
                "subscription_id": subscription["id"],
                "next_billing_date": subscription["next_billing_date"]
            }
    except PaymentError as e:
        log_error(f"Payment failed for user {user.id}: {str(e)}")
        return {
            "success": False,
            "error": "payment_failed",
            "message": str(e)
        }

# Using authentication providers
async def handle_social_login(provider, auth_code):
    # Initialize social login manager
    social_auth = SocialLoginManager()
    
    # Exchange auth code for user profile
    user_profile = await social_auth.authenticate(
        provider=provider,
        auth_code=auth_code
    )
    
    # Find or create user
    user = find_user_by_email(user_profile["email"])
    if not user:
        user = create_new_user(
            email=user_profile["email"],
            name=user_profile["name"],
            auth_provider=provider,
            auth_provider_id=user_profile["id"]
        )
    
    # Generate session token
    token = generate_auth_token(user.id)
    
    return {
        "user_id": user.id,
        "token": token,
        "is_new_user": user.is_new
    }

# Using storage services
def store_chart_image(chart_id, image_data):
    # Initialize storage service
    storage = CloudStorage()
    asset_manager = AssetManager()
    
    # Store image in cloud storage
    image_path = f"charts/{chart_id}/chart_wheel.png"
    image_url = storage.store_file(
        path=image_path,
        data=image_data,
        content_type="image/png",
        public=True
    )
    
    # Register in asset manager
    asset_manager.register_asset(
        asset_type="chart_image",
        entity_id=chart_id,
        url=image_url,
        metadata={
            "type": "wheel_chart",
            "format": "png",
            "creation_date": get_current_date()
        }
    )
    
    return image_url

# Using analytics tracking
def track_chart_generation(user_id, chart_type, generation_time_ms):
    # Initialize analytics
    analytics = AnalyticsTracker()
    
    # Track event
    analytics.track_event(
        event_name="chart_generated",
        user_id=user_id,
        properties={
            "chart_type": chart_type,
            "generation_time_ms": generation_time_ms,
            "subscription_level": get_user_subscription_level(user_id)
        }
    )
    
    # Update user properties if needed
    analytics.update_user_properties(
        user_id=user_id,
        properties={
            "last_chart_generated_at": get_current_timestamp(),
            "total_charts_generated": increment_counter("charts_generated", user_id)
        }
    )
```

## Integration Principles

### 1. Abstraction and Decoupling

The integration utilities follow these principles:

- **Adapter Pattern:** Provide consistent interfaces for varied implementations
- **Dependency Inversion:** Depend on abstractions, not concrete implementations
- **Service Locator:** Allow runtime selection of implementation
- **Feature Detection:** Adaptively use available services
- **Graceful Degradation:** Handle unavailable services gracefully

### 2. Error Handling

Robust error handling strategies include:

- **Retry Mechanisms:** Configurable retries for transient failures
- **Circuit Breakers:** Prevent cascading failures
- **Fallbacks:** Alternative implementations when primary fails
- **Detailed Logging:** Comprehensive error context
- **Rate Limit Handling:** Respectful backoff when rate limited
- **Timeout Management:** Appropriate timeouts for external calls

### 3. Consistency and Standards

Standardized approaches across integrations:

- **Common Interface Patterns:** Consistent method signatures
- **Error Standardization:** Normalized error formats
- **Configuration Structure:** Uniform configuration approach
- **Authentication Handling:** Standard authentication flow
- **Logging Conventions:** Consistent integration logging
- **Metrics Collection:** Standard performance metrics

## Integration Configuration

Each integration can be configured through:

1. **Environment Variables:** For deployment-specific settings
2. **Configuration Files:** For standard settings
3. **Runtime Configuration:** For dynamic adjustments
4. **Feature Flags:** For enabling/disabling integrations
5. **Credentials Store:** For secure API keys and secrets

## Testing Integrations

The integration utilities include comprehensive testing support:

1. **Mock Implementations:** For testing without external dependencies
2. **Recorded Responses:** For reliable testing with real response patterns
3. **Integration Tests:** For verifying actual external service behavior
4. **Contract Tests:** For ensuring interface compliance
5. **Configuration Tests:** For validating configuration handling

## Monitoring and Observability

Integration monitoring capabilities include:

1. **Performance Metrics:** Response times, error rates, etc.
2. **Health Checks:** Availability monitoring
3. **Usage Tracking:** API call volumes and patterns
4. **Dependency Mapping:** Service dependency visualization
5. **Alert Configuration:** Thresholds for integration issues 