"""
app.py
------
Spotify Review Discovery Engine — Streamlit entry point.
Multi-page app routing all UI pages.
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Spotify Review Discovery Engine",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from src.db.supabase_client import ping

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #121212;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    /* Spotify green accent for metric labels */
    [data-testid="stMetricLabel"] {
        color: #1DB954 !important;
    }
    /* Card-like containers */
    .block-container {
        padding-top: 1.5rem;
    }
    /* Green divider */
    hr {
        border-color: #1DB954;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎵 Review Engine")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        options=[
            "📊 Overview",
            "⬇️  Ingestion",
            "⚙️  Data Pipeline",
            "🔍 Review Explorer",
            "💡 Insights & Themes",
            "💬 Ask the Reviews",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # DB connection health badge
    with st.spinner("Checking DB…"):
        db_ok = ping()
    if db_ok:
        st.success("🟢 Database connected")
    else:
        st.error("🔴 Database offline\nCheck your SUPABASE credentials.")

# ── Page routing ──────────────────────────────────────────────────────────────
if page == "📊 Overview":
    from src.ui.pages_overview import render
    render()

elif page == "⬇️  Ingestion":
    from src.ui.pages_ingestion import render
    render()

elif page == "⚙️  Data Pipeline":
    from src.ui.pages_pipeline import render
    render()

elif page == "🔍 Review Explorer":
    from src.ui.pages_explorer import render
    render()

elif page == "💡 Insights & Themes":
    from src.ui.pages_insights import render
    render()

elif page == "💬 Ask the Reviews":
    from src.ui.pages_ask import render
    render()
