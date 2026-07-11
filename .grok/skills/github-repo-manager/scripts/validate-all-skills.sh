#!/usr/bin/env bash
#
# validate-all-skills.sh — github-repo-manager (v3.7.1)
# Validates every skill in .grok/skills/ using cinematic-skill-creator when available.
# Usage: from repo root → bash .grok/skills/github-repo-manager/scripts/validate-all-skills.sh
#

set -euo pipefail

# scripts/ → skill/ → skills/ → .grok/ → repo root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"

SKILLS_DIR=".grok/skills"
VALIDATE_CANDIDATES=(
  "${HOME}/.grok/skills/cinematic-skill-creator/scripts/validate_skill.sh"
  "${ROOT}/.grok/skills/cinematic-skill-creator/scripts/validate_skill.sh"
  "${HOME}/.grok/skills/skill-creator/scripts/validate-skill.sh"
  "${HOME}/.grok/skills/create-skill/scripts/validate-skill.sh"
)

VALIDATE_SCRIPT=""
for candidate in "${VALIDATE_CANDIDATES[@]}"; do
  if [[ -f "$candidate" ]]; then
    VALIDATE_SCRIPT="$candidate"
    break
  fi
done

if [[ -z "$VALIDATE_SCRIPT" ]]; then
  echo "❌ No validate_skill.sh found. Tried cinematic-skill-creator and skill-creator paths."
  echo "   Install cinematic-skill-creator or pass a validator path."
  exit 1
fi

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "❌ $SKILLS_DIR not found. Run from repo root."
  exit 1
fi

echo "🔍 Validating skills in $SKILLS_DIR"
echo "   Validator: $VALIDATE_SCRIPT"
echo "──────────────────────────────────────────────"

passed=0
failed=0
skipped=0

for skill_path in "$SKILLS_DIR"/*/; do
  [[ -d "$skill_path" ]] || continue
  skill_name="$(basename "$skill_path")"
  if [[ ! -f "${skill_path}SKILL.md" ]]; then
    echo "→ $skill_name ... ⚠️  skip (no SKILL.md)"
    skipped=$((skipped + 1))
    continue
  fi
  echo -n "→ $skill_name ... "
  if bash "$VALIDATE_SCRIPT" "$skill_path" >/dev/null 2>&1; then
    echo "✅ valid"
    passed=$((passed + 1))
  else
    echo "❌ INVALID"
    bash "$VALIDATE_SCRIPT" "$skill_path" || true
    failed=$((failed + 1))
  fi
done

echo "──────────────────────────────────────────────"
echo "Summary: $passed passed | $failed failed | $skipped skipped"

if [[ "$failed" -eq 0 ]]; then
  echo "🎉 All validated skills are ready."
  exit 0
fi

echo "⚠️  Fix invalid skills before committing."
exit 1
