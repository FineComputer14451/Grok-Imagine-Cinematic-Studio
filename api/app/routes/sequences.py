from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..deps import StudioBackend, get_backend, require_api_key, source_label, studio_version
from ..schemas.sequences import (
    SequenceInitIn,
    SequenceInitOut,
    SequenceListOut,
    SequenceRow,
)
from ..services.mock_data import mock_snapshot

router = APIRouter(
    prefix="/api/v1/sequences",
    tags=["sequences"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=SequenceListOut)
def list_sequences(backend: StudioBackend = Depends(get_backend)) -> SequenceListOut:
    fn = backend.get("list_sequences")
    if callable(fn):
        try:
            raw = fn() or []
            rows = [_normalize_sequence(s) for s in raw]
            return SequenceListOut(
                source="live",
                studio_version=studio_version(backend),
                sequences=rows,
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    snap = mock_snapshot()
    rows = [
        SequenceRow(
            name=s["name"],
            slug=s.get("slug"),
            clips=int(s.get("clips") or 0),
            target_duration=s.get("target_duration"),
            health=s.get("health"),
        )
        for s in snap.get("sequences") or []
    ]
    return SequenceListOut(
        source="mock",
        studio_version=studio_version(backend),
        sequences=rows,
    )


@router.post("/init", response_model=SequenceInitOut)
def init_sequence(
    body: SequenceInitIn,
    backend: StudioBackend = Depends(get_backend),
) -> SequenceInitOut:
    """Create sequence scaffold (create_sequence_scaffold or mock)."""
    fn = backend.get("create_sequence_scaffold")
    if callable(fn):
        try:
            try:
                result = fn(body.name, target_duration=body.target_duration)
            except TypeError:
                result = fn(body.name)
            row = _normalize_sequence(
                result if isinstance(result, dict) else {"name": body.name}
            )
            return SequenceInitOut(
                source="live",
                studio_version=studio_version(backend),
                sequence=row,
                message=f"Initialized sequence {row.name}",
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return SequenceInitOut(
        source=source_label(backend),  # type: ignore[arg-type]
        studio_version=studio_version(backend),
        sequence=SequenceRow(
            name=body.name,
            clips=0,
            target_duration=body.target_duration,
            health="draft",
        ),
        message=f"Mock sequence init · {body.name}",
    )


def _normalize_sequence(raw: object) -> SequenceRow:
    if not isinstance(raw, dict):
        return SequenceRow(name=str(raw))
    return SequenceRow(
        id=str(raw.get("id") or raw.get("slug") or "") or None,
        name=str(raw.get("name") or raw.get("slug") or "unknown"),
        slug=raw.get("slug"),
        clips=int(raw.get("clips") or raw.get("clip_count") or 0),
        target_duration=raw.get("target_duration") or raw.get("duration"),
        health=str(raw.get("health") or raw.get("status") or "") or None,
        chain_qa_status=raw.get("chain_qa_status") or raw.get("chain_qa"),
        raw=raw,
    )
