from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..deps import StudioBackend, get_backend, require_api_key, studio_version
from ..schemas.quota import QuotaEstimateIn, QuotaOut
from ..services.mock_data import mock_snapshot

router = APIRouter(
    prefix="/api/v1/quota",
    tags=["quota"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/dashboard", response_model=QuotaOut)
def quota_dashboard(backend: StudioBackend = Depends(get_backend)) -> QuotaOut:
    """Session quota dashboard (+ alignment when available)."""
    dash_fn = backend.get("quota_dashboard")
    if callable(dash_fn):
        try:
            dash = dict(dash_fn() or {})
            alignment = None
            align_fn = backend.get("ledger_recon_alignment")
            if callable(align_fn):
                try:
                    alignment = align_fn()
                except Exception:
                    alignment = None
            return QuotaOut(
                source="live",
                studio_version=studio_version(backend),
                dashboard=dash,
                alignment=alignment if isinstance(alignment, dict) else None,
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    snap = mock_snapshot()
    return QuotaOut(
        source="mock",
        studio_version=studio_version(backend),
        dashboard=dict(snap.get("quota") or {}),
        alignment=dict(snap.get("quota_alignment") or {}),
    )


@router.post("/estimate", response_model=QuotaOut)
def quota_estimate(
    body: QuotaEstimateIn,
    backend: StudioBackend = Depends(get_backend),
) -> QuotaOut:
    """Estimate production cost + risk for duration/complexity (Streamlit session twin)."""
    est_fn = backend.get("estimate_production")
    risk_fn = backend.get("assess_budget_risk")
    dash_fn = backend.get("quota_dashboard")

    if callable(est_fn):
        try:
            kwargs = {
                "complexity": body.complexity.lower(),
                "fast_mode": body.fast_mode,
            }
            if body.video_model:
                kwargs["video_model"] = body.video_model
            try:
                est = est_fn(body.duration_sec, **kwargs)
            except TypeError:
                est = est_fn(body.duration_sec)
            dash = dict(dash_fn() or {}) if callable(dash_fn) else {}
            risk = None
            if callable(risk_fn):
                try:
                    risk = risk_fn(
                        est,
                        tier=body.tier,
                        budget_remaining=dash.get("budget_remaining"),
                    )
                except TypeError:
                    risk = risk_fn(est)
            return QuotaOut(
                source="live",
                studio_version=studio_version(backend),
                dashboard=dash,
                estimate=est if isinstance(est, dict) else {"raw": est},
                risk=risk if isinstance(risk, dict) else None,
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    # mock estimate
    low = max(20, body.duration_sec * 2)
    high = low * 2
    return QuotaOut(
        source="mock",
        studio_version=studio_version(backend),
        dashboard=dict(mock_snapshot().get("quota") or {}),
        estimate={
            "credits_low": low,
            "credits_high": high,
            "usd_low": round(low * 0.01, 2),
            "usd_high": round(high * 0.01, 2),
            "duration_sec": body.duration_sec,
            "complexity": body.complexity,
        },
        risk={"risk_level": "moderate", "tier": body.tier},
    )
