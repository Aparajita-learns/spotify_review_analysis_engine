"""
src/ingest/reddit_ingest.py
---------------------------
Reddit discussions ingestion using public RSS endpoints.
This bypasses the strict 403 blocks on Reddit's JSON search API.
"""

import time
import feedparser
from typing import Dict, Any
from bs4 import BeautifulSoup
from src.config.settings import REDDIT_KEYWORDS
from src.ingest.normalize import normalize_record
from src.db.repository import insert_raw_document, upsert_source
from src.utils.logging import get_logger

logger = get_logger(__name__)


def ingest_reddit(limit_per_keyword: int = 25) -> Dict[str, int]:
    """
    Search Reddit for specific keywords via RSS and ingest matching posts as discussions.
    Returns a dict with counts of inserted vs skipped records.
    """
    logger.info(f"Starting Reddit RSS ingestion for {len(REDDIT_KEYWORDS)} keywords...")
    
    source_id = upsert_source(
        source_name="reddit",
        source_type="discussion",
        platform="Reddit",
        ingestion_method="rss"
    )
    
    results = {"inserted": 0, "skipped": 0, "errors": 0}
    
    # We must use a standard browser User-Agent to avoid RSS blocks
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    import urllib.parse
    
    for keyword in REDDIT_KEYWORDS:
        logger.info(f"Searching Reddit for: '{keyword}'")
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://www.reddit.com/search.rss?q={encoded_keyword}&limit={limit_per_keyword}&type=link"
        
        try:
            # feedparser can take custom request headers by monkeypatching or just passing agent
            feed = feedparser.parse(url, agent=user_agent)
            
            if feed.bozo and hasattr(feed, 'status') and feed.status == 429:
                logger.warning("Rate limited by Reddit RSS. Stopping early.")
                break
                
            if not feed.entries:
                logger.warning(f"No results or RSS blocked for keyword: {keyword}")
                continue
                
            for entry in feed.entries:
                # RSS gives HTML in summary, we can parse it
                title = entry.get("title")
                raw_html = entry.get("summary", "")
                
                # Extract text from HTML summary
                try:
                    body = BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()
                except:
                    body = raw_html
                    
                author = entry.get("author", "").replace("/u/", "")
                
                raw_record = {
                    "source_name": "reddit",
                    "source_type": "discussion",
                    "platform": "Reddit",
                    "ingestion_method": "rss",
                    "external_id": entry.get("id"),
                    "title": title,
                    "body": body,
                    "author_name": author,
                    "rating": None,
                    "review_date": entry.get("published"),
                    "country": None,
                    "language": "en",
                    "url": entry.get("link"),
                    "app_version": None,
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
            logger.error(f"Error parsing Reddit RSS for '{keyword}': {e}")
            results["errors"] += 1
            
        # Be polite to the RSS endpoint
        time.sleep(2)
            
    logger.info(f"Reddit RSS ingestion complete. Inserted: {results['inserted']}, Skipped: {results['skipped']}, Errors: {results['errors']}")
    return results

if __name__ == "__main__":
    res = ingest_reddit(limit_per_keyword=5)
    print("Result:", res)
