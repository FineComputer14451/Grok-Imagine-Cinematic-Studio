#!/usr/bin/env python3
"""
Grok Imagine Cinematic Studio — Streamlit Web UI (multi-page, Grok 4.5).
"""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt
from lib import session as sess
from lib.styles import apply_styles
from pages import dashboard, dna, imagine, nsfw, production, quota, sequences, settings, tools

sess.init_session_defaults()

st.set_page_config(
    page_title=f"Grok Imagine Cinematic Studio v{rt.STUDIO_VERSION}",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()

with st.sidebar:
    st.markdown(f"### 🎥 Cinematic Studio v{rt.STUDIO_VERSION}")
    st.caption(
        f"{rt.core_agent_count()}-agent production · DNA · Sequences · Quota · Grok **4.5**"
    )
    rt.render_sidebar_stack()

pages = [
    st.Page(dashboard.render, title="Dashboard", icon="📊", url_path="dashboard", default=True),
    st.Page(production.render, title="Production", icon="📝", url_path="production"),
    st.Page(dna.render, title="DNA & Memory", icon="🧬", url_path="dna"),
    st.Page(sequences.render, title="Sequences", icon="🎬", url_path="sequences"),
    st.Page(imagine.render, title="Imagine", icon="✨", url_path="imagine"),
    st.Page(quota.render, title="Quota", icon="💰", url_path="quota"),
    st.Page(tools.render, title="Tools", icon="🛠️", url_path="tools"),
    st.Page(settings.render, title="Settings", icon="⚙️", url_path="settings"),
]
if st.session_state.get("nsfw_opt_in"):
    pages.append(st.Page(nsfw.render, title="NSFW", icon="🔞", url_path="nsfw"))

pg = st.navigation(pages)
pg.run()
rt.render_footer()
