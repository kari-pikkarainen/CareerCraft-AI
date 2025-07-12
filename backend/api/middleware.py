"""
Authentication Middleware

FastAPI middleware for request authentication and authorization.
Handles HMAC signature verification and JWT token validation.
"""

import json
import logging
from typing import Callable, Optional, Dict, Any, Tuple
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config import get_config, SecurityUtils, RateLimiter
from services.auth_service import (
    validate_session, 
    AuthenticationError, 
    TokenExpiredError,
    SessionData
)

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for FastAPI.
    
    Handles:
    - HMAC signature verification for API requests
    - Rate limiting per API key
    - JWT token validation for authenticated endpoints
    - Request/response logging for security auditing
    """
    
    def __init__(self, app, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(app)
        self.config = get_config()
        self.rate_limiter = rate_limiter or RateLimiter(
            max_requests=self.config.security.rate_limit,
            window_seconds=60
        )
        self.public_paths = {
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through authentication pipeline.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain
            
        Returns:
            Response object
        """
        start_time = logger.time() if hasattr(logger, 'time') else None
        
        try:
            # Skip authentication for public paths
            if self._is_public_path(request.url.path):
                response = await call_next(request)
                self._log_request(request, response, start_time, "public")
                return response
            
            # Skip authentication for CORS preflight OPTIONS requests
            if request.method == "OPTIONS":
                response = await call_next(request)
                self._log_request(request, response, start_time, "cors_preflight")
                return response
            
            # Verify HMAC signature
            auth_result = await self._verify_hmac_signature(request)
            if not auth_result["valid"]:
                return self._create_error_response(
                    status.HTTP_401_UNAUTHORIZED,
                    "INVALID_SIGNATURE",
                    auth_result["error"]
                )
            
            # Check rate limiting
            api_key = auth_result["api_key"]
            rate_limit_result = self._check_rate_limit(api_key)
            if not rate_limit_result["allowed"]:
                return self._create_rate_limit_response(rate_limit_result)
            
            # Add authentication info to request state
            request.state.api_key = api_key
            request.state.authenticated = True
            request.state.auth_method = "hmac"
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            self._add_rate_limit_headers(response, rate_limit_result)
            
            self._log_request(request, response, start_time, "authenticated")
            return response
            
        except Exception as e:
            import traceback
            logger.error(f"Authentication middleware error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._create_error_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "INTERNAL_ERROR",
                "Authentication processing failed"
            )
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (no authentication required)"""
        return path in self.public_paths or path.startswith("/static/")
    
    async def _verify_hmac_signature(self, request: Request) -> Dict[str, Any]:
        """
        Verify HMAC signature for API request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dictionary with verification result
        """
        try:
            # Extract required headers
            api_key = request.headers.get("X-API-Key")
            signature = request.headers.get("X-Signature")
            timestamp = request.headers.get("X-Timestamp")
            
            if not all([api_key, signature, timestamp]):
                return {
                    "valid": False,
                    "error": "Missing authentication headers (X-API-Key, X-Signature, X-Timestamp)"
                }
            
            # Validate API key
            if api_key != self.config.security.api_key:
                logger.warning(f"Invalid API key: {SecurityUtils.mask_sensitive_value(api_key)}")
                return {
                    "valid": False,
                    "error": "Invalid API key"
                }
            
            # Read request body for signature verification
            body = await self._get_request_body(request)
            
            # Verify signature
            is_valid, error = SecurityUtils.verify_api_signature(
                self.config.security.api_secret,
                api_key,
                timestamp,
                signature,
                body,
                max_age_seconds=300  # 5 minutes
            )
            
            if not is_valid:
                logger.warning(f"HMAC signature verification failed: {error}")
                return {
                    "valid": False,
                    "error": error or "Invalid signature"
                }
            
            return {
                "valid": True,
                "api_key": api_key
            }
            
        except Exception as e:
            logger.error(f"HMAC verification error: {e}")
            return {
                "valid": False,
                "error": f"Signature verification failed: {str(e)}"
            }
    
    async def _get_request_body(self, request: Request) -> str:
        """
        Get request body for signature verification.
        Preserves body for downstream processing.
        """
        try:
            # Check if this is a multipart/form-data request
            content_type = request.headers.get("content-type", "")
            if content_type.startswith("multipart/form-data"):
                # For FormData requests, use empty body for signature verification
                # This matches the frontend behavior where FormData signatures use empty body
                logger.debug("FormData request detected, using empty body for signature verification")
                return ""
            
            body = await request.body()
            
            # Store body in request state for reuse
            request.state.cached_body = body
            
            return body.decode('utf-8') if body else ""
        except Exception as e:
            logger.error(f"Failed to read request body: {e}")
            return ""
    
    def _check_rate_limit(self, api_key: str) -> Dict[str, Any]:
        """Check rate limiting for API key"""
        try:
            allowed, info = self.rate_limiter.is_allowed(api_key)
            return info
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # Allow request if rate limiter fails
            return {"allowed": True}
    
    def _create_error_response(
        self,
        status_code: int,
        error_code: str,
        message: str
    ) -> JSONResponse:
        """Create standardized error response"""
        return JSONResponse(
            status_code=status_code,
            content={
                "error": True,
                "error_code": error_code,
                "message": message,
                "timestamp": SecurityUtils.generate_secure_token(8)  # Simple timestamp placeholder
            }
        )
    
    def _create_rate_limit_response(self, rate_info: Dict[str, Any]) -> JSONResponse:
        """Create rate limit exceeded response"""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": True,
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests",
                "retry_after": rate_info.get("retry_after", 60)
            },
            headers={
                "Retry-After": str(int(rate_info.get("retry_after", 60))),
                "X-RateLimit-Limit": str(rate_info.get("max_requests", 60)),
                "X-RateLimit-Remaining": str(max(0, rate_info.get("max_requests", 60) - rate_info.get("current_requests", 0))),
                "X-RateLimit-Reset": rate_info.get("reset_time", "")
            }
        )
    
    def _add_rate_limit_headers(self, response: Response, rate_info: Dict[str, Any]) -> None:
        """Add rate limiting headers to response"""
        try:
            response.headers["X-RateLimit-Limit"] = str(rate_info.get("max_requests", 60))
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, rate_info.get("max_requests", 60) - rate_info.get("current_requests", 0))
            )
            response.headers["X-RateLimit-Reset"] = rate_info.get("reset_time", "")
        except Exception as e:
            logger.warning(f"Failed to add rate limit headers: {e}")
    
    def _log_request(
        self,
        request: Request,
        response: Response,
        start_time: Optional[float],
        auth_type: str
    ) -> None:
        """Log request for security auditing"""
        try:
            api_key = getattr(request.state, "api_key", "unknown")
            masked_key = SecurityUtils.mask_sensitive_value(api_key) if api_key != "unknown" else "none"
            
            duration = f"{(logger.time() - start_time):.3f}s" if start_time and hasattr(logger, 'time') else "unknown"
            
            logger.info(
                f"{request.method} {request.url.path} "
                f"status={response.status_code} "
                f"auth={auth_type} "
                f"api_key={masked_key} "
                f"duration={duration}"
            )
        except Exception as e:
            logger.warning(f"Request logging failed: {e}")


class JWTBearer(HTTPBearer):
    """
    JWT Bearer token authentication for FastAPI dependency injection.
    
    Use this as a dependency for endpoints that require JWT authentication.
    """
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> SessionData:
        """
        Validate JWT token and return session data.
        
        Args:
            request: FastAPI request object
            
        Returns:
            SessionData object
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Get token from Authorization header
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header missing",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Validate JWT token
            session_data = validate_session(credentials.credentials)
            
            # Add session info to request state
            request.state.session = session_data
            request.state.session_id = session_data.session_id
            request.state.user_id = session_data.user_id
            
            logger.debug(f"JWT authentication successful for session {session_data.session_id}")
            return session_data
            
        except TokenExpiredError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            logger.error(f"JWT authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication processing failed"
            )


