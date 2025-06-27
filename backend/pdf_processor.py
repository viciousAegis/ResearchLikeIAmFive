"""
PDF processing utilities for ResearchLikeIAmFive.
Handles PDF text extraction and figure extraction functionality.
"""

import os
import base64
import fitz  # PyMuPDF for PDF parsing
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

from config import Config

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file with size and content validation.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content
        
    Raises:
        HTTPException: If PDF is too large or processing fails
    """
    try:
        # Check file size
        file_size = os.path.getsize(pdf_path)
        if file_size > Config.MAX_PDF_SIZE:
            os.remove(pdf_path)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="PDF file too large"
            )
        
        paper_text = ""
        
        # Use PyMuPDF to extract text from the PDF
        doc = fitz.open(pdf_path)
        page_count = 0
        
        for page_num in range(min(doc.page_count, Config.MAX_PAGES)):
            page = doc.load_page(page_num)
            page_text = page.get_text() # type: ignore
            paper_text += page_text
            page_count += 1
            
            # Limit total text length
            if len(paper_text) > Config.TEXT_LIMIT:
                break
                
        doc.close()
        
        # Basic check for valid content
        if len(paper_text) < Config.MIN_TEXT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Insufficient text extracted from PDF"
            )
            
        logger.info(f"Successfully extracted {len(paper_text)} characters from {page_count} pages")
        return paper_text
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process PDF"
        )


def extract_figures_from_pdf(pdf_path: str, max_figures: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Extract figures from PDF and return them as base64 encoded images.
    
    Args:
        pdf_path: Path to the PDF file
        max_figures: Maximum number of figures to extract (default from Config)
        
    Returns:
        List of dictionaries containing figure data
    """
    if max_figures is None:
        max_figures = Config.MAX_FIGURES
        
    figures = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                if len(figures) >= max_figures:
                    break
                    
                # Get the image
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Skip very small images (likely decorative elements)
                if len(image_bytes) < 10000:  # 10KB threshold
                    continue
                
                # Convert to base64
                image_base64 = base64.b64encode(image_bytes).decode()
                image_ext = base_image["ext"]
                
                figures.append({
                    "data": f"data:image/{image_ext};base64,{image_base64}",
                    "page": page_num + 1,
                    "index": len(figures)
                })
            
            if len(figures) >= max_figures:
                break
        
        doc.close()
        logger.info(f"Extracted {len(figures)} figures from PDF")
        return figures
        
    except Exception as e:
        logger.error(f"Error extracting figures from PDF: {e}")
        # Return empty list if figure extraction fails - don't fail the whole request
        return []


def cleanup_pdf_file(pdf_path: str) -> None:
    """
    Safely remove a PDF file.
    
    Args:
        pdf_path: Path to the PDF file to remove
    """
    try:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.debug(f"Cleaned up PDF file: {pdf_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up PDF file {pdf_path}: {e}")
