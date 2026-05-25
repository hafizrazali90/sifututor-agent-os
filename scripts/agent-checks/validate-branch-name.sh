#!/usr/bin/env bash
set -euo pipefail

branch="$(git branch --show-current 2>/dev/null || true)"

if [[ -z "$branch" ]]; then
  echo "branch-name: no git branch detected"
  exit 0
fi

case "$branch" in
  main|master|develop|staging|dev|live-qa|integration|sifu-staging|sifu-backport)
    echo "branch-name: ok ($branch)"
    exit 0
    ;;
esac

if [[ "$branch" =~ ^(sifu|lls|learnest|nakngaji)-[a-z0-9][a-z0-9-]*$ ]]; then
  echo "branch-name: ok ($branch)"
  exit 0
fi

if [[ "$branch" =~ ^release[/-][a-z0-9][a-z0-9./-]*$ ]]; then
  echo "branch-name: ok ($branch)"
  exit 0
fi

if [[ "$branch" =~ ^(feat|feature|fix|refactor|hotfix|chore|docs|perf|test|ci)/[a-z0-9][a-z0-9-]*$ ]]; then
  echo "branch-name: ok ($branch)"
  exit 0
fi

cat <<EOF
branch-name: invalid ($branch)

Expected:
  type/description

Valid types:
  feat, feature, fix, refactor, hotfix, chore, docs, perf, test, ci

Example:
  fix/login-null-crash
EOF
exit 1
