"""
src/ui/pages_overview.py
------------------------
Overview dashboard showing high-level system health and ingestion metrics.
"""

import streamlit as st
from src.db.supabase_client import ping, get_client
from src.config.taxonomy import THEMES, USER_SEGMENTS

def render():
    st.title("📊 Overview")
    st.markdown("---")

    st.markdown(
        "Welcome to the **Spotify Review Discovery Engine**. This system automatically ingests, cleans, "
        "classifies, and semantically indexes user feedback from across the web."
    )

    # Fetch real metrics from the DB
    with st.spinner("Loading metrics..."):
        client = get_client()
        try:
            raw_count = client.table("raw_documents").select("id", count="exact").execute().count
            clean_count = client.table("clean_documents").select("id", count="exact").execute().count
            embeddings_count = client.table("embeddings").select("id", count="exact").execute().count
        except Exception:
            raw_count, clean_count, embeddings_count = 0, 0, 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Raw Documents", f"{raw_count:,}")
    with col2:
        st.metric("Clean Documents", f"{clean_count:,}")
    with col3:
        st.metric("Vector Embeddings", f"{embeddings_count:,}")

    st.markdown("---")
    st.subheader("System Status")

    db_status = "🟢 Connected" if ping() else "🔴 Offline"
    st.write(f"**Database:** {db_status}")
    st.write(f"**Taxonomy loaded:** {len(THEMES)} themes · {len(USER_SEGMENTS)} user segments")
    st.write("**Capabilities:** Ingestion · NLP Cleaning · RAG Semantic Search · Theme Insights")

