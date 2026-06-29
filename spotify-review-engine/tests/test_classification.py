"""
tests/test_classification.py
----------------------------
Phase 4 — Tests for theme and segment heuristic classification.
"""

import sys
from pathlib import Path

# Ensure project root is on path when running directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_classify_document_heuristics():
    from src.process.classify_themes import classify_document_heuristics
    
    # 1. Loop/Repetitive
    text1 = "The algorithm just repeats the same songs over and over."
    themes1 = classify_document_heuristics(text1)
    assert "repetitive_recommendations" in themes1, themes1
    
    # 2. Reset / Explain
    text2 = "I want to reset my recommendations and understand why it picked this."
    themes2 = classify_document_heuristics(text2)
    assert "reset_recommendations" in themes2, themes2
    assert "explainability" in themes2, themes2
    
    # 3. No match
    text3 = "This is a great app."
    themes3 = classify_document_heuristics(text3)
    assert len(themes3) == 0, themes3


def test_classify_user_segment():
    from src.process.segment_users import classify_user_segment
    
    # 1. Passive
    text1 = "I just play the radio in the background while working."
    segs1 = classify_user_segment(text1)
    assert "passive_consumers" in segs1, segs1
    
    # 2. Active
    text2 = "I am always digging for underground new music."
    segs2 = classify_user_segment(text2)
    assert "active_seekers" in segs2, segs2
    
    # 3. Frustrated
    text3 = "I cant find anything good, it sucks."
    segs3 = classify_user_segment(text3)
    assert "frustrated_explorers" in segs3, segs3


if __name__ == "__main__":
    print("\n=== Phase 4: Classification Tests ===")
    
    test_classify_document_heuristics()
    print("OK Theme classification works")
    
    test_classify_user_segment()
    print("OK User segmentation works")
    
    print("=== All tests passed ===\n")
