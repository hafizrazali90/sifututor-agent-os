#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/check-sensitive-paths.sh"

failures=0

assert_blocked() {
  local label="$1"
  local status_line="$2"
  local expected="$3"
  local actual
  actual="$(printf '%s\n' "$status_line" | sensitive_paths_from_status)"

  if [[ "$actual" == "$expected" ]]; then
    printf 'PASS %-36s %s\n' "$label" "$expected"
  else
    printf 'FAIL %-36s expected=%s actual=%s\n' "$label" "$expected" "${actual:-<empty>}"
    failures=$((failures + 1))
  fi
}

assert_allowed() {
  local label="$1"
  local status_line="$2"
  local actual
  actual="$(printf '%s\n' "$status_line" | sensitive_paths_from_status)"

  if [[ -z "$actual" ]]; then
    printf 'PASS %-36s allowed\n' "$label"
  else
    printf 'FAIL %-36s expected=allowed actual=%s\n' "$label" "$actual"
    failures=$((failures + 1))
  fi
}

assert_blocked "root live snapshot" " M live/sifu-tutor/file.txt" "live/sifu-tutor/file.txt"
assert_blocked "nested env file" " M ripple-suite/.env.production" "ripple-suite/.env.production"
assert_blocked "workflow rollout path" " M .workflow-rollout/sifu-tutor/file.txt" ".workflow-rollout/sifu-tutor/file.txt"
assert_blocked "rename into root live" "R  docs/example.txt -> live/example.txt" "live/example.txt"
assert_allowed "qa live route segment" " M src/app/api/qa/live/route.ts"
assert_allowed "ripple qa live route segment" " M ripple-suite/src/app/api/qa/live/start/route.ts"

if [[ "$failures" -gt 0 ]]; then
  printf 'check-sensitive-paths-fixture-runner: %d failure(s)\n' "$failures"
  exit 1
fi

echo "check-sensitive-paths-fixture-runner: all passed"
