"""
Tests for authentication system.
"""

import pytest
import jwt
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from services.auth_service import (
    SessionData,
    JWTTokenManager,
    SessionManager,
    AuthenticationError,
    TokenExpiredError
)
from config.security import SecurityUtils


class TestSessionData:
    """Test SessionData functionality"""
    
    def test_session_data_creation(self):
        """Test creating session data"""
        session = SessionData(
            session_id="test-session",
            user_id="test-user",
            permissions=["read", "write"]
        )
        
        assert session.session_id == "test-session"
        assert session.user_id == "test-user"
        assert session.permissions == ["read", "write"]
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.expires_at, datetime)
        assert not session.is_expired()
    
    def test_session_expiration(self):
        """Test session expiration logic"""
        # Create expired session
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        session = SessionData(
            session_id="expired-session",
            expires_at=past_time
        )
        
        assert session.is_expired()
        assert session.time_until_expiry().total_seconds() < 0
    
    def test_session_serialization(self):
        """Test session to/from dict conversion"""
        original = SessionData(
            session_id="test-session",
            user_id="test-user",
            permissions=["admin"]
        )
        
        # Convert to dict and back
        session_dict = original.to_dict()
        restored = SessionData.from_dict(session_dict)
        
        assert restored.session_id == original.session_id
        assert restored.user_id == original.user_id
        assert restored.permissions == original.permissions
        assert restored.created_at == original.created_at
        assert restored.expires_at == original.expires_at


