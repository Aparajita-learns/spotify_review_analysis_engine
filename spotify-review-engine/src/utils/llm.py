"""
src/utils/llm.py
----------------
Utilities for calling Generative AI APIs (like Google Gemini) 
for Retrieval-Augmented Generation (RAG).
"""

import os
import google.generativeai as genai
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Configure the API key from environment variables
# Note: Streamlit's load_dotenv() from app.py ensures this is available
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def summarize_reviews(query: str, search_results: list) -> str:
    """
    Takes the user's natural language query and the list of retrieved reviews,
    and uses Google Gemini to synthesize a conversational answer.
    """
    if not GEMINI_API_KEY:
        return "⚠️ Gemini API Key not found. Please set `GEMINI_API_KEY` in your `.env` file to enable AI summarization."
        
    if not search_results:
        return "No reviews found to summarize."

    # Construct the context block
    context_blocks = []
    for i, res in enumerate(search_results):
        context_blocks.append(f"Review {i+1}: {res['clean_text']}")
        
    context_str = "\n".join(context_blocks)
    
    prompt = f"""
You are a Product Management AI Assistant helping analyze user feedback for Spotify.
A user asked the following question: "{query}"

Here are the most relevant reviews retrieved from the database:
{context_str}

Please synthesize these reviews into a brief, conversational summary that directly answers the user's question. 
Quote specific user feedback where relevant. Do not include information outside of the provided reviews.
"""

    try:
        # Use the latest available gemini model
        model = genai.GenerativeModel('gemini-3.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        return f"⚠️ An error occurred while generating the summary: {e}"
