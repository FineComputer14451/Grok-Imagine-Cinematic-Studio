"""Project dashboard — state overview and health checks."""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt
from lib import session as sess


def render() -> None:
    st.header("📊 Dashboard")
    st.caption(f"{rt.core_agent_count()}-agent studio · v{rt.STUDIO_VERSION}")

    state = rt.load_project_state() if rt.DNA_AVAILABLE else {}
    project = state.get("project") or {}
    title = project.get("project_title") or project.get("title") or "Untitled"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Project", title[:28] + ("…" if len(title) > 28 else ""))
    c2.metric("DNA Profiles", len(rt.list_characters()) if rt.DNA_AVAILABLE else 0)
    c3.metric("Sequences", len(rt.list_sequences()) if rt.SEQ_AVAILABLE else 0)
    c4.metric(
        "Identity Locked",
        len(state.get("identity_lock", {})) if rt.DNA_AVAILABLE else 0,
    )

    snapshot = sess.session_quota_snapshot()
    if snapshot:
        est = snapshot["estimate"]
        dash = snapshot["dashboard"]
        risk = snapshot["risk"]
        st.subheader("💰 Session Quota")
        q1, q2, q3 = st.columns(3)
        q1.metric("Tier", dash.get("tier", st.session_state.quota_tier))
        q2.metric("Est. Credits", f"{est['credits_low']:.0f}–{est['credits_high']:.0f}")
        q3.metric("Risk", risk["risk_level"].title())

    st.subheader("🤖 Model Stack")
    if rt.MODELS_AVAILABLE:
        result = rt.verify_model_compatibility()
        if result["compatible"]:
            st.success("Model compatibility verified")
        else:
            st.error("Model compatibility issues")
            for issue in result["issues"]:
                st.markdown(f"- {issue}")
        st.json(result["model_stack"])
    else:
        st.warning("Models module unavailable")

    with st.expander("Project state (`.cinematic_project_state.json`)", expanded=False):
        st.json(state if state else {"status": "empty"})