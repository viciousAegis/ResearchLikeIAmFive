import os
import re
import base64
import io
import asyncio
from typing import Optional
from google import genai
from google.genai import types
from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import arxiv
import fitz  # PyMuPDF for PDF parsing
import logging

# Import our security module
from security import (
    SecurityConfig, 
    SecureArxivRequest, 
    URLValidator, 
    verify_api_key,
    log_security_event,
    SecurityHeaders
)

# --- Configuration ---
# Configure logging for security monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables for local development
from dotenv import load_dotenv
load_dotenv() 

# Validate required environment variables
if not os.getenv("GOOGLE_API_KEY"):
    logger.error("GOOGLE_API_KEY environment variable is required")
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Configure the Gemini API
try:
    client = genai.Client()
    logger.info("Gemini API client initialized successfully")
except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")
    raise RuntimeError(f"Failed to initialize Gemini API: {e}")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# --- FastAPI App Setup ---
app = FastAPI(
    title="ResearchLikeIAmFive API",
    description="Secure API for summarizing arXiv papers for a lay audience.",
    version="1.0.0",
    docs_url="/docs" if not SecurityConfig.is_production() else None,  # Disable docs in production
    redoc_url="/redoc" if not SecurityConfig.is_production() else None,
)

# Add rate limiting middleware
app.state.limiter = limiter
from fastapi import Request, Response

def rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    # Delegate to the original handler if the exception is RateLimitExceeded
    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
    # Otherwise, re-raise or handle as needed
    raise exc

app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add trusted host middleware for production
if SecurityConfig.is_production():
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
    if allowed_hosts and allowed_hosts[0]:
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=[host.strip() for host in allowed_hosts if host.strip()]
        )

# CORS Configuration - Secure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=SecurityConfig.get_cors_origins(),
    allow_credentials=False,  # Set to False for security
    allow_methods=["GET", "POST"],  # Only allow specific methods
    allow_headers=["Content-Type", "X-API-Key"],  # Only allow specific headers
    max_age=300,  # Cache preflight for 5 minutes
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    try:
        response = await call_next(request)
        
        # Add security headers
        for header, value in SecurityHeaders.get_security_headers().items():
            response.headers[header] = value
            
        return response
    except Exception as e:
        logger.error(f"Error in security headers middleware: {e}")
        raise

