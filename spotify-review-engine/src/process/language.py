"""
src/process/language.py
-----------------------
Language detection using langdetect.
"""

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Enforce consistent results across runs
DetectorFactory.seed = 42

def detect_language(text: str) -> str:
    """
    Detect the language of the provided text.
    Returns the ISO 639-1 language code (e.g., 'en', 'es', 'fr'),
    or 'unknown' if detection fails or text is too short.
    """
    if not text or len(text.strip()) < 5:
        return "unknown"
        
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return "unknown"
