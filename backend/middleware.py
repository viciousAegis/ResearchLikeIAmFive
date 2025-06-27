"""
FastAPI middleware configuration for ResearchLikeIAmFive.
Handles CORS, security headers, rate limiting, and request validation.
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from security import SecurityConfig, SecurityHeaders, log_security_event

logger = logging.getLogger(__name__)


def setup_rate_limiter() -> Limiter:
    """Initialize and configure rate limiter."""
    return Limiter(key_func=get_remote_address)


def configure_middleware(app: FastAPI, limiter: Limiter) -> None:
    """
    Configure all middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        limiter: Rate limiter instance
    """
    # Add rate limiting middleware
    app.state.limiter = limiter
    
    def rate_limit_exceeded_handler(request: Request, exc: Exception):
        # Delegate to the original handler if the exception is RateLimitExceeded
        if isinstance(exc, RateLimitExceeded):
            return _rate_limit_exceeded_handler(request, exc)
        # Otherwise, re-raise or handle as needed
        raise exc

    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # Add trusted host middleware for production
    if SecurityConfig.is_production():
        allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
        if allowed_hosts and allowed_hosts[0]:
            app.add_middleware(
                TrustedHostMiddleware, 
                allowed_hosts=[host.strip() for host in allowed_hosts if host.strip()]
            )

    # CORS Configuration - Secure for production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=SecurityConfig.get_cors_origins(),
        allow_credentials=False,  # Set to False for security
        allow_methods=["GET", "POST"],  # Only allow specific methods
        allow_headers=["Content-Type", "X-API-Key"],  # Only allow specific headers
        max_age=300,  # Cache preflight for 5 minutes
    )

    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """Add security headers to all responses."""
        try:
            response = await call_next(request)
            
            # Add security headers
            for header, value in SecurityHeaders.get_security_headers().items():
                response.headers[header] = value
                
            return response
        except Exception as e:
            logger.error(f"Error in security headers middleware: {e}")
            raise

    # Request size limiting middleware
    @app.middleware("http") 
    async def limit_request_size(request: Request, call_next):
        """Limit request body size."""
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > SecurityConfig.MAX_REQUEST_SIZE:
            log_security_event("LARGE_REQUEST", f"Request size: {content_length}", request)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request too large. Maximum size: {SecurityConfig.MAX_REQUEST_SIZE} bytes"
            )
        return await call_next(request)
