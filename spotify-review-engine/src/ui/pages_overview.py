"""
src/ui/pages_overview.py
------------------------
Overview dashboard — Phase 1 stub.
Shows DB connectivity status and taxonomy summary.
Full metrics will render once ingestion (Phase 2) and processing (Phase 3) are complete.
"""

import streamlit as st


def render():
    st.title("📊 Overview")
    st.markdown("---")

    st.info(
        "**Phase 1 complete.** Database schema, taxonomy, and utilities are initialized. "
        "Proceed to **Ingestion** to start loading reviews.",
        icon="✅",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Raw Documents", "—", help="Available after Phase 2 ingestion")
    with col2:
        st.metric("Clean Documents", "—", help="Available after Phase 3 processing")
    with col3:
        st.metric("Duplicates Removed", "—", help="Available after Phase 3 deduplication")

    st.markdown("---")
    st.subheader("System Status")

    from src.db.supabase_client import ping
    from src.config.taxonomy import THEMES, USER_SEGMENTS

    db_status = "🟢 Connected" if ping() else "🔴 Offline"
    st.write(f"**Database:** {db_status}")
    st.write(f"**Taxonomy loaded:** {len(THEMES)} themes · {len(USER_SEGMENTS)} user segments")
    st.write("**Ingestion sources:** Play Store · App Store · Reddit · Manual CSV")
