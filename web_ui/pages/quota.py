"""Quota estimation, budget tier, and optimization recommendations."""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt
from lib import session as sess


def render() -> None:
    st.header("💰 Quota & Budget")
    st.caption(
        "Video spend is `grok-imagine-*` only · chat orchestration is **Grok 4.5** "
        "(not billed as Imagine seconds)."
    )
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
        f"Tokens ~{est.get('estimated_tokens', 0):,} · "
        f"Video: `{est.get('video_model', st.session_state.video_model)}` · "
        f"Chat: `{st.session_state.chat_model}` · "
        f"Reasoning: {st.session_state.get('reasoning_level', 'high')}"
    )
    if "1.5" in str(st.session_state.video_model):
        st.info("1.5 selected — higher $/sec for native audio. Prefer 1.0 when silent/post-mix is fine.")

    recon = dash.get("reconciliation") or {}
    if recon:
        st.subheader("Reconciliation (cascade)")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Cascade", str(recon.get("cascade_source") or "none"))
        r2.metric("Burn", f"{recon.get('burn_rate_multiplier', 1.0)}x")
        r3.metric("Burn risk", str(dash.get("burn_rate_risk") or recon.get("risk_level") or "low"))
        r4.metric("Entries", int(recon.get("entry_count") or 0))
        st.caption(
            f"Est {recon.get('estimated_total', 0)} · "
            f"Act {recon.get('actual_total', 0)} · "
            f"Variance {recon.get('variance_pct', 0)}% · "
            f"Session spent {dash.get('session_spent', 0)} credits"
        )
        st.caption("CLI: `cinematic-studio quota sync` · doctor: section 13 Quota recon")

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