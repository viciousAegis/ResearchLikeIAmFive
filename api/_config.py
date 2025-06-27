"""
Shared configuration for Vercel serverless functions.
Adapted from the original backend config.py
"""

import os
import logging
from google import genai

# Configure logging for serverless environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Application configuration class for serverless functions."""
    
    # Environment validation
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY environment variable is required")
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    # File size limits (adjusted for serverless)
    MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB limit for serverless
    MAX_TEXT_LENGTH = 100000  # Maximum text length for API processing
    MAX_PAGES = 50  # Reduced for serverless execution time limits
    TEXT_LIMIT = 500000  # 500KB text limit
    
    # API limits
    MAX_FIGURES = 5
    MIN_TEXT_LENGTH = 500  # Minimum text for valid content
    
    # Serverless specific settings
    MAX_EXECUTION_TIME = 25  # Vercel function timeout is 30s for hobby plan


def get_gemini_client():
    """Initialize and return Gemini API client for serverless function."""
    try:
        # Set the API key as environment variable for the client
        if Config.GOOGLE_API_KEY:
            os.environ["GOOGLE_AI_STUDIO_API_KEY"] = Config.GOOGLE_API_KEY
        client = genai.Client()
        logger.info("Gemini API client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Error configuring Gemini API: {e}")
        raise RuntimeError(f"Failed to initialize Gemini API: {e}")


# Cache client initialization for serverless reuse
_gemini_client = None

def get_cached_gemini_client():
    """Get cached Gemini client to reduce cold start times."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = get_gemini_client()
    return _gemini_client
