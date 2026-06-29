"""
src/process/clean_text.py
-------------------------
Text cleaning and normalization pipeline.
Transforms raw review text into clean_text for NLP tasks,
and normalized_text for deduplication matching.
"""

import re
from bs4 import BeautifulSoup
from typing import Tuple


def clean_review_text(raw_text: str) -> Tuple[str, str]:
    """
    Cleans raw review text.
    
    Returns:
        (clean_text, normalized_text)
        
        clean_text: Stripped of HTML and weird whitespace, but preserves casing and punctuation
                    suitable for LLM extraction or sentiment analysis.
        normalized_text: Lowercased, stripped of all punctuation, suitable for fuzzy deduplication.
    """
    if not raw_text or not isinstance(raw_text, str):
        return "", ""
        
    # 1. Remove HTML tags (sometimes present in Reddit or scraped data)
    try:
        # BeautifulSoup is safer for HTML stripping
        text = BeautifulSoup(raw_text, "html.parser").get_text(separator=" ")
    except Exception:
        # Fallback if bs4 fails
        text = re.sub(r'<[^>]+>', ' ', raw_text)
        
    # 2. Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 3. Clean text (for LLM / NLP)
    # Remove some known boilerplate if needed, but mostly keep it intact
    clean_text = text
    
    # 4. Normalized text (for deduplication)
    # Lowercase, remove all non-alphanumeric characters except spaces
    normalized_text = text.lower()
    normalized_text = re.sub(r'[^\w\s]', '', normalized_text)
    normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
    
    return clean_text, normalized_text


def count_tokens_approx(text: str) -> int:
    """
    Approximate token count for the text (useful for LLM context window sizing).
    A simple approximation: ~4 chars per token for English.
    """
    return len(text) // 4
