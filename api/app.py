"""
Flask API for ResearchLikeIAmFive - Main application
Handles paper summarization using Flask for Vercel deployment
"""

import os
import json
import logging
import tempfile
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import arxiv
import fitz  # PyMuPDF
from google.genai import types

from api._config import get_cached_gemini_client, Config
from api._utils import (
    validate_arxiv_url,
    extract_arxiv_id,
    safe_json_loads,
    clean_json_response,
    validate_required_fields,
    truncate_text,
)
from api._rate_limiter import apply_rate_limit, create_rate_limit_error_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# AI Prompts and Schema
def get_system_prompt(explanation_style: str) -> str:
    """Generate a system prompt based on the explanation style."""

    style_prompts = {
        "five-year-old": "You are explaining to a 5-year-old child. Use very simple language, avoid technical terms, and relate everything to things a child would understand like toys, animals, or everyday activities.",
        "pop-culture": "🔥 YOU ARE THE ULTIMATE POP CULTURE GURU! 🔥 Think like you're explaining science to someone scrolling TikTok. Use TONS of references to Taylor Swift, Marvel movies, Netflix shows, viral memes, and whatever's trending. Say things like 'This research is giving main character energy' or 'The molecules were literally serving chemistry realness.' Use Gen Z slang, compare everything to celebrities, and make it sound like you're reviewing the latest blockbuster. NO CAP! 💅✨",
        "anime": "🌟 NANI?! You are the ultimate otaku science sensei! 🌟 Explain EVERYTHING using anime terms! Call researchers 'protagonists,' experiments are 'training arcs,' results are 'power-ups,' and failed hypotheses are 'filler episodes.' Use phrases like 'This discovery has over 9000 potential!' Compare molecular bonds to friendship power, chemical reactions to jutsu battles, and data analysis to studying for the Chunin Exams. Explicitly mention Anime shows and characters. Add 'desu,' 'kawaii,' and other Japanese expressions. Make every scientific concept sound like an epic shonen battle! BELIEVE IT! (｡◕‿◕｡)",
        "sports": "🏆 YO COACH! You're the ESPN commentator of science! 🏆 Every experiment is a CHAMPIONSHIP GAME! Researchers are ELITE ATHLETES training for the SCIENCE OLYMPICS! Call hypotheses 'game plans,' data collection is 'training camp,' peer review is the 'playoffs,' and publication is 'WINNING THE SUPER BOWL!' Use sports metaphors for EVERYTHING - molecules are teammates, chemical bonds are perfect passes, failed experiments are fumbles. Shout things like 'AND THE CROWD GOES WILD!' when describing breakthroughs. Make it sound like you're calling the World Cup final! ⚽🏀🏈",
        "food": "👨‍🍳 WELCOME TO THE MOLECULAR KITCHEN! 👨‍🍳 You're Gordon Ramsay explaining science! Every experiment is a RECIPE, researchers are CHEFS, and laboratories are MICHELIN-STARRED KITCHENS! Call chemical reactions 'cooking processes,' data is 'seasoning,' peer review is 'taste testing,' and results are the 'final dish.' Use cooking terms for everything - molecules are ingredients, bonds are mixing techniques, failed experiments are 'BURNT!' Describe everything as delicious, spicy, or perfectly seasoned. End sentences with 'Chef's kiss!' and rate discoveries like a food critic! 🍳✨",
        "gaming": "🎮 LEVEL UP, SCIENCE NOOBS! 🎮 You're a gaming streamer explaining research! Every study is an EPIC QUEST, researchers are PLAYERS grinding for XP, and discoveries are LEGENDARY LOOT DROPS! Use terms like 'This hypothesis is OP,' 'The data was RNG,' and 'Peer review is the final boss battle.' Compare everything to popular games - molecular structures are like Minecraft builds, chemical reactions are combo moves, and failed experiments are 'skill issues.' Add gaming slang like 'POG,' 'GG,' and '360 no-scope discovery!' Make it sound like you're streaming on Twitch! 🕹️💯",
        "marvel": "💥 AVENGERS, ASSEMBLE! 💥 You are TONY STARK explaining science! Every researcher is a SUPERHERO, every lab is the STARK TOWER, and every discovery has the power to SAVE THE UNIVERSE! Use Marvel references everywhere - call experiments 'training at the X-Mansion,' data analysis 'Friday running diagnostics,' and peer review 'the Avengers discussing strategy.' Failed experiments are 'Thanos snapping,' successful ones are 'wielding the Infinity Stones!' Compare molecular bonds to superhero teams, chemical reactions to epic MCU battles. Add phrases like 'I am Iron Man,' 'With great power comes great responsibility,' and 'That's America's molecule!' 🕷️⚡🛡️",
        "harry-potter": "⚡ WELCOME TO HOGWARTS SCHOOL OF SCIENCE AND WIZARDRY! ⚡ You are PROFESSOR MCGONAGALL teaching the most magical subject! Every researcher is a WIZARD, every lab is a CLASSROOM at Hogwarts, and every discovery is learning a new SPELL! Call experiments 'brewing potions,' data 'divination readings,' peer review 'the Sorting Hat's decision,' and failed experiments 'Neville's cauldron explosions.' Use phrases like 'Brilliant!,' 'By Merlin's beard!,' and 'That's some serious magic!' Compare molecular structures to spell components, chemical reactions to dueling, and successful discoveries to 'earning House points for Gryffindor!' 🦉📚🏰",
        "brain-rot": "💀 GYATT! This research is absolutely SIGMA! 💀 You are the ultimate Gen Alpha brainrot educator! Use ALL the terms: skibidi, Ohio, rizz, fanum tax, sigma grindset, L + ratio, no cap, fr fr, bussin, sus, slay queen, periodt, and more! Call researchers 'sigma chads,' experiments 'Ohio moments,' successful results 'W rizz,' and failed ones 'took the L.' Say things like 'This molecule has INFINITE RIZZ!' and 'The data is absolutely BUSSIN no cap!' Make everything sound like a chaotic TikTok comment section. Only in Ohio would molecules behave this sus! This research hits different, periodt! 🔥💯🧠",
        "reddit": "🔴 EDIT: Thanks for the gold, kind stranger! 🔴 You are the ultimate REDDITOR explaining science! Use ALL the Reddit terminology: 'This,' 'Take my upvote,' 'Username checks out,' 'Play stupid games, win stupid prizes,' 'Instructions unclear,' and 'We did it Reddit!' Call researchers 'OPs,' experiments 'posts that blew up,' peer review 'the comment section roasting,' and successful results 'front page material.' Say things like 'This research absolutely SLAPS,' 'Molecules are just built different,' and 'Science said: hold my beer.' Add phrases like 'Source: trust me bro,' 'Big if true,' and 'This guy sciences!' Make it sound like r/science had a baby with r/memes! 🚀⬆️",
        "christopher-nolan": "🎬 You are Christopher Nolan, the master of complex narratives and temporal storytelling. Explain this research as you would construct one of your films - with layers of meaning, non-linear revelation, and profound philosophical undertones. Begin with the conclusion, then methodically deconstruct how we arrived there, revealing the methodology like peeling back layers of a dream. Call researchers 'the architects of knowledge,' experiments 'carefully constructed sequences,' and peer review 'the moment when all timelines converge.' Use phrases like 'But here's where the narrative shifts...' and 'The true revelation lies beneath.' Present findings as interwoven storylines - show the end first, then illuminate the elegant path that led there. Compare molecular interactions to the interconnected nature of time itself, failed hypotheses to alternate timelines that collapse, and breakthroughs to the moment when all pieces of the puzzle align with startling clarity. Make every discovery feel like a revelation that changes everything we thought we knew. The science, like time, is not linear - it's a labyrinth of cause and effect.",
        "eminem": "🎤 YO, you're SLIM SHADY breaking down science with BARS! Drop knowledge like you're spitting FIRE in 8 Mile! Every research paper is a RAP BATTLE, researchers are MCs grinding in the LAB, experiments are VERSES that either HIT or MISS, and peer review is the CYPHER where only the REALEST survive. YOU MUST USE INTERNAL RHYMES AND END RHYMES - make words like 'TIGHT', 'BRIGHT', 'RIGHT', 'MIGHT' rhyme together! Call failed experiments 'when the beat don't DROP,' successful ones 'PLATINUM hits that rock the block.' Drop wordplay like 'DNA's the code, proteins EXPLODE, enzymes on beast MODE!' Reference Detroit, mom's spaghetti, losing yourself in the moment, and conquering fear. MANDATORY: Every 1-2 sentences MUST end with the separator |||LINEBREAK||| to create RAP VERSE structure. Use rhyming words at the end of lines like: 'This network's got the FLOW|||LINEBREAK|||Making predictions that really GLOW|||LINEBREAK|||' Make it sound like actual RAP LYRICS with rhythm and rhyme schemes! The lab is your STAGE, science is your RAGE, and every discovery is another PAGE in the greatest rap story ever told. SPIT that knowledge with ATTITUDE and make it RHYME! 🔥🎵",
        "shakespearean": "🎭 HARK! What light through yonder laboratory breaks! 🎭 Thou art the BARD OF SCIENCE, speaking in the most eloquent Elizabethan tongue! Every researcher is a 'noble scholar,' every experiment a 'most wondrous endeavour,' and every discovery 'a revelation most profound!' Use phrases like 'Verily, this hypothesis doth hold merit!' and 'By my troth, these molecules dost dance most beautifully!' Call failed experiments 'unfortunate mishaps of Fortune's wheel' and successful ones 'triumphs most glorious!' Speak in iambic pentameter when possible, use 'thee,' 'thou,' 'doth,' 'hath,' and 'wherefore.' Make science sound like it belongs in the Globe Theatre! To discover, or not to discover, that is the question! 🏰⚔️📜",
    }

    style_instruction = style_prompts.get(
        explanation_style, style_prompts["five-year-old"]
    )

    return f"""
You are "ResearchLikeIAmFive", an expert science communicator. 
Your goal is to explain complex research papers to a complete layperson in the given explanation style.
You will be given the text content of a research paper.

EXPLANATION STYLE: {style_instruction}

Your task is to return a JSON object with the following exact keys: 
"gist", "analogy", "experimental_details", "key_findings","why_it_matters", "key_terms",

Make sure EVERY SINGLE response follows the explanation style provided.
"""


