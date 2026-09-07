#!/usr/bin/env python3
"""Post-board cross-ref consistency check for Characters / Props / Locations.

Validates that DNA packets, naming, and hero plates agree after a board pass.
Portable — no Studio install required.

Exit codes: 0 = pass (warnings ok), 1 = failures, 2 = usage/IO error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff", ".PLACEHOLDER"}
# treat .webp stubs and any file matching stem as a plate (samples use .webp placeholders)


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-") or "character"


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        return {"__error__": str(e)}


def find_plates(root: Path) -> dict[str, Path]:
    """Map plate stem → path under characters/ props/ locations/."""
    found: dict[str, Path] = {}
    for folder in ("characters", "props", "locations"):
        base = root / folder
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() in {".txt", ".md", ".json"}:
                continue
            # accept image-like + sample PLACEHOLDER stubs
            if p.suffix.lower() in IMAGE_EXTS or p.read_bytes()[:16].startswith(b"PLACEHOLDER"):
                found[p.stem] = p
            elif p.suffix.lower() in {".webp", ".png", ".jpg", ".jpeg"}:
                found[p.stem] = p
    return found


def dna_files(root: Path) -> list[Path]:
    chars = root / "characters"
    if not chars.is_dir():
        return []
    return sorted(chars.glob("*/dna.json"))


def check_dna(path: Path, plates: dict[str, Path], failures: list[str], warnings: list[str]) -> None:
    data = load_json(path)
    if data is None or "__error__" in data:
        failures.append(f"DNA unreadable: {path} ({data})")
        return

    slug = data.get("slug") or slugify(str(data.get("character_name", "")))
    folder_slug = path.parent.name
    if slug != folder_slug:
        failures.append(f"DNA slug `{slug}` ≠ folder `{folder_slug}` ({path})")

    for field in ("character_name", "core_identity", "facial_dna"):
        if not (data.get(field) or "").strip():
            failures.append(f"DNA missing `{field}`: {path}")

    anchors = data.get("key_consistency_anchors") or []
    if len(anchors) < 1:
        failures.append(f"DNA needs ≥1 key_consistency_anchors: {path}")
    elif len(anchors) < 3:
        warnings.append(f"DNA has <3 anchors (recommend 3–7): {path}")

    status = data.get("identity_lock_status", "pending")
    refs = data.get("reference_image_ids") or []
    if not refs:
        # infer heroes from naming convention in folder
        folder_plates = [s for s in plates if s.startswith(f"char_{slug.replace('-', '_')}_hero") or s.startswith(f"char_{slug}_hero")]
        # also try slug with underscores
        u = slug.replace("-", "_")
        folder_plates = [s for s in plates if f"char_{u}_hero" in s or f"char_{slug}_hero" in s]
        if not folder_plates:
            failures.append(f"No reference_image_ids and no char_*_hero plates for `{slug}`")
        else:
            warnings.append(f"DNA `{slug}` has empty reference_image_ids — found plates: {', '.join(sorted(folder_plates))}")
        return

    for rid in refs:
        if rid not in plates:
            failures.append(f"DNA `{slug}` refs missing plate `{rid}` on board")
        # naming soft-check
        u = slug.replace("-", "_")
        if not (rid.startswith(f"char_{u}_") or rid.startswith(f"char_{slug}_")):
            warnings.append(f"Plate id `{rid}` does not start with char_{u}_ (NAMING.md)")


def check_manifest(root: Path, plates: dict[str, Path], failures: list[str], warnings: list[str]) -> None:
    man_path = root / "board" / "manifest.json"
    if not man_path.is_file():
        warnings.append("No board/manifest.json — skipping manifest cross-check (optional)")
        return
    man = load_json(man_path)
    if man is None or "__error__" in man:
        failures.append(f"manifest unreadable: {man_path}")
        return

    for char in man.get("characters") or []:
        slug = char.get("slug", "")
        dna_rel = char.get("dna")
        if dna_rel:
            dp = root / dna_rel
            if not dp.is_file():
                failures.append(f"manifest DNA missing: {dna_rel}")
        for hero in char.get("heroes") or []:
            if hero not in plates:
                failures.append(f"manifest character `{slug}` missing hero plate `{hero}`")

    for prop in man.get("props") or []:
        slug = prop.get("slug", "")
        for hero in (prop.get("heroes") or []) + (prop.get("details") or []):
            if hero not in plates:
                failures.append(f"manifest prop `{slug}` missing plate `{hero}`")

    for loc in man.get("locations") or []:
        slug = loc.get("slug", "")
        est = loc.get("establish")
        if est and est not in plates:
            failures.append(f"manifest location `{slug}` missing establish `{est}`")
        for cov in loc.get("coverage") or []:
            if cov not in plates:
                failures.append(f"manifest location `{slug}` missing coverage `{cov}`")


def check_naming_orphans(plates: dict[str, Path], warnings: list[str]) -> None:
    for stem in plates:
        if stem.startswith("char_") and "_hero" not in stem and "_var_" not in stem:
            warnings.append(f"Character plate `{stem}` is not hero/var per NAMING.md")
        if stem.startswith("prop_") and "_hero" not in stem and "_detail_" not in stem:
            warnings.append(f"Prop plate `{stem}` is not hero/detail per NAMING.md")
        if stem.startswith("loc_") and "_establish" not in stem:
            # coverage angles are ok without establish in name
            pass


def check_props_locations(root: Path, plates: dict[str, Path], warnings: list[str]) -> None:
    props = root / "props"
    if props.is_dir():
        for d in props.iterdir():
            if not d.is_dir():
                continue
            heroes = [s for s in plates if s.startswith(f"prop_{d.name.replace('-', '_')}_hero") or s.startswith(f"prop_{d.name}_hero")]
            if not heroes:
                # try underscore slug
                u = d.name.replace("-", "_")
                heroes = [s for s in plates if s.startswith(f"prop_{u}_hero")]
            if not heroes:
                warnings.append(f"Prop folder `{d.name}` has no prop_*_hero plate")
            if not (d / "DNA.txt").is_file() and not (d / "DNA.md").is_file():
                warnings.append(f"Prop `{d.name}` missing DNA.txt one-liner")

    locs = root / "locations"
    if locs.is_dir():
        for d in locs.iterdir():
            if not d.is_dir():
                continue
            u = d.name.replace("-", "_")
            est = [s for s in plates if s == f"loc_{u}_establish" or s == f"loc_{d.name}_establish"]
            if not est:
                warnings.append(f"Location `{d.name}` missing loc_*_establish plate")


def main() -> int:
    ap = argparse.ArgumentParser(description="Post-board cross-ref consistency check")
    ap.add_argument(
        "project_root",
        nargs="?",
        default=".",
        type=Path,
        help="Project root containing characters/ props/ locations/ (default: .)",
    )
    ap.add_argument("--json", action="store_true", help="Machine-readable JSON report")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = ap.parse_args()
    root = args.project_root.resolve()

    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    failures: list[str] = []
    warnings: list[str] = []

    plates = find_plates(root)
    if not plates:
        warnings.append("No plates found under characters/ props/ locations/ (empty board?)")

    dnas = dna_files(root)
    if not dnas:
        failures.append("No characters/*/dna.json found — run dna_init or copy sample packets")
    for dp in dnas:
        check_dna(dp, plates, failures, warnings)

    check_manifest(root, plates, failures, warnings)
    check_naming_orphans(plates, warnings)
    check_props_locations(root, plates, warnings)

    # sample flag note
    for dp in dnas:
        data = load_json(dp) or {}
        if data.get("sample"):
            warnings.append(f"Sample DNA still marked sample=true: {dp} — replace before production lock")

    if args.strict and warnings:
        failures.extend(f"[strict] {w}" for w in warnings)
        warnings = []

    report = {
        "project_root": str(root),
        "plates": len(plates),
        "dna_profiles": len(dnas),
        "failures": failures,
        "warnings": warnings,
        "ok": not failures,
    }

    if args.json:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"Post-board cross-ref check — {root}")
        print(f"  plates: {len(plates)}  dna: {len(dnas)}")
        if failures:
            print("FAILURES:")
            for f in failures:
                print(f"  ✗ {f}")
        if warnings:
            print("WARNINGS:")
            for w in warnings:
                print(f"  ! {w}")
        if not failures and not warnings:
            print("  ✓ all checks passed")
        elif not failures:
            print("  ✓ passed with warnings")
        else:
            print("  ✗ failed — fix before Identity Lock / motion")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
