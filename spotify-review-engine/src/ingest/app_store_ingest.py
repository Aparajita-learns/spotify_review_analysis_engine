"""
src/ingest/app_store_ingest.py
------------------------------
Apple App Store review ingestion using iTunes RSS feed.
"""

import requests
import datetime
from typing import Dict, Any
from src.config.settings import SPOTIFY_APPLE_ID, APP_STORE_COUNTRIES
from src.ingest.normalize import normalize_record
from src.db.repository import insert_raw_document, upsert_source
from src.utils.logging import get_logger

logger = get_logger(__name__)


def ingest_app_store(pages_per_country: int = 1) -> Dict[str, int]:
    """
    Fetch Apple App Store reviews for Spotify via RSS feed and insert into raw_documents.
    Apple's RSS feed supports pages 1 through 10, with up to 50 items per page.
    
    Returns a dict with counts of inserted vs skipped records.
    """
    logger.info(f"Starting App Store ingestion for {len(APP_STORE_COUNTRIES)} countries...")
    
    source_id = upsert_source(
        source_name="app_store",
        source_type="review",
        platform="Apple",
        ingestion_method="api"
    )
    
    results = {"inserted": 0, "skipped": 0, "errors": 0}
    
    for country in APP_STORE_COUNTRIES:
        for page in range(1, pages_per_country + 1):
            logger.info(f"Fetching App Store reviews for country: {country}, page: {page}")
            # The RSS endpoint for customer reviews
            url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={SPOTIFY_APPLE_ID}/sortby=mostrecent/json"
            
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                entries = data.get("feed", {}).get("entry", [])
                if not entries:
                    logger.info(f"No more entries found for {country} at page {page}.")
                    break
                    
                # First entry is sometimes the app metadata itself, so we filter it out if it lacks an author name
                for entry in entries:
                    if "author" not in entry:
                        continue
                        
                    # Apple returns text fields in {"label": "..."} format
                    try:
                        title = entry.get("title", {}).get("label")
                        body = entry.get("content", {}).get("label")
                        author_name = entry.get("author", {}).get("name", {}).get("label")
                        rating_str = entry.get("im:rating", {}).get("label")
                        external_id = entry.get("id", {}).get("label")
                        version = entry.get("im:version", {}).get("label")
                        
                        raw_record = {
                            "source_name": "app_store",
                            "source_type": "review",
                            "platform": "Apple",
                            "ingestion_method": "api",
                            "external_id": external_id,
                            "title": title,
                            "body": body,
                            "author_name": author_name,
                            "rating": int(rating_str) if rating_str else None,
                            "review_date": None,  # Apple RSS JSON often lacks a strict timestamp, or it's buried
                            "country": country,
                            "language": "en",  # We assume English for MVP based on country selection
                            "url": None,
                            "app_version": version,
                            "metadata": {}
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
                        logger.warning(f"Failed to parse an App Store entry: {e}")
                        results["errors"] += 1
            except requests.RequestException as e:
                logger.error(f"Network error fetching App Store reviews for {country}: {e}")
                results["errors"] += 1
                break # Move to next country if we hit a network issue (e.g. 404 or 403)
                
    logger.info(f"App Store ingestion complete. Inserted: {results['inserted']}, Skipped: {results['skipped']}, Errors: {results['errors']}")
    return results

if __name__ == "__main__":
    res = ingest_app_store(pages_per_country=1)
    print("Result:", res)
