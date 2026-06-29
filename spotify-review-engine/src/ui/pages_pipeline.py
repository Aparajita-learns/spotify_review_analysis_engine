"""
src/ui/pages_pipeline.py
------------------------
Processing pipeline control dashboard.
Allows triggering data cleaning, deduplication, and classification.
"""

import streamlit as st
import pandas as pd
from src.process.dedupe import process_raw_documents
from src.process.classify_themes import process_themes
from src.process.segment_users import process_segments
from src.db.repository import get_client


def render():
    st.title("⚙️ Data Processing Pipeline")
    st.markdown("---")
    
    st.markdown("""
    Once data is ingested into the raw tables, it must pass through the NLP processing pipelines 
    before it appears in the Explorer or Insights dashboards.
    """)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.subheader("1. Clean & Deduplicate")
        st.caption("Strips HTML, normalizes text, detects language, and runs TF-IDF fuzzy deduplication.")
        batch_size = st.number_input("Batch Size (Clean)", min_value=10, max_value=2000, value=200, step=100)
        if st.button("Run Cleaning Pipeline", type="primary"):
            with st.spinner("Processing raw documents..."):
                res = process_raw_documents(batch_size=batch_size)
                st.success(f"✅ Processed {res['processed']} documents. Found {res['duplicates']} duplicates. Errors: {res['errors']}")

    with col2:
        st.subheader("2. Classify Themes")
        st.caption("Runs heuristic/regex keyword matching to assign reviews to the 13 PM themes.")
        theme_limit = st.number_input("Batch Size (Themes)", min_value=10, max_value=2000, value=500, step=100)
        if st.button("Run Theme Classifier", type="primary"):
            with st.spinner("Classifying themes..."):
                res = process_themes(limit=theme_limit)
                st.success(f"✅ Processed {res['processed']} documents. Assigned {res['themes_assigned']} themes.")

    with col3:
        st.subheader("3. Segment Users")
        st.caption("Maps review text to the 5 distinct user personas defined in the taxonomy.")
        seg_limit = st.number_input("Batch Size (Segments)", min_value=10, max_value=2000, value=500, step=100)
        if st.button("Run Segmenter", type="primary"):
            with st.spinner("Assigning segments..."):
                res = process_segments(limit=seg_limit)
                st.success(f"✅ Processed {res['processed']} documents. Assigned {res['segments_assigned']} segments.")

    with col4:
        st.subheader("4. Aggregate Insights")
        st.caption("Analyzes the classified themes and segments to generate high-level PM insights.")
        if st.button("Generate Insights", type="primary"):
            with st.spinner("Aggregating data..."):
                from src.process.aggregate_insights import generate_insights
                res = generate_insights()
                st.success(f"✅ Generated {res['insights_generated']} strategic insights.")

    with col5:
        st.subheader("5. Generate Embeddings")
        st.caption("Computes vector embeddings for clean text using sentence-transformers (384-dim).")
        embed_limit = st.number_input("Batch Size (Embed)", min_value=10, max_value=2000, value=50, step=10)
        if st.button("Generate Embeddings", type="primary"):
            with st.spinner("Computing embeddings locally..."):
                from src.process.generate_embeddings import generate_embeddings
                res = generate_embeddings(batch_size=embed_limit)
                st.success(f"✅ Processed {res['processed']} docs. Inserted {res['inserted']} embeddings.")

    st.markdown("---")
    st.subheader("Database Status")
    
    # Show counts
    client = get_client()
    raw_count = client.table("raw_documents").select("id", count="exact").execute().count
    clean_count = client.table("clean_documents").select("id", count="exact").execute().count
    theme_count = client.table("document_themes").select("id", count="exact").execute().count
    seg_count = client.table("document_segments").select("id", count="exact").execute().count
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Raw Records", raw_count)
    m2.metric("Clean Records", clean_count)
    m3.metric("Theme Assignments", theme_count)
    m4.metric("Segment Assignments", seg_count)
