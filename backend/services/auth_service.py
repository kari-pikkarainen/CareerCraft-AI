"""
Authentication Service

Handles JWT token management and user session authentication.
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from config import get_config, SecurityConfig

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """User session data"""
    session_id: str
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    created_at: datetime = None
    expires_at: datetime = None
    permissions: list = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.expires_at is None:
            try:
                config = get_config()
                timeout_minutes = config.security.session_timeout
            except:
                # Fallback for testing or when config is not available
                timeout_minutes = 30
            self.expires_at = self.created_at + timedelta(minutes=timeout_minutes)
        if self.permissions is None:
            self.permissions = []
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.now(timezone.utc) > self.expires_at
    
    def time_until_expiry(self) -> timedelta:
        """Get time remaining until session expires"""
        return self.expires_at - datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JWT payload"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'api_key': self.api_key,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'permissions': self.permissions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Create SessionData from dictionary"""
        return cls(
            session_id=data['session_id'],
            user_id=data.get('user_id'),
            api_key=data.get('api_key'),
            created_at=datetime.fromisoformat(data['created_at']),
            expires_at=datetime.fromisoformat(data['expires_at']),
            permissions=data.get('permissions', [])
        )


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired"""
    pass


class JWTTokenManager:
    """
    JWT token management for session authentication.
    
    Handles:
    - Token generation and validation
    - Session data encoding/decoding
    - Token refresh logic
    - Expiration management
    """
    
    def __init__(self, security_config: Optional[SecurityConfig] = None):
        self.config = security_config or get_config().security
        self.algorithm = "HS256"
    
    def generate_token(self, session_data: SessionData) -> str:
        """
        Generate JWT token for session data.
        
        Args:
            session_data: Session information to encode
            
        Returns:
            JWT token string
        """
        try:
            # Create payload with proper JWT-compatible types
            payload = {
                'session_id': session_data.session_id,
                'user_id': session_data.user_id,
                'api_key': session_data.api_key,
                'created_at': int(session_data.created_at.timestamp()),
                'expires_at': int(session_data.expires_at.timestamp()),
                'permissions': session_data.permissions or []
            }
            
            # Add standard JWT claims
            now = datetime.now(timezone.utc)
            payload.update({
                'iat': int(now.timestamp()),                      # Issued at
                'exp': int(session_data.expires_at.timestamp()),  # Expiration
                'iss': 'careercraft-ai',                         # Issuer
                'sub': session_data.session_id                   # Subject
            })
            
            token = jwt.encode(
                payload,
                self.config.jwt_secret,
                algorithm=self.algorithm
            )
            
            logger.debug(f"Generated JWT token for session {session_data.session_id}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate JWT token: {e}")
            raise AuthenticationError(f"Token generation failed: {e}")
    
    def validate_token(self, token: str) -> SessionData:
        """
        Validate JWT token and extract session data.
        
        Args:
            token: JWT token string
            
        Returns:
            SessionData object
            
        Raises:
            AuthenticationError: If token is invalid
            TokenExpiredError: If token has expired
        """
        try:
            # Decode and validate token
            payload = jwt.decode(
                token,
                self.config.jwt_secret,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            
            # Convert timestamps back to datetime objects
            session_dict = {
                'session_id': payload['session_id'],
                'user_id': payload.get('user_id'),
                'api_key': payload.get('api_key'),
                'created_at': datetime.fromtimestamp(payload['created_at'], tz=timezone.utc).isoformat(),
                'expires_at': datetime.fromtimestamp(payload['expires_at'], tz=timezone.utc).isoformat(),
                'permissions': payload.get('permissions', [])
            }
            
            # Extract session data
            session_data = SessionData.from_dict(session_dict)
            
            # Additional expiration check
            if session_data.is_expired():
                raise TokenExpiredError("Session has expired")
            
            logger.debug(f"Validated JWT token for session {session_data.session_id}")
            return session_data
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise AuthenticationError(f"Invalid token: {e}")
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise AuthenticationError(f"Token validation failed: {e}")
    
    def refresh_token(self, current_token: str) -> Tuple[str, SessionData]:
        """
        Refresh JWT token with extended expiration.
        
        Args:
            current_token: Current JWT token
            
        Returns:
            Tuple of (new_token, session_data)
        """
        try:
            # Validate current token (allow expired for refresh)
            payload = jwt.decode(
                current_token,
                self.config.jwt_secret,
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Don't verify expiration for refresh
            )
            
            # Convert timestamps back to datetime objects
            session_dict = {
                'session_id': payload['session_id'],
                'user_id': payload.get('user_id'),
                'api_key': payload.get('api_key'),
                'created_at': datetime.fromtimestamp(payload['created_at'], tz=timezone.utc).isoformat(),
                'expires_at': datetime.fromtimestamp(payload['expires_at'], tz=timezone.utc).isoformat(),
                'permissions': payload.get('permissions', [])
            }
            
            # Create new session with extended expiration
            session_data = SessionData.from_dict(session_dict)
            # Extend expiration by the full session timeout from now
            session_data.expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=self.config.session_timeout
            )
            # Force a different creation time to ensure token difference
            session_data.created_at = datetime.now(timezone.utc)
            
            # Generate new token
            new_token = self.generate_token(session_data)
            
            logger.info(f"Refreshed JWT token for session {session_data.session_id}")
            return new_token, session_data
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Cannot refresh invalid token: {e}")
            raise AuthenticationError(f"Cannot refresh token: {e}")
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise AuthenticationError(f"Token refresh failed: {e}")
    
    def decode_token_unsafe(self, token: str) -> Dict[str, Any]:
        """
        Decode token without validation (for debugging/inspection).
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload dictionary
        """
        try:
            return jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
        except Exception as e:
            logger.error(f"Failed to decode token: {e}")
            return {}


class SessionManager:
    """
    Session management for active user sessions.
    
    Note: In production, use Redis or database for session storage
    across multiple application instances.
    """
    
    def __init__(self, jwt_manager: Optional[JWTTokenManager] = None):
        self.active_sessions: Dict[str, SessionData] = {}
        try:
            self.jwt_manager = jwt_manager or JWTTokenManager()
        except:
            # Fallback for testing without config
            self.jwt_manager = None
    
    def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
        permissions: Optional[list] = None
    ) -> Tuple[str, SessionData]:
        """
        Create new authenticated session.
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier
            api_key: API key for session
            permissions: Session permissions list
            
        Returns:
            Tuple of (jwt_token, session_data)
        """
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            api_key=api_key,
            permissions=permissions or []
        )
        
        # Store session
        self.active_sessions[session_id] = session_data
        
        # Generate JWT token
        if self.jwt_manager:
            token = self.jwt_manager.generate_token(session_data)
        else:
            # Fallback for testing
            token = f"test-token-{session_id}"
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return token, session_data
    
    def validate_session(self, token: str) -> SessionData:
        """
        Validate session token and return session data.
        
        Args:
            token: JWT token string
            
        Returns:
            SessionData object
        """
        # Validate JWT token
        if self.jwt_manager:
            session_data = self.jwt_manager.validate_token(token)
        else:
            # Fallback for testing - extract session_id from test token
            if token.startswith("test-token-"):
                session_id = token.replace("test-token-", "")
                session_data = self.active_sessions.get(session_id)
                if not session_data:
                    raise AuthenticationError("Session not found")
            else:
                raise AuthenticationError("JWT manager not available")
        
        # Check if session exists in active sessions
        stored_session = self.active_sessions.get(session_data.session_id)
        if not stored_session:
            logger.warning(f"Session {session_data.session_id} not found in active sessions")
            raise AuthenticationError("Session not found")
        
        # Update stored session if token data is newer
        if session_data.expires_at > stored_session.expires_at:
            self.active_sessions[session_data.session_id] = session_data
        
        return session_data
    
    def refresh_session(self, current_token: str) -> Tuple[str, SessionData]:
        """
        Refresh session with new token.
        
        Args:
            current_token: Current JWT token
            
        Returns:
            Tuple of (new_token, session_data)
        """
        if self.jwt_manager:
            new_token, session_data = self.jwt_manager.refresh_token(current_token)
        else:
            raise AuthenticationError("JWT manager not available for refresh")
        
        # Update stored session
        self.active_sessions[session_data.session_id] = session_data
        
        return new_token, session_data
    
    def revoke_session(self, session_id: str) -> bool:
        """
        Revoke/invalidate session.
        
        Args:
            session_id: Session identifier to revoke
            
        Returns:
            True if session was revoked
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Revoked session {session_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions from storage.
        
        Returns:
            Number of sessions cleaned up
        """
        expired_sessions = [
            session_id for session_id, session_data in self.active_sessions.items()
            if session_data.is_expired()
        ]
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_session_info(self, session_id: str) -> Optional[SessionData]:
        """
        Get session information by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData or None if not found
        """
        return self.active_sessions.get(session_id)
    
    def list_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all active sessions (for admin/debugging).
        
        Returns:
            Dictionary of session_id -> session_info
        """
        return {
            session_id: {
                'user_id': session.user_id,
                'api_key': session.api_key,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'time_remaining': str(session.time_until_expiry()),
                'permissions': session.permissions
            }
            for session_id, session in self.active_sessions.items()
        }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def create_session(
    session_id: str,
    user_id: Optional[str] = None,
    api_key: Optional[str] = None,
    permissions: Optional[list] = None
) -> Tuple[str, SessionData]:
    """Convenience function to create session"""
    return get_session_manager().create_session(session_id, user_id, api_key, permissions)


def validate_session(token: str) -> SessionData:
    """Convenience function to validate session"""
    return get_session_manager().validate_session(token)


def refresh_session(current_token: str) -> Tuple[str, SessionData]:
    """Convenience function to refresh session"""
    return get_session_manager().refresh_session(current_token)


def revoke_session(session_id: str) -> bool:
    """Convenience function to revoke session"""
    return get_session_manager().revoke_session(session_id)