"""
src/utils/validators.py
-----------------------
Input validation helpers for ingestion records.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

REQUIRED_FIELDS = ["body", "source_name", "source_type", "platform", "ingestion_method"]
CONTROLLED_SOURCE_NAMES = {"app_store", "play_store", "reddit", "manual_social"}
CONTROLLED_SOURCE_TYPES = {"review", "discussion"}


def validate_normalized_record(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a normalized ingestion record before DB insertion.

    Returns:
        (is_valid: bool, errors: list[str])
    """
    errors: List[str] = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if not record.get(field):
            errors.append(f"Missing required field: '{field}'")

    # body must be non-empty string
    body = record.get("body", "")
    if isinstance(body, str) and len(body.strip()) < 3:
        errors.append("'body' is too short (minimum 3 characters after strip)")

    # Controlled vocabulary checks
    source_name = record.get("source_name", "")
    if source_name and source_name not in CONTROLLED_SOURCE_NAMES:
        errors.append(
            f"Invalid source_name '{source_name}'. "
            f"Must be one of: {sorted(CONTROLLED_SOURCE_NAMES)}"
        )

    source_type = record.get("source_type", "")
    if source_type and source_type not in CONTROLLED_SOURCE_TYPES:
        errors.append(
            f"Invalid source_type '{source_type}'. "
            f"Must be one of: {sorted(CONTROLLED_SOURCE_TYPES)}"
        )

    # Rating range
    rating = record.get("rating")
    if rating is not None:
        try:
            r = float(rating)
            if not (1.0 <= r <= 5.0):
                errors.append(f"'rating' must be between 1 and 5, got {r}")
        except (ValueError, TypeError):
            errors.append(f"'rating' must be numeric, got {rating!r}")

    is_valid = len(errors) == 0
    return is_valid, errors
