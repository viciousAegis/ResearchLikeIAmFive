"""
AI service integration for ResearchLikeIAmFive.
Handles communication with the Gemini AI API.
"""

import logging
from google.genai import types
from fastapi import HTTPException, status
from typing import Dict, Any

from config import gemini_client, Config
from ai_prompts import get_system_prompt, PAPER_SUMMARY_SCHEMA
from utils import safe_json_loads, clean_json_response, validate_required_fields, truncate_text

logger = logging.getLogger(__name__)


def generate_paper_summary(paper_text: str, explanation_style: str) -> Dict[str, Any]:
    """
    Generate a paper summary using the Gemini AI API.
    
    Args:
        paper_text: The extracted text from the research paper
        explanation_style: The style of explanation to use
        
    Returns:
        Dictionary containing the parsed summary
        
    Raises:
        HTTPException: If AI service fails or returns invalid response
    """
    try:
        # Truncate paper text if too long to prevent API abuse
        if len(paper_text) > Config.MAX_TEXT_LENGTH:
            paper_text = truncate_text(paper_text, Config.MAX_TEXT_LENGTH)
            logger.info(f"Truncated paper text to {Config.MAX_TEXT_LENGTH} characters")
        
        # Generate system prompt
        system_prompt = get_system_prompt(explanation_style)
        
        # Call Gemini API
        response = gemini_client.models.generate_content(
            model="models/gemini-2.5-flash-lite-preview-06-17",
            contents=paper_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=PAPER_SUMMARY_SCHEMA,
            )
        )
        
        if not response.text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Empty response from AI service"
            )
        
        # Clean and validate JSON response
        cleaned_json_string = clean_json_response(response.text)
        
        # Parse and validate JSON
        parsed_summary = safe_json_loads(cleaned_json_string)
        if parsed_summary is None:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response format from AI service"
            )
        
        # Validate required fields
        try:
            required_fields = ["gist", "analogy", "experimental_details", "key_findings", "why_it_matters", "key_terms"]
            validate_required_fields(parsed_summary, required_fields)
                
            logger.info(f"Successfully generated summary in {explanation_style} style")
            return {"summary": cleaned_json_string, "parsed": parsed_summary}
            
        except ValueError as e:
            logger.error(f"Missing required fields in AI response: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response format from AI service"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable"
        )
