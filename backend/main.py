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
