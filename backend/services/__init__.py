"""
Services package for CareerCraft AI.

Provides authentication, file processing, and external service integrations.
"""

from .auth_service import (
    SessionData,
    AuthenticationError,
    TokenExpiredError,
    JWTTokenManager,
    SessionManager,
    create_session,
    validate_session,
    refresh_session,
    revoke_session,
    get_session_manager
)

__all__ = [
    # Authentication
    'SessionData',
    'AuthenticationError',
    'TokenExpiredError',
    'JWTTokenManager',
    'SessionManager',
    'create_session',
    'validate_session',
    'refresh_session',
    'revoke_session',
    'get_session_manager'
]