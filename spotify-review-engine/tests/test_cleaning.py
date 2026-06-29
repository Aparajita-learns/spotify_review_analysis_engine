"""
tests/test_cleaning.py
----------------------
Phase 3 — Tests for clean_text pipeline and language detection.
"""

import sys
from pathlib import Path

# Ensure project root is on path when running directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_clean_review_text_html():
    from src.process.clean_text import clean_review_text
    raw = "<p>This is a <b>great</b> app!</p>"
    clean, norm = clean_review_text(raw)
    
    assert clean == "This is a great app!"
    assert norm == "this is a great app"


def def_clean_review_text_whitespace():
    from src.process.clean_text import clean_review_text
    raw = "Too   much \n\n whitespace \t here."
    clean, norm = clean_review_text(raw)
    
    assert clean == "Too much whitespace here."
    assert norm == "too much whitespace here"


def test_clean_review_text_punctuation():
    from src.process.clean_text import clean_review_text
    raw = "Wait, what?! I can't believe it... #Spotify"
    clean, norm = clean_review_text(raw)
    
    assert clean == "Wait, what?! I can't believe it... #Spotify"
    # Note: the normalized version strips most punctuation but keeps alphanumeric
    assert "wait what i cant believe it spotify" in norm


def test_detect_language_english():
    from src.process.language import detect_language
    text = "The algorithm always plays the same songs over and over."
    lang = detect_language(text)
    assert lang == "en"


def test_detect_language_spanish():
    from src.process.language import detect_language
    text = "La aplicación siempre reproduce las mismas canciones una y otra vez."
    lang = detect_language(text)
    assert lang == "es"


def test_detect_language_too_short():
    from src.process.language import detect_language
    text = "hi"
    lang = detect_language(text)
    assert lang == "unknown"


if __name__ == "__main__":
    print("\n=== Phase 3: Cleaning Tests ===")
    
    test_clean_review_text_html()
    def_clean_review_text_whitespace()
    test_clean_review_text_punctuation()
    print("OK Text cleaning works")
    
    test_detect_language_english()
    test_detect_language_spanish()
    test_detect_language_too_short()
    print("OK Language detection works")
    
    print("=== All tests passed ===\n")
