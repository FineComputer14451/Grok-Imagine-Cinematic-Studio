"""UI-agnostic studio core shared by CLI, TUI, Web, and future API shells.

PR1 introduces ``studio_core.services.dashboard`` (snapshot aggregation only).
Rich/Textual/Streamlit rendering stays in their respective UI packages.
"""

from __future__ import annotations

__all__ = ["__version__"]

# Keep in sync with repo VERSION when packaging; runtime prefers VERSION file.
__version__ = "3.9.0"
