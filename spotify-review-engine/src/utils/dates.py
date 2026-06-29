"""
src/utils/dates.py
------------------
Date/time normalization helpers.
All timestamps stored in DB must be ISO 8601 UTC strings.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional


def to_utc_iso(value: object) -> Optional[str]:
    """
    Convert various date representations to ISO 8601 UTC string.
    Accepts: datetime, unix timestamp (int/float), ISO string, or None.
    Returns None if value cannot be parsed.
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        dt = value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
        except (OSError, OverflowError, ValueError):
            return None

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        # Try common ISO formats
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(value, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc).isoformat()
            except ValueError:
                continue
        return None

    return None


def now_utc_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(tz=timezone.utc).isoformat()
