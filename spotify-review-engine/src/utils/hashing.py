"""
src/utils/hashing.py
--------------------
Deterministic hash functions for deduplication.
"""

import hashlib


def sha256_hash(text: str) -> str:
    """
    Return the SHA-256 hex digest of the given text.
    Used to compute raw_hash for deduplication checks.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def document_hash(body: str, source_name: str, external_id: str = "") -> str:
    """
    Compute the canonical raw_hash for a document:
        sha256(normalized_body + "|" + source_name + "|" + external_id)

    If external_id is empty or None, it is replaced with a hash of the body
    to still produce a stable, collision-resistant identifier.
    """
    body_clean = " ".join(body.lower().split())
    ext_id = external_id.strip() if external_id else sha256_hash(body_clean)[:16]
    raw = f"{body_clean}|{source_name}|{ext_id}"
    return sha256_hash(raw)
