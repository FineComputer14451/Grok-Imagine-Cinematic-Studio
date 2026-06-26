"""NSFW batch and sequence planners (explicit opt-in)."""

from __future__ import annotations

import json

import streamlit as st

from lib import runtime as rt  # noqa: I001 — sets tools/ on sys.path first
from lib import nsfw_runtime as nr


def _gate() -> bool:
    if not st.session_state.get("nsfw_opt_in"):
        st.warning("Enable NSFW planning tools in **Settings → Enable NSFW planning tools**.")
        return False
    if not rt.NSFW_AVAILABLE:
        st.error("NSFW modules unavailable in this environment.")
        return False
    st.caption("ErosForge planners — explicit `ACTIVATE EROSFORGE` still required in Grok.")
    return True


def render() -> None:
    st.header("🔞 NSFW Pipelines")
    if not _gate():
        return

    tab_batch, tab_queue, tab_execute, tab_tools, tab_extend, tab_report = st.tabs(
        ["Batch plan", "Queue", "Execute", "Decide / retry", "Extension", "Daily report"]
    )

    with tab_batch:
        st.subheader("Plan batch")
        with st.form("nsfw_batch_plan"):
            batch_title = st.text_input("Batch title")
            shots = st.text_area(
                "Shots (one per line)",
                placeholder="hero:Cover frame, golden hour\nconsistency_anchor:Profile neutral\nkey_explicit:high:Slow reveal",
                help="Format: tier:description or tier:motion:description",
            )
            col1, col2 = st.columns(2)
            with col1:
                budget = st.number_input("Budget credits", 100, 5000, 800)
            with col2:
                fast = st.checkbox("Fast mode", value=st.session_state.fast_mode)
            if st.form_submit_button("Plan batch", width="stretch"):
                if batch_title and shots.strip():
                    shot_list = nr.parse_shot_lines(shots)
                    batch, path = nr.plan_and_save_batch(
                        batch_title,
                        shot_list,
                        tier=st.session_state.quota_tier,
                        budget_credits=float(budget),
                        fast_mode=fast,
                    )
                    st.session_state["nsfw_last_batch"] = batch["slug"]
                    st.success(f"Planned {batch['shots_scheduled']}/{batch['shots_total']} shots · saved {path}")
                    st.json({
                        "slug": batch["slug"],
                        "risk": batch["risk"]["risk_level"],
                        "scheduled_credits": batch["scheduled_credits"],
                        "execution_order": batch.get("execution_order", []),
                    })
                    with st.expander("Shot model routing (Reference Curator)"):
                        for s in batch.get("shots", [])[:12]:
                            st.markdown(
                                f"**{s.get('shot_id')}** ({s.get('tier')}) — "
                                f"`{s.get('image_model')}` → `{s.get('video_model')}` · "
                                f"{s.get('recommended_mode')} · ~{s.get('estimated_credits')} cr"
                            )
                    st.download_button(
                        "Download plan (Markdown)",
                        nr.batch_to_markdown(batch),
                        file_name=f"{batch['slug']}-plan.md",
                        mime="text/markdown",
                    )
                else:
                    st.warning("Batch title and shots are required.")

    with tab_queue:
        st.subheader("Batch queue")
        batches = nr.list_batches()
        if not batches:
            st.info("No batches yet. Plan one in the **Batch plan** tab.")
        else:
            st.dataframe(
                [{"id": b["batch_id"], "title": b.get("title"), "status": b.get("status"), "path": b.get("path")} for b in batches],
                width="stretch",
                hide_index=True,
            )
        slug = st.text_input(
            "Batch slug",
            value=st.session_state.get("nsfw_last_batch", ""),
            key="nsfw_queue_slug",
        )
        count = st.slider("Next shots count", 1, 10, 3)
        if st.button("Show next shots", key="nsfw_next_btn"):
            if slug:
                try:
                    shots = nr.next_shots(slug, count=count)
                    if shots:
                        st.dataframe(shots, width="stretch")
                    else:
                        st.info("No pending shots in this batch.")
                except Exception as exc:
                    st.error(str(exc))
            else:
                st.warning("Enter a batch slug.")

    with tab_execute:
        st.subheader("Batch shot execute")
        st.caption("Generate next NSFW shots via Imagine API, preview, record QA.")
        batches = nr.list_batches()
        batch_slugs = [b.get("slug") or b.get("batch_id", "") for b in batches]
        sel = st.selectbox("Batch", batch_slugs or ["(none)"], key="nsfw_exec_batch")
        if sel and sel != "(none)":
            try:
                next_shots = nr.next_shots(sel, count=8)
            except Exception:
                next_shots = []
            if next_shots:
                opts = {s["shot_id"]: s for s in next_shots}
                shot_id = st.selectbox(
                    "Next shot",
                    list(opts.keys()),
                    format_func=lambda sid: (
                        f"{sid} · {opts[sid].get('tier')} · "
                        f"{opts[sid].get('decision', {}).get('mode', opts[sid].get('recommended_mode', ''))}"
                    ),
                    key="nsfw_exec_shot",
                )
                shot = opts[shot_id]
                st.markdown(
                    f"**Models:** `{shot.get('image_model')}` → `{shot.get('video_model')}` · "
                    f"**Est.:** ~{shot.get('cost_estimate', {}).get('credits', '?')} cr"
                )
                c1, c2 = st.columns(2)
                dry = c1.checkbox("Dry-run", value=True, key="nsfw_exec_dry")
                session_n = c2.number_input("Session count", 1, 5, 1, key="nsfw_sess_n")
                if st.button("Generate shot", key="nsfw_exec_gen"):
                    try:
                        result = nr.run_nsfw_shot(sel, shot_id, dry_run=dry)
                        st.session_state["nsfw_exec_result"] = result
                        st.success(f"Job {result['job_id']}")
                    except Exception as exc:
                        st.error(str(exc))
                if st.button("Run session", key="nsfw_sess_btn"):
                    summary = nr.run_nsfw_session(sel, count=int(session_n), dry_run=dry)
                    st.json(summary)
                if st.session_state.get("nsfw_exec_result", {}).get("shot_id") == shot_id:
                    url = st.session_state["nsfw_exec_result"].get("result_url")
                    if url:
                        st.link_button("Open result", url)
            else:
                st.caption("No pending shots.")

    with tab_tools:
        st.subheader("Generation mode decision")
        with st.form("nsfw_decide"):
            d_id = st.text_input("Shot ID", value="shot_hero_001")
            c1, c2, c3 = st.columns(3)
            with c1:
                d_tier = st.selectbox("Tier", nr.SHOT_TIER_OPTIONS, index=0)
            with c2:
                d_motion = st.selectbox("Motion", nr.MOTION_OPTIONS, index=1)
            with c3:
                d_explicit = st.selectbox("Explicit level", nr.EXPLICIT_OPTIONS, index=1)
            d_ref = st.checkbox("Has approved reference")
            if st.form_submit_button("Decide mode"):
                decision = nr.mode_decision(
                    d_id,
                    shot_tier=d_tier,
                    motion=d_motion,
                    has_ref=d_ref,
                    explicit=d_explicit,
                )
                st.json(decision)

        st.divider()
        st.subheader("Retry strategy")
        with st.form("nsfw_retry"):
            r_id = st.text_input("Failed shot ID", value="shot_key_001")
            r_reason = st.selectbox("Failure reason", nr.RETRY_REASONS)
            r_score = st.slider("QA score received", 1.0, 10.0, 5.5, 0.5)
            r_attempts = st.number_input("Prior attempts", 0, 5, 0)
            if st.form_submit_button("Suggest retry"):
                st.json(nr.retry_plan(r_id, reason=r_reason, score=r_score, attempts=int(r_attempts)))

        st.divider()
        st.subheader("Record shot result")
        with st.form("nsfw_record"):
            rec_slug = st.text_input("Batch slug", key="nsfw_rec_slug")
            rec_shot = st.text_input("Shot ID", key="nsfw_rec_shot")
            rec_score = st.slider("Quality score", 1.0, 10.0, 8.0, 0.5)
            rec_credits = st.number_input("Credits spent", 1.0, 500.0, 80.0)
            rec_reason = st.selectbox("Failure reason (if fail)", ["", *nr.RETRY_REASONS])
            if st.form_submit_button("Record"):
                if rec_slug and rec_shot:
                    result = nr.record_shot(
                        rec_slug,
                        rec_shot,
                        score=rec_score,
                        credits=rec_credits,
                        failure_reason=rec_reason or None,
                    )
                    st.success("PASS" if result.get("qa_pass") else "FAIL")
                    st.json(result)
                else:
                    st.warning("Batch slug and shot ID required.")

    with tab_extend:
        st.subheader("NSFW sequence extension")
        profiles = list(nr.TENSION_PROFILES.keys())
        with st.form("nsfw_extend"):
            seq_name = st.text_input("Sequence name")
            duration = st.number_input("Target duration (s)", 30, 180, 90)
            profile = st.selectbox("Tension profile", profiles, index=profiles.index("passionate") if "passionate" in profiles else 0)
            reference = st.text_area("Reference frame / clip description", height=80)
            if st.form_submit_button("Plan extension"):
                if seq_name:
                    seq = nr.plan_extension(
                        seq_name,
                        duration=int(duration),
                        profile=profile,
                        reference=reference,
                    )
                    st.session_state["nsfw_last_seq"] = seq
                    st.success(f"Planned {len(seq.get('clips', []))} clips · profile **{profile}**")
                    st.json({
                        "title": seq.get("sequence_name"),
                        "clips": len(seq.get("clips", [])),
                        "tension_profile": seq.get("tension_profile"),
                        "target_duration": seq.get("target_duration_seconds"),
                    })
                    st.download_button(
                        "Download extension plan",
                        nr.nsfw_sequence_to_markdown(seq),
                        file_name=f"{seq.get('slug', 'sequence')}-nsfw-plan.md",
                        mime="text/markdown",
                        key="nsfw_ext_dl",
                    )
                else:
                    st.warning("Sequence name is required.")
        if st.session_state.get("nsfw_last_seq"):
            if st.button("Save extension to sequences/", key="nsfw_save_seq"):
                path = nr.save_extension(st.session_state["nsfw_last_seq"])
                st.success(f"Saved {path}")

    with tab_report:
        st.subheader("Daily NSFW report")
        report_date = st.text_input("Date (YYYY-MM-DD, blank = today)", value="")
        if st.button("Generate report", key="nsfw_report_btn"):
            report = nr.daily_report(report_date or None)
            st.metric("Credits today", f"{report['credits_used_today']} / {report['daily_soft_cap']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Pass rate", f"{report['pass_rate_pct']}%")
            c2.metric("Avg quality", f"{report['avg_quality_score']}/10")
            c3.metric("Shots done", report["shots_completed"])
            st.json(report)
            if report.get("recommendations"):
                st.markdown("**Recommendations**")
                for r in report["recommendations"]:
                    st.markdown(f"- {r}")