"""
src/db/supabase_client.py
-------------------------
Singleton Supabase client.
Call get_client() anywhere in the codebase to obtain a connected client.
"""

import os
from functools import lru_cache
from supabase import create_client, Client
from src.config.settings import SUPABASE_URL, SUPABASE_KEY


@lru_cache(maxsize=1)
def get_client() -> Client:
    """
    Return a cached Supabase client instance.

    The client is created once and reused for the lifetime of the process.
    In Streamlit Cloud, SUPABASE_URL and SUPABASE_KEY come from st.secrets.
    Locally they come from .env.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise EnvironmentError(
            "SUPABASE_URL and SUPABASE_KEY must be set. "
            "Copy .env.example → .env and fill in your credentials."
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def ping() -> bool:
    """
    Quick connection check — returns True if the DB responds.
    Used by the smoke test and Streamlit health badge.
    """
    try:
        client = get_client()
        # A minimal query that returns fast
        client.table("sources").select("id").limit(1).execute()
        return True
    except Exception as exc:
        print(f"[supabase_client] ping failed: {exc}")
        return False
