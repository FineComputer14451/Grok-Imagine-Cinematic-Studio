from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ..deps import StudioBackend, get_backend, require_api_key, studio_version

router = APIRouter(
    prefix="/api/v1/models",
    tags=["models"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/verify")
def models_verify(backend: StudioBackend = Depends(get_backend)) -> dict[str, Any]:
    """Model stack compatibility (cached on Streamlit side; live here)."""
    fn = backend.get("verify_model_compatibility")
    if callable(fn):
        try:
            result = fn()
            if isinstance(result, dict):
                return {
                    "source": "live",
                    "studio_version": studio_version(backend),
                    **result,
                }
            return {
                "source": "live",
                "studio_version": studio_version(backend),
                "ok": bool(result),
                "raw": result,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "source": "live",
                "studio_version": studio_version(backend),
                "ok": False,
                "issues": [str(exc)],
                "warnings": [],
            }

    return {
        "source": "mock",
        "studio_version": studio_version(backend),
        "ok": True,
        "compatible": True,
        "issues": [],
        "warnings": [],
        "stack": {
            "cinematic": "grok-4.5",
            "build": "grok-4.5",
            "imagine_video": "grok-imagine-video-1.5",
        },
    }
