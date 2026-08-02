"""Service-layer facades over domain tools (no UI framework imports)."""

from __future__ import annotations

from studio_core.services.dashboard import build_studio_dashboard

__all__ = ["build_studio_dashboard"]
