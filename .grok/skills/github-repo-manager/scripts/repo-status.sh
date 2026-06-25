#!/bin/bash
#
# repo-status.sh
# Part of github-repo-manager skill
#
# Quick health check of the repository + cinematic studio context
#

echo "📊 GitHub Repo Manager — Quick Status Report"
echo "============================================"

echo ""
echo "🔹 Git Status"
git status --short | head -20 || echo "Not a git repo or no changes"

echo ""
echo "🔹 Current Branch & Last Commits"
git branch --show-current
git log --oneline -5 --decorate

echo ""
echo "🔹 Remote Info"
git remote -v

echo ""
echo "🔹 .grok/skills count"
if [ -d ".grok/skills" ]; then
    count=$(find .grok/skills -mindepth 1 -maxdepth 1 -type d | wc -l)
    echo "$count skills found"
else
    echo ".grok/skills directory not present"
fi

echo ""
echo "🔹 VERSION file"
if [ -f "VERSION" ]; then
    cat VERSION
else
    echo "No VERSION file"
fi

echo ""
echo "🔹 Recent tags (last 5)"
git tag --sort=-version:refname | head -5 || echo "No tags"

echo ""
echo "✅ Status check complete. Run validate-all-skills.sh for deeper skill validation."
