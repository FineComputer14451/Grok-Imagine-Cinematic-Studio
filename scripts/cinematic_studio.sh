#!/usr/bin/env bash
#
# Grok Imagine Cinematic Studio v3.6.6 — meta installer entry point
# https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio
#
# Usage:
#   ./scripts/cinematic_studio.sh install
#   ./scripts/cinematic_studio.sh update
#   ./scripts/cinematic_studio.sh verify [--all|--plugin]
#   ./scripts/cinematic_studio.sh version
#
# One-liner (curl):
#   bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh) install
#

set -euo pipefail

cinematic_studio_resolve_script_dir() {
    local source="${BASH_SOURCE[0]}"
    if [[ -f "$source" ]]; then
        cd "$(dirname "$source")" && pwd
        return 0
    fi

    local tmp_dir="${TMPDIR:-/tmp}/cinematic-studio-install-$$"
    mkdir -p "$tmp_dir/lib"
    echo "$tmp_dir"
}

CINEMATIC_SCRIPT_DIR="$(cinematic_studio_resolve_script_dir)"
CINEMATIC_COMMON_LIB="$CINEMATIC_SCRIPT_DIR/lib/cinematic_studio_common.sh"
CINEMATIC_RAW_BASE="${CINEMATIC_RAW_BASE:-https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main}"

if [[ ! -f "$CINEMATIC_COMMON_LIB" ]]; then
    curl -fsSL "$CINEMATIC_RAW_BASE/scripts/lib/cinematic_studio_common.sh" -o "$CINEMATIC_COMMON_LIB"
fi

# shellcheck source=lib/cinematic_studio_common.sh
source "$CINEMATIC_COMMON_LIB"
cinematic_studio_init_paths "$CINEMATIC_SCRIPT_DIR"

usage() {
    cat <<EOF
🎥 Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION}

Usage:
  cinematic_studio.sh install          Install or reinstall the skill bundle
  cinematic_studio.sh update           Update with backup of existing skills
  cinematic_studio.sh verify [--all|--plugin]
                                     Verify core (default), all manifest skills, or Grok plugin install
  cinematic_studio.sh version          Print installed release version

Examples:
  ./scripts/cinematic_studio.sh install
  ./scripts/cinematic_studio.sh verify --all
  ./scripts/cinematic_studio.sh verify --plugin
  bash <(curl -sL $CINEMATIC_RAW_BASE/scripts/cinematic_studio.sh) install
EOF
}

cmd_install() {
    echo "🎥 Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION} Installer"
    echo "================================================"
    echo ""

    cinematic_studio_apply_release_bundle
    cinematic_studio_print_next_steps
}

cmd_update() {
    echo "🔄 Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION} Updater"
    echo "=============================================="
    echo ""

    if [[ ! -d "$SKILLS_DIR" ]]; then
        echo "❌ No existing installation found at $SKILLS_DIR"
        echo "Run: cinematic_studio.sh install"
        exit 1
    fi

    local backup_dir="$HOME/.grok/skills-backup-$(date +%Y%m%d-%H%M%S)"
    echo "→ Creating backup at: $backup_dir"
    mkdir -p "$backup_dir"
    cp -r "$SKILLS_DIR/"* "$backup_dir/" 2>/dev/null || true

    cinematic_studio_apply_release_bundle

    echo ""
    echo "✅ Update complete!"
    echo "Backup saved to: $backup_dir"
    cinematic_studio_print_next_steps
}

cmd_verify() {
    if [[ "${1:-}" == "--plugin" ]]; then
        cinematic_studio_verify_plugin
        return $?
    fi

    local tier="core"
    if [[ "${1:-}" == "--all" ]]; then
        tier="all"
    fi
    cinematic_studio_verify "$tier"
}

cmd_version() {
    echo "Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION}"
}

main() {
    local cmd="${1:-}"
    shift || true

    case "$cmd" in
        install) cmd_install "$@" ;;
        update) cmd_update "$@" ;;
        verify) cmd_verify "$@" ;;
        version) cmd_version "$@" ;;
        -h|--help|help|"") usage ;;
        *)
            echo "❌ Unknown command: $cmd"
            echo ""
            usage
            exit 1
            ;;
    esac
}

main "$@"