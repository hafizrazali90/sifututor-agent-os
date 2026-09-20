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

# Issue 112. Staff documentation release enforcement. Advisory here on purpose:
# a project still learning the habit should not be blocked from committing, but
# the finding is printed in plain English and the same engine blocks at release
# (--mode blocking --base main). Scoped to the decisions this change touches, so
# an older release's decision is never re-opened. A project with no configured
# or detected staff-documentation shape reports UNAVAILABLE and passes.
python3 "$script_dir/release_documentation.py" --project . --mode advisory --staged

echo "pre-commit-guard: completed"
