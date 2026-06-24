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
STAGING="/tmp/cinematic-bundle-staging-$$"

cleanup() {
    rm -rf "$STAGING"
}
trap cleanup EXIT

mkdir -p "$STAGING/.grok/skills" "$STAGING/references"

while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue
    skill="${line%%#*}"
    skill="$(echo "$skill" | xargs)"
    [[ -z "$skill" ]] && continue

    src="$REPO_ROOT/.grok/skills/$skill"
    if [[ ! -d "$src" || ! -f "$src/SKILL.md" ]]; then
        echo "❌ Missing skill in repository: $skill"
        exit 1
    fi
    cp -r "$src" "$STAGING/.grok/skills/"
done < "$SCRIPT_DIR/required_skills.manifest"

if [[ -d "$REPO_ROOT/references" ]]; then
    cp -r "$REPO_ROOT/references/"* "$STAGING/references/"
fi

for doc in AGENTS.md MASTER_PROMPT_v3.6.md; do
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
echo "   Skills: $(find "$STAGING/.grok/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"