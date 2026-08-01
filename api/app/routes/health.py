from __future__ import annotations

from fastapi import APIRouter, Depends

from ..config import get_settings
from ..deps import StudioBackend, get_backend, require_api_key, studio_version
from ..schemas.common import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health(backend: StudioBackend = Depends(get_backend)) -> HealthOut:
    """Liveness + whether monorepo tools resolved."""
    return HealthOut(
        status="ok" if backend.live else "degraded",
        studio_version=studio_version(backend),
        tools_available=backend.live,
        studio_root=str(backend.root) if backend.root else None,
    )


@router.get("/api/v1/meta", dependencies=[Depends(require_api_key)])
def meta(backend: StudioBackend = Depends(get_backend)) -> dict:
    settings = get_settings()
    return {
        "name": settings.app_name,
        "studio_version": studio_version(backend),
        "api_prefix": settings.api_prefix,
        "source": "live" if backend.live else "mock",
        "modules": sorted(backend.modules.keys()),
    }
