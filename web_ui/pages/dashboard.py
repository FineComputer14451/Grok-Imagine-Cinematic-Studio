"""Project dashboard — shared snapshot from CLI dashboard builder."""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt


def render() -> None:
    st.header("📊 Dashboard")
    st.caption(f"{rt.core_agent_count()}-agent studio · v{rt.STUDIO_VERSION}")

    if not rt.DASHBOARD_AVAILABLE:
        st.error("Dashboard module unavailable in this environment.")
        return

    snap = rt.build_studio_dashboard()
    project = snap["project"]
    studio = snap["studio"]
    quota = snap["quota"]
    prod = snap["production"]

    title = project["title"]
    st.caption(f"Updated {snap['generated_at']}")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Project", title[:24] + ("…" if len(title) > 24 else ""))
    c2.metric("Sequences", prod["sequences"])
    c3.metric("DNA Profiles", prod["characters"])
    c4.metric("Identity Locked", prod["identity_locked"])
    c5.metric("NSFW Batches", prod["nsfw_batches"])

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🏥 Studio Health")
        st.markdown(
            f"- **Agents:** {studio['core_agents']} core · {studio['total_agents']} total\n"
            f"- **Role Cards:** {studio['role_cards']}/{studio['role_cards_expected']}\n"
            f"- **Skills:** {studio['skills']}\n"
            f"- **Models:** {'✅ compatible' if studio['models_compatible'] else '❌ issues'}"
        )
        if not studio["models_compatible"]:
            for issue in studio.get("model_issues", []):
                st.markdown(f"- {issue}")
    with col_r:
        st.subheader("💰 Quota")
        st.markdown(
            f"- **Tier:** {quota.get('tier_label', quota.get('tier', '—'))}\n"
            f"- **Session Spent:** {quota.get('session_spent', 0)} credits\n"
            f"- **Generations:** {quota.get('session_generations', 0)}\n"
            f"- **Risk:** {quota.get('risk_level', 'unknown').title()}"
        )
        if quota.get("budget_remaining") is not None:
            st.markdown(f"- **Budget Left:** {quota['budget_remaining']} credits")
        if quota.get("daily_soft_cap"):
            st.markdown(f"- **Daily Soft Cap:** {quota['daily_soft_cap']} credits")

    if snap["sequences"]:
        st.subheader("🎞 Sequences")
        st.dataframe(
            [
                {
                    "Name": s["name"],
                    "Clips": s["clips"],
                    "Target": f"{s['target_duration']}s",
                    "Health": str(s.get("health") or "—"),
                    "Chain QA": s.get("chain_qa_status", "pending"),
                }
                for s in snap["sequences"]
            ],
            width="stretch",
            hide_index=True,
        )

    if snap["characters"]:
        st.subheader("🧬 Characters")
        st.dataframe(
            [
                {"Name": c["name"], "Slug": c["slug"], "Lock": c.get("status", "pending")}
                for c in snap["characters"]
            ],
            width="stretch",
            hide_index=True,
        )

    if snap["nsfw_batches"]:
        st.subheader("🔞 NSFW Batches")
        st.dataframe(
            [
                {
                    "ID": b.get("batch_id", "?"),
                    "Title": b.get("title", ""),
                    "Status": b.get("status", "—"),
                }
                for b in snap["nsfw_batches"]
            ],
            width="stretch",
            hide_index=True,
        )

    st.subheader("🤖 Model Stack")
    st.json(studio.get("model_stack", {}))

    if quota.get("recent_history"):
        with st.expander("Recent spend", expanded=False):
            st.dataframe(quota["recent_history"], width="stretch", hide_index=True)

    with st.expander("Full dashboard snapshot (JSON)", expanded=False):
        st.json(snap)