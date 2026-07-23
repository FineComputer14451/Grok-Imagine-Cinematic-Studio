#!/usr/bin/env bash
#
# Verify Grok plugin manifest, marketplace catalog, and installed plugin checkout.
# Delegates catalog checks to the in-repo CLI (preferred) so release pin checks
# resolve *this* checkout's git HEAD — PATH cinematic-studio often points at
# ~/Grok-Cinematic-Projects, which may not be a git clone.
#
#   bash scripts/verify_plugins.sh
#   bash scripts/verify_plugins.sh --release
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

release_mode=false
if [[ "${1:-}" == "--release" ]]; then
    release_mode=true
fi

# Run plugin catalog check against this repository tree.
# Prefer: python3 -m tools.cinematic_studio_cli (STUDIO_ROOT = this clone).
# Fallback: cinematic-studio with CINEMATIC_PROJECT_DIR pinned to REPO_ROOT.
run_catalog_check() {
    local -a args=(plugin catalog check)
    if $release_mode; then
        args+=(--release)
    fi

    if [[ -f "$REPO_ROOT/tools/cinematic_studio_cli.py" ]]; then
        # Ensure module imports resolve from this checkout even if PYTHONPATH is set.
        PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}" \
            python3 -m tools.cinematic_studio_cli "${args[@]}"
        return
    fi

    if command -v cinematic-studio >/dev/null 2>&1; then
        CINEMATIC_PROJECT_DIR="$REPO_ROOT" \
        CINEMATIC_REPO_ROOT="$REPO_ROOT" \
            cinematic-studio "${args[@]}"
        return
    fi

    echo "❌ No in-repo tools/cinematic_studio_cli.py and no cinematic-studio on PATH" >&2
    exit 1
}

echo "→ Validating plugin manifest..."
if command -v grok >/dev/null 2>&1; then
    grok plugin validate
else
    echo "ℹ️  grok not on PATH — skipping grok plugin validate"
fi

echo "→ Checking marketplace catalog + plugin-index..."
run_catalog_check

if command -v grok >/dev/null 2>&1 && grok plugin details grok-imagine-cinematic-studio >/dev/null 2>&1; then
    echo "→ Verifying installed plugin checkout..."
    bash scripts/cinematic_studio.sh verify --plugin
else
    echo "ℹ️  grok-imagine-cinematic-studio not installed — skipping verify --plugin"
fi

echo "✅ Plugin verification complete"
