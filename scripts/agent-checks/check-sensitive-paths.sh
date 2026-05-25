#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

if [[ "$repo_root" == *"/Projects/Sifututor/live"* ]]; then
  echo "sensitive-paths: refusing to operate inside live/ snapshot"
  exit 1
fi

status="$(git status --porcelain 2>/dev/null || true)"
if [[ -z "$status" ]]; then
  echo "sensitive-paths: clean"
  exit 0
fi

blocked="$(printf '%s\n' "$status" | awk '{print $2}' | grep -E '(^|/)(\.env($|[.])|live/|\.workflow-rollout/)' || true)"

if [[ -n "$blocked" ]]; then
  echo "sensitive-paths: blocked paths present"
  printf '%s\n' "$blocked"
  exit 1
fi

echo "sensitive-paths: ok"
