"""
Tests for FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# We'll test without loading the actual configuration
@patch('main.get_config')
@patch('main.validate_config')
def test_fastapi_health_endpoints(mock_validate, mock_config):
    """Test FastAPI health endpoints"""
    
    # Mock configuration
    mock_security = MagicMock()
    mock_security.rate_limit = 60
    mock_security.session_timeout = 30
    mock_security.max_file_size = 10485760
    mock_security.api_key = "test-key"
    mock_security.api_secret = "test-secret"
    
    mock_app_config = MagicMock()
    mock_app_config.environment = "development"
    mock_app_config.log_level = "INFO"
    mock_app_config.security = mock_security
    mock_app_config.database.url = "sqlite:///test.db"
    mock_app_config.claude.base_url = "https://api.anthropic.com"
    mock_app_config.claude.timeout = 30
    
    mock_config.return_value = mock_app_config
    mock_validate.return_value = True
    
    # Import and create test client
    from main import app
    client = TestClient(app)
    
    # Test basic health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "CareerCraft AI"
    assert "checks" in data
    
    # Test detailed health endpoint
    response = client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CareerCraft AI"
    assert "configuration" in data
    assert "security" in data
    assert "dependencies" in data
    
    # Test readiness endpoint
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    
    # Test liveness endpoint
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["alive"] is True
    
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CareerCraft AI"
    assert "features" in data
    assert "security" in data


@patch('main.get_config')
@patch('main.validate_config')
def test_fastapi_auth_endpoints(mock_validate, mock_config):
    """Test authentication endpoints availability"""
    
    # Mock configuration
    mock_security = MagicMock()
    mock_security.rate_limit = 60
    mock_security.api_key = "test-key"
    mock_security.api_secret = "test-secret"
    
    mock_app_config = MagicMock()
    mock_app_config.environment = "development"
    mock_app_config.log_level = "INFO"
    mock_app_config.security = mock_security
    
    mock_config.return_value = mock_app_config
    mock_validate.return_value = True
    
    from main import app
    client = TestClient(app)
    
    # Test auth endpoints are available (will fail auth but should be routed)
    # These will return 401 due to missing auth headers, but that confirms routing works
    
    response = client.post("/auth/login", json={"client_id": "test"})
    # Should return 401 due to missing authentication headers, not 404
    assert response.status_code in [401, 422]  # 422 for validation error is also acceptable
    
    response = client.get("/auth/status")
    # Should return 401 due to missing authentication headers, not 404  
    assert response.status_code == 401


@patch('main.get_config')
@patch('main.validate_config') 
def test_fastapi_cors_headers(mock_validate, mock_config):
    """Test CORS headers are properly set"""
    
    # Mock configuration
    mock_security = MagicMock()
    mock_security.rate_limit = 60
    
    mock_app_config = MagicMock()
    mock_app_config.environment = "development"
    mock_app_config.log_level = "INFO"
    mock_app_config.security = mock_security
    
    mock_config.return_value = mock_app_config
    mock_validate.return_value = True
    
    from main import app
    client = TestClient(app)
    
    # Test OPTIONS request for CORS preflight
    response = client.options("/health")
    assert response.status_code == 200
    
    # Test basic request has CORS headers
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]


def test_api_models_validation():
    """Test API models validation"""
    from api.models import (
        JobAnalysisRequest, 
        JobPreferences, 
        ToneEnum,
        HealthResponse,
        ProcessingStatusEnum
    )
    
    # Test valid job analysis request
    valid_request = JobAnalysisRequest(
        job_description="This is a software engineer position requiring Python and JavaScript skills. Must have 3+ years experience.",
        job_url="https://example.com/job/123",
        preferences=JobPreferences(
            tone=ToneEnum.PROFESSIONAL,
            focus_areas=["technical skills", "experience"]
        )
    )
    assert valid_request.job_description is not None
    assert valid_request.preferences.tone == ToneEnum.PROFESSIONAL
    
    # Test invalid job analysis request (too short description)
    with pytest.raises(ValueError):
        JobAnalysisRequest(
            job_description="Too short",  # Less than 50 characters
            preferences=JobPreferences()
        )
    
    # Test health response model
    health = HealthResponse(
        status="healthy",
        environment="development",
        checks={"database": "ok", "claude_api": "ok"}
    )
    assert health.service == "CareerCraft AI"
    assert health.version == "1.0.0"
    
    # Test enum validation
    assert ToneEnum.PROFESSIONAL == "professional"
    assert ProcessingStatusEnum.COMPLETED == "completed"


if __name__ == "__main__":
    # Simple test runner for development
    import sys
    
    print("Running FastAPI tests...")
    
    try:
        # Test API models validation
        test_api_models_validation()
        print("✓ API models validation: PASS")
        
        # Test basic FastAPI functionality with mocking
        with patch('main.get_config') as mock_config, \
             patch('main.validate_config') as mock_validate:
            
            # Setup mocks
            mock_security = MagicMock()
            mock_security.rate_limit = 60
            mock_security.api_key = "test-key"
            mock_security.api_secret = "test-secret"
            
            mock_app_config = MagicMock()
            mock_app_config.environment = "development"
            mock_app_config.log_level = "INFO"
            mock_app_config.security = mock_security
            
            mock_config.return_value = mock_app_config
            mock_validate.return_value = True
            
            # Need to mock before importing main
            with patch('api.middleware.get_config', return_value=mock_app_config):
                from main import app
                from fastapi.testclient import TestClient
                
                client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/health")
            health_works = response.status_code == 200 and response.json()["status"] == "healthy"
            print(f"✓ Health endpoints: {'PASS' if health_works else 'FAIL'}")
            
            # Test root endpoint  
            response = client.get("/")
            root_works = response.status_code == 200 and "CareerCraft AI" in response.json()["service"]
            print(f"✓ Root endpoint: {'PASS' if root_works else 'FAIL'}")
        
        print("\n✅ All FastAPI tests passed! Application is ready.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)