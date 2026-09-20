#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$script_dir/validate-branch-name.sh"
"$script_dir/check-sensitive-paths.sh"
"$script_dir/check-active-task.sh"
python3 "$script_dir/secret_artifact_scan.py"
python3 "$script_dir/mission-ledger-check.py"

# Issue 2 / CP-11. Model-agnostic test-coverage enforcement. Scoped to the rows
# this change actually touches, so pre-existing coverage debt elsewhere in a
# project's TESTING.md never blocks an unrelated commit. A project without a
# manifest reports UNAVAILABLE and passes.
python3 "$script_dir/coverage_enforcement.py" --project . --mode change --staged

echo "pre-commit-guard: completed"
