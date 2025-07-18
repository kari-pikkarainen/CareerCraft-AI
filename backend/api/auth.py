"""
Authentication API endpoints and utilities.

Handles session creation, token refresh, and authentication status.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
import secrets
import logging

from config import SecurityUtils
from services.auth_service import (
    create_session,
    validate_session,
    refresh_session,
    revoke_session,
    get_session_manager,
    AuthenticationError,
    TokenExpiredError,
    SessionData
)
from api.middleware import jwt_bearer, optional_jwt_bearer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models
class AuthRequest(BaseModel):
    """Authentication request model"""
    client_id: Optional[str] = Field(None, description="Client identifier")
    permissions: Optional[list[str]] = Field(default_factory=list, description="Requested permissions")


class AuthResponse(BaseModel):
    """Authentication response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    session_id: str = Field(..., description="Session identifier")
    permissions: list[str] = Field(default_factory=list, description="Granted permissions")


class TokenRefreshRequest(BaseModel):
    """Token refresh request model"""
    refresh_token: Optional[str] = Field(None, description="Current token to refresh")


class SessionInfoResponse(BaseModel):
    """Session information response model"""
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    api_key: Optional[str] = Field(None, description="Associated API key")
    created_at: datetime = Field(..., description="Session creation time")
    expires_at: datetime = Field(..., description="Session expiration time")
    permissions: list[str] = Field(default_factory=list, description="Session permissions")
    time_remaining: str = Field(..., description="Time until expiration")


class StatusResponse(BaseModel):
    """Authentication status response model"""
    authenticated: bool = Field(..., description="Whether request is authenticated")
    session_id: Optional[str] = Field(None, description="Current session ID")
    user_id: Optional[str] = Field(None, description="Current user ID")
    permissions: list[str] = Field(default_factory=list, description="Current permissions")
    expires_at: Optional[datetime] = Field(None, description="Session expiration time")


# Authentication Endpoints

@router.post("/login", response_model=AuthResponse)
async def login(request: Request) -> AuthResponse:
    """
    Create new authenticated session.
    
    This endpoint creates a new session and returns a JWT token.
    In a production system, this would typically validate user credentials.
    """
    try:
        # Get the cached body from middleware to avoid conflicts
        if hasattr(request.state, 'cached_body'):
            body = request.state.cached_body
        else:
            # Fallback to reading body directly
            body = await request.body()
            
        logger.debug(f"Request body length: {len(body) if body else 0}")
        logger.debug(f"Request body: {body.decode('utf-8') if body else 'empty'}")
        
        if body:
            import json
            body_data = json.loads(body.decode('utf-8'))
            auth_request = AuthRequest(**body_data)
        else:
            auth_request = AuthRequest()
        
        logger.info(f"Login request received for client: {auth_request.client_id}")
        
        # Generate session ID
        session_id = f"session_{secrets.token_urlsafe(16)}"
        logger.debug(f"Generated session ID: {session_id}")
        
        # Create session
        token, session_data = create_session(
            session_id=session_id,
            user_id=auth_request.client_id,
            permissions=auth_request.permissions or []
        )
        logger.debug(f"Session created successfully")
        
        # Calculate expiration time
        try:
            expires_in = int(session_data.time_until_expiry().total_seconds())
            logger.debug(f"Expires in: {expires_in} seconds")
        except Exception as e:
            logger.error(f"Error calculating expiration: {e}")
            expires_in = 1800  # Default to 30 minutes
        
        logger.info(f"Created session {session_id} for client {auth_request.client_id}")
        
        auth_response = AuthResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
            session_id=session_id,
            permissions=session_data.permissions
        )
        
        logger.debug(f"Returning auth response: {auth_response.model_dump()}")
        return auth_response
        
    except Exception as e:
        import traceback
        logger.error(f"Login failed: {e}")
        logger.error(f"Login traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    current_session: Optional[SessionData] = Depends(optional_jwt_bearer)
) -> AuthResponse:
    """
    Refresh JWT token with extended expiration.
    
    Can use either the current token from Authorization header
    or provide a token in the request body.
    """
    try:
        # Determine which token to refresh
        if current_session:
            # Use current session token
            current_token = None  # We'll need to get this from the request
            # For now, create a new session (simplified approach)
            new_token, session_data = create_session(
                session_id=current_session.session_id,
                user_id=current_session.user_id,
                permissions=current_session.permissions
            )
        elif request.refresh_token:
            # Refresh provided token
            new_token, session_data = refresh_session(request.refresh_token)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No token provided for refresh"
            )
        
        expires_in = int(session_data.time_until_expiry().total_seconds())
        
        logger.info(f"Refreshed token for session {session_data.session_id}")
        
        return AuthResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=expires_in,
            session_id=session_data.session_id,
            permissions=session_data.permissions
        )
        
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired and cannot be refreshed"
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(session: SessionData = Depends(jwt_bearer)) -> Dict[str, str]:
    """
    Revoke current session (logout).
    """
    try:
        success = revoke_session(session.session_id)
        
        if success:
            logger.info(f"Session {session.session_id} logged out")
            return {"message": "Successfully logged out"}
        else:
            return {"message": "Session not found"}
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/status", response_model=StatusResponse)
async def get_auth_status(
    request: Request,
    session: Optional[SessionData] = Depends(optional_jwt_bearer)
) -> StatusResponse:
    """
    Get current authentication status.
    
    Returns authentication information if valid session exists.
    """
    if session:
        return StatusResponse(
            authenticated=True,
            session_id=session.session_id,
            user_id=session.user_id,
            permissions=session.permissions,
            expires_at=session.expires_at
        )
    else:
        return StatusResponse(
            authenticated=False,
            session_id=None,
            user_id=None,
            permissions=[],
            expires_at=None
        )


