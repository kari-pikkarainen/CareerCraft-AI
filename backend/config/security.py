"""
Security Utilities

Provides cryptographic utilities and security helpers for the application.
"""

import hmac
import hashlib
import secrets
import base64
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SecurityUtils:
    """
    Security utilities for cryptographic operations.
    
    Provides:
    - HMAC signature generation and verification
    - Secure token generation
    - Timestamp validation
    - Password hashing utilities
    """
    
    @staticmethod
    def generate_hmac_signature(
        secret: str,
        message: str,
        algorithm: str = "sha256"
    ) -> str:
        """
        Generate HMAC signature for message authentication.
        
        Args:
            secret: Secret key for HMAC
            message: Message to sign
            algorithm: Hash algorithm (default: sha256)
            
        Returns:
            Base64-encoded HMAC signature
        """
        try:
            hash_func = getattr(hashlib, algorithm)
            signature = hmac.new(
                secret.encode(),
                message.encode(),
                hash_func
            ).digest()
            return base64.b64encode(signature).decode()
        except Exception as e:
            logger.error(f"Failed to generate HMAC signature: {e}")
            raise
    
    @staticmethod
    def verify_hmac_signature(
        secret: str,
        message: str,
        signature: str,
        algorithm: str = "sha256"
    ) -> bool:
        """
        Verify HMAC signature for message authentication.
        
        Args:
            secret: Secret key for HMAC
            message: Original message
            signature: Base64-encoded signature to verify
            algorithm: Hash algorithm (default: sha256)
            
        Returns:
            True if signature is valid
        """
        try:
            expected_signature = SecurityUtils.generate_hmac_signature(
                secret, message, algorithm
            )
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Failed to verify HMAC signature: {e}")
            return False
    
    @staticmethod
    def generate_api_signature(
        api_secret: str,
        api_key: str,
        timestamp: str,
        body: str = ""
    ) -> str:
        """
        Generate API request signature using standardized format.
        
        Args:
            api_secret: API secret key
            api_key: API key identifier
            timestamp: ISO format timestamp
            body: Request body content
            
        Returns:
            Base64-encoded signature
        """
        # Create standardized message format
        message_parts = [api_key, timestamp, body]
        message = "\n".join(message_parts)
        
        return SecurityUtils.generate_hmac_signature(api_secret, message)
    
    @staticmethod
    def verify_api_signature(
        api_secret: str,
        api_key: str,
        timestamp: str,
        signature: str,
        body: str = "",
        max_age_seconds: int = 300
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify API request signature with timestamp validation.
        
        Args:
            api_secret: API secret key
            api_key: API key identifier
            timestamp: ISO format timestamp from request
            signature: Signature to verify
            body: Request body content
            max_age_seconds: Maximum age of request in seconds
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Validate timestamp format and age
            is_valid_time, time_error = SecurityUtils.validate_timestamp(
                timestamp, max_age_seconds
            )
            if not is_valid_time:
                return False, time_error
            
            # Generate expected signature
            expected_signature = SecurityUtils.generate_api_signature(
                api_secret, api_key, timestamp, body
            )
            
            # Verify signature
            if not hmac.compare_digest(signature, expected_signature):
                return False, "Invalid signature"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False, f"Signature verification error: {str(e)}"
    
    @staticmethod
    def validate_timestamp(
        timestamp_str: str,
        max_age_seconds: int = 300
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate timestamp format and age to prevent replay attacks.
        
        Args:
            timestamp_str: ISO format timestamp string
            max_age_seconds: Maximum allowed age in seconds
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse timestamp
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Ensure timezone awareness
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            # Check age
            now = datetime.now(timezone.utc)
            age = (now - timestamp).total_seconds()
            
            if age > max_age_seconds:
                return False, f"Timestamp too old: {age} seconds (max: {max_age_seconds})"
            
            if age < -60:  # Allow 1 minute clock skew
                return False, f"Timestamp in the future: {age} seconds"
            
            return True, None
            
        except ValueError as e:
            return False, f"Invalid timestamp format: {e}"
        except Exception as e:
            logger.error(f"Timestamp validation error: {e}")
            return False, f"Timestamp validation error: {str(e)}"
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate cryptographically secure random token.
        
        Args:
            length: Token length in bytes
            
        Returns:
            URL-safe base64 encoded token
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_api_credentials() -> Dict[str, str]:
        """
        Generate new API key and secret pair.
        
        Returns:
            Dictionary with 'api_key' and 'api_secret'
        """
        return {
            'api_key': SecurityUtils.generate_secure_token(16),
            'api_secret': SecurityUtils.generate_secure_token(32)
        }
    
    @staticmethod
    def create_request_headers(
        api_key: str,
        api_secret: str,
        body: str = ""
    ) -> Dict[str, str]:
        """
        Create authenticated request headers for API calls.
        
        Args:
            api_key: API key identifier
            api_secret: API secret for signing
            body: Request body content
            
        Returns:
            Dictionary of authentication headers
        """
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        signature = SecurityUtils.generate_api_signature(
            api_secret, api_key, timestamp, body
        )
        
        return {
            'X-API-Key': api_key,
            'X-Signature': signature,
            'X-Timestamp': timestamp,
            'Content-Type': 'application/json'
        }
    
    @staticmethod
    def mask_sensitive_value(value: str, visible_chars: int = 4) -> str:
        """
        Mask sensitive value for logging/display.
        
        Args:
            value: Sensitive value to mask
            visible_chars: Number of characters to show at start
            
        Returns:
            Masked value (e.g., "abc123..." for API keys)
        """
        if not value or len(value) <= visible_chars:
            return "***"
        
        return value[:visible_chars] + "..." + "*" * max(0, len(value) - visible_chars - 3)


class RateLimiter:
    """
    Simple in-memory rate limiter for API requests.
    
    Note: In production, use Redis or database-backed rate limiting
    for multi-instance deployments.
    """
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = {}
    
    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            identifier: Unique identifier (e.g., API key, IP address)
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Initialize or clean old requests for this identifier
        if identifier not in self._requests:
            self._requests[identifier] = []
        
        # Remove requests outside the window
        self._requests[identifier] = [
            req_time for req_time in self._requests[identifier]
            if req_time > window_start
        ]
        
        current_requests = len(self._requests[identifier])
        
        # Check if under limit
        if current_requests < self.max_requests:
            self._requests[identifier].append(now)
            return True, {
                'allowed': True,
                'current_requests': current_requests + 1,
                'max_requests': self.max_requests,
                'window_seconds': self.window_seconds,
                'reset_time': (now + timedelta(seconds=self.window_seconds)).isoformat()
            }
        else:
            # Calculate when the limit will reset
            oldest_request = min(self._requests[identifier])
            reset_time = oldest_request + timedelta(seconds=self.window_seconds)
            
            return False, {
                'allowed': False,
                'current_requests': current_requests,
                'max_requests': self.max_requests,
                'window_seconds': self.window_seconds,
                'reset_time': reset_time.isoformat(),
                'retry_after': (reset_time - now).total_seconds()
            }
    
    def cleanup_old_entries(self) -> None:
        """Remove entries older than the rate limit window"""
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=self.window_seconds * 2)
        
        for identifier in list(self._requests.keys()):
            self._requests[identifier] = [
                req_time for req_time in self._requests[identifier]
                if req_time > cutoff
            ]
            
            # Remove empty entries
            if not self._requests[identifier]:
                del self._requests[identifier]