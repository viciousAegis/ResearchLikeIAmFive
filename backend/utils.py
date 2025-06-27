"""
Utility functions for ResearchLikeIAmFive backend.
Common helper functions used across multiple modules.
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def safe_json_loads(json_string: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON string with error handling.
    
    Args:
        json_string: JSON string to parse
        
    Returns:
        Parsed dictionary or None if parsing fails
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return None


def clean_json_response(response_text: str) -> str:
    """
    Clean JSON response by removing markdown formatting.
    
    Args:
        response_text: Raw response text that may contain markdown
        
    Returns:
        Cleaned JSON string
    """
    return response_text.strip().replace('```json', '').replace('```', '').strip()


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> bool:
    """
    Validate that all required fields are present in a dictionary.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if all fields are present, raises ValueError otherwise
    """
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    return True


def truncate_text(text: str, max_length: int, suffix: str = "\n\n[Text truncated due to length]") -> str:
    """
    Truncate text to a maximum length with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        suffix: Suffix to add if text is truncated
        
    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix
