"""
src/ui/pages_ask.py
-------------------
Semantic search interface to query the review database using natural language.
"""

import streamlit as st
import pandas as pd
from src.process.generate_embeddings import semantic_search
from src.utils.llm import summarize_reviews

def render():
    st.title("💬 Ask the Reviews")
    st.markdown("---")
    
    st.markdown("Ask natural language questions about the user feedback. The engine uses vector embeddings to find the most conceptually relevant reviews, even if they don't share exact keywords.")
    
    query = st.text_input("What do you want to know?", placeholder="e.g., Why do users hate the new UI?")
    
    limit = st.number_input("Max Results", min_value=1, max_value=50, value=5)
    threshold = 0.10  # Hardcoded default
                              
    if st.button("Search", type="primary"):
        if not query.strip():
            st.warning("Please enter a question.")
            return
            
        with st.spinner("Searching semantic index..."):
            try:
                results = semantic_search(query, limit=limit, threshold=threshold)
                
                if not results:
                    st.info("No matching reviews found. Try lowering the similarity threshold or rephrasing your question.")
                else:
                    st.success(f"Found {len(results)} relevant reviews.")
                    
                    # 1. AI Synthesized Answer
                    with st.spinner("Synthesizing answer with Gemini..."):
                        summary = summarize_reviews(query, results)
                    
                    st.info(summary)
                    
                    st.markdown("### Source Reviews")
                    
                    # 2. Raw Source Results
                    for i, res in enumerate(results):
                        with st.container():
                            st.markdown(f"**Result {i+1}** (Similarity: `{res['similarity']:.3f}`)")
                            st.markdown(f"> {res['clean_text']}")
                            st.caption(f"Document ID: {res['clean_document_id']}")
                            st.markdown("---")
            except Exception as e:
                st.error(f"Error during search: {e}")
                st.info("Have you generated embeddings yet? Make sure you ran the migration script in Supabase and clicked 'Generate Embeddings' on the Pipeline page.")
