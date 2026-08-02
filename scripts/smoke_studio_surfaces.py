#!/usr/bin/env python3
"""Smoke-check studio_core + optional surfaces (no long-running servers)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))


def main() -> int:
    errors: list[str] = []

    try:
        from studio_core.services.dashboard import build_studio_dashboard

        snap = build_studio_dashboard()
        assert "studio_version" in snap
        print("OK  studio_core.dashboard", snap.get("studio_version"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"dashboard: {exc}")
        print("FAIL studio_core.dashboard", exc)

    try:
        from studio_core.services.execute import execute_action

        r = execute_action("status", mode="inprocess", timeout=60.0)
        assert r.ok, r.stderr
        print("OK  studio_core.execute status")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"execute: {exc}")
        print("FAIL studio_core.execute", exc)

    try:
        from studio_core.services.actions import ACTIONS

        assert len(ACTIONS) >= 10
        print("OK  studio_core.actions", len(ACTIONS))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"actions: {exc}")
        print("FAIL studio_core.actions", exc)

    try:
        import fastapi  # noqa: F401
        from fastapi.testclient import TestClient
        from studio_api.app import create_app

        client = TestClient(create_app())
        assert client.get("/health").status_code == 200
        assert client.get("/").status_code == 200
        print("OK  studio_api /health")
    except ImportError:
        print("SKIP studio_api (fastapi not installed)")
    except Exception as exp:  # noqa: BLE001
        errors.append(f"api: {exp}")
        print("FAIL studio_api", exp)

    try:
        import nicegui  # noqa: F401
        from web_nicegui.app import create_app as create_nicegui

        create_nicegui()
        print("OK  web_nicegui create_app")
    except ImportError:
        print("SKIP web_nicegui (nicegui not installed)")
    except Exception as exp:  # noqa: BLE001
        errors.append(f"nicegui: {exp}")
        print("FAIL web_nicegui", exp)

    if errors:
        print("SMOKE FAILED:", "; ".join(errors))
        return 1
    print("SMOKE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
