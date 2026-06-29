"""
src/config/settings.py
----------------------
Centralized configuration loader.
Reads all environment variables from .env (local) or Streamlit secrets (cloud).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file when running locally
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path, override=False)


def _require(key: str) -> str:
    """Return env var or raise a clear error if missing."""
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Copy .env.example → .env and fill in your credentials."
        )
    return val


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# ──────────────────────────────────────────────
# Supabase (required)
# ──────────────────────────────────────────────
SUPABASE_URL: str = _require("SUPABASE_URL")
SUPABASE_KEY: str = _require("SUPABASE_KEY")

# ──────────────────────────────────────────────
# LLM APIs (optional — needed in Phase 4+)
# ──────────────────────────────────────────────
OPENAI_API_KEY: str = _optional("OPENAI_API_KEY")
ANTHROPIC_API_KEY: str = _optional("ANTHROPIC_API_KEY")

# ──────────────────────────────────────────────
# Reddit API (optional — fallback to public JSON if missing)
# ──────────────────────────────────────────────
REDDIT_CLIENT_ID: str = _optional("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET: str = _optional("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT: str = _optional("REDDIT_USER_AGENT", "spotify-review-engine/0.1")

# ──────────────────────────────────────────────
# App-level constants
# ──────────────────────────────────────────────
SPOTIFY_APP_ID = "com.spotify.music"          # Google Play app ID
SPOTIFY_APPLE_ID = "324684580"                # Apple App Store app ID

PLAY_STORE_COUNTRIES = ["us", "in", "gb"]
APP_STORE_COUNTRIES = ["us", "gb", "in"]

REDDIT_KEYWORDS = [
    "spotify recommendations",
    "spotify same songs",
    "spotify discover weekly bad",
    "spotify not discovering music",
    "spotify repeats songs",
    "spotify algorithm bad",
    "spotify keeps playing same music",
]

DEDUPE_COSINE_THRESHOLD = 0.92   # TF-IDF cosine similarity threshold for near-dupe
DEDUPE_LEVENSHTEIN_THRESHOLD = 0.90

EMBEDDING_MODEL = "text-embedding-3-small"   # OpenAI model; update for other providers
EMBEDDING_DIM = 1536

TOP_K_RETRIEVAL = 10   # number of semantic search results to retrieve

SUPPORTED_LANGUAGES = ["en"]   # MVP: English only; extend in later phases
