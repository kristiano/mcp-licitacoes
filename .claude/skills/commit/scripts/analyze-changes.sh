#!/bin/bash
# Analyze git changes for commit message generation

echo "=== Git Status ==="
git status --short

echo ""
echo "=== Changed Files Stats ==="
git diff --stat 2>/dev/null || echo "(no unstaged changes)"

echo ""
echo "=== Staged Files Stats ==="
git diff --cached --stat 2>/dev/null || echo "(no staged changes)"

echo ""
echo "=== Recent Commits (context) ==="
git log --oneline -3 2>/dev/null || echo "(no commits yet)"
