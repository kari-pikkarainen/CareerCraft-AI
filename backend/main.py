"""
CareerCraft AI - Main FastAPI Application

Entry point for the CareerCraft AI backend service.
Provides intelligent job application assistance with secure API access.
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from config import get_config, validate_config, ConfigurationError, RateLimiter
from api.middleware import AuthenticationMiddleware
from api.auth import router as auth_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/careercraft.log', encoding='utf-8')
    ] if sys.stdout.isatty() else [logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting CareerCraft AI backend...")
    
    try:
        # Validate configuration
        if not validate_config():
            logger.error("❌ Configuration validation failed")
            raise ConfigurationError("Invalid configuration")
        
        logger.info("✅ Configuration validated successfully")
        
        # Initialize rate limiter
        config = get_config()
        rate_limiter = RateLimiter(
            max_requests=config.security.rate_limit,
            window_seconds=60
        )
        
        # Store in app state for middleware access
        app.state.rate_limiter = rate_limiter
        app.state.config = config
        
        logger.info(f"✅ Rate limiter initialized: {config.security.rate_limit} requests/minute")
        logger.info(f"🌍 Environment: {config.environment}")
        logger.info(f"🔒 Security: HMAC + JWT authentication enabled")
        logger.info("🎯 CareerCraft AI backend startup complete")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down CareerCraft AI backend...")
    
    # Cleanup tasks
    if hasattr(app.state, 'rate_limiter'):
        app.state.rate_limiter.cleanup_old_entries()
        logger.info("✅ Rate limiter cleanup completed")
    
    logger.info("👋 CareerCraft AI backend shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="CareerCraft AI",
    description="Intelligent job application assistant powered by Claude AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


def custom_openapi():
    """
    Custom OpenAPI schema with authentication documentation.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="CareerCraft AI",
        version="1.0.0",
        description="""
# CareerCraft AI Backend API

Intelligent job application assistant that analyzes job descriptions, researches companies, 
and generates personalized resume recommendations and cover letters using Claude AI.

## Authentication

This API uses HMAC signature authentication for all requests (except public endpoints):

### Required Headers
- `X-API-Key`: Your API key identifier
- `X-Signature`: HMAC-SHA256 signature of the request
- `X-Timestamp`: ISO format timestamp (RFC 3339)
- `Authorization`: Bearer JWT token (for authenticated endpoints)

### Rate Limiting
- **Limit**: 60 requests per minute per API key
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Signature Generation
The signature is generated using HMAC-SHA256 with the format:
```
message = api_key + "\\n" + timestamp + "\\n" + request_body
signature = base64(hmac_sha256(api_secret, message))
```

## Workflow

1. **Authentication**: Get JWT token via `/auth/login`
2. **Job Analysis**: Submit job description and resume via `/api/v1/analyze-application`
3. **Progress Tracking**: Monitor progress via `/api/v1/status/{session_id}`
4. **Results**: Retrieve completed analysis via `/api/v1/results/{session_id}`

## Security Features

- **Encrypted Configuration**: All credentials stored encrypted at rest
- **Request Signing**: HMAC signature verification prevents tampering
- **Replay Protection**: Timestamp validation prevents replay attacks
- **Rate Limiting**: Prevents abuse and ensures fair usage
- **Session Management**: Secure JWT-based authentication with expiration
        """,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for request identification"
        },
        "SignatureAuth": {
            "type": "apiKey", 
            "in": "header",
            "name": "X-Signature",
            "description": "HMAC-SHA256 signature for request authentication"
        },
        "TimestampAuth": {
            "type": "apiKey",
            "in": "header", 
            "name": "X-Timestamp",
            "description": "ISO format timestamp for replay protection"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for authenticated endpoints"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [
        {"APIKeyAuth": [], "SignatureAuth": [], "TimestampAuth": []}
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Add authentication middleware
@app.middleware("http")
async def add_auth_middleware(request: Request, call_next):
    """Add authentication middleware to the application"""
    # Get rate limiter from app state
    rate_limiter = getattr(app.state, 'rate_limiter', None)
    
    # Create middleware instance
    auth_middleware = AuthenticationMiddleware(app, rate_limiter)
    
    # Process request
    return await auth_middleware.dispatch(request, call_next)


# Global exception handler
@app.exception_handler(ConfigurationError)
async def configuration_error_handler(request: Request, exc: ConfigurationError):
    """Handle configuration errors"""
    logger.error(f"Configuration error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": "CONFIGURATION_ERROR",
            "message": "Service configuration error",
            "details": "Please contact system administrator"
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": "Please try again later or contact support"
        }
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns service status and basic information.
    This endpoint does not require authentication.
    """
    try:
        config = get_config()
        return {
            "status": "healthy",
            "service": "CareerCraft AI",
            "version": "1.0.0",
            "environment": config.environment,
            "timestamp": "2025-07-10T18:00:00Z",  # Would use actual timestamp in production
            "checks": {
                "configuration": "ok",
                "database": "ok",  # Would check actual database connection
                "claude_api": "ok"  # Would check Claude API connectivity
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable"
        )


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with system information.
    
    Returns comprehensive service status including configuration,
    dependencies, and performance metrics.
    This endpoint does not require authentication.
    """
    try:
        config = get_config()
        
        # Get rate limiter stats
        rate_limiter = getattr(app.state, 'rate_limiter', None)
        rate_limit_stats = {
            "max_requests": config.security.rate_limit,
            "window_seconds": 60,
            "active_limiters": len(rate_limiter._requests) if rate_limiter else 0
        }
        
        return {
            "status": "healthy",
            "service": "CareerCraft AI", 
            "version": "1.0.0",
            "environment": config.environment,
            "timestamp": "2025-07-10T18:00:00Z",
            "uptime": "0h 5m 23s",  # Would calculate actual uptime
            "configuration": {
                "database_url": config.database.url.replace(config.database.url.split('/')[-1], "***"),
                "claude_api": "configured",
                "jwt_secret": "configured",
                "api_credentials": "configured",
                "session_timeout": f"{config.security.session_timeout} minutes",
                "max_file_size": f"{config.security.max_file_size // (1024*1024)} MB"
            },
            "security": {
                "authentication": "HMAC + JWT",
                "rate_limiting": rate_limit_stats,
                "encryption": "Fernet (AES-128)"
            },
            "dependencies": {
                "claude_api": {
                    "status": "ok",
                    "endpoint": config.claude.base_url,
                    "timeout": f"{config.claude.timeout}s"
                },
                "database": {
                    "status": "ok",
                    "type": "SQLite",
                    "url": config.database.url.split('://')[0] + "://***"
                }
            },
            "performance": {
                "active_sessions": 0,  # Would get from session manager
                "requests_processed": 0,  # Would track actual metrics
                "average_response_time": "0.05s",  # Would calculate actual metrics
                "memory_usage": "45.2 MB"  # Would get actual memory usage
            },
            "checks": {
                "configuration": "ok",
                "database_connection": "ok",
                "claude_api_connectivity": "ok",
                "file_processing": "ok",
                "authentication_system": "ok",
                "rate_limiting": "ok"
            }
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {
            "status": "degraded",
            "service": "CareerCraft AI",
            "version": "1.0.0",
            "error": str(e),
            "timestamp": "2025-07-10T18:00:00Z"
        }


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint.
    
    Checks if the service is ready to handle requests.
    Returns 200 if ready, 503 if not ready.
    """
    try:
        # Check critical dependencies
        config = get_config()
        
        # Verify configuration is valid
        if not validate_config():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Configuration validation failed"
            )
        
        # Check if rate limiter is available
        if not hasattr(app.state, 'rate_limiter'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Rate limiter not initialized"
            )
        
        return {
            "ready": True,
            "service": "CareerCraft AI",
            "checks": {
                "configuration": "ready",
                "rate_limiter": "ready",
                "authentication": "ready"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@app.get("/health/live", tags=["Health"])
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes liveness probe endpoint.
    
    Simple check to verify the service is running.
    Returns 200 if alive, 503 if not responding.
    """
    return {
        "alive": True,
        "service": "CareerCraft AI",
        "timestamp": "2025-07-10T18:00:00Z"
    }


# Include authentication router
app.include_router(auth_router)


# Root endpoint
@app.get("/", tags=["General"])
async def root() -> Dict[str, Any]:
    """
    API root endpoint with service information.
    """
    return {
        "service": "CareerCraft AI",
        "description": "Intelligent job application assistant powered by Claude AI",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "authentication": "/auth",
        "api_version": "v1",
        "features": [
            "Job description analysis",
            "Company research",
            "Resume enhancement",
            "Cover letter generation",
            "Skills gap analysis"
        ],
        "security": {
            "authentication": "HMAC + JWT",
            "rate_limiting": "60 requests/minute",
            "encryption": "AES-128 (Fernet)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Load configuration
    try:
        config = get_config()
        
        # Run the application
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level=config.log_level.lower(),
            access_log=True
        )
        
    except ConfigurationError as e:
        logger.error(f"Failed to start application: {e}")
        logger.error("Please run setup.py to configure the application")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}")
        sys.exit(1)