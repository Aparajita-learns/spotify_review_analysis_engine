"""
src/process/dedupe.py
---------------------
Three-stage deduplication pipeline.
Identifies duplicates within the clean_documents table using TF-IDF and Cosine Similarity.
"""

import pandas as pd
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.config.settings import DEDUPE_COSINE_THRESHOLD, SUPPORTED_LANGUAGES
from src.process.clean_text import clean_review_text, count_tokens_approx
from src.process.language import detect_language
from src.db.repository import (
    get_unprocessed_raw_documents, 
    insert_clean_document, 
    get_client
)
from src.utils.logging import get_logger

logger = get_logger(__name__)


def find_near_duplicate(normalized_text: str, existing_docs: List[Dict]) -> Optional[str]:
    """
    Check if `normalized_text` is a near duplicate of any text in `existing_docs`.
    Returns the ID of the duplicate_of document, or None if unique.
    """
    if not existing_docs or len(normalized_text.strip()) < 10:
        return None
        
    texts = [doc["normalized_text"] for doc in existing_docs]
    texts.append(normalized_text)
    
    try:
        vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 4))
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Calculate cosine similarity between the new text (last item) and all existing texts
        cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
        
        max_sim_idx = cosine_similarities.argmax()
        max_sim = cosine_similarities[max_sim_idx]
        
        if max_sim >= DEDUPE_COSINE_THRESHOLD:
            return existing_docs[max_sim_idx]["id"]
            
    except Exception as e:
        logger.warning(f"Error computing TF-IDF dedupe: {e}")
        
    return None


def fetch_recent_clean_documents(limit: int = 1000) -> List[Dict]:
    """Fetch the most recent clean documents to use as the corpus for deduplication."""
    client = get_client()
    res = client.table("clean_documents").select("id, normalized_text").order("processed_at", desc=True).limit(limit).execute()
    return res.data or []


def process_raw_documents(batch_size: int = 200) -> Dict[str, int]:
    """
    Pulls unprocessed raw documents, cleans them, checks for duplicates,
    and inserts them into the clean_documents table.
    """
    logger.info("Starting text cleaning and deduplication pipeline...")
    unprocessed = get_unprocessed_raw_documents(limit=batch_size)
    
    if not unprocessed:
        logger.info("No unprocessed documents found.")
        return {"processed": 0, "duplicates": 0, "errors": 0}
        
    logger.info(f"Processing batch of {len(unprocessed)} raw documents.")
    
    # Pre-fetch recent clean docs for fuzzy deduplication
    existing_clean_docs = fetch_recent_clean_documents(limit=5000)
    
    results = {"processed": 0, "duplicates": 0, "errors": 0}
    
    for raw in unprocessed:
        try:
            body = raw.get("body", "")
            raw_id = raw.get("id")
            
            clean_text, normalized_text = clean_review_text(body)
            language = detect_language(clean_text)
            
            # Skip non-target languages for MVP but mark them processed so we don't retry
            # Actually, the spec says "optionally filter to English", let's store all but mark the lang
            
            # Deduplication
            duplicate_of = find_near_duplicate(normalized_text, existing_clean_docs)
            is_duplicate = duplicate_of is not None
            
            clean_record = {
                "raw_document_id": raw_id,
                "clean_text": clean_text,
                "normalized_text": normalized_text,
                "detected_language": language,
                "is_duplicate": is_duplicate,
                "duplicate_of": duplicate_of,
                "token_count": count_tokens_approx(clean_text)
            }
            
            clean_id = insert_clean_document(clean_record)
            if clean_id:
                results["processed"] += 1
                if is_duplicate:
                    results["duplicates"] += 1
                
                # Add to existing docs so subsequent items in this batch are deduped against it
                if not is_duplicate:
                    existing_clean_docs.append({
                        "id": clean_id,
                        "normalized_text": normalized_text
                    })
            else:
                results["errors"] += 1
                
        except Exception as e:
            logger.error(f"Error processing raw document {raw.get('id')}: {e}")
            results["errors"] += 1
            
    logger.info(f"Processing complete. Processed: {results['processed']}, Duplicates marked: {results['duplicates']}, Errors: {results['errors']}")
    return results

if __name__ == "__main__":
    res = process_raw_documents(batch_size=10)
    print("Result:", res)
