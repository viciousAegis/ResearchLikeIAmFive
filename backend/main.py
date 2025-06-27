import os
import re
import base64
import io
from google import genai
from google.genai import types
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import arxiv
import fitz  # PyMuPDF for PDF parsing

# --- Configuration ---
# Load environment variables for local development
from dotenv import load_dotenv
load_dotenv() 

# Configure the Gemini API
# e.g., GOOGLE_API_KEY="your_api_key_here"
try:
    client = genai.Client()
except Exception as e:
    print(f"Error configuring Gemini API: {e}. Make sure the API key is set.")
    # In a real app, you might want to exit or handle this more gracefully
    
# --- FastAPI App Setup ---
app = FastAPI(
    title="ResearchLikeIAmFive API",
    description="API for summarizing arXiv papers for a lay audience.",
    version="0.1.0",
)

# Allow cross-origin requests (for our frontend to talk to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# --- Pydantic Models (for request data validation) ---
class ArxivRequest(BaseModel):
    url: str
    explanation_style: str = "five-year-old"

# --- The AI Prompt ---
# This is our "secret sauce". It tells the AI exactly what to do.
def get_system_prompt(explanation_style: str) -> str:
    """Generate a system prompt based on the explanation style."""
    
    style_prompts = {
        "five-year-old": "You are explaining to a 5-year-old child. Use very simple language, avoid technical terms, and relate everything to things a child would understand like toys, animals, or everyday activities.",
        
        "pop-culture": "You are explaining using pop culture references. Use examples from popular movies, TV shows, celebrities, music, memes, and social media trends. Make it relatable to someone who follows mainstream culture.",
        
        "anime": "You are explaining using anime and manga references. Use concepts from popular anime series, manga tropes, character archetypes, and Japanese pop culture. Reference things like power levels, jutsu, quirks, or magical systems.",
        
        "sports": "You are explaining using sports analogies. Compare everything to sports concepts like teamwork, strategy, training, competition, coaching, and game mechanics. Use examples from football, basketball, soccer, or other popular sports. Reference popular athletes or teams when relevant.",
        
        "food": "You are explaining using food and cooking analogies. Compare concepts to recipes, ingredients, cooking techniques, flavors, kitchen equipment, and restaurant operations. Make it delicious and appetizing!",
        
        "gaming": "You are explaining using video game terminology. Use concepts like leveling up, skill trees, game mechanics, NPCs, quests, achievements, multiplayer dynamics, and different game genres.",
        
        "fantasy": "You are explaining using fantasy and medieval concepts. Use analogies involving wizards, dragons, magical spells, kingdoms, quests, knights, and mystical creatures. Make it epic and magical!",
        
        "wild-west": "You are explaining using Wild West and cowboy terminology. Use concepts like frontier towns, sheriffs, outlaws, cattle ranching, gold mining, saloons, and horseback riding. Yeehaw!",
        
        "space": "You are explaining using space and sci-fi concepts. Use analogies involving rockets, planets, galaxies, astronauts, space missions, alien civilizations, and futuristic technology.",
        
        "superhero": "You are explaining using superhero and comic book concepts. Compare everything to superpowers, secret identities, villain schemes, hero teams, comic book physics, and saving the world."
    }
    
    style_instruction = style_prompts.get(explanation_style, style_prompts["five-year-old"])
    
    return f"""
You are "ResearchLikeIAmFive", an expert science communicator. 
Your goal is to explain complex research papers to a complete layperson.
You will be given the text content of a research paper.

EXPLANATION STYLE: {style_instruction}

Your task is to return a JSON object with the following exact keys: 
"gist", "analogy", "experimental_details", "key_findings","why_it_matters", "key_terms",

Make sure ALL explanations follow the specified style consistently throughout your response.
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


# --- API Endpoint ---
@app.post("/summarize")
async def summarize_paper(request: ArxivRequest):
    """
    Accepts an arXiv URL, fetches the paper, and returns a summary.
    """
    try:
        # 1. Extract arXiv ID from URL
        arxiv_id_match = re.search(r'abs/(\d+\.\d+)', request.url)
        if not arxiv_id_match:
            raise HTTPException(status_code=400, detail="Invalid arXiv URL. Please use a format like https://arxiv.org/abs/...")
        arxiv_id = arxiv_id_match.group(1)

        # 2. Fetch Paper from arXiv
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        
        # 3. Download and Extract Text from PDF
        pdf_path = paper.download_pdf()
        paper_text = ""
        
        # Use PyMuPDF to extract text from the PDF
        doc = fitz.open(pdf_path)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            paper_text += page.get_text()  # type: ignore
        doc.close()
        
        # Extract figures from the PDF (disabled for now)
        # extracted_figures = extract_figures_from_pdf(pdf_path)
        extracted_figures = []
        
        # Clean up the downloaded file
        os.remove(pdf_path)
        
        if len(paper_text) < 500: # Basic check for valid content
            raise HTTPException(status_code=500, detail="Failed to extract sufficient text from the PDF.")

        # 4. Call Gemini API with dynamic system prompt
        system_prompt = get_system_prompt(request.explanation_style)
        response = client.models.generate_content(
            model="models/gemini-2.5-flash-lite-preview-06-17",
            contents=paper_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=PAPER_SUMMARY_SCHEMA,
            )
        )
        
        # 5. Return the JSON response
        # The API returns markdown JSON, so we clean it up
        if not response.text:
            raise HTTPException(status_code=500, detail="No response from the AI model.")
        cleaned_json_string = response.text.strip().replace('```json', '').replace('```', '').strip()
        return {
            "summary": cleaned_json_string, 
            "title": paper.title, 
            "figures": extracted_figures
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

# Add a simple root endpoint to confirm the server is running
@app.get("/")
def read_root():
    return {"message": "ResearchLikeIAmFive API is running!"}