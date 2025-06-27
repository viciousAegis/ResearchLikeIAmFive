"""
ResearchLikeIAmFive API - Main application entry point.
A modular, secure API for summarizing arXiv papers for a lay audience.
"""

import logging
from fastapi import FastAPI

from security import SecurityConfig
from middleware import setup_rate_limiter, configure_middleware
from routes import create_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- FastAPI App Setup ---
app = FastAPI(
    title="ResearchLikeIAmFive API",
    description="Secure API for summarizing arXiv papers for a lay audience.",
    version="1.0.0",
    docs_url="/docs" if not SecurityConfig.is_production() else None,  # Disable docs in production
    redoc_url="/redoc" if not SecurityConfig.is_production() else None,
)

# Initialize rate limiter
limiter = setup_rate_limiter()

# Configure all middleware
configure_middleware(app, limiter)

# Create and include API routes
router = create_routes(limiter)
app.include_router(router)

logger.info("ResearchLikeIAmFive API initialized successfully")