@router.get("/session", response_model=SessionInfoResponse)
async def get_session_info(session: SessionData = Depends(jwt_bearer)) -> SessionInfoResponse:
    """
    Get detailed session information.
    
    Requires valid JWT token.
    """
    return SessionInfoResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        api_key=SecurityUtils.mask_sensitive_value(session.api_key) if session.api_key else None,
        created_at=session.created_at,
        expires_at=session.expires_at,
        permissions=session.permissions,
        time_remaining=str(session.time_until_expiry())
    )


@router.get("/sessions")
async def list_sessions(session: SessionData = Depends(jwt_bearer)) -> Dict[str, Any]:
    """
    List active sessions (admin endpoint).
    
    In production, this would require admin permissions.
    """
    try:
        # Check for admin permissions (simplified)
        if "admin" not in session.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )
        
        session_manager = get_session_manager()
        sessions = session_manager.list_active_sessions()
        
        return {
            "total_sessions": len(sessions),
            "sessions": sessions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list sessions"
        )


@router.post("/cleanup")
async def cleanup_sessions(session: SessionData = Depends(jwt_bearer)) -> Dict[str, Any]:
    """
    Cleanup expired sessions (admin endpoint).
    """
    try:
        # Check for admin permissions (simplified)
        if "admin" not in session.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )
        
        session_manager = get_session_manager()
        cleaned_count = session_manager.cleanup_expired_sessions()
        
        logger.info(f"Cleaned up {cleaned_count} expired sessions")
        
        return {
            "message": f"Cleaned up {cleaned_count} expired sessions",
            "cleaned_sessions": cleaned_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session cleanup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session cleanup failed"
        )


# Utility endpoints for development/testing

@router.get("/test-token")
async def create_test_token(
    permissions: str = "read,write"
) -> AuthResponse:
    """
    Create test token for development.
    
    This endpoint should be disabled in production.
    """
    try:
        # Parse permissions
        perm_list = [p.strip() for p in permissions.split(",") if p.strip()]
        
        # Generate test session
        session_id = f"test_{secrets.token_urlsafe(8)}"
        token, session_data = create_session(
            session_id=session_id,
            user_id="test-user",
            permissions=perm_list
        )
        
        expires_in = int(session_data.time_until_expiry().total_seconds())
        
        return AuthResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
            session_id=session_id,
            permissions=session_data.permissions
        )
        
    except Exception as e:
        logger.error(f"Test token creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Test token creation failed"
        )


@router.get("/verify-signature")
async def verify_signature_endpoint(request: Request) -> Dict[str, Any]:
    """
    Test endpoint for HMAC signature verification.
    
    Shows the expected signature format for debugging.
    """
    try:
        # Get headers
        api_key = request.headers.get("X-API-Key", "missing")
        signature = request.headers.get("X-Signature", "missing")
        timestamp = request.headers.get("X-Timestamp", "missing")
        
        # Get body
        body = await request.body()
        body_str = body.decode('utf-8') if body else ""
        
        return {
            "received_headers": {
                "X-API-Key": SecurityUtils.mask_sensitive_value(api_key),
                "X-Signature": signature[:16] + "..." if len(signature) > 16 else signature,
                "X-Timestamp": timestamp
            },
            "body_length": len(body_str),
            "signature_valid": "Use POST /auth/login to test full authentication"
        }
        
    except Exception as e:
        logger.error(f"Signature verification test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signature verification test failed"
        )


@router.post("/test-simple", response_model=Dict[str, Any])
async def test_simple_endpoint(request: Request) -> Dict[str, Any]:
    """
    Simple test endpoint that doesn't use request body parsing.
    """
    try:
        logger.info("Test endpoint called")
        
        return {
            "status": "success",
            "message": "Simple test endpoint working",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Test endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Test endpoint failed"
        )