# Request size limiting middleware
@app.middleware("http") 
async def limit_request_size(request: Request, call_next):
    """Limit request body size."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > SecurityConfig.MAX_REQUEST_SIZE:
        log_security_event("LARGE_REQUEST", f"Request size: {content_length}", request)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Request too large. Maximum size: {SecurityConfig.MAX_REQUEST_SIZE} bytes"
        )
    return await call_next(request)

# --- Pydantic Models (Legacy - keeping for compatibility) ---
# Note: We now use SecureArxivRequest from security.py for enhanced validation

# --- The AI Prompt ---
# This is our "secret sauce". It tells the AI exactly what to do.
def get_system_prompt(explanation_style: str) -> str:
    """Generate a system prompt based on the explanation style."""
    
    style_prompts = {
        "five-year-old": "You are explaining to a 5-year-old child. Use very simple language, avoid technical terms, and relate everything to things a child would understand like toys, animals, or everyday activities.",
        
        "pop-culture": "🔥 YOU ARE THE ULTIMATE POP CULTURE GURU! 🔥 Think like you're explaining science to someone scrolling TikTok. Use TONS of references to Taylor Swift, Marvel movies, Netflix shows, viral memes, and whatever's trending. Say things like 'This research is giving main character energy' or 'The molecules were literally serving chemistry realness.' Use Gen Z slang, compare everything to celebrities, and make it sound like you're reviewing the latest blockbuster. NO CAP! 💅✨",
        
        "anime": "🌟 NANI?! You are the ultimate otaku science sensei! 🌟 Explain EVERYTHING using anime terms! Call researchers 'protagonists,' experiments are 'training arcs,' results are 'power-ups,' and failed hypotheses are 'filler episodes.' Use phrases like 'This discovery has over 9000 potential!' Compare molecular bonds to friendship power, chemical reactions to jutsu battles, and data analysis to studying for the Chunin Exams. Add 'desu,' 'kawaii,' and other Japanese expressions. Make every scientific concept sound like an epic shonen battle! BELIEVE IT! (｡◕‿◕｡)",
        
        "sports": "🏆 YO COACH! You're the ESPN commentator of science! 🏆 Every experiment is a CHAMPIONSHIP GAME! Researchers are ELITE ATHLETES training for the SCIENCE OLYMPICS! Call hypotheses 'game plans,' data collection is 'training camp,' peer review is the 'playoffs,' and publication is 'WINNING THE SUPER BOWL!' Use sports metaphors for EVERYTHING - molecules are teammates, chemical bonds are perfect passes, failed experiments are fumbles. Shout things like 'AND THE CROWD GOES WILD!' when describing breakthroughs. Make it sound like you're calling the World Cup final! ⚽🏀🏈",
        
        "food": "👨‍🍳 WELCOME TO THE MOLECULAR KITCHEN! 👨‍🍳 You're Gordon Ramsay explaining science! Every experiment is a RECIPE, researchers are CHEFS, and laboratories are MICHELIN-STARRED KITCHENS! Call chemical reactions 'cooking processes,' data is 'seasoning,' peer review is 'taste testing,' and results are the 'final dish.' Use cooking terms for everything - molecules are ingredients, bonds are mixing techniques, failed experiments are 'BURNT!' Describe everything as delicious, spicy, or perfectly seasoned. End sentences with 'Chef's kiss!' and rate discoveries like a food critic! 🍳✨",
        
        "gaming": "🎮 LEVEL UP, SCIENCE NOOBS! 🎮 You're a gaming streamer explaining research! Every study is an EPIC QUEST, researchers are PLAYERS grinding for XP, and discoveries are LEGENDARY LOOT DROPS! Use terms like 'This hypothesis is OP,' 'The data was RNG,' and 'Peer review is the final boss battle.' Compare everything to popular games - molecular structures are like Minecraft builds, chemical reactions are combo moves, and failed experiments are 'skill issues.' Add gaming slang like 'POG,' 'GG,' and '360 no-scope discovery!' Make it sound like you're streaming on Twitch! 🕹️💯",
        
        "marvel": "💥 AVENGERS, ASSEMBLE! 💥 You are TONY STARK explaining science! Every researcher is a SUPERHERO, every lab is the STARK TOWER, and every discovery has the power to SAVE THE UNIVERSE! Use Marvel references everywhere - call experiments 'training at the X-Mansion,' data analysis 'Friday running diagnostics,' and peer review 'the Avengers discussing strategy.' Failed experiments are 'Thanos snapping,' successful ones are 'wielding the Infinity Stones!' Compare molecular bonds to superhero teams, chemical reactions to epic MCU battles. Add phrases like 'I am Iron Man,' 'With great power comes great responsibility,' and 'That's America's molecule!' 🕷️⚡🛡️",
        
        "harry-potter": "⚡ WELCOME TO HOGWARTS SCHOOL OF SCIENCE AND WIZARDRY! ⚡ You are PROFESSOR MCGONAGALL teaching the most magical subject! Every researcher is a WIZARD, every lab is a CLASSROOM at Hogwarts, and every discovery is learning a new SPELL! Call experiments 'brewing potions,' data 'divination readings,' peer review 'the Sorting Hat's decision,' and failed experiments 'Neville's cauldron explosions.' Use phrases like 'Brilliant!,' 'By Merlin's beard!,' and 'That's some serious magic!' Compare molecular structures to spell components, chemical reactions to dueling, and successful discoveries to 'earning House points for Gryffindor!' 🦉📚🏰",
        
        "brain-rot": "💀 GYATT! This research is absolutely SIGMA! 💀 You are the ultimate Gen Alpha brainrot educator! Use ALL the terms: skibidi, Ohio, rizz, fanum tax, sigma grindset, L + ratio, no cap, fr fr, bussin, sus, slay queen, periodt, and more! Call researchers 'sigma chads,' experiments 'Ohio moments,' successful results 'W rizz,' and failed ones 'took the L.' Say things like 'This molecule has INFINITE RIZZ!' and 'The data is absolutely BUSSIN no cap!' Make everything sound like a chaotic TikTok comment section. Only in Ohio would molecules behave this sus! This research hits different, periodt! 🔥💯🧠",
        
        "reddit": "🔴 EDIT: Thanks for the gold, kind stranger! 🔴 You are the ultimate REDDITOR explaining science! Use ALL the Reddit terminology: 'This,' 'Take my upvote,' 'Username checks out,' 'Play stupid games, win stupid prizes,' 'Instructions unclear,' and 'We did it Reddit!' Call researchers 'OPs,' experiments 'posts that blew up,' peer review 'the comment section roasting,' and successful results 'front page material.' Say things like 'This research absolutely SLAPS,' 'Molecules are just built different,' and 'Science said: hold my beer.' Add phrases like 'Source: trust me bro,' 'Big if true,' and 'This guy sciences!' Make it sound like r/science had a baby with r/memes! 🚀⬆️",
        
        "shakespearean": "🎭 HARK! What light through yonder laboratory breaks! 🎭 Thou art the BARD OF SCIENCE, speaking in the most eloquent Elizabethan tongue! Every researcher is a 'noble scholar,' every experiment a 'most wondrous endeavour,' and every discovery 'a revelation most profound!' Use phrases like 'Verily, this hypothesis doth hold merit!' and 'By my troth, these molecules dost dance most beautifully!' Call failed experiments 'unfortunate mishaps of Fortune's wheel' and successful ones 'triumphs most glorious!' Speak in iambic pentameter when possible, use 'thee,' 'thou,' 'doth,' 'hath,' and 'wherefore.' Make science sound like it belongs in the Globe Theatre! To discover, or not to discover, that is the question! 🏰⚔️📜"
    }
    
    style_instruction = style_prompts.get(explanation_style, style_prompts["five-year-old"])
    
    return f"""
