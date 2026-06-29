"""
src/process/segment_users.py
----------------------------
Maps users (based on their clean_documents) to user_segments.
"""

import re
from typing import Dict, Set, List
from src.config.taxonomy import USER_SEGMENTS
from src.db.repository import get_client
from src.utils.logging import get_logger

logger = get_logger(__name__)


# ── Keyword Heuristics for User Segments ─────────────────────────────
SEGMENT_KEYWORDS = {
    "passive_consumers": [r"\bbackground\b", r"\bdon'?t care\b", r"\bjust play\b"],
    "active_seekers": [r"\bsearch\b", r"\bnew\b", r"\bdigging\b", r"\bunderground\b"],
    "playlist_curators": [r"\bcurat(e|ing)\b", r"\bmy playlists\b", r"\bcollection\b"],
    "habitual_listeners": [r"\bdaily mix\b", r"\broutine\b", r"\bevery day\b"],
    "frustrated_explorers": [r"\bcant find\b", r"\bsucks\b", r"\bbad recommendations\b", r"\bstuck\b"]
}

COMPILED_RULES = {
    segment: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for segment, patterns in SEGMENT_KEYWORDS.items()
}


def classify_user_segment(text: str) -> Set[str]:
    """Returns a set of segment codes that match the document text."""
    matched_segments = set()
    for segment, regex_list in COMPILED_RULES.items():
        for regex in regex_list:
            if regex.search(text):
                matched_segments.add(segment)
                break
    return matched_segments


def process_segments(limit: int = 500) -> Dict[str, int]:
    """
    Finds clean_documents without segments, extracts segments, 
    and inserts into document_segments.
    """
    logger.info("Starting user segmentation...")
    client = get_client()
    
    res = client.table("clean_documents") \
        .select("id, clean_text") \
        .eq("is_duplicate", False) \
        .limit(limit) \
        .execute()
        
    docs = res.data or []
    if not docs:
        return {"processed": 0, "segments_assigned": 0}
        
    doc_ids = [d["id"] for d in docs]
    existing_segments = client.table("document_segments") \
        .select("clean_document_id") \
        .in_("clean_document_id", doc_ids) \
        .execute()
        
    already_processed_ids = {row["clean_document_id"] for row in (existing_segments.data or [])}
    
    results = {"processed": 0, "segments_assigned": 0}
    
    segments_db = client.table("user_segments").select("id, segment_code").execute()
    segment_id_map = {row["segment_code"]: row["id"] for row in (segments_db.data or [])}
    
    inserts = []
    for doc in docs:
        if doc["id"] in already_processed_ids:
            continue
            
        matched_codes = classify_user_segment(doc["clean_text"])
        
        for code in matched_codes:
            if code in segment_id_map:
                inserts.append({
                    "clean_document_id": doc["id"],
                    "segment_id": segment_id_map[code],
                    "confidence": 0.85
                })
                results["segments_assigned"] += 1
                
        results["processed"] += 1
        
    if inserts:
        client.table("document_segments").insert(inserts).execute()
        
    logger.info(f"User segmentation complete. Processed {results['processed']} docs, assigned {results['segments_assigned']} segments.")
    return results

if __name__ == "__main__":
    res = process_segments(limit=10)
    print("Result:", res)
