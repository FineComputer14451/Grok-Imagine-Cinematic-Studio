"""Validation, reports, plugin status, and role card browser."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from lib import runtime as rt


def render() -> None:
    st.header("🛠️ Tools")
    st.caption(f"Studio v{rt.STUDIO_VERSION} · Grok 4.5 stack · CLI helpers")

    st.subheader("🤖 Models verify")
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        if st.button("Run models verify", width="stretch", key="tools_models_verify"):
            rt.cached_models_verify.clear()
            st.session_state["_tools_verify"] = rt.cached_models_verify()
    with col_m2:
        result = st.session_state.get("_tools_verify") or (
            rt.cached_models_verify() if rt.MODELS_AVAILABLE else {}
        )
        if result.get("ok"):
            st.success("Grok 4.5 cinematic+Build stack compatible")
        elif result:
            st.warning("Compatibility issues — see details")
            for issue in result.get("issues") or []:
                st.markdown(f"- {issue}")
        else:
            st.caption("Click to verify registry + CLI pin.")

    st.divider()
    st.subheader("⚡ Safe ActionSpec actions")
    st.caption(
        "Runs via `studio_core.services.execute` (same catalog as TUI / NiceGUI). "
        "No free-form argv."
    )
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if st.button("Status", width="stretch", key="tools_core_status"):
            st.session_state["_tools_core_out"] = rt.execute_registered("status")
    with a2:
        if st.button("Validate", width="stretch", key="tools_core_validate"):
            st.session_state["_tools_core_out"] = rt.execute_registered("validate")
    with a3:
        if st.button("Stack", width="stretch", key="tools_core_stack"):
            st.session_state["_tools_core_out"] = rt.execute_registered("stack")
    with a4:
        if st.button("Doctor quick", width="stretch", key="tools_core_doctor"):
            st.session_state["_tools_core_out"] = rt.execute_registered("doctor_quick")
    core_out = st.session_state.get("_tools_core_out")
    if core_out:
        if core_out.get("ok"):
            st.success(
                f"OK · `{' '.join(core_out.get('argv') or [])}` · mode={core_out.get('mode')}"
            )
        else:
            st.error(
                f"Failed · exit {core_out.get('returncode')} · "
                f"`{' '.join(core_out.get('argv') or [])}`"
            )
        st.code(core_out.get("output") or core_out.get("stderr") or "(no output)", language="text")

    st.divider()
    st.subheader("🔌 Plugin")
    if st.button("Refresh plugin details", key="tools_plugin_refresh"):
        rt.cached_plugin_details.clear()
    st.code(rt.cached_plugin_details(), language="text")

    st.divider()
    st.subheader("📋 Role Cards")
    options = rt.list_role_card_options()
    if options:
        labels = [label for label, _ in options]
        pick = st.selectbox("Browse Role Card", labels, key="tools_role_card")
        path = dict(options)[pick]
        with st.expander(f"📖 {pick}", expanded=True):
            st.markdown(rt.read_role_card_preview(path))
    else:
        st.warning("references/agents/ not found")

    st.divider()
    st.subheader("📦 Handoff packet validate")
    st.caption(
        "Schema + soft readiness (no Imagine spend) · CLI: `cinematic-studio handoff validate PATH`"
    )
    ho_path = st.text_input(
        "Handoff JSON path",
        placeholder="sequences/.../handoff_clip.json",
        key="tools_handoff_path",
    )
    if st.button("Validate handoff", width="stretch", key="tools_handoff_validate"):
        if not (ho_path or "").strip():
            st.warning("Enter a path to a handoff JSON file")
        else:
            code, output = rt.run_cli_or_action(
                "handoff_validate",
                {"path": ho_path.strip()},
                timeout=60,
            )
            st.code(output, language="text")
            if code == 0:
                st.success("Handoff OK")
            else:
                st.error("Handoff validation failed")

    st.divider()
    st.subheader("✨ Imagine bridge preview (grok.com)")
    st.caption("Copy-paste packet · no API spend · paste into grok.com/imagine")
    b1, b2 = st.columns(2)
    with b1:
        bridge_seq = st.text_input("Sequence slug", key="tools_bridge_seq")
        bridge_clip = st.text_input("Clip id", key="tools_bridge_clip")
    with b2:
        bridge_batch = st.text_input("SFW batch slug", key="tools_bridge_batch")
        bridge_shot = st.text_input("Shot id", key="tools_bridge_shot")
    if st.button("Preview bridge packet", width="stretch", key="tools_bridge_preview"):
        answers = {
            "sequence": (bridge_seq or "").strip(),
            "clip": (bridge_clip or "").strip(),
            "batch": (bridge_batch or "").strip(),
            "shot": (bridge_shot or "").strip(),
            "format": "markdown",
        }
        code, output = rt.run_cli_or_action("imagine_bridge", answers, timeout=60)
        st.code(output or "(empty)", language="markdown")
        if code == 0:
            st.success("Bridge packet ready to paste")
        else:
            st.warning(f"Bridge exit {code} — check sequence/clip/batch ids")

    st.divider()
    st.subheader("📋 Parallel Brief starter log")
    st.caption("Wave A · writes `parallel_brief_dispatch_log` JSON")
    pb_session = st.text_input("Session id", value="ops-session", key="tools_pb_session")
    pb_out = st.text_input(
        "Output path",
        value="artifacts/briefs_ops-session.json",
        key="tools_pb_out",
    )
    if st.button("Build brief log", width="stretch", key="tools_pb_build"):
        if not (pb_session or "").strip():
            st.warning("Session id required")
        else:
            args = [
                "wave-a",
                "briefs",
                pb_session.strip(),
                "-o",
                (pb_out or "artifacts/briefs_session.json").strip(),
            ]
            code, output = rt.run_cli(args, timeout=60)
            st.code(output or "(done)", language="text")
            if code == 0:
                st.success("Brief log written — refresh Dashboard to list it")
            else:
                st.error(f"exit {code}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Run validate", width="stretch", key="tools_validate"):
            code, output = rt.run_cli(["validate"])
            st.code(output, language="text")
            if code == 0:
                st.success("Passed")
            else:
                st.warning("Completed with issues")
    with col2:
        if st.button("Generate PDF report", width="stretch", key="tools_report"):
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "production_report.pdf"
                code, output = rt.run_cli(["report", "--output", str(out)])
                if code == 0 and out.exists():
                    st.download_button(
                        "⬇️ Download production_report.pdf",
                        data=out.read_bytes(),
                        file_name="production_report.pdf",
                        mime="application/pdf",
                        key="tools_report_download",
                    )
                else:
                    st.error(output or "Report generation failed")

    st.divider()
    st.subheader("🎬 Agent roster")
    if rt.AGENTS:
        for group, names in rt.AGENTS.items():
            st.markdown(f"**{group}**")
            for name in names:
                st.markdown(f"- {name}")
    else:
        st.caption(f"{rt.core_agent_count()} core agents + i2i + NSFW specialists (opt-in)")