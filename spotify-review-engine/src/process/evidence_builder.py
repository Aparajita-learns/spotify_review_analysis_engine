"""
src/process/evidence_builder.py
-------------------------------
Phase 5 — Evidence span extraction helper.
Fetches representative quotes (clean text) for a given theme to support insights.
"""

from src.db.repository import get_client
from src.utils.logging import get_logger

logger = get_logger(__name__)

def get_evidence_for_theme(theme_id: str, limit: int = 3) -> list[str]:
    """
    Fetches up to `limit` clean_text snippets for documents tagged with `theme_id`.
    In a real system, this might use LLMs to extract exact spans.
    For this MVP, we just grab the shortest clean texts to serve as punchy quotes.
    """
    client = get_client()
    try:
        # Join document_themes with clean_documents
        res = client.table("document_themes")\
            .select("clean_document_id, clean_documents(clean_text)")\
            .eq("theme_id", theme_id)\
            .limit(limit * 3)\
            .execute()
            
        data = res.data or []
        
        # Filter out empty and sort by length to get punchy quotes
        quotes = []
        for row in data:
            if row.get("clean_documents") and row["clean_documents"].get("clean_text"):
                quotes.append(row["clean_documents"]["clean_text"])
                
        # Sort by length ascending, but filter out tiny useless ones (len < 10)
        valid_quotes = [q for q in quotes if len(q) > 10]
        valid_quotes.sort(key=len)
        
        return valid_quotes[:limit]
        
    except Exception as e:
        logger.error(f"Error fetching evidence for theme {theme_id}: {e}")
        return []

def get_evidence_for_segment(segment_id: str, limit: int = 3) -> list[str]:
    """
    Fetches up to `limit` clean_text snippets for documents tagged with `segment_id`.
    """
    client = get_client()
    try:
        res = client.table("document_segments")\
            .select("clean_document_id, clean_documents(clean_text)")\
            .eq("segment_id", segment_id)\
            .limit(limit * 3)\
            .execute()
            
        data = res.data or []
        
        quotes = []
        for row in data:
            if row.get("clean_documents") and row["clean_documents"].get("clean_text"):
                quotes.append(row["clean_documents"]["clean_text"])
                
        valid_quotes = [q for q in quotes if len(q) > 10]
        valid_quotes.sort(key=len)
        
        return valid_quotes[:limit]
        
    except Exception as e:
        logger.error(f"Error fetching evidence for segment {segment_id}: {e}")
        return []
