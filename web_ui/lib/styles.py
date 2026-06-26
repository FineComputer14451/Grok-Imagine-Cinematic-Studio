"""Shared Streamlit styling for Cinematic Studio Web UI."""

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
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 0 20px #00d4ff; }
    .section-header { color: #00d4ff; margin-top: 1rem; }
</style>
""",
        unsafe_allow_html=True,
    )