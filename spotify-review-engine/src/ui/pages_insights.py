"""
src/ui/pages_insights.py
------------------------
Displays actionable PM insights aggregated from the underlying classification data.
"""

import streamlit as st
import pandas as pd
from src.db.repository import get_client
from src.process.aggregate_insights import generate_insights

def render():
    st.title("💡 Strategic Insights")
    st.markdown("---")
    
    st.markdown("High-level product management insights aggregated from the underlying thematic and behavioral data.")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 Generate Latest Insights", type="primary", use_container_width=True):
            with st.spinner("Aggregating classifications..."):
                res = generate_insights()
                st.success(f"Generated {res['insights_generated']} new insights.")
                
    client = get_client()
    
    # Fetch insights
    res = client.table("insights").select("*").order("supporting_doc_count", desc=True).execute()
    insights_data = res.data or []
    
    if not insights_data:
        st.info("No insights found. Click 'Generate Latest Insights' to aggregate data, or ensure you have run the Pipeline.")
        return
        
    # Ensure "Repetitive Recommendations" is always pinned to the very top
    pinned_idx = None
    for i, insight in enumerate(insights_data):
        if "Repetitive Recommendations" in insight["insight_title"]:
            pinned_idx = i
            break
            
    if pinned_idx is not None and pinned_idx > 0:
        pinned_insight = insights_data.pop(pinned_idx)
        insights_data.insert(0, pinned_insight)
        
    st.markdown("### Top Aggregated Insights")
    
    # Display cards
    for insight in insights_data:
        # Determine color/icon based on type
        icon = "📌"
        if insight["insight_type"] == "friction":
            icon = "⚠️"
        elif insight["insight_type"] == "behavior":
            icon = "👤"
            
        with st.container():
            st.subheader(f"{icon} {insight['insight_title']}")
            st.caption(f"**Type:** {insight['insight_type'].capitalize()}  |  **Supporting Evidence:** {insight['supporting_doc_count']} reviews")
            st.markdown(insight["insight_summary"])
            st.markdown("---")
