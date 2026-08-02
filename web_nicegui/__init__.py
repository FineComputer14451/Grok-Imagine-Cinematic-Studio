"""NiceGUI web shell for Grok Imagine Cinematic Studio (PR4+).

Read-only dashboard first; later pages call ``studio_core.services.execute``.
Optional install: ``pip install -r requirements-nicegui.txt``
"""

from __future__ import annotations

__all__ = ["run_web"]


def __getattr__(name: str):
    if name == "run_web":
        from web_nicegui.app import run_web

        return run_web
    raise AttributeError(name)