class OptionalJWTBearer(JWTBearer):
    """
    Optional JWT Bearer authentication.
    Returns None if no token provided, validates if token is present.
    """
    
    def __init__(self):
        super().__init__(auto_error=False)
    
    async def __call__(self, request: Request) -> Optional[SessionData]:
        """
        Optionally validate JWT token.
        
        Args:
            request: FastAPI request object
            
        Returns:
            SessionData object or None if no token
        """
        try:
            credentials: Optional[HTTPAuthorizationCredentials] = await super(JWTBearer, self).__call__(request)
            
            if not credentials:
                return None
            
            # Validate token if provided
            session_data = validate_session(credentials.credentials)
            
            # Add session info to request state
            request.state.session = session_data
            request.state.session_id = session_data.session_id
            request.state.user_id = session_data.user_id
            
            return session_data
            
        except (TokenExpiredError, AuthenticationError):
            # For optional auth, return None on auth failure
            return None
        except Exception as e:
            logger.error(f"Optional JWT authentication error: {e}")
            return None


# Dependency instances for FastAPI
jwt_bearer = JWTBearer()
optional_jwt_bearer = OptionalJWTBearer()


def require_permissions(*permissions: str):
    """
    Dependency factory for permission-based authorization.
    
    Args:
        *permissions: Required permissions
        
    Returns:
        Dependency function
    """
    async def check_permissions(session: SessionData = jwt_bearer) -> SessionData:
        """Check if session has required permissions"""
        if not session.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        missing_permissions = set(permissions) - set(session.permissions)
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing_permissions)}"
            )
        
        return session
    
    return check_permissions