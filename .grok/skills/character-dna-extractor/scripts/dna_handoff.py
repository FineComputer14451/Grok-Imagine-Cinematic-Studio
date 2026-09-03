#!/usr/bin/env python3
"""Generate Identity Lock handoff packet from a Character DNA profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from aup_gate import AUPGateError  # noqa: E402
from character_dna import (  # noqa: E402
    build_handoff_packet,
    find_character_dna,
    load_character_dna,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Identity Lock handoff packet")
    parser.add_argument("--name", "-n", required=True, help="Character name or slug")
    parser.add_argument("--file", "-f", type=Path, help="Path to dna.json (overrides --name lookup)")
    parser.add_argument("--output", "-o", type=Path, help="Output path (default: characters/{slug}/handoff.json)")
    args = parser.parse_args()

    if args.file:
        dna_path = args.file
    else:
        dna_path = find_character_dna(args.name)
        if not dna_path:
            print(f"ERROR: No DNA profile found for '{args.name}'", file=sys.stderr)
            sys.exit(1)

    try:
        dna = load_character_dna(dna_path)
        handoff = build_handoff_packet(dna)
    except (ValueError, AUPGateError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    out = args.output or dna_path.parent / "handoff.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(handoff, indent=2))

    print(f"Handoff packet written: {out}")
    print(f"Target: Identity Lock Specialist | Character: {dna['character_name']}")
    print(f"Anchors: {len(handoff.get('key_consistency_anchors', []))}")
    print(f"Next: python tools/cinematic_studio_cli.py dna lock --name \"{dna['character_name']}\"")


if __name__ == "__main__":
    main()