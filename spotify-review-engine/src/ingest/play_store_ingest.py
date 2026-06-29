"""
src/ingest/play_store_ingest.py
-------------------------------
Google Play Store review ingestion using google-play-scraper.
"""

from typing import List, Dict, Any
from google_play_scraper import reviews, Sort
from src.config.settings import SPOTIFY_APP_ID, PLAY_STORE_COUNTRIES
from src.ingest.normalize import normalize_record
from src.db.repository import insert_raw_document, upsert_source
from src.utils.logging import get_logger

logger = get_logger(__name__)


def ingest_play_store(
    count_per_country: int = 100,
    sort_order: Sort = Sort.NEWEST
) -> Dict[str, int]:
    """
    Scrape Google Play Store reviews for Spotify and insert into raw_documents.
    
    Returns a dict with counts of inserted vs skipped records.
    """
    logger.info(f"Starting Play Store ingestion for {len(PLAY_STORE_COUNTRIES)} countries...")
    
    # Ensure source exists in DB
    source_id = upsert_source(
        source_name="play_store",
        source_type="review",
        platform="GooglePlay",
        ingestion_method="scraper"
    )
    
    results = {"inserted": 0, "skipped": 0, "errors": 0}
    
    for country in PLAY_STORE_COUNTRIES:
        logger.info(f"Fetching Play Store reviews for country: {country}")
        try:
            # We fetch up to `count_per_country`. If more is needed, pagination logic (continuation_token) is required.
            result, continuation_token = reviews(
                SPOTIFY_APP_ID,
                lang="en",  # MVP focused on English
                country=country,
                sort=sort_order,
                count=count_per_country
            )
            
            for review in result:
                raw_record = {
                    "source_name": "play_store",
                    "source_type": "review",
                    "platform": "GooglePlay",
                    "ingestion_method": "scraper",
                    "external_id": str(review.get("reviewId")),
                    "title": None,  # Play Store reviews typically don't have titles
                    "body": review.get("content"),
                    "author_name": review.get("userName"),
                    "rating": review.get("score"),
                    "review_date": review.get("at"),
                    "country": country,
                    "language": "en",
                    "url": None,
                    "app_version": review.get("reviewCreatedVersion"),
                    "metadata": {
                        "thumbs_up": review.get("thumbsUpCount"),
                        "reply_content": review.get("replyContent"),
                        "reply_date": review.get("repliedAt").isoformat() if review.get("repliedAt") else None,
                    }
                }
                
                normalized = normalize_record(raw_record)
                if not normalized:
                    results["errors"] += 1
                    continue
                
                normalized["source_id"] = source_id
                
                inserted_id = insert_raw_document(normalized)
                if inserted_id:
                    results["inserted"] += 1
                else:
                    results["skipped"] += 1
                    
        except Exception as e:
            logger.error(f"Error fetching Play Store reviews for {country}: {e}")
            results["errors"] += 1
            
    logger.info(f"Play Store ingestion complete. Inserted: {results['inserted']}, Skipped: {results['skipped']}, Errors: {results['errors']}")
    return results

if __name__ == "__main__":
    # Simple CLI test
    res = ingest_play_store(count_per_country=10)
    print("Result:", res)
