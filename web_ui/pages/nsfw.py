"""NSFW batch and sequence planners (explicit opt-in)."""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt


def render() -> None:
    st.header("🔞 NSFW Pipelines")
    st.caption("ErosForge planners — explicit activation still required in Grok.")

    if not st.session_state.get("nsfw_opt_in"):
        st.warning("Enable NSFW planning tools in Settings → NSFW opt-in.")
        return
    if not rt.NSFW_AVAILABLE:
        st.error("NSFW modules unavailable in this environment.")
        return

    with st.form("nsfw_batch"):
        batch_title = st.text_input("Batch title")
        shots = st.text_area(
            "Shots (one per line)",
            placeholder="hero:Cover frame\nconsistency_anchor:Wide",
        )
        budget = st.number_input("Budget credits", 100, 5000, 800)
        if st.form_submit_button("Plan NSFW batch"):
            if batch_title and shots:
                shot_list = [line.strip() for line in shots.splitlines() if line.strip()]
                batch = rt.plan_batch(
                    batch_title,
                    shot_list,
                    tier=st.session_state.quota_tier,
                    budget_credits=budget,
                    fast_mode=st.session_state.fast_mode,
                )
                st.json(batch)
            else:
                st.warning("Batch title and shots are required")

    with st.form("nsfw_extend"):
        seq_name = st.text_input("Sequence name")
        duration = st.number_input("Extension duration (s)", 30, 180, 90)
        if st.form_submit_button("Plan NSFW extension"):
            if seq_name:
                seq = rt.plan_nsfw_extension(
                    seq_name,
                    target_duration=int(duration),
                    tension_profile="passionate",
                )
                st.json({"title": seq.get("title"), "clips": len(seq.get("clips", []))})
            else:
                st.warning("Sequence name is required")