You are "ResearchLikeIAmFive", an expert science communicator. 
Your goal is to explain complex research papers to a complete layperson in the given explanation style.
You will be given the text content of a research paper.

EXPLANATION STYLE: {style_instruction}

Your task is to return a JSON object with the following exact keys: 
"gist", "analogy", "experimental_details", "key_findings","why_it_matters", "key_terms",

Make sure EVERY SINGLE response follows the explanation style provided.
"""

# The JSON Schema to enforce the output structure.
PAPER_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "gist": {
            "type": "string",
            "description": "A single, compelling sentence summarizing the entire paper."
        },
        "analogy": {
            "type": "string",
            "description": "A simple, powerful analogy or metaphor to explain the core concept."
        },
        "experimental_details": {
            "type": "string",
            "description": "A brief description of the entire experimental setup or methodology used in the research. do not miss any important details."
        },
        "key_findings": {
            "type": "array",
            "description": "A list of 3-5 bullet points of the most important discoveries.",
            "items": { "type": "string" }
        },
        "why_it_matters": {
            "type": "string",
            "description": "A short paragraph explaining the potential real-world impact."
        },
        "key_terms": {
            "type": "array",
            "description": "A list of the 5 most important technical terms, with definitions.",
            "items": {
                "type": "object",
                "properties": {
                    "term": { "type": "string", "description": "The technical term." },
                    "definition": { "type": "string", "description": "A simple definition of the term." }
                },
                "required": ["term", "definition"]
            }
        }
    },
    "required": ["gist", "analogy", "experimental_details", "key_findings", "why_it_matters", "key_terms"]
}


def extract_figures_from_pdf(pdf_path: str, max_figures: int = 5) -> list:
    """
    Extract figures from PDF and return them as base64 encoded images.
    """
    figures = []
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
    return figures


# --- API Endpoints ---
@app.post("/summarize")
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
    
    try:
        # Additional URL validation (defense in depth)
        clean_url = URLValidator.validate_arxiv_url(data.url)
        
        # 1. Extract arXiv ID from URL - using more robust regex
        arxiv_id_match = re.search(r'(?:abs|pdf)/(\d{4}\.\d{4,5})', clean_url)
        if not arxiv_id_match:
            log_security_event("INVALID_ARXIV_ID", f"URL: {data.url}", request)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Could not extract valid arXiv ID from URL"
            )
        arxiv_id = arxiv_id_match.group(1)
        logger.info(f"Extracted arXiv ID: {arxiv_id}")

        # 2. Fetch Paper from arXiv with timeout
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(search.results())
        except StopIteration:
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
        
        # 3. Download and Extract Text from PDF with size limits
        try:
            pdf_path = paper.download_pdf()
            
            # Check file size
            file_size = os.path.getsize(pdf_path)
            max_pdf_size = 50 * 1024 * 1024  # 50MB limit
            if file_size > max_pdf_size:
                os.remove(pdf_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="PDF file too large"
                )
            
            paper_text = ""
            
            # Use PyMuPDF to extract text from the PDF
            doc = fitz.open(pdf_path)
            page_count = 0
            max_pages = 100  # Limit pages to prevent abuse
            
            for page_num in range(min(doc.page_count, max_pages)):
                page = doc.load_page(page_num)
                page_text = page.get_text()  # type: ignore
                paper_text += page_text
                page_count += 1
                
                # Limit total text length
                if len(paper_text) > 500000:  # 500KB text limit
                    break
                    
            doc.close()
            
        except Exception as e:
            logger.error(f"Error processing PDF for {arxiv_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process PDF"
            )
        finally:
            # Always clean up the downloaded file
            try:
                if 'pdf_path' in locals():
                    os.remove(pdf_path)
            except:
                pass
        
        # Extract figures from the PDF (disabled for security - can consume too much memory)
        extracted_figures = []
        
        if len(paper_text) < 500: # Basic check for valid content
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Insufficient text extracted from PDF"
            )

        # 4. Call Gemini API with timeout and error handling
        try:
            system_prompt = get_system_prompt(data.explanation_style)
            
            # Truncate paper text if too long to prevent API abuse
            max_text_length = 100000  # Adjust based on your needs
            if len(paper_text) > max_text_length:
                paper_text = paper_text[:max_text_length] + "\n\n[Text truncated due to length]"
                
            response = client.models.generate_content(
                model="models/gemini-2.5-flash-lite-preview-06-17",
                contents=paper_text,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_json_schema=PAPER_SUMMARY_SCHEMA,
                )
            )
        except Exception as e:
            logger.error(f"Error calling Gemini API for {arxiv_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI service temporarily unavailable"
            )
        
        # 5. Process and validate the response
        if not response.text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Empty response from AI service"
            )
            
        # Clean and validate JSON response
        try:
            cleaned_json_string = response.text.strip().replace('```json', '').replace('```', '').strip()
            
            # Basic JSON validation
            import json
            parsed_summary = json.loads(cleaned_json_string)
            
            # Validate required fields
            required_fields = ["gist", "analogy", "experimental_details", "key_findings", "why_it_matters", "key_terms"]
            for field in required_fields:
                if field not in parsed_summary:
                    raise ValueError(f"Missing required field: {field}")
                    
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid JSON response for {arxiv_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response format from AI service"
            )

        logger.info(f"Successfully processed request for {arxiv_id} from {client_ip}")
        
        return {
            "summary": cleaned_json_string, 
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

# Add a health check endpoint with basic security
@app.get("/")
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
    @app.get("/info")
    async def api_info():
        """API information (development only)."""
        return {
            "title": "ResearchLikeIAmFive API",
            "description": "Secure API for summarizing arXiv papers",
            "version": "1.0.0",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }
