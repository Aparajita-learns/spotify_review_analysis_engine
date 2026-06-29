"""
tests/test_dedupe.py
--------------------
Phase 3 — Tests for deduplication logic.
"""

import sys
from pathlib import Path

# Ensure project root is on path when running directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_find_near_duplicate_exact():
    from src.process.dedupe import find_near_duplicate
    
    existing = [
        {"id": "doc1", "normalized_text": "this is a very specific sentence about the app"},
        {"id": "doc2", "normalized_text": "another unrelated review here that talks about podcasts"}
    ]
    
    # Exact match
    new_text = "this is a very specific sentence about the app"
    dup_id = find_near_duplicate(new_text, existing)
    
    assert dup_id == "doc1", f"Expected doc1, got {dup_id}"


def test_find_near_duplicate_fuzzy():
    from src.process.dedupe import find_near_duplicate
    
    existing = [
        {"id": "doc1", "normalized_text": "this is a very specific sentence about the spotify algorithm"},
        {"id": "doc2", "normalized_text": "another unrelated review here that talks about podcasts"}
    ]
    
    import src.process.dedupe
    # Temporarily lower threshold just for this fuzzy test to guarantee a match
    original_threshold = src.process.dedupe.DEDUPE_COSINE_THRESHOLD
    src.process.dedupe.DEDUPE_COSINE_THRESHOLD = 0.7
    
    # Fuzzy match (minor typo / missing word)
    new_text = "this is a very specfic sentence about the spotify algoritm"
    dup_id = src.process.dedupe.find_near_duplicate(new_text, existing)
    
    src.process.dedupe.DEDUPE_COSINE_THRESHOLD = original_threshold
    
    assert dup_id == "doc1", f"Expected doc1, got {dup_id}"


def test_find_near_duplicate_unique():
    from src.process.dedupe import find_near_duplicate
    
    existing = [
        {"id": "doc1", "normalized_text": "this is a very specific sentence about the spotify algorithm"},
        {"id": "doc2", "normalized_text": "another unrelated review here that talks about podcasts"}
    ]
    
    # Totally unique
    new_text = "i really wish there was a way to reset my discovery weekly"
    dup_id = find_near_duplicate(new_text, existing)
    
    assert dup_id is None, f"Expected None, got {dup_id}"


def test_find_near_duplicate_too_short():
    from src.process.dedupe import find_near_duplicate
    
    existing = [
        {"id": "doc1", "normalized_text": "short"},
        {"id": "doc2", "normalized_text": "bad"}
    ]
    
    # Too short to reliably fuzzy match
    new_text = "short"
    dup_id = find_near_duplicate(new_text, existing)
    
    assert dup_id is None, "Should skip duplicate check for very short text"


if __name__ == "__main__":
    print("\n=== Phase 3: Dedupe Tests ===")
    
    test_find_near_duplicate_exact()
    test_find_near_duplicate_fuzzy()
    test_find_near_duplicate_unique()
    test_find_near_duplicate_too_short()
    
    print("OK Deduplication logic works")
    print("=== All tests passed ===\n")
