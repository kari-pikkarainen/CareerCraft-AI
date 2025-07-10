"""
API package for CareerCraft AI.

Provides FastAPI routers, middleware, and authentication.
"""

from .auth import router as auth_router
from .middleware import (
    AuthenticationMiddleware,
    JWTBearer,
    OptionalJWTBearer,
    jwt_bearer,
    optional_jwt_bearer,
    require_permissions
)

__all__ = [
    # Routers
    'auth_router',
    
    # Middleware
    'AuthenticationMiddleware',
    'JWTBearer',
    'OptionalJWTBearer',
    'jwt_bearer',
    'optional_jwt_bearer',
    'require_permissions'
]