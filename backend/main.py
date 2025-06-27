import os
import re
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

# --- The AI Prompt ---
# This is our "secret sauce". It tells the AI exactly what to do.
SYSTEM_PROMPT = """
You are "ResearchLikeIAmFive", an expert science communicator. 
Your goal is to explain complex research papers to a complete layperson.
You will be given the text content of a research paper.

Your task is to return a JSON object with the following exact keys: 
"gist", "analogy", "experimental_details", "key_findings", "why_it_matters", "key_terms".
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
        
        # Clean up the downloaded file
        os.remove(pdf_path)
        
        if len(paper_text) < 500: # Basic check for valid content
            raise HTTPException(status_code=500, detail="Failed to extract sufficient text from the PDF.")

        # 4. Call Gemini API
        response = client.models.generate_content(
            model="models/gemini-2.5-flash-lite-preview-06-17",
            contents=paper_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_json_schema=PAPER_SUMMARY_SCHEMA,
            )
        )
        
        # 5. Return the JSON response
        # The API returns markdown JSON, so we clean it up
        if not response.text:
            raise HTTPException(status_code=500, detail="No response from the AI model.")
        cleaned_json_string = response.text.strip().replace('```json', '').replace('```', '').strip()
        return {"summary": cleaned_json_string, "title": paper.title}

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

# Add a simple root endpoint to confirm the server is running
@app.get("/")
def read_root():
    return {"message": "ResearchLikeIAmFive API is running!"}