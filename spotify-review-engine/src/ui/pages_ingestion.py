"""
src/ui/pages_ingestion.py
-------------------------
Ingestion control dashboard.
Allows triggering data pulls from Play Store, App Store, Reddit, and manual CSVs.
"""

import streamlit as st
import pandas as pd
from src.ingest.play_store_ingest import ingest_play_store
from src.ingest.app_store_ingest import ingest_app_store
from src.ingest.reddit_ingest import ingest_reddit
from src.ingest.manual_import import ingest_csv
from src.db.repository import get_source_counts


def render():
    st.title("⬇️ Ingestion Controls")
    st.markdown("---")
    
    st.markdown("Pull raw reviews and discussions from public sources. Duplicates (by content and source ID) will be automatically skipped.")
    
    tabs = st.tabs(["🎮 Play Store", "🍎 App Store", "🤖 Reddit", "📁 CSV Upload"])
    
    with tabs[0]:
        st.subheader("Google Play Store Reviews")
        count = st.slider("Reviews per country to fetch (Play Store)", 10, 500, 100, step=10)
        if st.button("Run Play Store Ingestion", type="primary"):
            with st.spinner("Fetching Play Store reviews..."):
                res = ingest_play_store(count_per_country=count)
                _show_result(res)

    with tabs[1]:
        st.subheader("Apple App Store Reviews")
        pages = st.slider("RSS Pages per country (1 page = 50 reviews)", 1, 10, 1)
        if st.button("Run App Store Ingestion", type="primary"):
            with st.spinner("Fetching App Store reviews..."):
                res = ingest_app_store(pages_per_country=pages)
                _show_result(res)

    with tabs[2]:
        st.subheader("Reddit Discussions")
        limit = st.slider("Max posts per keyword", 5, 100, 25, step=5)
        if st.button("Run Reddit Ingestion", type="primary"):
            with st.spinner("Fetching Reddit discussions..."):
                res = ingest_reddit(limit_per_keyword=limit)
                _show_result(res)

    with tabs[3]:
        st.subheader("Manual CSV Upload")
        st.markdown("""
        **Required columns:** `body`
        **Optional columns:** `source_name`, `source_type`, `platform`, `external_id`, `title`, `author_name`, `rating`, `review_date`, `country`, `language`, `url`, `app_version`
        """)
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head(3))
            if st.button("Ingest CSV", type="primary"):
                with st.spinner("Processing CSV..."):
                    res = ingest_csv(df)
                    _show_result(res)

    st.markdown("---")
    st.subheader("Current Database Counts")
    _render_counts()


def _show_result(res: dict):
    if res["inserted"] > 0:
        st.success(f"✅ Successfully inserted {res['inserted']} new records.")
    if res["skipped"] > 0:
        st.info(f"⏭️ Skipped {res['skipped']} exact duplicates.")
    if res["errors"] > 0:
        st.error(f"⚠️ Encountered {res['errors']} errors during processing.")
    if res["inserted"] == 0 and res["skipped"] == 0 and res["errors"] == 0:
        st.warning("No records processed.")


def _render_counts():
    counts = get_source_counts()
    if not counts:
        st.info("No data in the database yet.")
        return
        
    df = pd.DataFrame(counts)
    st.dataframe(
        df,
        column_config={
            "source_name": "Source",
            "platform": "Platform",
            "total_raw": st.column_config.NumberColumn("Total Raw", help="Records ingested"),
            "total_clean": st.column_config.NumberColumn("Total Clean", help="Records processed"),
            "duplicates": st.column_config.NumberColumn("Duplicates", help="Found duplicates"),
            "last_ingested_at": st.column_config.DatetimeColumn("Last Ingestion", format="YYYY-MM-DD HH:mm"),
        },
        hide_index=True,
        use_container_width=True
    )
