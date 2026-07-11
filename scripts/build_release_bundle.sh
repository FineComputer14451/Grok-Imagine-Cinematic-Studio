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
OUTPUT="${1:-/tmp/$ZIP_NAME}"
if [[ "$OUTPUT" != /* ]]; then
    mkdir -p "$(dirname "$OUTPUT")"
    OUTPUT="$(cd "$(dirname "$OUTPUT")" && pwd)/$(basename "$OUTPUT")"
fi
STAGING="/tmp/cinematic-bundle-staging-$$"

# shellcheck source=lib/cinematic_studio_common.sh
source "$SCRIPT_DIR/lib/cinematic_studio_common.sh"

cleanup() {
    rm -rf "$STAGING"
}
trap cleanup EXIT

mkdir -p "$STAGING/.grok/skills" "$STAGING/references" "$STAGING/tools/cli" "$STAGING/config" "$STAGING/scripts/lib"

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

for pyfile in "$REPO_ROOT/tools"/*.py; do
    [[ -f "$pyfile" ]] || continue
    cp "$pyfile" "$STAGING/tools/"
done

for pyfile in "$REPO_ROOT/tools/cli"/*.py; do
    [[ -f "$pyfile" ]] || continue
    cp "$pyfile" "$STAGING/tools/cli/"
done

if [[ -d "$REPO_ROOT/config" ]]; then
    cp -r "$REPO_ROOT/config/"* "$STAGING/config/"
fi

for script in "${CINEMATIC_INSTALLER_SCRIPTS[@]}"; do
    [[ -f "$REPO_ROOT/scripts/$script" ]] && cp "$REPO_ROOT/scripts/$script" "$STAGING/scripts/"
done
cp "$REPO_ROOT/scripts/lib/cinematic_studio_common.sh" "$STAGING/scripts/lib/"

if [[ -f "$REPO_ROOT/requirements.txt" ]]; then
    cp "$REPO_ROOT/requirements.txt" "$STAGING/"
fi

for doc in AGENTS.md MASTER_PROMPT.md; do
    if [[ -f "$REPO_ROOT/$doc" ]]; then
        cp "$REPO_ROOT/$doc" "$STAGING/"
    fi
done

rm -f "$OUTPUT"
(
    cd "$STAGING"
    zip -qr "$OUTPUT" .
)

echo "✅ Built release bundle: $OUTPUT"
echo "   Version: v${VERSION}"
echo "   Skills: $(find "$STAGING/.grok/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"