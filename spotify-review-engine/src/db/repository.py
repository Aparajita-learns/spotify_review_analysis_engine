"""
src/db/repository.py
--------------------
Data access layer.

All database reads and writes go through functions in this module.
Keeps Supabase query logic out of ingestion/processing/UI code.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from src.db.supabase_client import get_client


# ──────────────────────────────────────────────────────────────────────────────
# Sources
# ──────────────────────────────────────────────────────────────────────────────

def upsert_source(
    source_name: str,
    source_type: str,
    platform: str,
    ingestion_method: str,
) -> str:
    """
    Insert a source row if it doesn't exist, or return the existing id.
    Returns the UUID of the source row.
    """
    client = get_client()
    existing = (
        client.table("sources")
        .select("id")
        .eq("source_name", source_name)
        .limit(1)
        .execute()
    )
    if existing.data:
        return existing.data[0]["id"]

    result = (
        client.table("sources")
        .insert({
            "source_name": source_name,
            "source_type": source_type,
            "platform": platform,
            "ingestion_method": ingestion_method,
        })
        .execute()
    )
    return result.data[0]["id"]


def get_all_sources() -> List[Dict]:
    client = get_client()
    return client.table("sources").select("*").execute().data


# ──────────────────────────────────────────────────────────────────────────────
# Raw Documents
# ──────────────────────────────────────────────────────────────────────────────

def insert_raw_document(record: Dict[str, Any]) -> Optional[str]:
    """
    Insert a raw document row.
    Returns the new row UUID, or None if skipped (duplicate hash).

    Expected keys: source_id, external_id, title, body, author_name, rating,
                   review_date, country, language, url, app_version, metadata, raw_hash
    """
    client = get_client()

    # Check for exact hash duplicate
    dupe = (
        client.table("raw_documents")
        .select("id")
        .eq("raw_hash", record["raw_hash"])
        .limit(1)
        .execute()
    )
    if dupe.data:
        return None   # silently skip exact duplicates

    db_record = {
        k: v for k, v in record.items()
        if k not in ("source_name", "source_type", "platform", "ingestion_method")
    }

    result = client.table("raw_documents").insert(db_record).execute()
    if result.data:
        return result.data[0]["id"]
    return None


def get_raw_documents(
    source_name: Optional[str] = None,
    limit: int = 500,
    offset: int = 0,
) -> List[Dict]:
    client = get_client()
    query = client.table("raw_documents").select("*, sources(source_name, platform)")
    if source_name:
        # join filter via sources table
        source = client.table("sources").select("id").eq("source_name", source_name).execute()
        if source.data:
            query = query.eq("source_id", source.data[0]["id"])
    return query.range(offset, offset + limit - 1).execute().data


def count_raw_documents() -> int:
    client = get_client()
    result = client.table("raw_documents").select("id", count="exact").execute()
    return result.count or 0


# ──────────────────────────────────────────────────────────────────────────────
# Clean Documents
# ──────────────────────────────────────────────────────────────────────────────

def insert_clean_document(record: Dict[str, Any]) -> Optional[str]:
    """Insert a clean_document row. Returns new UUID or None on error."""
    client = get_client()
    result = client.table("clean_documents").insert(record).execute()
    if result.data:
        return result.data[0]["id"]
    return None


def get_unprocessed_raw_documents(limit: int = 200) -> List[Dict]:
    """Return raw_documents that have no corresponding clean_document yet."""
    client = get_client()
    # LEFT JOIN equivalent: get raw docs without a clean counterpart
    all_raw = (
        client.table("raw_documents")
        .select("id, body, source_id")
        .execute()
        .data
    )
    processed_ids = set(
        r["raw_document_id"]
        for r in client.table("clean_documents").select("raw_document_id").execute().data
    )
    unprocessed = [r for r in all_raw if r["id"] not in processed_ids]
    return unprocessed[:limit]


def count_clean_documents() -> int:
    client = get_client()
    result = client.table("clean_documents").select("id", count="exact").execute()
    return result.count or 0


def count_duplicates() -> int:
    client = get_client()
    result = (
        client.table("clean_documents")
        .select("id", count="exact")
        .eq("is_duplicate", True)
        .execute()
    )
    return result.count or 0


# ──────────────────────────────────────────────────────────────────────────────
# Themes & Segments
# ──────────────────────────────────────────────────────────────────────────────

def get_all_themes() -> List[Dict]:
    client = get_client()
    return client.table("themes").select("*").execute().data


def get_all_segments() -> List[Dict]:
    client = get_client()
    return client.table("user_segments").select("*").execute().data


def get_theme_by_code(code: str) -> Optional[Dict]:
    client = get_client()
    result = client.table("themes").select("*").eq("theme_code", code).limit(1).execute()
    return result.data[0] if result.data else None


def get_segment_by_code(code: str) -> Optional[Dict]:
    client = get_client()
    result = client.table("user_segments").select("*").eq("segment_code", code).limit(1).execute()
    return result.data[0] if result.data else None


def insert_document_theme(record: Dict[str, Any]) -> Optional[str]:
    client = get_client()
    result = client.table("document_themes").insert(record).execute()
    return result.data[0]["id"] if result.data else None


def insert_document_segment(record: Dict[str, Any]) -> Optional[str]:
    client = get_client()
    result = client.table("document_segments").insert(record).execute()
    return result.data[0]["id"] if result.data else None


# ──────────────────────────────────────────────────────────────────────────────
# Insights
# ──────────────────────────────────────────────────────────────────────────────

def upsert_insight(record: Dict[str, Any]) -> Optional[str]:
    client = get_client()
    result = (
        client.table("insights")
        .upsert(record, on_conflict="insight_title")
        .execute()
    )
    return result.data[0]["id"] if result.data else None


def get_all_insights(insight_type: Optional[str] = None) -> List[Dict]:
    client = get_client()
    query = client.table("insights").select("*").order("supporting_doc_count", desc=True)
    if insight_type:
        query = query.eq("insight_type", insight_type)
    return query.execute().data


# ──────────────────────────────────────────────────────────────────────────────
# Embeddings
# ──────────────────────────────────────────────────────────────────────────────

def insert_embedding(clean_document_id: str, embedding: List[float], model: str) -> Optional[str]:
    client = get_client()
    result = (
        client.table("embeddings")
        .upsert(
            {
                "clean_document_id": clean_document_id,
                "embedding": embedding,
                "embedding_model": model,
            },
            on_conflict="clean_document_id",
        )
        .execute()
    )
    return result.data[0]["id"] if result.data else None


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard / View helpers
# ──────────────────────────────────────────────────────────────────────────────

def get_source_counts() -> List[Dict]:
    """Pull from v_source_counts view."""
    client = get_client()
    return client.table("v_source_counts").select("*").execute().data


def get_theme_distribution() -> List[Dict]:
    client = get_client()
    return client.table("v_theme_distribution").select("*").execute().data


def get_segment_distribution() -> List[Dict]:
    client = get_client()
    return client.table("v_segment_distribution").select("*").execute().data


def get_segment_theme_matrix() -> List[Dict]:
    client = get_client()
    return client.table("v_segment_theme_matrix").select("*").execute().data


def get_review_explorer(
    source_name: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    country: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict]:
    client = get_client()
    query = client.table("v_review_explorer").select("*")
    if source_name:
        query = query.eq("source_name", source_name)
    if min_rating is not None:
        query = query.gte("rating", min_rating)
    if max_rating is not None:
        query = query.lte("rating", max_rating)
    if country:
        query = query.eq("country", country)
    return query.range(offset, offset + limit - 1).execute().data
