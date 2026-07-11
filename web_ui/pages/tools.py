"""Validation, reports, plugin status, and role card browser."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from lib import runtime as rt


def render() -> None:
    st.header("🛠️ Tools")
    st.caption(f"Studio v{rt.STUDIO_VERSION} · Grok 4.5 stack · CLI helpers")

    st.subheader("🤖 Models verify")
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        if st.button("Run models verify", width="stretch", key="tools_models_verify"):
            rt.cached_models_verify.clear()
            st.session_state["_tools_verify"] = rt.cached_models_verify()
    with col_m2:
        result = st.session_state.get("_tools_verify") or (
            rt.cached_models_verify() if rt.MODELS_AVAILABLE else {}
        )
        if result.get("ok"):
            st.success("Grok 4.5 cinematic+Build stack compatible")
        elif result:
            st.warning("Compatibility issues — see details")
            for issue in result.get("issues") or []:
                st.markdown(f"- {issue}")
        else:
            st.caption("Click to verify registry + CLI pin.")

    st.divider()
    st.subheader("🔌 Plugin")
    if st.button("Refresh plugin details", key="tools_plugin_refresh"):
        rt.cached_plugin_details.clear()
    st.code(rt.cached_plugin_details(), language="text")

    st.divider()
    st.subheader("📋 Role Cards")
    options = rt.list_role_card_options()
    if options:
        labels = [label for label, _ in options]
        pick = st.selectbox("Browse Role Card", labels, key="tools_role_card")
        path = dict(options)[pick]
        with st.expander(f"📖 {pick}", expanded=True):
            st.markdown(rt.read_role_card_preview(path))
    else:
        st.warning("references/agents/ not found")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Run validate", width="stretch", key="tools_validate"):
            code, output = rt.run_cli(["validate"])
            st.code(output, language="text")
            if code == 0:
                st.success("Passed")
            else:
                st.warning("Completed with issues")
    with col2:
        if st.button("Generate PDF report", width="stretch", key="tools_report"):
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "production_report.pdf"
                code, output = rt.run_cli(["report", "--output", str(out)])
                if code == 0 and out.exists():
                    st.download_button(
                        "⬇️ Download production_report.pdf",
                        data=out.read_bytes(),
                        file_name="production_report.pdf",
                        mime="application/pdf",
                        key="tools_report_download",
                    )
                else:
                    st.error(output or "Report generation failed")

    st.divider()
    st.subheader("🎬 Agent roster")
    if rt.AGENTS:
        for group, names in rt.AGENTS.items():
            st.markdown(f"**{group}**")
            for name in names:
                st.markdown(f"- {name}")
    else:
        st.caption(f"{rt.core_agent_count()} core agents + i2i + NSFW specialists (opt-in)")