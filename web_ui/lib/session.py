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
    "nsfw_opt_in": False,
    "xai_api_key": "",
}


def select_index(options: list, value, default: int = 0) -> int:
    try:
        return options.index(value)
    except ValueError:
        return default


def init_session_defaults() -> None:
    for key, value in SESSION_DEFAULTS.items():
        st.session_state.setdefault(key, value)


def clip_story(text: str, max_len: int) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"


def complexity_for_estimate() -> str:
    return str(st.session_state.get("complexity", "Medium")).lower()


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
    return {"estimate": est, "dashboard": dash, "risk": risk}