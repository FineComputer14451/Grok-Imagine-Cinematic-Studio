#!/usr/bin/env bash
#
# repo-status.sh — github-repo-manager (v3.7.1 / Grok 4.5)
# Quick health check of the repository + cinematic studio context
#

set -euo pipefail

# scripts/ → skill/ → skills/ → .grok/ → repo root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"

echo "📊 GitHub Repo Manager — Quick Status Report (v3.7.1)"
echo "============================================"
echo "Root: $ROOT"
echo ""

echo "🔹 Git Status"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git status --short | head -30 || true
  dirty="$(git status --porcelain | wc -l | tr -d ' ')"
  echo "Dirty paths: $dirty"
else
  echo "Not a git repository"
  exit 0
fi

echo ""
echo "🔹 Current Branch & Last Commits"
git branch --show-current 2>/dev/null || true
git log --oneline -5 --decorate 2>/dev/null || true
echo "HEAD: $(git rev-parse --short HEAD 2>/dev/null || echo n/a)"

echo ""
echo "🔹 Remote Info"
git remote -v 2>/dev/null || true

echo ""
echo "🔹 .grok/skills count"
if [[ -d .grok/skills ]]; then
  count="$(find .grok/skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
  with_md="$(find .grok/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
  echo "$count skill dirs | $with_md SKILL.md files"
else
  echo ".grok/skills directory not present"
fi

echo ""
echo "🔹 Plugin catalog"
if [[ -f .grok-plugin/plugin.json ]]; then
  python3 - <<'PY' 2>/dev/null || echo "plugin.json present (python parse failed)"
import json
from pathlib import Path
pj = json.loads(Path(".grok-plugin/plugin.json").read_text())
print(f"plugin.json skills: {len(pj.get('skills', []))}")
print(f"plugin version: {pj.get('version', '?')}")
mp = Path(".grok-plugin/marketplace.json")
if mp.exists():
    m = json.loads(mp.read_text())
    for p in m.get("plugins", []):
        src = p.get("source") or {}
        sha = src.get("sha", "")
        print(f"marketplace pin: {sha[:12] + '…' if sha else 'none'}")
PY
else
  echo "No .grok-plugin/plugin.json"
fi

echo ""
echo "🔹 VERSION file"
if [[ -f VERSION ]]; then
  cat VERSION
else
  echo "No VERSION file"
fi

echo ""
echo "🔹 Recent tags (last 5)"
git tag --sort=-version:refname 2>/dev/null | head -5 || echo "No tags"

echo ""
echo "✅ Status check complete."
echo "   Validate skills: bash .grok/skills/github-repo-manager/scripts/validate-all-skills.sh"
echo "   Studio verify:   bash scripts/verify_cinematic_studio.sh"
echo "   Plugin verify:   bash scripts/verify_plugins.sh"
