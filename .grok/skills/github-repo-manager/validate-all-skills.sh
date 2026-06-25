#!/bin/bash
#
# validate-all-skills.sh
# Part of the github-repo-manager skill
#
# Validates every skill in .grok/skills/ using the official validate-skill.sh
# Usage: ./scripts/validate-all-skills.sh
#

set -euo pipefail

VALIDATE_SCRIPT="/root/.grok/skills/skill-creator/scripts/validate-skill.sh"
SKILLS_DIR=".grok/skills"

if [[ ! -f "$VALIDATE_SCRIPT" ]]; then
    echo "❌ Error: validate-skill.sh not found at $VALIDATE_SCRIPT"
    echo "   Make sure skill-creator is installed in your environment."
    exit 1
fi

if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "❌ Error: $SKILLS_DIR directory not found. Run from repo root."
    exit 1
fi

echo "🔍 Validating all skills in $SKILLS_DIR ..."
echo "──────────────────────────────────────────────"

passed=0
failed=0

for skill_path in "$SKILLS_DIR"/*/; do
    if [[ -d "$skill_path" ]]; then
        skill_name=$(basename "$skill_path")
        echo -n "→ $skill_name ... "

        if bash "$VALIDATE_SCRIPT" "$skill_path" >/dev/null 2>&1; then
            echo "✅ valid"
            ((passed++))
        else
            echo "❌ INVALID"
            echo ""
            bash "$VALIDATE_SCRIPT" "$skill_path" || true
            echo ""
            ((failed++))
        fi
    fi
done

echo "──────────────────────────────────────────────"
echo "Summary: $passed passed  |  $failed failed"

if [[ $failed -eq 0 ]]; then
    echo "🎉 All skills are valid and ready!"
else
    echo "⚠️  Please fix the invalid skills above before committing."
fi

exit $failed
