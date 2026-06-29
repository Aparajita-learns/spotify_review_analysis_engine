"""
src/process/classify_themes.py
------------------------------
Maps clean_documents to themes from the taxonomy.
For the MVP, we use a robust keyword/regex-based approach.
If an OPENAI_API_KEY is present, we could switch to an LLM extraction (stubbed).
"""

import re
import os
from typing import List, Dict, Set
from src.config.taxonomy import THEMES
from src.db.repository import get_client
from src.utils.logging import get_logger

logger = get_logger(__name__)


# ── Keyword Heuristics for MVP ──────────────────────────────────────────
# These map directly to THEMES keys in the taxonomy
THEME_KEYWORDS = {
    "repetitive_recommendations": [r"\bsame\b.*\bsongs\b", r"\brepeats\b", r"\bloop\b", r"over and over", r"already heard"],
    "weak_novelty": [r"\bnot discovering\b", r"\bno new\b", r"\bhard to find\b"],
    "playlist_overdependence": [r"\bplaylist\b.*\bonly\b", r"\brely on playlists\b", r"\btired of playlists\b"],
    "passive_discovery": [r"\bjust play\b", r"\bradio\b", r"\bbackground\b", r"\bauto(?:\-)?play\b"],
    "active_exploration": [r"\bsearching for\b", r"\blooking for new\b", r"\bdigging\b"],
    "social_discovery": [r"\bfriends\b", r"\bshared\b", r"\bwhat others are listening to\b", r"\bblend\b"],
    "genre_expansion": [r"\bgenre\b", r"\bnew style\b", r"\bexpand\b"],
    "comfort_listening": [r"\bfamiliar\b", r"\bcomfort\b", r"\bnostalgia\b", r"\bold favorites\b"],
    "habit_loop": [r"\bdaily mix\b", r"\balgorithm\b", r"\broutine\b"],
    "novelty_control": [r"\bcontrol\b", r"\btweak\b", r"\badjust\b"],
    "reset_recommendations": [r"\breset\b", r"\bstart over\b", r"\bclear\b", r"\bwipe\b"],
}

# Pre-compile regexes for speed
COMPILED_RULES = {
    theme: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for theme, patterns in THEME_KEYWORDS.items()
}


def classify_document_heuristics(text: str) -> Set[str]:
    """
    Returns a set of theme codes that match the document text based on regex rules.
    """
    matched_themes = set()
    for theme, regex_list in COMPILED_RULES.items():
        for regex in regex_list:
            if regex.search(text):
                matched_themes.add(theme)
                break  # Move to next theme if one regex matches
    return matched_themes


def process_themes(limit: int = 500) -> Dict[str, int]:
    """
    Finds clean_documents without themes, extracts themes, and inserts into document_themes.
    """
    logger.info("Starting theme classification...")
    client = get_client()
    
    # Get clean docs that aren't marked as duplicates
    # and don't yet have themes
    res = client.table("clean_documents") \
        .select("id, clean_text") \
        .eq("is_duplicate", False) \
        .limit(limit) \
        .execute()
        
    docs = res.data or []
    if not docs:
        logger.info("No documents need theme classification.")
        return {"processed": 0, "themes_assigned": 0}
        
    # We must filter out docs that already have themes in python since Supabase 
    # doesn't support complex NOT IN joins easily over REST for this schema
    doc_ids = [d["id"] for d in docs]
    existing_themes = client.table("document_themes") \
        .select("clean_document_id") \
        .in_("clean_document_id", doc_ids) \
        .execute()
        
    already_processed_ids = {row["clean_document_id"] for row in (existing_themes.data or [])}
    
    results = {"processed": 0, "themes_assigned": 0}
    
    # We also need the theme UUIDs from the DB
    themes_db = client.table("themes").select("id, theme_code").execute()
    theme_id_map = {row["theme_code"]: row["id"] for row in (themes_db.data or [])}
    
    inserts = []
    for doc in docs:
        if doc["id"] in already_processed_ids:
            continue
            
        matched_codes = classify_document_heuristics(doc["clean_text"])
        
        for code in matched_codes:
            if code in theme_id_map:
                inserts.append({
                    "clean_document_id": doc["id"],
                    "theme_id": theme_id_map[code],
                    "confidence": 0.85, # Heuristic confidence
                    "extraction_method": "rules"
                })
                results["themes_assigned"] += 1
                
        results["processed"] += 1
        
    if inserts:
        # Batch insert
        client.table("document_themes").insert(inserts).execute()
        
    logger.info(f"Theme classification complete. Processed {results['processed']} docs, assigned {results['themes_assigned']} themes.")
    return results

if __name__ == "__main__":
    res = process_themes(limit=10)
    print("Result:", res)
