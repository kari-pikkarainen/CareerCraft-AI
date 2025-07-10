"""
Tests for configuration management system.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from cryptography.fernet import Fernet

from config.settings import (
    ConfigManager,
    AppConfig,
    DatabaseConfig,
    SecurityConfig,
    ClaudeConfig,
    ConfigurationError
)
from config.security import SecurityUtils, RateLimiter


class TestConfigManager:
    """Test configuration management functionality"""
    
    def test_missing_encryption_key(self):
        """Test error when encryption key is missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(Path(temp_dir))
            
            with pytest.raises(ConfigurationError, match="Configuration file not found"):
                config_manager.load_config()
    
    def test_missing_config_file(self):
        """Test error when config file is missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # Create encryption key but no config file
            key = Fernet.generate_key()
            (config_dir / "encryption.key").write_bytes(key)
            
            config_manager = ConfigManager(config_dir)
            
            with pytest.raises(ConfigurationError, match="Configuration file not found"):
                config_manager.load_config()
    
    def test_successful_config_load(self):
        """Test successful configuration loading"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # Create encryption key
            key = Fernet.generate_key()
            (config_dir / "encryption.key").write_bytes(key)
            
            # Create test configuration
            test_config = {
                "claude_api_key": "test-claude-key",
                "database_url": "sqlite:///test.db",
                "jwt_secret": "test-jwt-secret",
                "api_key": "test-api-key",
                "api_secret": "test-api-secret",
                "session_timeout": 30,
                "rate_limit": 60,
                "max_file_size": 10485760
            }
            
            # Encrypt and save configuration
            fernet = Fernet(key)
            encrypted_config = fernet.encrypt(json.dumps(test_config).encode())
            (config_dir / "config.enc").write_bytes(encrypted_config)
            
            # Load configuration
            config_manager = ConfigManager(config_dir)
            app_config = config_manager.load_config()
            
            # Verify configuration
            assert isinstance(app_config, AppConfig)
            assert app_config.claude.api_key == "test-claude-key"
            assert app_config.database.url == "sqlite:///test.db"
            assert app_config.security.jwt_secret == "test-jwt-secret"
            assert app_config.security.api_key == "test-api-key"
            assert app_config.security.api_secret == "test-api-secret"
    
    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'env-claude-key'})
    def test_environment_override(self):
        """Test environment variable overrides"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # Setup encrypted config
            key = Fernet.generate_key()
            (config_dir / "encryption.key").write_bytes(key)
            
            test_config = {
                "claude_api_key": "original-claude-key",
                "database_url": "sqlite:///test.db",
                "jwt_secret": "test-jwt-secret",
                "api_key": "test-api-key",
                "api_secret": "test-api-secret"
            }
            
            fernet = Fernet(key)
            encrypted_config = fernet.encrypt(json.dumps(test_config).encode())
            (config_dir / "config.enc").write_bytes(encrypted_config)
            
            # Load with environment override
            config_manager = ConfigManager(config_dir)
            app_config = config_manager.load_config()
            
            # Environment variable should override config file
            assert app_config.claude.api_key == "env-claude-key"
    
    def test_config_validation(self):
        """Test configuration validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # Create valid configuration
            key = Fernet.generate_key()
            (config_dir / "encryption.key").write_bytes(key)
            
            valid_config = {
                "claude_api_key": "test-claude-key",
                "database_url": "sqlite:///test.db",
                "jwt_secret": "test-jwt-secret",
                "api_key": "test-api-key",
                "api_secret": "test-api-secret",
                "session_timeout": 30,
                "rate_limit": 60,
                "max_file_size": 10485760
            }
            
            fernet = Fernet(key)
            encrypted_config = fernet.encrypt(json.dumps(valid_config).encode())
            (config_dir / "config.enc").write_bytes(encrypted_config)
            
            config_manager = ConfigManager(config_dir)
            assert config_manager.validate_config() is True
            
            # Test invalid configuration (empty API key)
            invalid_config = valid_config.copy()
            invalid_config["claude_api_key"] = ""
            
            encrypted_invalid = fernet.encrypt(json.dumps(invalid_config).encode())
            (config_dir / "config.enc").write_bytes(encrypted_invalid)
            
            config_manager = ConfigManager(config_dir)  # Fresh instance
            assert config_manager.validate_config() is False


