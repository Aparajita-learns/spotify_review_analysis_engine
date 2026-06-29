"""
src/ingest/manual_import.py
---------------------------
Manual CSV import pathway for public forums, social exports, etc.
"""

import pandas as pd
from typing import Dict
from src.ingest.normalize import normalize_record
from src.db.repository import insert_raw_document, upsert_source
from src.utils.logging import get_logger

logger = get_logger(__name__)


def ingest_csv(df: pd.DataFrame) -> Dict[str, int]:
    """
    Ingest a pandas DataFrame (e.g., from an uploaded CSV) into the DB.
    The CSV should have columns matching the raw record dictionary.
    """
    logger.info(f"Starting manual CSV ingestion for {len(df)} rows.")
    results = {"inserted": 0, "skipped": 0, "errors": 0}
    
    # Pre-cache source IDs to avoid DB calls for every row
    source_cache = {}
    
    for _, row in df.iterrows():
        raw_dict = row.to_dict()
        
        # Ensure source details exist
        source_name = str(raw_dict.get("source_name", "manual_social")).strip().lower()
        source_type = str(raw_dict.get("source_type", "review")).strip().lower()
        platform = str(raw_dict.get("platform", "Manual")).strip()
        ingestion_method = "csv_import"
        
        # Need at least source_name to proceed safely if user forgets
        raw_dict["source_name"] = source_name if source_name else "manual_social"
        raw_dict["source_type"] = source_type if source_type else "review"
        raw_dict["platform"] = platform if platform else "Manual"
        raw_dict["ingestion_method"] = ingestion_method
        
        # Replace NaN with None
        for k, v in raw_dict.items():
            if pd.isna(v):
                raw_dict[k] = None
                
        normalized = normalize_record(raw_dict)
        if not normalized:
            results["errors"] += 1
            continue
            
        # Get or create source ID
        source_key = (normalized["source_name"], normalized["source_type"], normalized["platform"])
        if source_key not in source_cache:
            source_id = upsert_source(
                source_name=normalized["source_name"],
                source_type=normalized["source_type"],
                platform=normalized["platform"],
                ingestion_method=ingestion_method
            )
            source_cache[source_key] = source_id
            
        normalized["source_id"] = source_cache[source_key]
        
        try:
            inserted_id = insert_raw_document(normalized)
            if inserted_id:
                results["inserted"] += 1
            else:
                results["skipped"] += 1
        except Exception as e:
            logger.error(f"Error inserting row from CSV: {e}")
            results["errors"] += 1
            
    logger.info(f"CSV ingestion complete. Inserted: {results['inserted']}, Skipped: {results['skipped']}, Errors: {results['errors']}")
    return results
