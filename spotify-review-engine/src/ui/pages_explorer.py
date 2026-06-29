"""
src/ui/pages_explorer.py
------------------------
Review Explorer dashboard to filter and search through processed reviews.
"""

import streamlit as st
import pandas as pd
from src.db.repository import get_client


def render():
    st.title("🔍 Review Explorer")
    st.markdown("---")
    
    st.markdown("Search and filter through all cleaned and classified reviews.")
    
    # We will query raw_documents joined with clean_documents, document_themes, and themes
    client = get_client()
    
    # ── Filters ──
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sources_res = client.table("sources").select("source_name").execute()
        available_sources = list(set([s["source_name"] for s in (sources_res.data or [])]))
        selected_source = st.selectbox("Source", ["All"] + available_sources)
        
    with col2:
        themes_res = client.table("themes").select("theme_name").execute()
        available_themes = [t["theme_name"] for t in (themes_res.data or [])]
        selected_theme = st.selectbox("Theme", ["All"] + available_themes)
        
    with col3:
        search_query = st.text_input("Keyword Search (body text)")
        
    st.markdown("---")
    
    # ── Fetch Data ──
    # Note: For MVP we do a basic pull and filter in pandas for flexibility,
    # in production with millions of rows this would be purely SQL/RPC.
    
    with st.spinner("Loading reviews..."):
        # We query the view or join manually. Supabase REST joins can be tricky, 
        # so let's pull clean_documents with their raw_document and themes
        query = client.table("clean_documents").select(
            "id, clean_text, is_duplicate, raw_documents(source_id, rating, review_date, url, sources(source_name)), document_themes(themes(theme_name))"
        ).eq("is_duplicate", False).limit(1000)
        
        res = query.execute()
        docs = res.data or []
        
        if not docs:
            st.info("No processed reviews found. Make sure you have run the Ingestion, Cleaning, and Classification pipelines.")
            return
            
        # Flatten the nested JSON for pandas
        flat_docs = []
        for d in docs:
            raw = d.get("raw_documents") or {}
            source = raw.get("sources") or {}
            
            # Extract themes
            themes = []
            for dt in (d.get("document_themes") or []):
                if dt.get("themes"):
                    themes.append(dt["themes"]["theme_name"])
            
            flat_docs.append({
                "source": source.get("source_name", "unknown"),
                "rating": raw.get("rating"),
                "date": raw.get("review_date")[:10] if raw.get("review_date") else None,
                "text": d.get("clean_text", ""),
                "themes": ", ".join(themes) if themes else "Uncategorized"
            })
            
        df = pd.DataFrame(flat_docs)
        
        # Apply filters
        if selected_source != "All":
            df = df[df["source"] == selected_source]
            
        if selected_theme != "All":
            # Using contains since a doc might have multiple themes
            df = df[df["themes"].str.contains(selected_theme, na=False, regex=False)]
            
        if search_query:
            df = df[df["text"].str.contains(search_query, case=False, na=False)]
            
        st.subheader(f"Results ({len(df)})")
        
        if len(df) == 0:
            st.warning("No reviews match your filters.")
        else:
            st.dataframe(
                df,
                column_config={
                    "source": "Platform",
                    "rating": st.column_config.NumberColumn("Rating", format="⭐ %d"),
                    "date": "Date",
                    "text": st.column_config.TextColumn("Review Text", width="large"),
                    "themes": "Themes"
                },
                hide_index=True,
                use_container_width=True
            )
