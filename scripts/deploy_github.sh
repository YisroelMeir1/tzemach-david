#!/usr/bin/env bash
# Create/push a public GitHub repo and enable GitHub Pages (Actions).
# Prerequisites: gh auth login
set -euo pipefail

REPO_NAME="${1:-tzemach-david}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh >/dev/null; then
  echo "Install GitHub CLI first: brew install gh"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Not logged in to GitHub."
  echo "Run:  gh auth login"
  echo "Choose: GitHub.com → HTTPS → Login with a web browser"
  exit 1
fi

# Create public repo from current directory (if remote missing)
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "Creating public repo: $REPO_NAME"
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
else
  echo "Remote origin exists; pushing main…"
  git push -u origin main
fi

# Enable Pages via GitHub Actions
echo "Enabling GitHub Pages (build from Actions)…"
gh api -X POST "repos/{owner}/{repo}/pages" \
  -f build_type=workflow \
  -f source[branch]=main \
  -f source[path]=/ 2>/dev/null || \
gh api -X PUT "repos/{owner}/{repo}/pages" \
  -f build_type=workflow 2>/dev/null || true

# Trigger workflow
gh workflow run deploy-pages.yml 2>/dev/null || true

OWNER="$(gh api user -q .login)"
echo ""
echo "Pushed. After the Actions workflow finishes (1–2 min), the site will be at:"
echo "  https://${OWNER}.github.io/${REPO_NAME}/"
echo ""
echo "Check status:  gh run list --workflow=deploy-pages.yml"
echo "Open Actions:  https://github.com/${OWNER}/${REPO_NAME}/actions"
