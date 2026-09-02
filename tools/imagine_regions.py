#!/usr/bin/env python3
"""
Region-aware routing for xAI Imagine API requests.

Supports IMAGINE_REGION env, project state persistence, and failover chain.
"""

from __future__ import annotations

import os
from typing import Any

from project_state import load_project_state, save_project_state

IMAGINE_REGIONS: dict[str, dict[str, Any]] = {
    "us-east-1": {"label": "US East (Virginia)", "priority": 1},
    "eu-west-1": {"label": "EU West (Ireland)", "priority": 2},
    "us-west-2": {"label": "US West (Oregon)", "priority": 3},
}

DEFAULT_REGION = "us-east-1"
# 403/429 are policy, geo, or rate-limit denies — do not hop regions (AUP).
POLICY_FAIL_CLOSED_CODES = frozenset({403, 429})
FAILOVER_STATUS_CODES = frozenset({500, 502, 503, 504})


def default_imagine_settings() -> dict[str, Any]:
    return {
        "region": DEFAULT_REGION,
        "failover_regions": ["us-east-1", "eu-west-1", "us-west-2"],
        "last_region_used": None,
        "last_failover_at": None,
        "failover_count": 0,
    }


def ensure_imagine_settings(state: dict[str, Any]) -> dict[str, Any]:
    if "imagine_settings" not in state or not isinstance(state.get("imagine_settings"), dict):
        state["imagine_settings"] = default_imagine_settings()
    settings = state["imagine_settings"]
    for key, val in default_imagine_settings().items():
        settings.setdefault(key, val)
    return settings


def get_region_from_env() -> str | None:
    region = os.getenv("IMAGINE_REGION", "").strip()
    return region if region in IMAGINE_REGIONS else None


def get_active_region(state: dict[str, Any] | None = None) -> str:
    env_region = get_region_from_env()
    if env_region:
        return env_region
    if state is None:
        state = load_project_state()
    settings = ensure_imagine_settings(state)
    region = settings.get("region", DEFAULT_REGION)
    return region if region in IMAGINE_REGIONS else DEFAULT_REGION


def get_failover_chain(primary: str | None = None, state: dict[str, Any] | None = None) -> list[str]:
    if state is None:
        state = load_project_state()
    settings = ensure_imagine_settings(state)
    chain = list(settings.get("failover_regions") or [])
    primary = primary or get_active_region(state)
    ordered: list[str] = []
    for r in [primary, *chain]:
        if r in IMAGINE_REGIONS and r not in ordered:
            ordered.append(r)
    return ordered or [DEFAULT_REGION]


def set_imagine_region(
    region: str,
    *,
    failover_regions: list[str] | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    if region not in IMAGINE_REGIONS:
        raise ValueError(f"Unknown region: {region}. Choose: {', '.join(IMAGINE_REGIONS)}")
    state = load_project_state()
    settings = ensure_imagine_settings(state)
    settings["region"] = region
    if failover_regions:
        settings["failover_regions"] = [r for r in failover_regions if r in IMAGINE_REGIONS]
    if persist:
        save_project_state(state)
    return settings


def record_region_used(region: str, *, failed: bool = False) -> None:
    state = load_project_state()
    settings = ensure_imagine_settings(state)
    settings["last_region_used"] = region
    if failed:
        settings["failover_count"] = settings.get("failover_count", 0) + 1
        from datetime import datetime, timezone
        settings["last_failover_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    save_project_state(state)


def region_request_headers(region: str) -> dict[str, str]:
    """Headers and metadata sent with Imagine API calls."""
    return {
        "x-xai-region": region,
        "X-Region": region,
    }


def region_payload_fields(region: str) -> dict[str, str]:
    return {"region": region}