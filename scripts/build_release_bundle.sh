#!/usr/bin/env bash
#
# Build the skills release zip for GitHub Releases.
# Includes every skill listed in scripts/required_skills.manifest.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "$REPO_ROOT/VERSION")"
ZIP_NAME="grok-imagine-cinematic-studio-skills-install-v${VERSION}.zip"
TMPDIR="${TMPDIR:-/tmp}"
OUTPUT="${1:-$TMPDIR/$ZIP_NAME}"
if [[ "$OUTPUT" != /* ]]; then
    mkdir -p "$(dirname "$OUTPUT")"
    OUTPUT="$(cd "$(dirname "$OUTPUT")" && pwd)/$(basename "$OUTPUT")"
fi
STAGING="$TMPDIR/cinematic-bundle-staging-$$"

# shellcheck source=lib/cinematic_studio_common.sh
source "$SCRIPT_DIR/lib/cinematic_studio_common.sh"

cleanup() {
    rm -rf "$STAGING"
}
trap cleanup EXIT

mkdir -p "$STAGING/.grok/skills" "$STAGING/references" \
    "$STAGING/config" "$STAGING/scripts/lib" "$STAGING/scripts/wrappers"

cinematic_studio_read_manifest "$SCRIPT_DIR/required_skills.manifest" "all" skills

for skill in "${skills[@]}"; do
    src="$REPO_ROOT/.grok/skills/$skill"
    if [[ ! -d "$src" || ! -f "$src/SKILL.md" ]]; then
        echo "❌ Missing skill in repository: $skill"
        exit 1
    fi
    cp -r "$src" "$STAGING/.grok/skills/"
done

if [[ -d "$REPO_ROOT/references" ]]; then
    cp -r "$REPO_ROOT/references/"* "$STAGING/references/"
fi

# Full tools/ tree (cli/tui package) + studio_core — same payload Method A install requires.
cinematic_studio_copy_package_tree "$REPO_ROOT/tools" "$STAGING/tools"
if [[ -d "$REPO_ROOT/studio_core" ]]; then
    cinematic_studio_copy_package_tree "$REPO_ROOT/studio_core" "$STAGING/studio_core"
fi

if [[ -d "$REPO_ROOT/config" ]]; then
    cp -r "$REPO_ROOT/config/"* "$STAGING/config/"
fi

for script in "${CINEMATIC_INSTALLER_SCRIPTS[@]}"; do
    [[ -f "$REPO_ROOT/scripts/$script" ]] && cp "$REPO_ROOT/scripts/$script" "$STAGING/scripts/"
done
for libf in cinematic_studio_common.sh install_cli_wrappers.sh; do
    [[ -f "$REPO_ROOT/scripts/lib/$libf" ]] && cp "$REPO_ROOT/scripts/lib/$libf" "$STAGING/scripts/lib/"
done
if [[ -d "$REPO_ROOT/scripts/wrappers" ]]; then
    cp -r "$REPO_ROOT/scripts/wrappers/." "$STAGING/scripts/wrappers/"
    chmod +x "$STAGING/scripts/wrappers/"* 2>/dev/null || true
fi

if [[ -f "$REPO_ROOT/requirements.txt" ]]; then
    cp "$REPO_ROOT/requirements.txt" "$STAGING/"
fi

for doc in AGENTS.md MASTER_PROMPT.md VERSION; do
    if [[ -f "$REPO_ROOT/$doc" ]]; then
        cp "$REPO_ROOT/$doc" "$STAGING/"
    fi
done

if [[ ! -f "$STAGING/tools/cli/tui/__init__.py" ]]; then
    echo "❌ Bundle missing tools/cli/tui (incomplete tools tree)"
    exit 1
fi
if [[ ! -f "$STAGING/studio_core/services/dashboard.py" ]]; then
    echo "❌ Bundle missing studio_core/services/dashboard.py"
    exit 1
fi

rm -f "$OUTPUT"
cinematic_studio_zip_dir "$STAGING" "$OUTPUT"

echo "✅ Built release bundle: $OUTPUT"
echo "   Version: v${VERSION}"
echo "   Skills: $(find "$STAGING/.grok/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"