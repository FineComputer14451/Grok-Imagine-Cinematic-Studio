"""Shared Streamlit styling for Cinematic Studio Web UI (Grok 4.5)."""

from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
<style>
    .main { background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%); }
    .stApp { color: #e0e0ff; }
    .stButton>button {
        background: linear-gradient(90deg, #6a00ff, #00d4ff);
        color: white; border: none; border-radius: 12px;
        padding: 12px 28px; font-weight: 600; transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: scale(1.03); box-shadow: 0 0 18px #00d4ff88; }
    .section-header { color: #00d4ff; margin-top: 1rem; }
    .stack-badge {
        display: inline-block;
        background: linear-gradient(90deg, #5b21b6, #0891b2);
        color: #f0f9ff;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        margin: 0.25rem 0 0.5rem 0;
    }
    .stack-card {
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        background: rgba(15, 23, 42, 0.65);
        margin-bottom: 0.75rem;
    }
    .stack-card h4 { margin: 0 0 0.35rem 0; color: #67e8f9; font-size: 0.95rem; }
    .stack-card p { margin: 0; color: #cbd5e1; font-size: 0.85rem; }
    div[data-testid="stMetricValue"] { color: #e2e8f0; }
</style>
""",
        unsafe_allow_html=True,
    )
