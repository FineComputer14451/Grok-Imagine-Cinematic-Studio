#!/bin/bash
#
# Verify Grok Imagine Cinematic Studio Installation
#

echo "🔍 Verifying Grok Imagine Cinematic Studio v3.6.4 Installation"
echo "============================================================"
echo ""

SKILLS_DIR="$HOME/.grok/skills"
REQUIRED_SKILLS=(
    "grok-imagine-cinematic-studio"
    "ai-video-upscaler"
    "cinematic-sequence-extender"
    "studio-director"
    "quality-assurance-guardian"
    "identity-lock-specialist"
    "workflow-quota-optimizer"
)

MISSING=0

for skill in "${REQUIRED_SKILLS[@]}"; do
    if [ -d "$SKILLS_DIR/$skill" ] && [ -f "$SKILLS_DIR/$skill/SKILL.md" ]; then
        echo "✅ $skill"
    else
        echo "❌ $skill (missing)"
        MISSING=$((MISSING + 1))
    fi
done

echo ""
if [ $MISSING -eq 0 ]; then
    echo "✅ All core skills are installed correctly!"
    echo ""
    echo "You can now activate the studio with:"
    echo "Activate Grok Imagine Cinematic Studio v3.6.4"
else
    echo "⚠️  $MISSING skill(s) are missing."
    echo "Please re-run the installer:"
    echo "bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/install_cinematic_studio.sh)"
fi

