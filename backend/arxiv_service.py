"""
ArXiv service for fetching research papers.
Handles paper retrieval and URL validation.
"""

import re
import logging
import arxiv
from fastapi import HTTPException, status
from typing import Any

from security import URLValidator

logger = logging.getLogger(__name__)


def extract_arxiv_id_from_url(url: str) -> str:
    """
    Extract arXiv ID from a given URL.
    
    Args:
        url: ArXiv URL to extract ID from
        
    Returns:
        ArXiv paper ID
        
    Raises:
        HTTPException: If URL is invalid or ID cannot be extracted
    """
    try:
        # Validate and clean the URL
        clean_url = URLValidator.validate_arxiv_url(url)
        
        # Extract arXiv ID using robust regex
        arxiv_id_match = re.search(r'(?:abs|pdf)/(\d{4}\.\d{4,5})', clean_url)
        if not arxiv_id_match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Could not extract valid arXiv ID from URL"
            )
            
        arxiv_id = arxiv_id_match.group(1)
        logger.info(f"Extracted arXiv ID: {arxiv_id}")
        return arxiv_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting arXiv ID from URL {url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid arXiv URL format"
        )


def fetch_paper_from_arxiv(arxiv_id: str) -> Any:
    """
    Fetch a paper from arXiv by its ID.
    
    Args:
        arxiv_id: The arXiv paper ID
        
    Returns:
        ArXiv paper object
        
    Raises:
        HTTPException: If paper not found or fetch fails
    """
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        logger.info(f"Successfully fetched paper: {paper.title}")
        return paper
        
    except StopIteration:
        logger.warning(f"Paper with ID {arxiv_id} not found on arXiv")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID {arxiv_id} not found on arXiv"
        )
    except Exception as e:
        logger.error(f"Error fetching paper {arxiv_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch paper from arXiv"
        )


def download_paper_pdf(paper: Any) -> str:
    """
    Download PDF from an arXiv paper object.
    
    Args:
        paper: ArXiv paper object
        
    Returns:
        Path to the downloaded PDF file
        
    Raises:
        HTTPException: If download fails
    """
    try:
        pdf_path = paper.download_pdf()
        logger.info(f"Successfully downloaded PDF to: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to download PDF from arXiv"
        )
