"""Project dashboard — shared snapshot from CLI dashboard builder (Grok 4.5)."""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt


def render() -> None:
    st.header("📊 Dashboard")
    st.caption(
        f"{rt.core_agent_count()}-agent studio · **v{rt.STUDIO_VERSION}** · Grok **4.5** orchestration"
    )
    st.markdown(rt.stack_banner_markdown())

    if rt.is_streamlit_cloud():
        st.info(
            "**Streamlit Community Cloud** — filesystem is ephemeral: DNA, sequences, and "
            "batches created here may reset on reboot. Prefer secrets for `XAI_API_KEY` "
            "(Settings). Full local workflow: clone the repo and run "
            "`streamlit run web_ui/app.py`."
        )

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
        if rt.MODELS_AVAILABLE:
            vr = rt.cached_models_verify()
            if vr.get("ok"):
                st.caption("Live `models verify`: OK (Grok 4.5 stack)")
            else:
                for issue in vr.get("issues") or []:
                    st.caption(f"verify: {issue}")
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

    st.subheader("🤖 Session Model Stack (Grok 4.5)")
    stack = rt.session_model_stack()
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Chat", str(stack.get("cinematic") or stack.get("xai_chat") or "—"))
    s2.metric("Build", str(stack.get("build") or stack.get("xai_build") or "—"))
    s3.metric("Video", str(stack.get("imagine_video") or "—"))
    s4.metric("Reasoning", str(stack.get("session_reasoning") or "high"))
    with st.expander("Full model stack + registry", expanded=False):
        st.json({"session": stack, "studio_snapshot": studio.get("model_stack", {})})
        if rt.MODELS_AVAILABLE:
            st.code(
                rt.build_video_pipeline_spec(st.session_state.get("video_model")),
                language=None,
            )

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

    if quota.get("recent_history"):
        with st.expander("Recent spend", expanded=False):
            st.dataframe(quota["recent_history"], width="stretch", hide_index=True)

    with st.expander("Full dashboard snapshot (JSON)", expanded=False):
        st.json(snap)

    st.info(
        f"Activate in Grok: `{rt.ACTIVATION_PHRASE}` · "
        "Prefer still → i2v on locked plates · video **1.0** cost default unless native audio needs **1.5**."
    )
