"""
tests/test_db_connection.py
---------------------------
Phase 1 smoke test: verifies the Supabase connection and confirms that
all required tables exist.

Run with:
    python -m pytest tests/test_db_connection.py -v
or simply:
    python tests/test_db_connection.py
"""

import sys
from pathlib import Path

# Ensure project root is on path when running directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


REQUIRED_TABLES = [
    "sources",
    "raw_documents",
    "clean_documents",
    "themes",
    "document_themes",
    "user_segments",
    "document_segments",
    "insights",
    "embeddings",
]


def test_supabase_ping():
    """Test that the Supabase client can connect."""
    from src.db.supabase_client import ping
    assert ping(), (
        "Supabase ping failed. Check SUPABASE_URL and SUPABASE_KEY in your .env file."
    )
    print("✓ Supabase connection OK")


def test_required_tables_exist():
    """Test that all schema tables have been created in Supabase."""
    from src.db.supabase_client import get_client
    client = get_client()

    missing = []
    for table in REQUIRED_TABLES:
        try:
            result = client.table(table).select("id").limit(1).execute()
            print(f"✓ Table '{table}' exists ({len(result.data)} rows sampled)")
        except Exception as exc:
            print(f"✗ Table '{table}' NOT found: {exc}")
            missing.append(table)

    assert not missing, (
        f"Missing tables: {missing}\n"
        f"Run schema.sql in your Supabase SQL Editor to create them."
    )


def test_taxonomy_seeded():
    """Test that themes and user_segments have been seeded."""
    from src.db.supabase_client import get_client
    client = get_client()

    themes = client.table("themes").select("id").execute()
    assert len(themes.data) > 0, (
        "No themes found. Run seeds.sql in your Supabase SQL Editor."
    )
    print(f"✓ {len(themes.data)} themes seeded")

    segments = client.table("user_segments").select("id").execute()
    assert len(segments.data) > 0, (
        "No user_segments found. Run seeds.sql in your Supabase SQL Editor."
    )
    print(f"✓ {len(segments.data)} user segments seeded")


def test_taxonomy_module():
    """Test that the local taxonomy module loads correctly."""
    from src.config.taxonomy import THEMES, USER_SEGMENTS, THEME_CODES, SEGMENT_CODES
    assert len(THEMES) == 11, f"Expected 11 themes, got {len(THEMES)}"
    assert len(USER_SEGMENTS) == 5, f"Expected 5 segments, got {len(USER_SEGMENTS)}"
    print(f"✓ Taxonomy module: {len(THEMES)} themes, {len(USER_SEGMENTS)} segments loaded")


def test_hashing_utility():
    """Test that the hashing utility produces stable, unique hashes."""
    from src.utils.hashing import document_hash
    h1 = document_hash("Great app!", "play_store", "abc123")
    h2 = document_hash("Great app!", "play_store", "abc123")
    h3 = document_hash("Different review", "play_store", "xyz999")
    assert h1 == h2, "Hash is not deterministic"
    assert h1 != h3, "Different content should produce different hash"
    print("✓ Hashing utility: stable and collision-resistant")


def test_date_normalization():
    """Test that date normalization handles common formats."""
    from src.utils.dates import to_utc_iso
    from datetime import datetime, timezone

    # Unix timestamp
    assert to_utc_iso(0) == "1970-01-01T00:00:00+00:00"
    # ISO string
    result = to_utc_iso("2024-06-15T12:00:00")
    assert "2024-06-15" in result
    # None
    assert to_utc_iso(None) is None
    print("✓ Date normalization: all formats convert correctly")


if __name__ == "__main__":
    print("\n=== Spotify Review Engine — Phase 1 Smoke Tests ===\n")
    tests = [
        test_taxonomy_module,
        test_hashing_utility,
        test_date_normalization,
        test_supabase_ping,
        test_required_tables_exist,
        test_taxonomy_seeded,
    ]
    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as exc:
            print(f"✗ {test_fn.__name__} FAILED: {exc}")
            failed += 1

    print(f"\n=== Results: {passed} passed, {failed} failed ===\n")
    sys.exit(0 if failed == 0 else 1)
