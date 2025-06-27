"""
API route handlers for ResearchLikeIAmFive.
Contains all endpoint logic and request processing.
"""

import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from slowapi import Limiter

from security import SecurityConfig, SecureArxivRequest, verify_api_key, log_security_event
from arxiv_service import extract_arxiv_id_from_url, fetch_paper_from_arxiv, download_paper_pdf
from pdf_processor import extract_text_from_pdf, extract_figures_from_pdf, cleanup_pdf_file
from ai_service import generate_paper_summary

logger = logging.getLogger(__name__)


def create_routes(limiter: Limiter) -> APIRouter:
    """Create and configure API routes."""
    router = APIRouter()

    @router.post("/summarize")
    @limiter.limit(f"{SecurityConfig.RATE_LIMIT_REQUESTS}/minute")
    async def summarize_paper(
        request: Request,
        data: SecureArxivRequest,
        api_key_valid: bool = Depends(verify_api_key)
    ):
        """
        Securely process an arXiv URL and return a summary.
        
        Security features:
        - Rate limiting
        - Input validation and sanitization
        - API key validation (if enabled)
        - Request size limiting
        - Comprehensive error handling
        """
        client_ip = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
        logger.info(f"Processing request from {client_ip} for URL: {data.url}")
        
        pdf_path = None
        
        try:
            # 1. Extract arXiv ID from URL
            arxiv_id = extract_arxiv_id_from_url(data.url)

            # 2. Fetch Paper from arXiv
            paper = fetch_paper_from_arxiv(arxiv_id)
            
            # 3. Download and process PDF
            pdf_path = download_paper_pdf(paper)
            
            # 4. Extract text from PDF
            paper_text = extract_text_from_pdf(pdf_path)
            
            # 5. Extract figures from PDF (optional - disabled for security in original)
            extracted_figures = []  # Can be enabled: extract_figures_from_pdf(pdf_path)
            
            # 6. Generate AI summary
            ai_response = generate_paper_summary(paper_text, data.explanation_style)

            logger.info(f"Successfully processed request for {arxiv_id} from {client_ip}")
            
            return {
                "summary": ai_response["summary"], 
                "title": paper.title, 
                "figures": extracted_figures
            }

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error processing {data.url}: {e}")
            log_security_event("UNEXPECTED_ERROR", str(e), request)
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
        finally:
            # Always clean up the downloaded file
            if pdf_path:
                cleanup_pdf_file(pdf_path)

    @router.get("/")
    @limiter.limit("30/minute")  # More permissive for health checks
    async def health_check(request: Request):
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "ResearchLikeIAmFive API",
            "version": "1.0.0",
            "environment": SecurityConfig.ENVIRONMENT
        }

    # Add API information endpoint (only in development)
    if not SecurityConfig.is_production():
        @router.get("/info")
        async def api_info():
            """API information (development only)."""
            return {
                "title": "ResearchLikeIAmFive API",
                "description": "Secure API for summarizing arXiv papers",
                "version": "1.0.0",
                "docs_url": "/docs",
                "redoc_url": "/redoc"
            }

    return router
