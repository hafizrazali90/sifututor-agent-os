#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$script_dir/validate-branch-name.sh"
"$script_dir/check-sensitive-paths.sh"
"$script_dir/check-active-task.sh"

echo "pre-commit-guard: completed"
