"""Project dashboard — dense ops board shared with CLI TUI signals (Grok 4.5)."""

from __future__ import annotations

import streamlit as st

from lib import dashboard_ui as dui
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

    top_l, top_r = st.columns([3, 1])
    with top_r:
        if st.button("↻ Refresh snapshot", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    snap = dui.attach_quota_alignment(rt.build_studio_dashboard())
    project = snap["project"]
    studio = snap["studio"]
    quota = snap["quota"]
    prod = snap["production"]
    sev = dui.severity(snap)

    # Status strip (TUI-parity)
    st.markdown(
        dui.status_strip_html(snap, studio_version=rt.STUDIO_VERSION),
        unsafe_allow_html=True,
    )

    # J1/J6 health action strip (safe CLI only — no spend)
    st.subheader("🩺 Health actions")
    st.caption(
        "Safe read/repair commands · same family as TUI keys **d** / **v** / **s** / **m**"
    )
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if st.button("Doctor (quick)", use_container_width=True, key="dash_doctor"):
            with st.spinner("Running doctor --quick…"):
                code, out = rt.run_cli(["doctor", "--quick"], timeout=180)
            st.session_state["_dash_health_out"] = {
                "title": "doctor --quick",
                "code": code,
                "out": out,
            }
    with a2:
        if st.button("Validate", use_container_width=True, key="dash_validate"):
            with st.spinner("Running validate…"):
                code, out = rt.run_cli(["validate"], timeout=180)
            st.session_state["_dash_health_out"] = {
                "title": "validate",
                "code": code,
                "out": out,
            }
    with a3:
        if st.button("Quota sync", use_container_width=True, key="dash_quota_sync"):
            with st.spinner("Running quota sync…"):
                code, out = rt.run_cli(["quota", "sync"], timeout=120)
            st.session_state["_dash_health_out"] = {
                "title": "quota sync",
                "code": code,
                "out": out,
            }
    with a4:
        if st.button("Models verify", use_container_width=True, key="dash_models"):
            rt.cached_models_verify.clear()
            with st.spinner("Running models verify…"):
                code, out = rt.run_cli(["models", "verify"], timeout=60)
            st.session_state["_dash_health_out"] = {
                "title": "models verify",
                "code": code,
                "out": out,
            }
    health = st.session_state.get("_dash_health_out")
    if health:
        title = health.get("title", "command")
        code = int(health.get("code") or 1)
        out = str(health.get("out") or "(no output)")
        if code == 0:
            st.success(f"`{title}` · exit {code}")
        else:
            st.warning(f"`{title}` · exit {code}")
        with st.expander(f"Output: {title}", expanded=True):
            st.code(out, language="text")

    # Attention board
    attention = dui.attention_rows(snap)
    st.subheader("⚡ Attention")
    if not attention:
        st.success("All clear — no blocking ops signals.")
    else:
        box = st.container(border=True)
        with box:
            if sev == "critical":
                st.error(f"**{len(attention)}** item(s) need attention")
            elif sev == "warn":
                st.warning(f"**{len(attention)}** item(s) to review")
            for i, line in enumerate(attention, 1):
                st.markdown(f"{i}. {line}")

    # Phase 2 readiness (J3–J5)
    readiness = snap.get("readiness") or {}
    st.subheader("🚦 Produce / gate readiness")
    if readiness:
        overall = str(readiness.get("overall") or "unknown").upper()
        ident = readiness.get("identity") or {}
        cq = readiness.get("chain_qa") or {}
        pm = readiness.get("plate_motion") or {}
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Overall", overall)
        r2.metric("Identity", ident.get("label", "—"))
        r3.metric("Chain QA", cq.get("label", "—"))
        if pm.get("available"):
            r4.metric(
                "Plate / motion",
                f"{pm.get('plate_ok', 0)}ok / {pm.get('motion_ok', 0)}mv",
            )
        else:
            r4.metric("Plate / motion", "n/a")
        next_actions = readiness.get("next_actions") or []
        if next_actions:
            st.markdown("**Next actions**")
            for a in next_actions[:6]:
                st.markdown(f"- {a}")
        elif overall == "READY":
            st.caption("Gate clear for careful video spend (still prefer strict flags on CLI).")
    else:
        st.caption("Readiness rollup unavailable — refresh snapshot.")

    # Phase 3 — Convergence (J8) + Parallel Briefs + Delivery (J7)
    conv = snap.get("convergence") or {}
    st.subheader("🔀 Convergence → agent-mode handoff (J8)")
    checklist = conv.get("checklist") or []
    if checklist:
        if conv.get("ready"):
            st.success(f"Convergence **READY** · {conv.get('label', '')}")
        else:
            st.warning(f"Convergence **HOLD** · {conv.get('label', '')}")
        for item in checklist:
            ok = item.get("ok")
            mark = "✅" if ok is True else ("❔" if ok is None else "❌")
            st.markdown(f"{mark} **{item.get('label', item.get('id'))}**")
            if ok is not True and item.get("hint"):
                st.caption(item["hint"])
    else:
        st.caption("Convergence checklist unavailable.")

    pb = snap.get("parallel_briefs") or {}
    st.subheader("📋 Parallel Brief logs (J8 · read-only)")
    st.caption(str(pb.get("label") or "—"))
    logs = pb.get("logs") or []
    if logs:
        st.dataframe(
            [
                {
                    "Session": lg.get("session_id"),
                    "Briefs": lg.get("brief_count"),
                    "Specialists": ", ".join(lg.get("specialists") or []),
                    "Path": lg.get("path"),
                }
                for lg in logs
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption(
            "No brief logs found · CLI: "
            "`cinematic-studio wave-a briefs <session> -o artifacts/briefs_<session>.json`"
        )

    delivery = snap.get("delivery") or {}
    st.subheader("📦 Delivery readiness (J7)")
    st.caption(str(delivery.get("label") or "—"))
    drows = delivery.get("sequences") or []
    if drows:
        st.dataframe(
            [
                {
                    "Sequence": r.get("name"),
                    "Polish": "pass" if r.get("polish_pass") else "hold",
                    "Deliver": "pass" if r.get("deliver_pass") else "hold",
                    "Blocker": (r.get("polish_blockers") or r.get("deliver_blockers") or ["—"])[0],
                }
                for r in drows
            ],
            width="stretch",
            hide_index=True,
        )
        st.caption(
            "Safe previews: `sequence polish NAME --dry-run` · "
            "`sequence deliver NAME --dry-run` (TUI Cockpit Delivery group)"
        )
    else:
        st.caption("No sequences for delivery assessment.")

    # KPI metrics
    title = project["title"]
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Project", title[:20] + ("…" if len(title) > 20 else ""))
    c2.metric("Sequences", prod["sequences"])
    c3.metric("DNA", prod["characters"])
    c4.metric("Locked", prod["identity_locked"])
    c5.metric("Risk", str(quota.get("risk_level", "—")).title())
    c6.metric("Severity", dui.severity_label(sev))

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🏥 Studio Health")
        st.markdown(
            f"- **Agents:** {studio['core_agents']} core · {studio['total_agents']} total\n"
            f"- **Role Cards:** {studio['role_cards']}/{studio['role_cards_expected']}\n"
            f"- **Skills:** {studio['skills']}\n"
            f"- **Models:** {'✅ compatible' if studio['models_compatible'] else '❌ issues'}\n"
            f"- **Bible:** {'loaded' if project.get('has_bible') else 'not started'}\n"
            f"- **SFW / NSFW batches:** {prod.get('sfw_batches', 0)} / {prod.get('nsfw_batches', 0)}\n"
            f"- **Imagine jobs:** {prod.get('imagine_jobs', 0)}"
        )
        if not studio["models_compatible"]:
            for issue in studio.get("model_issues", []):
                st.markdown(f"- ⚠️ {issue}")
        if rt.MODELS_AVAILABLE:
            vr = rt.cached_models_verify()
            if vr.get("ok") or vr.get("compatible"):
                st.caption("Live `models verify`: OK (Grok 4.5 stack)")
            else:
                for issue in vr.get("issues") or []:
                    st.caption(f"verify: {issue}")
    with col_r:
        st.subheader("💰 Quota")
        remaining = quota.get("budget_remaining")
        remaining_s = f"{remaining} credits" if remaining is not None else "—"
        st.markdown(
            f"- **Tier:** {quota.get('tier_label', quota.get('tier', '—'))}\n"
            f"- **Session Spent:** {quota.get('session_spent', 0)} credits\n"
            f"- **Generations:** {quota.get('session_generations', 0)}\n"
            f"- **Budget Left:** {remaining_s}\n"
            f"- **Risk:** {str(quota.get('risk_level', 'unknown')).title()}"
        )
        if quota.get("daily_soft_cap"):
            st.markdown(f"- **Daily Soft Cap:** {quota['daily_soft_cap']} credits")
        recon = quota.get("reconciliation") or {}
        cascade = recon.get("cascade_source")
        if cascade and cascade != "none":
            st.markdown(
                f"- **Cascade:** `{cascade}` · burn {recon.get('burn_rate_multiplier', 1.0)}x\n"
                f"- **Recon:** est {recon.get('estimated_total', 0)} / "
                f"act {recon.get('actual_total', 0)} "
                f"({recon.get('entry_count', 0)} entries)"
            )
        align = snap.get("quota_alignment") or {}
        if align.get("status"):
            st.markdown(f"- **Ledger alignment:** **{align['status']}**")
            if align.get("hint") and align["status"] not in ("aligned", "idle"):
                st.caption(align["hint"])
        st.caption("CLI: `cinematic-studio quota sync` · TUI Home: **s**")

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

    # Sequences (structure) + Chain QA (dedicated) — TUI-parity split
    seq_rows = dui.sequences_table_rows(snap)
    st.subheader("🎞 Sequences")
    if seq_rows:
        st.dataframe(seq_rows, width="stretch", hide_index=True)
    else:
        st.caption("No sequences yet — create one under Sequences or CLI cockpit.")

    qa_rows = dui.chain_qa_table_rows(snap)
    st.subheader("🧪 Chain QA")
    if qa_rows:
        st.dataframe(qa_rows, width="stretch", hide_index=True)
        if any(int(r.get("No-Go") or 0) > 0 for r in qa_rows):
            st.warning(
                "No-Go present — fix clips and re-run chain QA before sequence handoff/extend."
            )
        else:
            st.caption("All listed sequences free of no-go · validate handoff packets before stitch.")
    else:
        st.caption("No sequence QA data yet · generate clips then run chain QA before extend.")

    char_rows = dui.characters_table_rows(snap)
    st.subheader("🧬 Characters")
    if char_rows:
        st.dataframe(char_rows, width="stretch", hide_index=True)
    else:
        st.caption("No DNA profiles yet.")

    job_rows = dui.jobs_table_rows(snap)
    if job_rows:
        st.subheader("✨ Recent Imagine jobs")
        st.dataframe(job_rows, width="stretch", hide_index=True)

    if snap.get("nsfw_batches"):
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

    if snap.get("sfw_batches"):
        with st.expander("SFW batches", expanded=False):
            st.dataframe(
                [
                    {
                        "ID": b.get("batch_id") or b.get("slug") or "?",
                        "Title": b.get("title", ""),
                        "Status": b.get("status", "—"),
                    }
                    for b in snap["sfw_batches"]
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
        "Prefer still → i2v on locked plates · video **1.0** cost default unless native audio needs **1.5**. · "
        "Terminal twin: `cinematic-studio ui`"
    )
