"""Imagine generation jobs, SFW batch planner, and reference asset pipeline."""

from __future__ import annotations

import streamlit as st

from lib import imagine_runtime as ir
from lib import runtime as rt


def render() -> None:
    st.header("Imagine Production")
    if not rt.SEQ_AVAILABLE:
        st.error("Studio tools unavailable in this environment.")
        return

    dry = ir.dry_run_active()
    if dry:
        st.info("No `XAI_API_KEY` — dry-run mode active (mock URLs). Set key in Settings for live generation.")

    tab_jobs, tab_sfw, tab_refs, tab_run = st.tabs(
        ["Job queue", "SFW batch", "Reference plates", "Sequence run"]
    )

    with tab_jobs:
        st.subheader("Generation jobs")
        summary = ir.job_summary()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total jobs", summary["total"])
        c2.metric("Queued", summary["by_status"].get("queued", 0))
        c3.metric("Running", summary["by_status"].get("running", 0))
        c4.metric("Reference assets", summary["reference_assets"])

        jobs = ir.list_jobs(limit=30)
        if jobs:
            st.dataframe(
                [
                    {
                        "id": j["job_id"],
                        "type": j.get("job_type"),
                        "status": j.get("status"),
                        "sequence": j.get("sequence_slug"),
                        "clip": j.get("clip_id"),
                        "url": (j.get("result_url") or "")[:60],
                    }
                    for j in jobs
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No jobs yet — submit via CLI or Sequence run tab.")

        with st.form("imagine_submit"):
            st.markdown("**Quick submit** (via CLI subprocess)")
            job_type = st.selectbox("Job type", ["image", "image_edit", "video"])
            prompt = st.text_area("Prompt", placeholder="Cinematic wide shot, golden hour...")
            image_url = st.text_input("Image URL (edit / i2v)", value="")
            duration = st.slider("Video duration (s)", 4, 15, 10)
            force_dry = st.checkbox("Force dry-run", value=dry)
            if st.form_submit_button("Submit job", use_container_width=True):
                if prompt.strip():
                    code, out = ir.submit_imagine_via_cli(
                        job_type,
                        prompt.strip(),
                        image_url=image_url or None,
                        duration=duration,
                        dry_run=force_dry,
                    )
                    if code == 0:
                        st.success("Job submitted")
                    else:
                        st.error(f"Exit {code}")
                    st.code(out or "(no output)")
                else:
                    st.warning("Prompt required.")

    with tab_sfw:
        st.subheader("SFW batch planner")
        batches = ir.list_sfw_batches()
        if batches:
            st.dataframe(
                [{"id": b["batch_id"], "title": b.get("title"), "status": b.get("status")} for b in batches],
                use_container_width=True,
                hide_index=True,
            )

        with st.form("sfw_batch_plan"):
            title = st.text_input("Batch title")
            shots = st.text_area(
                "Shots (one per line)",
                placeholder="hero:Cover frame, golden hour\nconsistency_anchor:Profile neutral\nstory_beat:Reveal beat",
            )
            budget = st.number_input("Budget credits", 50, 5000, 250)
            fast = st.checkbox("Fast mode", value=st.session_state.get("fast_mode", False))
            if st.form_submit_button("Plan SFW batch", use_container_width=True):
                if title and shots.strip():
                    shot_list = ir.parse_shot_lines(shots)
                    batch, path = ir.plan_and_save_sfw_batch(
                        title,
                        shot_list,
                        tier=st.session_state.get("quota_tier", "supergrok_pro"),
                        budget_credits=float(budget),
                        fast_mode=fast,
                    )
                    st.session_state["sfw_last_batch"] = batch["slug"]
                    st.success(f"Planned {batch['shots_scheduled']}/{batch['shots_total']} shots · {path}")
                    with st.expander("Shot model routing"):
                        for s in batch.get("shots", [])[:12]:
                            st.markdown(
                                f"**{s.get('shot_id')}** ({s.get('tier')}) — "
                                f"`{s.get('image_model')}` → `{s.get('video_model')}` · "
                                f"{s.get('recommended_mode')} · ~{s.get('estimated_credits')} cr"
                            )
                    st.download_button(
                        "Download plan (Markdown)",
                        ir.batch_to_markdown(batch),
                        file_name=f"{batch['slug']}-sfw-plan.md",
                        mime="text/markdown",
                    )
                else:
                    st.warning("Title and shots required.")

    with tab_refs:
        st.subheader("Reference asset pipeline")
        assets = ir.list_reference_assets()
        if assets:
            st.dataframe(
                [
                    {
                        "asset_id": a["asset_id"],
                        "tier": a.get("tier"),
                        "lock": a.get("lock_status"),
                        "shot": a.get("shot_id"),
                        "url": (a.get("url") or "")[:50],
                    }
                    for a in assets
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No reference plates registered yet.")

        with st.form("ref_plate"):
            asset_id = st.text_input("Asset ID", placeholder="hero_anchor_001")
            url = st.text_input("Image URL or file reference")
            tier = st.selectbox("Asset tier", ["hero", "standard", "draft"])
            shot_id = st.text_input("Linked shot ID (optional)")
            notes = st.text_input("Notes", value="")
            if st.form_submit_button("Register plate", use_container_width=True):
                if asset_id and url:
                    entry = ir.add_reference_plate(
                        asset_id,
                        url,
                        tier=tier,
                        shot_id=shot_id or None,
                        notes=notes,
                    )
                    st.success(f"Registered {entry['asset_id']} ({entry['lock_status']})")
                else:
                    st.warning("Asset ID and URL required.")

        lock_id = st.text_input("Lock asset ID", key="imagine_lock_id")
        if st.button("Lock after QA", key="imagine_lock_btn"):
            if lock_id:
                try:
                    ir.lock_plate(lock_id)
                    st.success(f"Locked {lock_id}")
                except KeyError:
                    st.error("Asset not found")
            else:
                st.warning("Enter asset ID")

    with tab_run:
        st.subheader("Sequence clip runner")
        st.caption("Submits to Imagine API, polls job, runs chain QA, updates sequence health.")
        seqs = rt.list_sequences() if rt.SEQ_AVAILABLE else []
        seq_names = [s["name"] for s in seqs] if seqs else []
        seq_name = st.selectbox("Sequence", seq_names or ["(none)"])
        clip_id = st.text_input("Clip ID", value="clip_001")
        force_dry = st.checkbox("Dry-run", value=dry, key="seq_run_dry")
        if st.button("Run clip", use_container_width=True, key="seq_run_btn"):
            if seq_name and seq_name != "(none)" and clip_id:
                code, out = ir.run_sequence_clip_via_cli(seq_name, clip_id, dry_run=force_dry)
                if code == 0:
                    st.success("Clip run complete")
                elif code == 2:
                    st.warning("Run complete — chain QA no_go (extend blocked)")
                else:
                    st.error(f"Exit {code}")
                st.code(out or "(no output)")
            else:
                st.warning("Select sequence and clip ID.")