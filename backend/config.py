"""
Configuration module for ResearchLikeIAmFive backend.
Handles environment variables, logging setup, and API client initialization.
"""

import os
import logging
from google import genai

# Load environment variables for local development
from dotenv import load_dotenv
load_dotenv()

# Configure logging for security monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Application configuration class."""
    
    # Environment validation
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY environment variable is required")
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    # File size limits
    MAX_PDF_SIZE = 50 * 1024 * 1024  # 50MB limit
    MAX_TEXT_LENGTH = 100000  # Maximum text length for API processing
    MAX_PAGES = 100  # Maximum pages to process
    TEXT_LIMIT = 500000  # 500KB text limit
    
    # API limits
    MAX_FIGURES = 5
    MIN_TEXT_LENGTH = 500  # Minimum text for valid content


def get_gemini_client():
    """Initialize and return Gemini API client."""
    try:
        client = genai.Client()
        logger.info("Gemini API client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Error configuring Gemini API: {e}")
        raise RuntimeError(f"Failed to initialize Gemini API: {e}")


# Initialize the Gemini client
gemini_client = get_gemini_client()
