"""FastAPI control plane — dashboard + ActionSpec execute."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_TOOLS = _ROOT / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))


def _studio_version() -> str:
    vf = _ROOT / "VERSION"
    try:
        return vf.read_text(encoding="utf-8").strip() or "3.8.9"
    except OSError:
        return "3.8.9"


def _execute_body_model():
    from pydantic import BaseModel, Field

    class ExecuteBody(BaseModel):
        answers: dict[str, str] = Field(default_factory=dict)
        mode: str = Field(
            default="inprocess",
            description="'inprocess' (default) or 'subprocess'",
        )
        timeout: float = Field(default=90.0, ge=1.0, le=600.0)

    return ExecuteBody


def create_app() -> Any:
    """Build FastAPI app (lazy import so core install need not include FastAPI)."""
    try:
        from fastapi import Body, FastAPI, HTTPException
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "FastAPI is required for the API control plane.\n"
            "Install with:\n"
            "  pip install -r requirements-api.txt\n"
        ) from exc

    from studio_core.services.actions import ACTIONS, get_action
    from studio_core.services.dashboard import build_studio_dashboard
    from studio_core.services.execute import execute_action

    ExecuteBody = _execute_body_model()

    app = FastAPI(
        title="Grok Imagine Cinematic Studio API",
        description=(
            "Thin control plane over studio_core.services "
            "(dashboard snapshot + ActionSpec execute). "
            "Independent community project — not affiliated with xAI."
        ),
        version=_studio_version(),
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "ok": True,
            "studio_version": _studio_version(),
            "actions": len(ACTIONS),
        }

    @app.get("/v1/dashboard")
    def dashboard() -> dict[str, Any]:
        try:
            return build_studio_dashboard()
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/v1/actions")
    def list_actions() -> dict[str, Any]:
        items = []
        for spec in ACTIONS.values():
            items.append(
                {
                    "id": spec.id,
                    "label": spec.label,
                    "group": spec.group,
                    "description": spec.description,
                    "needs_confirm": spec.needs_confirm,
                    "has_form": bool(spec.fields),
                    "surfaces": sorted(spec.surfaces),
                    "base_argv": list(spec.base_argv),
                    "fields": [
                        {
                            "key": f.key,
                            "label": f.label,
                            "required": f.required,
                            "coerce": f.coerce,
                            "choices": sorted(f.choices) if f.choices else None,
                            "default": f.default,
                        }
                        for f in spec.fields
                    ],
                }
            )
        items.sort(key=lambda x: x["id"])
        return {"count": len(items), "actions": items}

    @app.get("/v1/actions/{action_id}")
    def get_action_detail(action_id: str) -> dict[str, Any]:
        try:
            spec = get_action(action_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown action: {action_id}") from exc
        return {
            "id": spec.id,
            "label": spec.label,
            "group": spec.group,
            "description": spec.description,
            "needs_confirm": spec.needs_confirm,
            "base_argv": list(spec.base_argv),
            "surfaces": sorted(spec.surfaces),
            "fields": [
                {
                    "key": f.key,
                    "label": f.label,
                    "required": f.required,
                    "coerce": f.coerce,
                    "choices": sorted(f.choices) if f.choices else None,
                    "default": f.default,
                    "help": f.help,
                }
                for f in spec.fields
            ],
        }

    @app.post("/v1/actions/{action_id}/execute")
    def run_action(
        action_id: str,
        payload: dict[str, Any] = Body(default_factory=dict),  # type: ignore[assignment]
    ) -> dict[str, Any]:
        if action_id not in ACTIONS:
            raise HTTPException(status_code=404, detail=f"Unknown action: {action_id}")
        try:
            body = ExecuteBody.model_validate(payload or {})
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        mode = (body.mode or "inprocess").strip().lower()
        if mode not in {"inprocess", "subprocess"}:
            raise HTTPException(
                status_code=400,
                detail="mode must be 'inprocess' or 'subprocess'",
            )
        result = execute_action(
            action_id,
            body.answers,
            mode=mode,  # type: ignore[arg-type]
            timeout=body.timeout,
            cwd=_ROOT,
        )
        return {
            "ok": result.ok,
            "action_id": result.action_id or action_id,
            "argv": result.argv,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "errors": list(result.errors or []),
            "timed_out": result.timed_out,
            "mode": result.mode,
            "output": result.output,
        }

    return app


def run_api(
    *,
    host: str = "127.0.0.1",
    port: int = 8090,
    reload: bool = False,
) -> None:
    """Start uvicorn (blocking)."""
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "uvicorn is required.\n  pip install -r requirements-api.txt\n"
        ) from exc
    uvicorn.run(
        "studio_api.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    run_api()
