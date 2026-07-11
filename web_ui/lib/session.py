"""Session defaults, production options, and shared session-state helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st

from lib import runtime as rt

PRODUCTION_OPTIONS: dict[str, list[str]] = {
    "genres": [
        "Sci-Fi",
        "Psychological Horror",
        "Action",
        "Drama",
        "Cyberpunk",
        "Intimate Drama",
        "Thriller",
        "Neo-Noir",
        "Fantasy",
        "Documentary Style",
    ],
    "directors": [
        "Denis Villeneuve",
        "Christopher Nolan",
        "David Fincher",
        "Roger Deakins",
        "Zack Snyder",
        "Default",
    ],
    "complexities": ["Low", "Medium", "High", "Extreme"],
    "tiers": ["supergrok_pro", "supergrok_heavy", "custom"],
    "reasoning_levels": ["low", "medium", "high"],
}

SESSION_DEFAULTS: dict[str, Any] = {
    "genre": PRODUCTION_OPTIONS["genres"][0],
    "director": PRODUCTION_OPTIONS["directors"][0],
    "video_model": rt.DEFAULT_IMAGINE_VIDEO_MODEL,
    "chat_model": rt.DEFAULT_XAI_CHAT_MODEL,
    "duration": 60,
    "complexity": "Medium",
    "fast_mode": False,
    "quota_tier": PRODUCTION_OPTIONS["tiers"][0],
    "imagine_region": "us-east-1",
    "nsfw_opt_in": False,
    "xai_api_key": "",
    # Grok 4.5 operating preferences
    "reasoning_level": "high",
    "prompt_cache_key": "",
}


def select_index(options: list, value, default: int = 0) -> int:
    try:
        return options.index(value)
    except ValueError:
        return default


def init_session_defaults() -> None:
    for key, value in SESSION_DEFAULTS.items():
        st.session_state.setdefault(key, value)
    # Coerce chat default to grok-4.5 if session still holds a removed slug
    if rt.MODELS_AVAILABLE and rt.XAI_CHAT_MODELS:
        chat = st.session_state.get("chat_model")
        if chat not in rt.XAI_CHAT_MODELS:
            st.session_state.chat_model = rt.DEFAULT_XAI_CHAT_MODEL
    if rt.MODELS_AVAILABLE and rt.IMAGINE_VIDEO_MODELS:
        video = st.session_state.get("video_model")
        if video not in rt.IMAGINE_VIDEO_MODELS:
            st.session_state.video_model = rt.DEFAULT_IMAGINE_VIDEO_MODEL
    # Streamlit Community Cloud secrets → env for imagine_client / CLI subprocesses
    rt.sync_xai_api_key_to_environ()


def clip_story(text: str, max_len: int) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"


def complexity_for_estimate() -> str:
    return str(st.session_state.get("complexity", "Medium")).lower()


def effective_prompt_cache_key(project_slug: str | None = None) -> str | None:
    """Stable cache key for multi-turn grok-4.5 loops (project slug preferred)."""
    key = (st.session_state.get("prompt_cache_key") or "").strip()
    if key:
        return key
    if project_slug:
        return project_slug
    return None


def session_quota_snapshot() -> dict[str, Any] | None:
    """Return estimate, dashboard, and risk for current session settings."""
    if not rt.QUOTA_AVAILABLE:
        return None
    dash = rt.quota_dashboard()
    est = rt.estimate_production(
        st.session_state.duration,
        complexity=complexity_for_estimate(),
        fast_mode=st.session_state.fast_mode,
        video_model=st.session_state.video_model,
    )
    risk = rt.assess_budget_risk(
        est,
        tier=st.session_state.quota_tier,
        budget_remaining=dash.get("budget_remaining"),
    )
    return {
        "estimate": est,
        "dashboard": dash,
        "risk": risk,
        "model_stack": rt.session_model_stack(),
    }
