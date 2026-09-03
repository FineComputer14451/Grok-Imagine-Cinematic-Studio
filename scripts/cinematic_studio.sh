#!/usr/bin/env bash
#
# Grok Imagine Cinematic Studio v3.11.2 — meta installer entry point
# https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio
#
# Usage:
#   ./scripts/cinematic_studio.sh install
#   ./scripts/cinematic_studio.sh update
#   ./scripts/cinematic_studio.sh verify [--all|--plugin]
#   ./scripts/cinematic_studio.sh declutter [--dry-run|--apply]
#   ./scripts/cinematic_studio.sh version
#   ./scripts/cinematic_studio.sh doctor [opts]
#   ./scripts/cinematic_studio.sh grok status|ensure|update|install
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
  cinematic_studio.sh declutter [opts]
                                     Remove Method A skill copies that duplicate the plugin;
                                     prune old ~/.grok/skills-backup-* dirs
  cinematic_studio.sh version          Print installed release version
  cinematic_studio.sh doctor [opts]    Grok Doctor via Python registry (alias: grok-doctor)
  cinematic_studio.sh grok <cmd>       Grok Build CLI binary (status|ensure|update|install)

Examples:
  ./scripts/cinematic_studio.sh install
  ./scripts/cinematic_studio.sh verify --all
  ./scripts/cinematic_studio.sh verify --plugin
  ./scripts/cinematic_studio.sh declutter --dry-run
  ./scripts/cinematic_studio.sh declutter --apply --keep-backups 1
  ./scripts/cinematic_studio.sh doctor
  ./scripts/cinematic_studio.sh doctor --quick
  ./scripts/cinematic_studio.sh grok status
  ./scripts/cinematic_studio.sh grok ensure
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

cmd_declutter() {
    cinematic_studio_declutter "$@"
}

cmd_doctor() {
    # Single resolution path: thin launcher owns CLI discovery.
    local doctor_sh="${CINEMATIC_SCRIPT_DIR}/grok_doctor.sh"
    if [[ ! -f "$doctor_sh" && -n "${PROJECT_DIR:-}" && -f "${PROJECT_DIR}/scripts/grok_doctor.sh" ]]; then
        doctor_sh="${PROJECT_DIR}/scripts/grok_doctor.sh"
    fi
    if [[ -f "$doctor_sh" ]]; then
        if [[ -z "${CINEMATIC_REPO_ROOT:-}" && -f "${CINEMATIC_SCRIPT_DIR}/../VERSION" ]]; then
            export CINEMATIC_REPO_ROOT="$(cd "${CINEMATIC_SCRIPT_DIR}/.." && pwd)"
        fi
        exec bash "$doctor_sh" "$@"
    fi
    echo "❌ grok_doctor.sh not found" >&2
    exit 1
}

cmd_grok() {
    # Forward to Python CLI: cinematic-studio grok status|ensure|update|install
    local cli_py=""
    local repo_root=""
    local py=""

    if [[ -z "${CINEMATIC_REPO_ROOT:-}" && -f "${CINEMATIC_SCRIPT_DIR}/../VERSION" ]]; then
        export CINEMATIC_REPO_ROOT="$(cd "${CINEMATIC_SCRIPT_DIR}/.." && pwd)"
    fi
    repo_root="${CINEMATIC_REPO_ROOT:-}"

    if [[ -n "$repo_root" && -f "$repo_root/tools/cinematic_studio_cli.py" ]]; then
        cli_py="$repo_root/tools/cinematic_studio_cli.py"
    elif [[ -n "${PROJECT_DIR:-}" && -f "${PROJECT_DIR}/tools/cinematic_studio_cli.py" ]]; then
        cli_py="${PROJECT_DIR}/tools/cinematic_studio_cli.py"
    fi

    if [[ -z "$cli_py" ]]; then
        echo "❌ cinematic_studio_cli.py not found (set CINEMATIC_REPO_ROOT or run install)" >&2
        exit 1
    fi

    if ! py="$(cinematic_studio_resolve_python)"; then
        echo "❌ python3 not found (create $PROJECT_DIR/.venv or install Python 3)" >&2
        exit 1
    fi

    exec "$py" "$cli_py" grok "$@"
}


main() {
    local cmd="${1:-}"
    shift || true

    case "$cmd" in
        install) cmd_install "$@" ;;
        update) cmd_update "$@" ;;
        verify) cmd_verify "$@" ;;
        declutter) cmd_declutter "$@" ;;
        version) cmd_version "$@" ;;
        doctor|grok-doctor|grok_doctor) cmd_doctor "$@" ;;
        grok) cmd_grok "$@" ;;
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