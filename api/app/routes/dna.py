from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..deps import StudioBackend, get_backend, require_api_key, source_label, studio_version
from ..schemas.dna import DnaListOut, DnaLockIn, DnaLockOut, DnaProfile
from ..services.mock_data import mock_snapshot

router = APIRouter(
    prefix="/api/v1/dna",
    tags=["dna"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=DnaListOut)
def list_dna(backend: StudioBackend = Depends(get_backend)) -> DnaListOut:
    """List character DNA profiles (live list_characters or mock)."""
    fn = backend.get("list_characters")
    if callable(fn):
        try:
            raw = fn() or []
            chars = [_normalize_character(c) for c in raw]
            return DnaListOut(
                source="live",
                studio_version=studio_version(backend),
                characters=chars,
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    snap = mock_snapshot()
    chars = [
        DnaProfile(
            name=c["name"],
            slug=c.get("slug"),
            status=c.get("status", "pending"),
            locked=c.get("status") == "locked",
        )
        for c in snap.get("characters") or []
    ]
    return DnaListOut(
        source="mock",
        studio_version=studio_version(backend),
        characters=chars,
    )


@router.post("/lock", response_model=DnaLockOut)
def lock_dna(
    body: DnaLockIn,
    backend: StudioBackend = Depends(get_backend),
) -> DnaLockOut:
    """
    Lock identity into the bank.

    Live path prefers `lock_to_identity_bank` when present; otherwise mock OK.
    """
    name = (body.name or body.slug or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="name or slug required")

    lock_fn = backend.get("lock_to_identity_bank")
    if callable(lock_fn):
        try:
            result = lock_fn(name)
            profile = _normalize_character(result if isinstance(result, dict) else {"name": name, "status": "locked"})
            profile.locked = True
            return DnaLockOut(
                source="live",
                studio_version=studio_version(backend),
                character=profile,
                message=f"Locked {profile.name}",
            )
        except TypeError:
            # Signature may differ across versions — try slug kw
            try:
                result = lock_fn(slug=name)  # type: ignore[call-arg]
                profile = _normalize_character(
                    result if isinstance(result, dict) else {"name": name, "status": "locked"}
                )
                profile.locked = True
                return DnaLockOut(
                    source="live",
                    studio_version=studio_version(backend),
                    character=profile,
                    message=f"Locked {profile.name}",
                )
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(status_code=500, detail=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return DnaLockOut(
        source=source_label(backend),  # type: ignore[arg-type]
        studio_version=studio_version(backend),
        character=DnaProfile(name=name, status="locked", locked=True),
        message=f"Mock lock · {name}",
    )


def _normalize_character(raw: object) -> DnaProfile:
    if not isinstance(raw, dict):
        return DnaProfile(name=str(raw), status="pending")
    status = str(raw.get("status") or raw.get("lock") or "pending")
    locked = status.lower() in {"locked", "lock", "active"}
    return DnaProfile(
        id=str(raw.get("id") or raw.get("slug") or "") or None,
        name=str(raw.get("name") or raw.get("slug") or "unknown"),
        slug=raw.get("slug"),
        status=status,
        locked=locked,
        drift_score=raw.get("drift_score"),
        traits=list(raw.get("traits") or []),
        looks=raw.get("looks") or raw.get("description"),
        project=raw.get("project") or raw.get("project_id"),
        raw=raw,
    )