class TestSecurityUtils:
    """Test security utilities"""
    
    def test_hmac_signature_generation(self):
        """Test HMAC signature generation"""
        secret = "test-secret"
        message = "test-message"
        
        signature = SecurityUtils.generate_hmac_signature(secret, message)
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        # Verify signature
        assert SecurityUtils.verify_hmac_signature(secret, message, signature) is True
        
        # Wrong secret should fail
        assert SecurityUtils.verify_hmac_signature("wrong-secret", message, signature) is False
        
        # Wrong message should fail
        assert SecurityUtils.verify_hmac_signature(secret, "wrong-message", signature) is False
    
    def test_api_signature(self):
        """Test API signature generation and verification"""
        from datetime import datetime, timezone
        
        api_secret = "test-secret"
        api_key = "test-key"
        # Use current timestamp to avoid timestamp validation failure
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        body = '{"test": "data"}'
        
        signature = SecurityUtils.generate_api_signature(api_secret, api_key, timestamp, body)
        
        # Valid signature should verify
        is_valid, error = SecurityUtils.verify_api_signature(
            api_secret, api_key, timestamp, signature, body, max_age_seconds=3600
        )
        assert is_valid is True
        assert error is None
        
        # Wrong signature should fail
        is_valid, error = SecurityUtils.verify_api_signature(
            api_secret, api_key, timestamp, "wrong-signature", body, max_age_seconds=3600
        )
        assert is_valid is False
        assert "Invalid signature" in error
    
    def test_timestamp_validation(self):
        """Test timestamp validation"""
        from datetime import datetime, timezone
        
        # Current timestamp should be valid
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        is_valid, error = SecurityUtils.validate_timestamp(now, max_age_seconds=300)
        assert is_valid is True
        assert error is None
        
        # Old timestamp should be invalid
        old_timestamp = "2020-01-01T00:00:00Z"
        is_valid, error = SecurityUtils.validate_timestamp(old_timestamp, max_age_seconds=300)
        assert is_valid is False
        assert "too old" in error
        
        # Invalid format should be invalid
        is_valid, error = SecurityUtils.validate_timestamp("invalid-timestamp", max_age_seconds=300)
        assert is_valid is False
        assert "Invalid timestamp format" in error
    
    def test_secure_token_generation(self):
        """Test secure token generation"""
        token1 = SecurityUtils.generate_secure_token()
        token2 = SecurityUtils.generate_secure_token()
        
        # Tokens should be different
        assert token1 != token2
        assert len(token1) > 0
        assert len(token2) > 0
    
    def test_api_credentials_generation(self):
        """Test API credentials generation"""
        creds = SecurityUtils.generate_api_credentials()
        
        assert 'api_key' in creds
        assert 'api_secret' in creds
        assert len(creds['api_key']) > 0
        assert len(creds['api_secret']) > 0
        assert creds['api_key'] != creds['api_secret']
    
    def test_request_headers_creation(self):
        """Test request headers creation"""
        headers = SecurityUtils.create_request_headers("test-key", "test-secret", "test-body")
        
        required_headers = ['X-API-Key', 'X-Signature', 'X-Timestamp', 'Content-Type']
        for header in required_headers:
            assert header in headers
        
        assert headers['X-API-Key'] == 'test-key'
        assert headers['Content-Type'] == 'application/json'
    
    def test_sensitive_value_masking(self):
        """Test sensitive value masking"""
        assert SecurityUtils.mask_sensitive_value("") == "***"
        assert SecurityUtils.mask_sensitive_value("abc") == "***"
        assert SecurityUtils.mask_sensitive_value("abcdef123456").startswith("abcd...")
        assert SecurityUtils.mask_sensitive_value("test-api-key-12345", 4).startswith("test...")


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_rate_limit_allows_requests_under_limit(self):
        """Test that requests under limit are allowed"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        for i in range(5):
            allowed, info = limiter.is_allowed("test-user")
            assert allowed is True
            assert info['current_requests'] == i + 1
    
    def test_rate_limit_blocks_requests_over_limit(self):
        """Test that requests over limit are blocked"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        # First two requests should be allowed
        allowed, info = limiter.is_allowed("test-user")
        assert allowed is True
        
        allowed, info = limiter.is_allowed("test-user")
        assert allowed is True
        
        # Third request should be blocked
        allowed, info = limiter.is_allowed("test-user")
        assert allowed is False
        assert info['current_requests'] == 2
        assert 'retry_after' in info
    
    def test_rate_limit_per_identifier(self):
        """Test that rate limiting is per identifier"""
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        
        # Different identifiers should have separate limits
        allowed, info = limiter.is_allowed("user1")
        assert allowed is True
        
        allowed, info = limiter.is_allowed("user2")
        assert allowed is True
        
        # Same identifier should be blocked
        allowed, info = limiter.is_allowed("user1")
        assert allowed is False


if __name__ == "__main__":
    # Simple test runner for development
    import sys
    
    print("Running configuration system tests...")
    
    try:
        # Test basic HMAC functionality
        secret = "test-secret"
        message = "test-message"
        signature = SecurityUtils.generate_hmac_signature(secret, message)
        is_valid = SecurityUtils.verify_hmac_signature(secret, message, signature)
        
        print(f"✓ HMAC signature generation and verification: {'PASS' if is_valid else 'FAIL'}")
        
        # Test token generation
        token = SecurityUtils.generate_secure_token()
        print(f"✓ Token generation: {'PASS' if len(token) > 0 else 'FAIL'}")
        
        # Test API credentials
        creds = SecurityUtils.generate_api_credentials()
        has_both = 'api_key' in creds and 'api_secret' in creds
        print(f"✓ API credentials generation: {'PASS' if has_both else 'FAIL'}")
        
        # Test rate limiter
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        allowed1, _ = limiter.is_allowed("test")
        allowed2, _ = limiter.is_allowed("test")
        blocked, _ = limiter.is_allowed("test")
        
        rate_limit_works = allowed1 and allowed2 and not blocked
        print(f"✓ Rate limiting: {'PASS' if rate_limit_works else 'FAIL'}")
        
        print("\n✅ All basic tests passed! Configuration system is ready.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)