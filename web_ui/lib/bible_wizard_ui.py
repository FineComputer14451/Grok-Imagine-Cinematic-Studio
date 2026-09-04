"""Streamlit multi-step Guided Production Bible form.

Uses shared stage data / kwargs mapping from ``cli.bible_stages``.
Final assembly always goes through ``build_production_bible``.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from lib import runtime as rt

_STEP_KEY = "bible_wizard_step"
_ANSWERS_KEY = "bible_wizard_answers"
_SUMMARY_KEY = "bible_wizard_summary"


def _ensure_state() -> None:
    if _STEP_KEY not in st.session_state:
        st.session_state[_STEP_KEY] = 0
    if _ANSWERS_KEY not in st.session_state:
        st.session_state[_ANSWERS_KEY] = {
            "genre": st.session_state.get("genre", "Cinematic"),
            "director_signature": st.session_state.get("director"),
            "complexity": st.session_state.get("complexity", "Medium"),
            "target_duration_seconds": st.session_state.get("duration", 60),
            "video_model": st.session_state.get(
                "video_model", rt.DEFAULT_IMAGINE_VIDEO_MODEL
            ),
            "chat_model": st.session_state.get(
                "chat_model", rt.DEFAULT_XAI_CHAT_MODEL
            ),
        }


def _widget_key(stage_id: str, field_key: str) -> str:
    return f"bw_{stage_id}_{field_key}"


def _collect_field_widgets(stage: dict[str, Any], answers: dict[str, Any]) -> None:
    """Render widgets for stage fields and write values into answers."""
    for field in stage["fields"]:
        key = field["key"]
        label = field["prompt"]
        help_txt = f"e.g. {field['example']}" if field.get("example") else None
        current = answers.get(key, field.get("default"))
        wkey = _widget_key(stage["id"], key)

        if key == "target_duration_seconds":
            try:
                default_n = int(current) if current is not None else 60
            except (TypeError, ValueError):
                default_n = 60
            answers[key] = st.number_input(
                label,
                min_value=1,
                max_value=3600,
                value=default_n,
                step=1,
                help=help_txt,
                key=wkey,
            )
        elif key == "video_model" and rt.MODELS_AVAILABLE and rt.IMAGINE_VIDEO_MODELS:
            options = rt.ordered_video_model_slugs()
            # Also allow short aliases users type in CLI
            for alias in ("1.0", "1.5", "grok-imagine-video", "grok-imagine-video-1.5"):
                if alias not in options:
                    options.append(alias)
            idx = 0
            if current in options:
                idx = options.index(current)
            elif current is None and rt.DEFAULT_IMAGINE_VIDEO_MODEL in options:
                idx = options.index(rt.DEFAULT_IMAGINE_VIDEO_MODEL)
            answers[key] = st.selectbox(
                label,
                options,
                index=idx,
                help=(help_txt or "") + " · 1.0 cost default; 1.5 for native audio",
                key=wkey,
                format_func=lambda s: (
                    rt.format_video_model_label(s)
                    if s in rt.IMAGINE_VIDEO_MODELS
                    else s
                ),
            )
        elif key == "chat_model" and rt.MODELS_AVAILABLE and rt.XAI_CHAT_MODELS:
            options = rt.ordered_chat_model_slugs()
            idx = 0
            if current in options:
                idx = options.index(current)
            elif rt.DEFAULT_XAI_CHAT_MODEL in options:
                idx = options.index(rt.DEFAULT_XAI_CHAT_MODEL)
            answers[key] = st.selectbox(
                label,
                options,
                index=idx,
                help=(help_txt or "") + " · grok-4.6 default; grok-4.3 = 1M opt-in only",
                key=wkey,
                format_func=rt.format_chat_model_label,
            )
        elif key in ("logline", "characters_text", "world_text", "tech_notes"):
            answers[key] = st.text_area(
                label,
                value=str(current) if current is not None else "",
                help=help_txt,
                height=80,
                key=wkey,
            )
        else:
            answers[key] = st.text_input(
                label,
                value=str(current) if current is not None else "",
                help=help_txt,
                key=wkey,
            )


def render_bible_wizard() -> None:
    """Render Guided Bible Creator section on the Production page."""
    st.subheader("📖 Guided Bible Creator")
    st.caption(
        "Step-by-step Production Bible — same stages as `create-bible --wizard`. "
        "Quick path: use Export Bible above."
    )

    if not rt.BIBLE_STAGES_AVAILABLE or not rt.PRODUCTION_AVAILABLE:
        st.info("Guided wizard unavailable (production / stages modules not loaded).")
        return

    _ensure_state()
    stages = rt.STAGES
    step = int(st.session_state[_STEP_KEY])
    step = max(0, min(step, len(stages) - 1))
    st.session_state[_STEP_KEY] = step
    answers: dict[str, Any] = st.session_state[_ANSWERS_KEY]
    stage = stages[step]
    n = len(stages)

    st.progress((step + 1) / n, text=f"Stage {step + 1}/{n}: {stage['title']}")

    if stage["id"] != "review":
        _collect_field_widgets(stage, answers)
        st.session_state[_ANSWERS_KEY] = answers
    else:
        st.markdown("**Review answers**")
        try:
            kwargs = rt.answers_to_kwargs(answers)
            st.json(kwargs)
            notes = rt.build_notes(answers)
            if notes:
                st.markdown("**Notes rollup**")
                st.code(notes)
        except ValueError as exc:
            st.error(str(exc))
            kwargs = None

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("← Back", width="stretch", disabled=step <= 0, key="bw_back"):
            st.session_state[_STEP_KEY] = step - 1
            st.rerun()
    with b2:
        if stage["id"] != "review":
            if st.button("Next →", width="stretch", type="primary", key="bw_next"):
                # Sync any widget values already written into answers
                errs = rt.validate_answers(stage["id"], answers)
                # Apply defaults for blank required-with-default
                for field in stage["fields"]:
                    key = field["key"]
                    val = answers.get(key)
                    blank = val is None or (isinstance(val, str) and not str(val).strip())
                    if blank and field.get("default") is not None:
                        answers[key] = field["default"]
                st.session_state[_ANSWERS_KEY] = answers
                errs = rt.validate_answers(stage["id"], answers)
                if errs:
                    for e in errs:
                        st.error(e)
                else:
                    st.session_state[_STEP_KEY] = step + 1
                    st.rerun()
        else:
            if st.button(
                "Generate Bible",
                width="stretch",
                type="primary",
                key="bw_generate",
                disabled=kwargs is None,
            ):
                try:
                    bible = rt.build_production_bible(**rt.answers_to_kwargs(answers))
                    st.session_state.last_bible = bible
                    st.session_state[_SUMMARY_KEY] = rt.summary_and_next_steps(bible)
                    st.success("Bible ready for download (see preview below)")
                    st.rerun()
                except (ValueError, TypeError) as exc:
                    st.error(f"Could not build bible: {exc}")
    with b3:
        if st.button("Reset wizard", width="stretch", key="bw_reset"):
            st.session_state[_STEP_KEY] = 0
            st.session_state.pop(_ANSWERS_KEY, None)
            st.session_state.pop(_SUMMARY_KEY, None)
            for k in list(st.session_state.keys()):
                if isinstance(k, str) and k.startswith("bw_") and k not in (
                    "bw_back",
                    "bw_next",
                    "bw_generate",
                    "bw_reset",
                ):
                    del st.session_state[k]
            st.rerun()

    if summary := st.session_state.get(_SUMMARY_KEY):
        st.markdown("**Next steps**")
        st.code(summary)
