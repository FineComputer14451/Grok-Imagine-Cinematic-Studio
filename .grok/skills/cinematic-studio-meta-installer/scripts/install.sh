#!/usr/bin/env bash
#
# Cinematic Studio Meta Installer v3.8.5 — skill wrapper
# Delegates to a verified studio root, PROJECT_DIR install, or curl fallback.
#

set -euo pipefail

RAW_BASE="${CINEMATIC_RAW_BASE:-https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main}"
PROJECT_DIR="${PROJECT_DIR:-$HOME/Grok-Cinematic-Projects}"

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

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALLER=""

if INSTALLER="$(cinematic_meta_find_installer "$SKILL_DIR")"; then
    exec bash "$INSTALLER" "$@"
fi

if [[ -f "$PROJECT_DIR/scripts/cinematic_studio.sh" ]]; then
    exec bash "$PROJECT_DIR/scripts/cinematic_studio.sh" "$@"
fi

exec bash <(curl -fsSL "$RAW_BASE/scripts/cinematic_studio.sh") "$@"