#!/bin/bash
#
# Verify Grok Imagine Cinematic Studio Installation
#

echo "🔍 Verifying Grok Imagine Cinematic Studio v3.6.4"
echo "================================================"
echo ""

SKILLS_DIR="$HOME/.grok/skills"
REQUIRED=("grok-imagine-cinematic-studio" "ai-video-upscaler" "cinematic-sequence-extender" "studio-director" "quality-assurance-guardian")

MISSING=0
for skill in "${REQUIRED[@]}"; do
    if [ -d "$SKILLS_DIR/$skill" ] && [ -f "$SKILLS_DIR/$skill/SKILL.md" ]; then
        echo "✅ $skill"
    else
        echo "❌ $skill (missing)"
        MISSING=$((MISSING + 1))
    fi
done

echo ""
if [ $MISSING -eq 0 ]; then
    echo "✅ All core skills installed correctly!"
else
    echo "⚠️  $MISSING skill(s) missing. Re-run the installer."
fi
