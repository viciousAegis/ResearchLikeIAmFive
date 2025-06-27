"""
Security configuration and utilities for the ResearchLikeIAmFive API.
"""
import os
import re
from typing import Set, Optional
from urllib.parse import urlparse
from fastapi import HTTPException, Request, status
from pydantic import BaseModel, validator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration settings."""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # CORS Settings
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Add production origins from environment
    PROD_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
    if PROD_ORIGINS and PROD_ORIGINS[0]:
        ALLOWED_ORIGINS.extend([origin.strip() for origin in PROD_ORIGINS if origin.strip()])
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # Request limits
    MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "1048576"))  # 1MB
    MAX_URL_LENGTH = int(os.getenv("MAX_URL_LENGTH", "2048"))
    
    # API Security
    API_KEY_REQUIRED = os.getenv("API_KEY_REQUIRED", "false").lower() == "true"
    VALID_API_KEYS: Set[str] = set()
    
    # Load API keys from environment
    api_keys = os.getenv("VALID_API_KEYS", "")
    if api_keys:
        VALID_API_KEYS = set(api_keys.split(","))

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def get_cors_origins(cls) -> list:
        """Get allowed CORS origins based on environment."""
        if cls.is_production():
            # In production, only allow specific origins
            return [origin for origin in cls.ALLOWED_ORIGINS if not origin.startswith("http://localhost")]
        return cls.ALLOWED_ORIGINS


class URLValidator:
    """Validates and sanitizes URLs."""
    
    ALLOWED_DOMAINS = {
        "arxiv.org",
        "www.arxiv.org",
        "export.arxiv.org"
    }
    
    ARXIV_URL_PATTERN = re.compile(
        r'^https?://(www\.)?arxiv\.org/(abs|pdf)/(\d{4}\.\d{4,5})(v\d+)?/?$'
    )
    
    @classmethod
    def validate_arxiv_url(cls, url: str) -> str:
        """
        Validate and sanitize arXiv URL.
        
        Args:
            url: The URL to validate
            
        Returns:
            Cleaned URL
            
        Raises:
            HTTPException: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL is required and must be a string"
            )
        
        # Basic length check
        if len(url) > SecurityConfig.MAX_URL_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"URL too long. Maximum length is {SecurityConfig.MAX_URL_LENGTH}"
            )
        
        # Clean the URL
        url = url.strip()
        
        # Validate URL format
        if not cls.ARXIV_URL_PATTERN.match(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid arXiv URL format. Please use format: https://arxiv.org/abs/XXXX.XXXXX"
            )
        
        # Parse and validate domain
        try:
            parsed = urlparse(url)
            if parsed.netloc.lower() not in cls.ALLOWED_DOMAINS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only arXiv URLs are allowed"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed URL"
            )
        
        return url


class SecureArxivRequest(BaseModel):
    """Secure request model with validation."""
    
    url: str
    explanation_style: str = "five-year-old"
    api_key: Optional[str] = None
    
    @validator('url')
    def validate_url(cls, v):
        """Validate arXiv URL."""
        return URLValidator.validate_arxiv_url(v)
    
    @validator('explanation_style')
    def validate_explanation_style(cls, v):
        """Validate explanation style."""
        allowed_styles = {
            "five-year-old", "pop-culture", "anime", "sports", "food",
            "gaming", "marvel", "harry-potter", "brain-rot", "reddit", "shakespearean"
        }
        
        if v not in allowed_styles:
            raise ValueError(f"Invalid explanation style. Must be one of: {', '.join(allowed_styles)}")
        
        return v


async def verify_api_key(request: Request) -> bool:
    """
    Verify API key if required.
    
    Args:
        request: FastAPI request object
        
    Returns:
        True if API key is valid or not required
        
    Raises:
        HTTPException: If API key is required but invalid
    """
    if not SecurityConfig.API_KEY_REQUIRED:
        return True
    
    # Check API key in header
    api_key = request.headers.get("X-API-Key")
    
    # Check API key in request body for POST requests
    if not api_key and hasattr(request, "json"):
        try:
            body = await request.json()
            api_key = body.get("api_key")
        except:
            pass
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
        
    if not request.client:
        logger.warning("Request client information is missing")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client information is missing"
        )
    
    if api_key not in SecurityConfig.VALID_API_KEYS:
        logger.warning(f"Invalid API key attempt from {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True


def log_security_event(event_type: str, details: str, request: Request):
    """Log security events."""
    if not request.client:
        logger.warning("Request client information is missing for security event logging")
        return
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    
    logger.warning(
        f"SECURITY_EVENT: {event_type} | IP: {client_ip} | UA: {user_agent} | Details: {details}"
    )


class SecurityHeaders:
    """Security headers for production deployment."""
    
    @staticmethod
    def get_security_headers():
        """Get recommended security headers."""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://arxiv.org https://export.arxiv.org; "
                "frame-ancestors 'none';"
            ),
        }
        
        if SecurityConfig.is_production():
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
        return headers
