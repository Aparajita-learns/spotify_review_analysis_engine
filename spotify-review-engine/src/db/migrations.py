"""
src/db/migrations.py
--------------------
Utility to apply schema.sql and seeds.sql via the Supabase REST API.

Usage (run once to bootstrap a fresh Supabase project):
    python -m src.db.migrations

Requires SUPABASE_URL and SUPABASE_KEY in your .env.
"""

import sys
from pathlib import Path

from src.db.supabase_client import get_client


SQL_DIR = Path(__file__).resolve().parents[2] / "sql"


def _run_sql(sql: str, label: str) -> None:
    """Execute raw SQL against Supabase using the postgres REST endpoint."""
    client = get_client()
    try:
        # Supabase Python client v2 supports rpc for raw SQL via postgrest-py
        client.rpc("exec_sql", {"sql": sql}).execute()
        print(f"[migrations] ✓ {label}")
    except Exception as exc:
        # Fallback: print instructions if exec_sql RPC is not available
        print(
            f"[migrations] ⚠  Could not auto-apply {label} via RPC: {exc}\n"
            f"  → Please run the SQL manually in your Supabase SQL Editor.\n"
            f"  → File: {SQL_DIR / label}"
        )


def apply_schema() -> None:
    schema_sql = (SQL_DIR / "schema.sql").read_text(encoding="utf-8")
    _run_sql(schema_sql, "schema.sql")


def apply_seeds() -> None:
    seeds_sql = (SQL_DIR / "seeds.sql").read_text(encoding="utf-8")
    _run_sql(seeds_sql, "seeds.sql")


def apply_views() -> None:
    views_sql = (SQL_DIR / "views.sql").read_text(encoding="utf-8")
    _run_sql(views_sql, "views.sql")


def run_all() -> None:
    print("[migrations] Applying all migrations…")
    apply_schema()
    apply_seeds()
    apply_views()
    print("[migrations] Done.")


if __name__ == "__main__":
    run_all()
