from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from fastapi import Header, HTTPException, status

from .config import get_settings, resolve_studio_root


@dataclass
class StudioBackend:
    """Resolved access to monorepo tools (or mock)."""

    root: Path | None
    live: bool
    modules: dict[str, Any] = field(default_factory=dict)

    def get(self, name: str) -> Any | None:
        return self.modules.get(name)


_backend: StudioBackend | None = None


def get_backend() -> StudioBackend:
    global _backend
    if _backend is None:
        _backend = _load_backend()
    return _backend


def _load_backend() -> StudioBackend:
    root = resolve_studio_root()
    modules: dict[str, Any] = {}
    if root is None:
        return StudioBackend(root=None, live=False, modules={})

    tools = root / "tools"
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    loaders: list[tuple[str, Callable[[], Any]]] = [
        ("build_studio_dashboard", lambda: __import__("cli.dashboard", fromlist=["build_studio_dashboard"]).build_studio_dashboard),
        ("list_characters", lambda: __import__("character_dna", fromlist=["list_characters"]).list_characters),
        ("lock_to_identity_bank", lambda: __import__("character_dna", fromlist=["lock_to_identity_bank"]).lock_to_identity_bank),
        ("list_sequences", lambda: __import__("sequence_chain", fromlist=["list_sequences"]).list_sequences),
        ("create_sequence_scaffold", lambda: __import__("sequence_chain", fromlist=["create_sequence_scaffold"]).create_sequence_scaffold),
        ("quota_dashboard", lambda: __import__("quota_optimizer", fromlist=["quota_dashboard"]).quota_dashboard),
        ("estimate_production", lambda: __import__("quota_optimizer", fromlist=["estimate_production"]).estimate_production),
        ("assess_budget_risk", lambda: __import__("quota_optimizer", fromlist=["assess_budget_risk"]).assess_budget_risk),
        ("ledger_recon_alignment", lambda: __import__("quota_sync", fromlist=["ledger_recon_alignment"]).ledger_recon_alignment),
        ("strip_severity", lambda: __import__("cli.tui.widgets", fromlist=["strip_severity"]).strip_severity),
        ("collect_home_alerts", lambda: __import__("cli.tui.widgets", fromlist=["collect_home_alerts"]).collect_home_alerts),
        ("verify_model_compatibility", lambda: __import__("models", fromlist=["verify_model_compatibility"]).verify_model_compatibility),
        ("STUDIO_VERSION", lambda: __import__("cli.shared", fromlist=["STUDIO_VERSION"]).STUDIO_VERSION),
    ]

    for name, loader in loaders:
        try:
            modules[name] = loader()
        except Exception:
            continue

    live = "build_studio_dashboard" in modules
    return StudioBackend(root=root, live=live, modules=modules)


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    expected = get_settings().studio_api_key
    if not expected:
        return
    if not x_api_key or x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key",
        )


def source_label(backend: StudioBackend) -> str:
    return "live" if backend.live else "mock"


def studio_version(backend: StudioBackend) -> str:
    ver = backend.get("STUDIO_VERSION")
    if isinstance(ver, str) and ver:
        return ver
    return get_settings().studio_version
