"""
Rate limiting utilities for Vercel serverless functions.
Implements in-memory rate limiting for API endpoints.
"""

import time
import logging
from typing import Dict, Tuple, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# In-memory storage for rate limiting (resets on cold starts)
_rate_limit_store: Dict[str, Dict[str, Any]] = {}

class RateLimiter:
    """Simple in-memory rate limiter for serverless functions."""
    
    def __init__(self, requests_per_minute: int = 10, window_size_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
            window_size_seconds: Time window for rate limiting in seconds
        """
        self.requests_per_minute = requests_per_minute
        self.window_size_seconds = window_size_seconds
    
    def is_allowed(self, client_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request from the client is allowed.
        
        Args:
            client_id: Unique identifier for the client (IP address, user ID, etc.)
            
        Returns:
            Tuple of (is_allowed: bool, rate_limit_info: dict)
        """
        current_time = time.time()
        
        # Initialize client data if not exists
        if client_id not in _rate_limit_store:
            _rate_limit_store[client_id] = {
                'requests': [],
                'first_request_time': current_time
            }
        
        client_data = _rate_limit_store[client_id]
        
        # Clean old requests outside the window
        cutoff_time = current_time - self.window_size_seconds
        client_data['requests'] = [
            req_time for req_time in client_data['requests'] 
            if req_time > cutoff_time
        ]
        
        # Check if request is allowed
        current_request_count = len(client_data['requests'])
        is_allowed = current_request_count < self.requests_per_minute
        
        # Add current request if allowed
        if is_allowed:
            client_data['requests'].append(current_time)
        
        # Calculate reset time
        if client_data['requests']:
            oldest_request = min(client_data['requests'])
            reset_time = oldest_request + self.window_size_seconds
        else:
            reset_time = current_time + self.window_size_seconds
        
        rate_limit_info = {
            'limit': self.requests_per_minute,
            'remaining': max(0, self.requests_per_minute - current_request_count - (1 if is_allowed else 0)),
            'reset': reset_time,
            'retry_after': max(0, reset_time - current_time) if not is_allowed else 0
        }
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for client {client_id}. Requests in window: {current_request_count}")
        
        return is_allowed, rate_limit_info


# Global rate limiter instance
default_rate_limiter = RateLimiter(requests_per_minute=5, window_size_seconds=60)

def get_client_id(request) -> str:
    """
    Extract client identifier from request.
    
    Args:
        request: The request object
        
    Returns:
        Client identifier string
    """
    # Handle different request object types
    if hasattr(request, 'headers') and isinstance(request.headers, dict):
        headers = request.headers
    else:
        headers = getattr(request, 'headers', {})
    
    # Check common headers for real IP
    ip = None
    if headers:
        ip = (
            headers.get('x-forwarded-for', '').split(',')[0].strip() or
            headers.get('x-real-ip', '') or
            headers.get('cf-connecting-ip', '') or  # Cloudflare
            headers.get('x-client-ip', '') or
            None
        )
    
    # Fallback to remote_addr if available
    if not ip:
        ip = getattr(request, 'remote_addr', 'unknown')
    
    return ip or 'unknown'


def apply_rate_limit(request, rate_limiter: Optional[RateLimiter] = None) -> Tuple[bool, Dict[str, Any], Dict[str, str]]:
    """
    Apply rate limiting to a request.
    
    Args:
        request: The request object
        rate_limiter: Optional custom rate limiter, uses default if None
        
    Returns:
        Tuple of (is_allowed: bool, rate_limit_info: dict, headers: dict)
    """
    if rate_limiter is None:
        rate_limiter = default_rate_limiter
    
    client_id = get_client_id(request)
    is_allowed, rate_limit_info = rate_limiter.is_allowed(client_id)
    
    # Prepare rate limit headers
    headers = {
        'X-RateLimit-Limit': str(rate_limit_info['limit']),
        'X-RateLimit-Remaining': str(rate_limit_info['remaining']),
        'X-RateLimit-Reset': str(int(rate_limit_info['reset'])),
    }
    
    if not is_allowed:
        headers['Retry-After'] = str(int(rate_limit_info['retry_after']))
    
    return is_allowed, rate_limit_info, headers


def create_rate_limit_error_response(rate_limit_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a standardized rate limit error response.
    
    Args:
        rate_limit_info: Rate limit information
        
    Returns:
        Error response dictionary
    """
    return {
        "error": "Rate limit exceeded",
        "message": f"Too many requests. Limit: {rate_limit_info['limit']} requests per minute.",
        "retry_after": int(rate_limit_info['retry_after']),
        "reset_time": datetime.fromtimestamp(rate_limit_info['reset']).isoformat(),
        "status_code": 429
    }
