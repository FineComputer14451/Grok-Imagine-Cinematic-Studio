"""HTTP control plane over studio_core (optional FastAPI)."""

from __future__ import annotations

__all__ = ["create_app"]


def __getattr__(name: str):
    if name == "create_app":
        from studio_api.app import create_app

        return create_app
    raise AttributeError(name)
