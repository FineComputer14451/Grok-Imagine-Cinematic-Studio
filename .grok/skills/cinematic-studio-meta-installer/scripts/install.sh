#!/usr/bin/env bash
#
# Cinematic Studio Meta Installer v3.9.1 — skill wrapper
# Delegates to a verified studio root, PROJECT_DIR install, or curl fallback.
# Supports: install|update|verify|declutter|version|doctor|grok
#
# Studio: Grok Imagine Cinematic Studio v3.9.1 "Odyssey Native"
# Suite:  64 skills (scripts/required_skills.manifest)
#

set -euo pipefail

RAW_BASE="${CINEMATIC_RAW_BASE:-https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main}"
PROJECT_DIR="${PROJECT_DIR:-$HOME/Grok-Cinematic-Projects}"
META_VERSION="3.9.1"

cinematic_meta_find_installer() {
    local start="$1"
    local dir="$start"

    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/VERSION" && -f "$dir/scripts/cinematic_studio.sh" ]]; then
            echo "$dir/scripts/cinematic_studio.sh"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# Local meta-version probe (does not require full installer)
if [[ "${1:-}" == "meta-version" ]]; then
    echo "cinematic-studio-meta-installer ${META_VERSION}"
    exit 0
fi

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALLER=""

if INSTALLER="$(cinematic_meta_find_installer "$SKILL_DIR")"; then
    exec bash "$INSTALLER" "$@"
fi

if [[ -f "$PROJECT_DIR/scripts/cinematic_studio.sh" ]]; then
    exec bash "$PROJECT_DIR/scripts/cinematic_studio.sh" "$@"
fi

if ! command -v curl >/dev/null 2>&1; then
    echo "error: curl not found and no local cinematic_studio.sh under:" >&2
    echo "  - repo root (VERSION + scripts/cinematic_studio.sh)" >&2
    echo "  - PROJECT_DIR=$PROJECT_DIR" >&2
    exit 1
fi

exec bash <(curl -fsSL "$RAW_BASE/scripts/cinematic_studio.sh") "$@"
