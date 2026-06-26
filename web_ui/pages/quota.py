"""Quota estimation, budget tier, and optimization recommendations."""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt
from lib import session as sess


def render() -> None:
    st.header("💰 Quota & Budget")
    snapshot = sess.session_quota_snapshot()
    if not snapshot:
        st.error("Quota module unavailable")
        return

    est = snapshot["estimate"]
    dash = snapshot["dashboard"]
    risk = snapshot["risk"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Credits", f"{est['credits_low']:.0f}–{est['credits_high']:.0f}")
    c2.metric("USD", f"${est['usd_low']}–${est['usd_high']}")
    c3.metric("Clips", est["clip_count"])
    c4.metric("Risk", risk["risk_level"].title())

    st.caption(
        f"Tokens ~{est['estimated_tokens']:,} · "
        f"Video model: {est.get('video_model', st.session_state.video_model)}"
    )

    if st.button("Apply tier to project state"):
        rt.set_budget(tier=st.session_state.quota_tier)
        st.success(f"Tier set: {st.session_state.quota_tier}")

    st.subheader("Optimization recommendations")
    recs = rt.get_optimization_recommendations(est, risk=risk)
    if recs:
        for rec in recs:
            st.markdown(f"**[{rec.get('priority', 'info').upper()}]** {rec.get('action', 'Tip')}")
            savings = rec.get("savings")
            if savings:
                st.caption(f"Savings: {savings}")
    else:
        st.caption("No recommendations for current settings.")

    with st.expander("Quota dashboard raw", expanded=False):
        st.json(dash)