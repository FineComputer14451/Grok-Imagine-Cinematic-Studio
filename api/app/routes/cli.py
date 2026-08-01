from __future__ import annotations

from fastapi import APIRouter, Depends, Path

from ..deps import StudioBackend, get_backend, require_api_key
from ..schemas.common import CliActionIn, CliActionOut
from ..services.cli_bridge import ACTION_ARGS, run_cli_action

router = APIRouter(
    prefix="/api/v1/cli",
    tags=["cli"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/actions")
def list_actions() -> dict:
    """Allowed health/repair actions (Streamlit dashboard buttons / TUI keys)."""
    return {
        "actions": sorted(ACTION_ARGS.keys()),
        "map": ACTION_ARGS,
        "streamlit_parity": {
            "doctor": "Doctor (quick)",
            "validate": "Validate",
            "quota-sync": "Quota sync",
            "models-verify": "Models verify",
        },
    }


@router.post(
    "/{action}",
    response_model=CliActionOut,
    summary="Run a safe CLI health action",
)
def post_action(
    action: str = Path(..., description="doctor | validate | quota-sync | models-verify"),
    body: CliActionIn | None = None,
    backend: StudioBackend = Depends(get_backend),
) -> CliActionOut:
    body = body or CliActionIn()
    return run_cli_action(
        backend,
        action,
        extra_args=body.args,
        timeout_sec=body.timeout_sec,
    )
