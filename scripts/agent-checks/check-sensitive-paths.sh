#!/usr/bin/env bash
set -euo pipefail

paths_from_status() {
  sed -E 's/^...//' | while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    printf '%s\n' "$path"
    if [[ "$path" == *" -> "* ]]; then
      printf '%s\n' "${path##* -> }"
    fi
  done
}

sensitive_paths_from_status() {
  paths_from_status | grep -E '(^|/)(\.env($|[.])|\.workflow-rollout/)|^live/' || true
}

main() {
  local repo_root
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  cd "$repo_root"

  if [[ "$repo_root" == *"/Projects/Sifututor/live"* ]]; then
    echo "sensitive-paths: refusing to operate inside live/ snapshot"
    exit 1
  fi

  local status
  status="$(git status --porcelain 2>/dev/null || true)"
  if [[ -z "$status" ]]; then
    echo "sensitive-paths: clean"
    exit 0
  fi

  local blocked
  blocked="$(printf '%s\n' "$status" | sensitive_paths_from_status)"

  if [[ -n "$blocked" ]]; then
    echo "sensitive-paths: blocked paths present"
    printf '%s\n' "$blocked"
    exit 1
  fi

  echo "sensitive-paths: ok"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
