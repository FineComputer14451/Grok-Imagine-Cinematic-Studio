#!/usr/bin/env python3
"""
Thin pure-generation wrapper around tools/plugin_catalog.py.

This script is intentionally minimal and only performs artifact generation (no pinning, no checks).

For pinning and checks, use the canonical CLI exclusively:
    cinematic-studio plugin catalog pin
    cinematic-studio plugin catalog check [--release]

This keeps the old script as a compatibility shim for generation only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow direct execution from scripts/ dir and import tools/* modules cleanly
_repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_repo_root))
sys.path.insert(0, str(_repo_root / "tools"))

from tools.plugin_catalog import (  # noqa: E402
    write_artifacts,
)

MARKETPLACE_PATH = Path(__file__).resolve().parent.parent / ".grok-plugin" / "marketplace.json"

def main() -> int:
    """Pure generation entrypoint.

    This script is now focused exclusively on generation.
    For pinning and checks, use the canonical CLI (see module docstring).
    """
    if not MARKETPLACE_PATH.exists():
        print(f"ERROR: missing {MARKETPLACE_PATH}", file=sys.stderr)
        return 1

    try:
        marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: failed to read marketplace.json: {e}", file=sys.stderr)
        return 1

    argv = sys.argv
    if "--check" in argv or "--release" in argv or "--sync-sha" in argv:
        print("ERROR: --check / --release / --sync-sha are no longer supported on this script.", file=sys.stderr)
        print("Use the canonical CLI instead:", file=sys.stderr)
        print("  cinematic-studio plugin catalog pin", file=sys.stderr)
        print("  cinematic-studio plugin catalog check [--release]", file=sys.stderr)
        return 1

    # Pure generation only (no SHA pinning)
    result = write_artifacts(marketplace, sync_sha=False)
    print(f"Wrote plugin artifacts ({result.get('skills', 0)} skills, {result.get('commands', 0)} commands)")
    print("Note: For release pinning use 'cinematic-studio plugin catalog pin'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())