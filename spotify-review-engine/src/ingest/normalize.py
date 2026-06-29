"""
src/ingest/normalize.py
-----------------------
Normalization contract enforcer.

Every ingestion module calls normalize_record() before inserting into the DB.
This guarantees a consistent shape regardless of the source platform.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.utils.dates import to_utc_iso
from src.utils.hashing import document_hash
from src.utils.validators import validate_normalized_record
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Controlled vocabulary — must match seeds.sql values
VALID_SOURCE_NAMES = {"app_store", "play_store", "reddit", "manual_social"}
VALID_SOURCE_TYPES = {"review", "discussion"}


def normalize_record(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalize a raw ingestion dict into the canonical DB shape.

    Required fields in raw:
        source_name, source_type, platform, ingestion_method, body

    Returns a dict ready for repository.insert_raw_document(), or None if invalid.
    """
    # ── Clean body ────────────────────────────────────────────────────────────
    body = str(raw.get("body") or "").strip()
    if not body:
        logger.warning("Skipping record with empty body (external_id=%s)", raw.get("external_id"))
        return None

    source_name = str(raw.get("source_name", "")).strip().lower()
    external_id = str(raw.get("external_id") or "").strip()

    # ── Compute stable hash ───────────────────────────────────────────────────
    raw_hash = document_hash(body, source_name, external_id)

    # ── Build normalized record ───────────────────────────────────────────────
    record: Dict[str, Any] = {
        "source_name":      source_name,
        "source_type":      str(raw.get("source_type", "review")).strip().lower(),
        "platform":         str(raw.get("platform", "")).strip(),
        "ingestion_method": str(raw.get("ingestion_method", "")).strip(),
        "external_id":      external_id or None,
        "title":            _safe_str(raw.get("title")),
        "body":             body,
        "author_name":      _safe_str(raw.get("author_name")),
        "rating":           _safe_rating(raw.get("rating")),
        "review_date":      to_utc_iso(raw.get("review_date")),
        "country":          _safe_str(raw.get("country")),
        "language":         _safe_str(raw.get("language")),
        "url":              _safe_str(raw.get("url")),
        "app_version":      _safe_str(raw.get("app_version")),
        "metadata":         raw.get("metadata") or {},
        "raw_hash":         raw_hash,
    }

    # ── Validate ──────────────────────────────────────────────────────────────
    is_valid, errors = validate_normalized_record(record)
    if not is_valid:
        logger.warning("Validation failed for record (hash=%s): %s", raw_hash[:8], errors)
        return None

    return record


# ──────────────────────────────────────────────────────────────────────────────
# Private helpers
# ──────────────────────────────────────────────────────────────────────────────

def _safe_str(value: Any) -> Optional[str]:
    """Return stripped string or None."""
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _safe_rating(value: Any) -> Optional[float]:
    """Return rating as float in [1, 5] or None."""
    if value is None:
        return None
    try:
        r = float(value)
        if 1.0 <= r <= 5.0:
            return r
        return None
    except (ValueError, TypeError):
        return None
