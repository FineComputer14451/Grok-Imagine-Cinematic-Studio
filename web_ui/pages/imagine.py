"""Imagine generation jobs, SFW batch planner, and reference asset pipeline."""

from __future__ import annotations

import streamlit as st

from lib import imagine_runtime as ir
from lib import runtime as rt
from files_client import FilesAPIError, save_inbox_file  # noqa: E402 — after runtime path setup


def _show_action_result(result: dict) -> None:
    argv = " ".join(result.get("argv") or [])
    if result.get("ok"):
        st.success(f"OK · `{argv}`")
    else:
        st.error(f"Failed · exit {result.get('returncode')} · `{argv}`")
    st.code(result.get("output") or result.get("stderr") or "(no output)", language="text")


def _render_files_tab(*, dry: bool) -> None:
    st.subheader("xAI Files API")
    st.caption(
        "ActionSpec `files_list` / `files_get` / `files_upload` / `files_delete` "
        "(same catalog as TUI / NiceGUI). Upload prints a file_id for Imagine `--file-id`."
    )
    if st.button("Refresh file list", key="files_list_btn"):
        st.session_state["_files_list"] = rt.execute_registered("files_list")
    listed = st.session_state.get("_files_list")
    if listed:
        _show_action_result(listed)

    st.markdown("**Get metadata**")
    get_id = st.text_input("file_id", key="files_get_id", placeholder="file_…")
    if st.button("Get file", key="files_get_btn"):
        if not (get_id or "").strip():
            st.warning("Enter a file_id")
        else:
            _show_action_result(
                rt.execute_registered("files_get", {"file_id": get_id.strip()})
            )

    st.markdown("**Upload plate**")
    dropped = st.file_uploader(
        "Drop image or short video (max 50 MB)",
        type=["png", "jpg", "jpeg", "webp", "gif", "mp4"],
        key="files_upload_bytes",
    )
    expires = st.number_input(
        "TTL seconds (0 = no expiry)",
        min_value=0,
        max_value=2_592_000,
        value=0,
        step=3600,
        key="files_upload_ttl",
    )
    force_dry = st.checkbox("Dry-run upload", value=dry, key="files_upload_dry")
    if st.button("Upload to Files API", width="stretch", key="files_upload_btn"):
        if dropped is None:
            st.warning("Choose a file first")
        else:
            try:
                dest = save_inbox_file(dropped.name, dropped.getvalue())
            except (FilesAPIError, OSError) as exc:
                st.error(str(exc))
            else:
                answers = {"path": str(dest), "purpose": "assistants"}
                if int(expires) >= 3600:
                    answers["expires_after"] = str(int(expires))
                if force_dry:
                    answers["dry_run"] = "--dry-run"
                result = rt.execute_registered("files_upload", answers, timeout=180.0)
                _show_action_result(result)
                if result.get("ok"):
                    st.info(f"Local copy: `{dest}` — copy file_id into Job queue submit.")

    st.markdown("**Delete**")
    del_id = st.text_input("file_id to delete", key="files_del_id")
    confirm = st.checkbox("I understand this deletes the stored file", key="files_del_yes")
    if st.button("Delete file", key="files_del_btn"):
        if not confirm:
            st.warning("Tick the confirmation box (ActionSpec still sends --yes).")
        elif not (del_id or "").strip():
            st.warning("Enter a file_id")
        else:
            _show_action_result(
                rt.execute_registered(
                    "files_delete",
                    {"file_id": del_id.strip(), "yes": "--yes"},
                )
            )

    st.markdown("**Share / unshare (public URL)**")
    share_id = st.text_input("file_id", key="files_share_id")
    share_ttl = st.number_input(
        "URL TTL seconds (0 = inherit / never)",
        min_value=0,
        max_value=2_592_000,
        value=0,
        step=3600,
        key="files_share_ttl",
    )
    c_share, c_unshare = st.columns(2)
    with c_share:
        if st.button("Share (public URL)", key="files_share_btn"):
            if not (share_id or "").strip():
                st.warning("Enter a file_id")
            else:
                answers = {"file_id": share_id.strip()}
                if int(share_ttl) >= 3600:
                    answers["expires_after"] = str(int(share_ttl))
                _show_action_result(rt.execute_registered("files_share", answers))
    with c_unshare:
        if st.button("Unshare (revoke)", key="files_unshare_btn"):
            if not (share_id or "").strip():
                st.warning("Enter a file_id")
            else:
                _show_action_result(
                    rt.execute_registered("files_unshare", {"file_id": share_id.strip()})
                )