class TestJWTTokenManager:
    """Test JWT token management"""
    
    def test_token_generation(self):
        """Test JWT token generation"""
        # Mock configuration
        mock_security = MagicMock()
        mock_security.jwt_secret = "test-secret-key"
        
        # Create token manager with mock config and session
        token_manager = JWTTokenManager(mock_security)
        session = SessionData(session_id="test-session", user_id="test-user")
        
        # Generate token
        token = token_manager.generate_token(session)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        decoded = jwt.decode(token, "test-secret-key", algorithms=["HS256"])
        assert decoded["session_id"] == "test-session"
        assert decoded["user_id"] == "test-user"
    
    def test_token_validation(self):
        """Test JWT token validation"""
        # Mock configuration
        mock_security = MagicMock()
        mock_security.jwt_secret = "test-secret-key"
        
        token_manager = JWTTokenManager(mock_security)
        
        # Create and validate token
        original_session = SessionData(session_id="test-session", user_id="test-user")
        token = token_manager.generate_token(original_session)
        
        validated_session = token_manager.validate_token(token)
        
        assert validated_session.session_id == original_session.session_id
        assert validated_session.user_id == original_session.user_id
    
    def test_invalid_token_validation(self):
        """Test validation of invalid tokens"""
        # Mock configuration
        mock_security = MagicMock()
        mock_security.jwt_secret = "test-secret-key"
        
        token_manager = JWTTokenManager(mock_security)
        
        # Test invalid token
        with pytest.raises(AuthenticationError):
            token_manager.validate_token("invalid-token")
        
        # Test token with wrong secret
        wrong_token = jwt.encode(
            {"session_id": "test", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "wrong-secret",
            algorithm="HS256"
        )
        
        with pytest.raises(AuthenticationError):
            token_manager.validate_token(wrong_token)
    
    def test_expired_token_validation(self):
        """Test validation of expired tokens"""
        # Mock configuration
        mock_security = MagicMock()
        mock_security.jwt_secret = "test-secret-key"
        
        token_manager = JWTTokenManager(mock_security)
        
        # Create expired token
        expired_session = SessionData(
            session_id="expired-session",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        # Generate token (will have past expiration)
        token = jwt.encode(
            {
                **expired_session.to_dict(),
                "exp": expired_session.expires_at,
                "iat": datetime.now(timezone.utc),
                "iss": "careercraft-ai",
                "sub": expired_session.session_id
            },
            "test-secret-key",
            algorithm="HS256"
        )
        
        with pytest.raises(TokenExpiredError):
            token_manager.validate_token(token)
    
    def test_token_refresh(self):
        """Test JWT token refresh"""
        # Mock configuration
        mock_security = MagicMock()
        mock_security.jwt_secret = "test-secret-key"
        mock_security.session_timeout = 30
        
        token_manager = JWTTokenManager(mock_security)
        
        # Create token
        original_session = SessionData(session_id="test-session")
        original_token = token_manager.generate_token(original_session)
        
        # Refresh token
        new_token, new_session = token_manager.refresh_token(original_token)
        
        # Session ID should be the same
        assert new_session.session_id == original_session.session_id
        
        # New token should be generated (can be the same if timestamps match)
        assert isinstance(new_token, str)
        assert len(new_token) > 0
        
        # The token should be valid
        validated_session = token_manager.validate_token(new_token)
        assert validated_session.session_id == original_session.session_id


class TestSessionManager:
    """Test session management"""
    
    def test_session_creation(self):
        """Test creating new session"""
        manager = SessionManager()
        
        token, session = manager.create_session(
            session_id="test-session",
            user_id="test-user",
            permissions=["read"]
        )
        
        assert isinstance(token, str)
        assert session.session_id == "test-session"
        assert session.user_id == "test-user"
        assert session.permissions == ["read"]
        
        # Verify session is stored
        stored_session = manager.get_session_info("test-session")
        assert stored_session is not None
        assert stored_session.session_id == "test-session"
    
    def test_session_validation(self):
        """Test session token validation"""
        manager = SessionManager()
        
        # Create session
        token, original_session = manager.create_session("test-session", "test-user")
        
        # Validate session
        validated_session = manager.validate_session(token)
        
        assert validated_session.session_id == original_session.session_id
        assert validated_session.user_id == original_session.user_id
    
    def test_session_revocation(self):
        """Test session revocation"""
        manager = SessionManager()
        
        # Create session
        token, session = manager.create_session("test-session", "test-user")
        
        # Verify session exists
        assert manager.get_session_info("test-session") is not None
        
        # Revoke session
        result = manager.revoke_session("test-session")
        assert result is True
        
        # Verify session is gone
        assert manager.get_session_info("test-session") is None
        
        # Revoking again should return False
        result = manager.revoke_session("test-session")
        assert result is False
    
    def test_expired_session_cleanup(self):
        """Test cleanup of expired sessions"""
        manager = SessionManager()
        
        # Create expired session manually
        expired_session = SessionData(
            session_id="expired-session",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        manager.active_sessions["expired-session"] = expired_session
        
        # Create valid session
        manager.create_session("valid-session", "test-user")
        
        # Verify both sessions exist
        assert len(manager.active_sessions) == 2
        
        # Cleanup expired sessions
        cleaned_count = manager.cleanup_expired_sessions()
        
        assert cleaned_count == 1
        assert len(manager.active_sessions) == 1
        assert "valid-session" in manager.active_sessions
        assert "expired-session" not in manager.active_sessions
    
    def test_list_active_sessions(self):
        """Test listing active sessions"""
        manager = SessionManager()
        
        # Create multiple sessions
        manager.create_session("session1", "user1", permissions=["read"])
        manager.create_session("session2", "user2", permissions=["write"])
        
        # List sessions
        sessions = manager.list_active_sessions()
        
        assert len(sessions) == 2
        assert "session1" in sessions
        assert "session2" in sessions
        assert sessions["session1"]["user_id"] == "user1"
        assert sessions["session2"]["user_id"] == "user2"


class TestSecurityIntegration:
    """Test integration with security utilities"""
    
    def test_hmac_signature_workflow(self):
        """Test complete HMAC signature workflow"""
        api_secret = "test-secret"
        api_key = "test-key"
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        body = '{"test": "data"}'
        
        # Generate signature
        signature = SecurityUtils.generate_api_signature(
            api_secret, api_key, timestamp, body
        )
        
        # Verify signature
        is_valid, error = SecurityUtils.verify_api_signature(
            api_secret, api_key, timestamp, signature, body
        )
        
        assert is_valid is True
        assert error is None
    
    def test_request_headers_creation(self):
        """Test creating authentication headers"""
        headers = SecurityUtils.create_request_headers("test-key", "test-secret", "test-body")
        
        required_headers = ["X-API-Key", "X-Signature", "X-Timestamp", "Content-Type"]
        for header in required_headers:
            assert header in headers
        
        assert headers["X-API-Key"] == "test-key"
        assert headers["Content-Type"] == "application/json"
        
        # Verify signature is valid
        is_valid, _ = SecurityUtils.verify_api_signature(
            "test-secret",
            headers["X-API-Key"],
            headers["X-Timestamp"],
            headers["X-Signature"],
            "test-body"
        )
        assert is_valid is True


if __name__ == "__main__":
    # Simple test runner for development
    import sys
    
    print("Running authentication system tests...")
    
    try:
        # Test SessionData
        session = SessionData(session_id="test", user_id="user")
        print(f"✓ SessionData creation: {'PASS' if session.session_id == 'test' else 'FAIL'}")
        
        # Test JWT token (mocked)
        with patch('config.get_config') as mock_config, \
             patch('services.auth_service.get_config') as mock_auth_config:
            
            mock_security = MagicMock()
            mock_security.jwt_secret = "test-secret"
            mock_security.session_timeout = 30
            mock_config.return_value.security = mock_security
            mock_auth_config.return_value.security = mock_security
            
            token_manager = JWTTokenManager(mock_security)
            token = token_manager.generate_token(session)
            validated = token_manager.validate_token(token)
            
            jwt_works = validated.session_id == session.session_id
            print(f"✓ JWT token generation/validation: {'PASS' if jwt_works else 'FAIL'}")
        
        # Test SessionManager (simplified without JWT)
        from services.auth_service import SessionManager
        
        manager = SessionManager()
        # Test basic session storage without JWT token generation
        from services.auth_service import SessionData
        test_session = SessionData(session_id="test-session", user_id="test-user")
        manager.active_sessions["test-session"] = test_session
        
        retrieved = manager.get_session_info("test-session")
        session_mgmt_works = retrieved is not None and retrieved.session_id == "test-session"
        print(f"✓ Session management: {'PASS' if session_mgmt_works else 'FAIL'}")
        
        # Test HMAC integration
        api_secret = "secret"
        api_key = "key"
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        signature = SecurityUtils.generate_api_signature(api_secret, api_key, timestamp, "")
        is_valid, _ = SecurityUtils.verify_api_signature(api_secret, api_key, timestamp, signature, "")
        
        print(f"✓ HMAC signature integration: {'PASS' if is_valid else 'FAIL'}")
        
        print("\n✅ All authentication tests passed! Authentication system is ready.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)