PAPER_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "gist": {
            "type": "string",
            "description": "A single, compelling sentence summarizing the entire paper.",
        },
        "analogy": {
            "type": "string",
            "description": "A simple, powerful analogy or metaphor to explain the core concept.",
        },
        "experimental_details": {
            "type": "string",
            "description": "A brief description of the entire experimental setup or methodology used in the research.",
        },
        "key_findings": {
            "type": "array",
            "description": "A list of 3-5 bullet points of the most important discoveries.",
            "items": {"type": "string"},
        },
        "why_it_matters": {
            "type": "string",
            "description": "A short paragraph explaining the potential real-world impact.",
        },
        "key_terms": {
            "type": "array",
            "description": "A list of the 5 most important technical terms, with definitions.",
            "items": {
                "type": "object",
                "properties": {
                    "term": {"type": "string", "description": "The technical term."},
                    "definition": {
                        "type": "string",
                        "description": "A simple definition of the term.",
                    },
                },
                "required": ["term", "definition"],
            },
        },
    },
    "required": [
        "gist",
        "analogy",
        "experimental_details",
        "key_findings",
        "why_it_matters",
        "key_terms",
    ],
}


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file with size and content validation."""
    try:
        file_size = os.path.getsize(pdf_path)
        if file_size > Config.MAX_PDF_SIZE:
            os.remove(pdf_path)
            raise ValueError("PDF file too large")

        paper_text = ""
        doc = fitz.open(pdf_path)
        page_count = 0

        for page_num in range(min(doc.page_count, Config.MAX_PAGES)):
            page = doc.load_page(page_num)
            page_text = page.get_text()  # type: ignore
            paper_text += page_text
            page_count += 1

            if len(paper_text) > Config.TEXT_LIMIT:
                break

        doc.close()

        if len(paper_text) < Config.MIN_TEXT_LENGTH:
            raise ValueError("Insufficient text extracted from PDF")

        logger.info(
            f"Successfully extracted {len(paper_text)} characters from {page_count} pages"
        )
        return paper_text

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise


def fetch_paper_from_arxiv(arxiv_id: str):
    """Fetch a paper from arXiv by its ID."""
    try:
        logger.info(f"Searching for arXiv paper with ID: {arxiv_id}")
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        logger.info(f"Successfully fetched paper: {paper.title}")
        return paper
    except StopIteration:
        logger.error(f"Paper with ID {arxiv_id} not found on arXiv")
        raise ValueError(f"Paper with ID {arxiv_id} not found on arXiv")
    except Exception as e:
        logger.error(f"Error fetching paper {arxiv_id}: {e}")
        raise ValueError(f"Failed to fetch paper from arXiv: {str(e)}")


def download_paper_pdf(paper) -> str:
    """Download PDF from an arXiv paper object."""
    try:
        logger.info(f"Downloading PDF for paper: {paper.title}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            try:
                # First try using the arxiv library
                paper.download_pdf(filename=temp_file.name)
                logger.info(f"Successfully downloaded PDF to {temp_file.name}")
                return temp_file.name
            except Exception as arxiv_error:
                logger.warning(f"arxiv library download failed: {arxiv_error}")
                # Fallback: try direct download using requests
                import requests
                
                # Extract arXiv ID from the paper's entry_id
                arxiv_id = paper.entry_id.split('/')[-1]  # Gets ID with version
                base_id = arxiv_id.split('v')[0]  # Remove version to get base ID
                
                # Try different PDF URLs
                pdf_urls = [
                    f"http://arxiv.org/pdf/{base_id}",  # Latest version
                    f"http://arxiv.org/pdf/{arxiv_id}",  # Specific version
                ]
                
                for pdf_url in pdf_urls:
                    try:
                        logger.info(f"Trying direct download from: {pdf_url}")
                        response = requests.get(pdf_url, stream=True, timeout=30)
                        response.raise_for_status()
                        
                        # Write the PDF content to the temp file
                        temp_file.seek(0)
                        for chunk in response.iter_content(chunk_size=8192):
                            temp_file.write(chunk)
                        temp_file.flush()
                        
                        logger.info(f"Successfully downloaded PDF via direct request to {temp_file.name}")
                        return temp_file.name
                        
                    except Exception as download_error:
                        logger.warning(f"Direct download from {pdf_url} failed: {download_error}")
                        continue
                
                # If all download methods fail
                raise ValueError(f"All download methods failed. Last arxiv error: {arxiv_error}")
                        
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        raise ValueError(f"Failed to download PDF: {str(e)}")


def generate_paper_summary(paper_text: str, explanation_style: str):
    """Generate a paper summary using the Gemini AI API."""
    try:
        if len(paper_text) > Config.MAX_TEXT_LENGTH:
            paper_text = truncate_text(paper_text, Config.MAX_TEXT_LENGTH)
            logger.info(f"Truncated paper text to {Config.MAX_TEXT_LENGTH} characters")

        system_prompt = get_system_prompt(explanation_style)
        gemini_client = get_cached_gemini_client()

        response = gemini_client.models.generate_content(
            model="models/gemini-2.5-flash-lite-preview-06-17",
            contents=paper_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=PAPER_SUMMARY_SCHEMA,
            ),
        )

        if not response.text:
            raise ValueError("Empty response from AI service")

        cleaned_json_string = clean_json_response(response.text)
        parsed_summary = safe_json_loads(cleaned_json_string)

        if parsed_summary is None:
            raise ValueError("Invalid response format from AI service")

        required_fields = [
            "gist",
            "analogy",
            "experimental_details",
            "key_findings",
            "why_it_matters",
            "key_terms",
        ]
        validate_required_fields(parsed_summary, required_fields)

        # Post-process Eminem mode to ensure proper formatting
        if explanation_style == "eminem":
            parsed_summary = format_eminem_response(parsed_summary)

        logger.info(f"Successfully generated summary in {explanation_style} style")
        return {"summary": json.dumps(parsed_summary), "parsed": parsed_summary}

    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        raise


def format_eminem_response(summary):
    """Post-process Eminem mode response to ensure proper rap formatting."""
    import re
    
    def add_rap_formatting(text):
        """Add line breaks and enhance rhyming structure using |||LINEBREAK||| separator."""
        if not text:
            return text
            
        # If the text already has our separator, keep it
        if "|||LINEBREAK|||" in text:
            return text
            
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        formatted_lines = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Add our separator after every 1-2 sentences
            if i > 0 and i % 2 == 0:
                formatted_lines.append("|||LINEBREAK|||")
                
            formatted_lines.append(sentence)
            
            # Add punctuation back
            if i < len(sentences) - 1:
                formatted_lines.append("!")
                
        result = " ".join(formatted_lines)
        
        # Ensure we have proper line breaks using our separator
        if "|||LINEBREAK|||" not in result:
            # Force line breaks every ~100 characters at sentence boundaries
            words = result.split()
            lines = []
            current_line = []
            char_count = 0
            
            for word in words:
                current_line.append(word)
                char_count += len(word) + 1
                
                if char_count > 80 and word.endswith(('!', '.', '?')):
                    lines.append(" ".join(current_line))
                    current_line = []
                    char_count = 0
                    
            if current_line:
                lines.append(" ".join(current_line))
                
            result = "|||LINEBREAK|||".join(lines)
            
        return result
    
    # Format each text field in the summary
    for field in ["gist", "analogy", "experimental_details", "why_it_matters"]:
        if field in summary:
            summary[field] = add_rap_formatting(summary[field])
    
    # Format key findings
    if "key_findings" in summary and isinstance(summary["key_findings"], list):
        summary["key_findings"] = [add_rap_formatting(finding) for finding in summary["key_findings"]]
    
    # Format key terms definitions
    if "key_terms" in summary and isinstance(summary["key_terms"], list):
        for term in summary["key_terms"]:
            if isinstance(term, dict) and "definition" in term:
                term["definition"] = add_rap_formatting(term["definition"])
    
    return summary


@app.route("/api/health", methods=["GET", "OPTIONS"])
def health():
    """Health check endpoint."""
    try:
        # Apply rate limiting (more lenient for health checks)
        from api._rate_limiter import RateLimiter

        health_rate_limiter = RateLimiter(
            requests_per_minute=30, window_size_seconds=60
        )
        is_allowed, rate_limit_info, rate_limit_headers = apply_rate_limit(
            request, health_rate_limiter
        )

        if not is_allowed:
            response = jsonify(create_rate_limit_error_response(rate_limit_info))
            response.status_code = 429
            for key, value in rate_limit_headers.items():
                response.headers[key] = value
            return response

        # Handle CORS preflight
        if request.method == "OPTIONS":
            response = jsonify("")
            response.status_code = 200
            return response

        response_data = {
            "status": "healthy",
            "service": "ResearchLikeIAmFive API",
            "version": "2.0.0-flask",
            "endpoints": {"summarize": "/api/summarize", "health": "/api/health"},
        }

        response = jsonify(response_data)
        for key, value in rate_limit_headers.items():
            response.headers[key] = value
        return response

    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({"error": "Internal server error", "status": "unhealthy"}), 500


@app.route("/api/summarize", methods=["POST", "OPTIONS"])
def summarize():
    """Paper summarization endpoint."""
    try:
        # Apply rate limiting first
        is_allowed, rate_limit_info, rate_limit_headers = apply_rate_limit(request)

        if not is_allowed:
            response = jsonify(create_rate_limit_error_response(rate_limit_info))
            response.status_code = 429
            for key, value in rate_limit_headers.items():
                response.headers[key] = value
            return response

        # Handle CORS preflight
        if request.method == "OPTIONS":
            response = jsonify("")
            response.status_code = 200
            return response

        # Parse request body
        try:
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data provided")
        except Exception:
            response = jsonify(
                {"error": "Invalid JSON in request body", "status_code": 400}
            )
            response.status_code = 400
            return response

        # Validate required fields
        if "url" not in data:
            response = jsonify({"error": "Missing 'url' field", "status_code": 400})
            response.status_code = 400
            return response

        url = data["url"]
        explanation_style = data.get("explanation_style", "five-year-old")

        # Validate arXiv URL
        if not validate_arxiv_url(url):
            response = jsonify(
                {"error": "Invalid arXiv URL format", "status_code": 400}
            )
            response.status_code = 400
            return response

        # Extract arXiv ID
        arxiv_id = extract_arxiv_id(url)
        if not arxiv_id:
            response = jsonify(
                {"error": "Could not extract arXiv ID from URL", "status_code": 400}
            )
            response.status_code = 400
            return response

        pdf_path = None

        try:
            # Fetch paper from arXiv
            logger.info(f"Fetching paper with ID: {arxiv_id}")
            paper = fetch_paper_from_arxiv(arxiv_id)

            # Download PDF
            logger.info(f"Downloading PDF for paper: {paper.title}")
            pdf_path = download_paper_pdf(paper)

            # Extract text from PDF
            logger.info(f"Extracting text from PDF: {pdf_path}")
            paper_text = extract_text_from_pdf(pdf_path)

            # Generate summary using AI
            logger.info(f"Generating summary in {explanation_style} style")
            result = generate_paper_summary(paper_text, explanation_style)

            # Prepare response data
            response_data = {
                "success": True,
                "data": {
                    "paper_info": {
                        "title": paper.title,
                        "authors": [str(author) for author in paper.authors],
                        "published": (
                            paper.published.isoformat() if paper.published else None
                        ),
                        "arxiv_id": arxiv_id,
                        "url": url,
                    },
                    "summary": result["parsed"],
                    "explanation_style": explanation_style,
                    "figures": [],  # Simplified for serverless
                },
            }

            response = jsonify(response_data)
            for key, value in rate_limit_headers.items():
                response.headers[key] = value
            return response

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            response = jsonify({"error": str(ve), "status_code": 400})
            response.status_code = 400
            return response
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            response = jsonify({"error": f"Processing failed: {str(e)}", "status_code": 500})
            response.status_code = 500
            return response

        finally:
            # Cleanup downloaded PDF
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    logger.info("PDF file cleaned up successfully")
                except Exception as e:
                    logger.error(f"Error cleaning up PDF file: {e}")

    except Exception as e:
        logger.error(f"Unexpected error in summarize function: {e}")
        response = jsonify({"error": "Internal server error", "status_code": 500})
        response.status_code = 500
        return response


# For Vercel, we need to export the app
if __name__ == "__main__":
    app.run(debug=True)