def render() -> None:
    st.header("Imagine Production")
    st.caption(
        f"Video: `{st.session_state.get('video_model', rt.DEFAULT_IMAGINE_VIDEO_MODEL)}` · "
        f"Image: `{st.session_state.get('image_model', rt.DEFAULT_IMAGINE_IMAGE_MODEL)}` · "
        f"Chat: `{st.session_state.get('chat_model', rt.DEFAULT_XAI_CHAT_MODEL)}` · "
        "Hero stills: Image 2.0 Quality Mode · Video 1.0 cost default · 1.5 native audio · no Video 2.0"
    )
    if not rt.SEQ_AVAILABLE:
        st.error("Studio tools unavailable in this environment.")
        return

    rt.sync_xai_api_key_to_environ()
    dry = ir.dry_run_active()
    if dry:
        st.info(
            "No `XAI_API_KEY` — dry-run mode active (mock URLs). "
            "Set key in **Settings**, or on Streamlit Cloud use **App settings → Secrets**."
        )

    tab_jobs, tab_files, tab_sfw, tab_execute, tab_refs, tab_run, tab_delivery = st.tabs(
        [
            "Job queue",
            "Files",
            "SFW plan",
            "Batch execute",
            "Reference plates",
            "Sequence run",
            "Delivery",
        ]
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
                        "file_id": j.get("result_file_id") or "",
                        "url": (j.get("result_url") or "")[:60],
                    }
                    for j in jobs
                ],
                width="stretch",
                hide_index=True,
            )
        else:
            st.caption("No jobs yet — submit via CLI or Sequence run tab.")

        st.markdown("**Poll video request_id** (`GET /v1/videos/{request_id}`)")
        poll_id = st.text_input("request_id", key="imagine_poll_rid")
        poll_job = st.text_input("Studio job id (optional)", key="imagine_poll_job")
        if st.button("Poll once", key="imagine_poll_btn"):
            if not (poll_id or "").strip():
                st.warning("Enter a request_id")
            else:
                answers = {"request_id": poll_id.strip()}
                if (poll_job or "").strip():
                    answers["job_id"] = poll_job.strip()
                _show_action_result(rt.execute_registered("imagine_poll", answers))

        with st.form("imagine_submit"):
            st.markdown("**Quick submit** (via CLI subprocess)")
            job_type = st.selectbox(
                "Job type",
                ["image", "image_edit", "video", "reference_to_video", "video_edit", "video_extend"],
            )
            prompt = st.text_area("Prompt", placeholder="Cinematic wide shot, golden hour...")
            image_url = st.text_input("Image or video URL (edit / i2v / extend)", value="")
            file_id = st.text_input("Files API file_id (preferred over URL when set)", value="")
            store_as = st.text_input("Store output as (Files filename, optional)", value="")
            duration = st.slider("Video duration (s)", 4, 15, 10)
            force_dry = st.checkbox("Force dry-run", value=dry)
            if st.form_submit_button("Submit job", width="stretch"):
                if prompt.strip():
                    code, out = ir.submit_imagine_via_cli(
                        job_type,
                        prompt.strip(),
                        model=st.session_state.get(
                            "image_model" if job_type in ("image", "image_edit") else "video_model"
                        ),
                        image_url=image_url or None,
                        file_id=file_id or None,
                        store_as=store_as or None,
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

    with tab_files:
        _render_files_tab(dry=dry)

    with tab_sfw:
        st.subheader("SFW batch planner")
        batches = ir.list_sfw_batches()
        if batches:
            st.dataframe(
                [{"id": b["batch_id"], "title": b.get("title"), "status": b.get("status")} for b in batches],
                width="stretch",
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
            if st.form_submit_button("Plan SFW batch", width="stretch"):
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

    with tab_execute:
        st.subheader("Batch shot execute")
        st.caption("Pick a planned batch shot, generate via Imagine, preview result, record QA.")
        batches = ir.list_sfw_batches()
        batch_slugs = [b.get("slug") or b.get("batch_id", "") for b in batches]
        sel_batch = st.selectbox("Batch", batch_slugs or ["(none)"], key="exec_batch")
        if sel_batch and sel_batch != "(none)":
            try:
                next_shots = ir.get_batch_next_shots(sel_batch, count=8)
            except FileNotFoundError:
                next_shots = []
                st.error("Batch not found")
            if next_shots:
                shot_options = {s["shot_id"]: s for s in next_shots}
                shot_id = st.selectbox(
                    "Next shot",
                    list(shot_options.keys()),
                    format_func=lambda sid: (
                        f"{sid} · {shot_options[sid].get('tier')} · "
                        f"{shot_options[sid].get('decision', {}).get('mode', shot_options[sid].get('recommended_mode', ''))}"
                    ),
                    key="exec_shot",
                )
                shot = shot_options[shot_id]
                st.markdown(
                    f"**Models:** `{shot.get('image_model')}` → `{shot.get('video_model')}` · "
                    f"**Est.:** ~{shot.get('cost_estimate', {}).get('credits', shot.get('estimated_credits', '?'))} cr · "
                    f"**Aspect:** {shot.get('aspect_ratio', '16:9')}"
                )
                st.text_area("Description", value=shot.get("description", ""), disabled=True, height=80)

                col_a, col_b, col_c = st.columns(3)
                force_dry = col_a.checkbox("Dry-run", value=dry, key="exec_dry")
                prompt_override = col_b.text_input("Prompt override", value="", key="exec_prompt")
                if col_c.button("Generate shot", width="stretch", key="exec_gen"):
                    try:
                        result = ir.run_sfw_shot(
                            sel_batch, shot_id,
                            dry_run=force_dry,
                            prompt=prompt_override or None,
                        )
                        st.session_state["exec_last_result"] = result
                        st.success(f"Job {result['job_id']} — {result['status']}")
                    except Exception as exc:
                        st.error(str(exc))

                if st.session_state.get("exec_last_result", {}).get("shot_id") == shot_id:
                    res = st.session_state["exec_last_result"]
                    url = res.get("result_url")
                    if url:
                        st.link_button("Open result", url)
                        if url.endswith((".mp4", ".webm")):
                            st.video(url)
                        elif url.endswith((".png", ".jpg", ".jpeg", ".webp")):
                            st.image(url)
                    with st.expander("Execution bridge (copy-paste)"):
                        try:
                            packet = ir.build_shot_bridge(sel_batch, shot_id)
                            st.code(ir.bridge_to_clipboard(packet), language="text")
                        except KeyError:
                            pass

                with st.form("exec_record"):
                    st.markdown("**Record QA result**")
                    score = st.slider("Quality score", 1.0, 10.0, 8.0, 0.5)
                    credits = st.number_input("Credits spent", 1.0, 500.0, 10.0, 1.0)
                    reason = st.text_input("Failure reason (if fail)", value="")
                    note = st.text_input("Notes", value="")
                    if st.form_submit_button("Record result", width="stretch"):
                        rec = ir.record_sfw_shot(
                            sel_batch, shot_id,
                            quality_score=score,
                            credits_spent=credits,
                            failure_reason=reason or None,
                            notes=note,
                        )
                        status = "PASS" if rec["qa_pass"] else "FAIL"
                        st.success(f"{status} — shot updated")
            else:
                st.caption("No pending shots — plan a batch first.")

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
                        "file_id": a.get("file_id") or "",
                        "url": (a.get("url") or "")[:50],
                    }
                    for a in assets
                ],
                width="stretch",
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
            if st.form_submit_button("Register plate", width="stretch"):
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
        if seq_name and seq_name != "(none)" and clip_id:
            try:
                packet = ir.build_clip_bridge(seq_name, clip_id)
                st.caption(
                    f"Resolved: `{packet.get('video_model')}` · aspect {packet.get('aspect_ratio', '16:9')}"
                )
                with st.expander("Clip bridge (grok.com/imagine)"):
                    st.code(ir.bridge_to_clipboard(packet), language="text")
            except (FileNotFoundError, KeyError):
                pass
        force_dry = st.checkbox("Dry-run", value=dry, key="seq_run_dry")
        if st.button("Run clip", width="stretch", key="seq_run_btn"):
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

    with tab_delivery:
        st.subheader("Polish & delivery pipeline")
        st.caption("QA assist → polish → EDL → deliver (Tier 2)")
        del_seq = st.selectbox("Sequence", seq_names or ["(none)"], key="del_seq")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("QA assist + apply", key="qa_assist_btn"):
                if del_seq and del_seq != "(none)":
                    code, out = rt.run_cli([
                        "sequence", "qa-assist", del_seq,
                        "--clip", "clip_001", "--apply",
                    ])
                    st.code(out)
            if st.button("Export EDL", key="edl_btn"):
                if del_seq and del_seq != "(none)":
                    code, out = rt.run_cli(["sequence", "edl", del_seq])
                    st.code(out)
        with col2:
            if st.button("Polish (dry-run)", key="polish_btn"):
                if del_seq and del_seq != "(none)":
                    code, out = rt.run_cli(["sequence", "polish", del_seq, "--dry-run"])
                    st.code(out)
            formats = st.text_input("Delivery formats", value="16:9,9:16", key="del_formats")
            if st.button("Deliver (dry-run)", key="deliver_btn"):
                if del_seq and del_seq != "(none)":
                    code, out = rt.run_cli([
                        "sequence", "deliver", del_seq,
                        "--formats", formats, "--dry-run",
                    ])
                    st.code(out)