#!/usr/bin/env python3
"""
Parent-workspace validate-branch-name hook.

Enforces the unified Sifututor branch pattern across all sub-projects:
  type/description

Valid types: feat, fix, refactor, hotfix, chore, docs, perf, test, ci
Description: kebab-case (lowercase letters, numbers, hyphens)

Also allows base branches, deployment/environment branches, and release branches.

History: until 2026-05-24, sifututor_tutor enforced a stricter type/TUT-XXX-description
pattern. That requirement was dropped for consistency — all projects now share the same
branch convention.
"""
import json
import sys
import re

try:
    input_data = json.load(sys.stdin)
except Exception:
    # Silent skip on malformed/empty input — never block legitimate work.
    sys.exit(0)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

# Only validate git checkout -b and git switch -c commands
if tool_name != "Bash":
    sys.exit(0)
if "git checkout -b" not in command and "git switch -c" not in command:
    sys.exit(0)

# Extract branch name
match = re.search(r'git (?:checkout -b|switch -c)\s+([^\s]+)', command)
if not match:
    sys.exit(0)
branch_name = match.group(1)

# Allow base branches across all projects
base_branches = {"main", "master", "develop", "staging", "dev", "live-qa",
                 "integration", "sifu-staging", "sifu-backport"}
if branch_name in base_branches:
    sys.exit(0)

# Allow deployment/environment branches (sifu-*, lls-*, learnest-*, nakngaji-*)
if re.match(r'^(sifu|lls|learnest|nakngaji)-[a-z0-9][a-z0-9-]*$', branch_name):
    sys.exit(0)

# Allow release branches (release/* and release-*)
if re.match(r'^release[/-][a-z0-9][a-z0-9./-]*$', branch_name):
    sys.exit(0)

# Skip validation inside SSH remote-server commands
if "ssh " in command and branch_name in command:
    sys.exit(0)

# Unified pattern: type/description
valid_types = "feat|feature|fix|refactor|hotfix|chore|docs|perf|test|ci"
pattern = rf'^({valid_types})/[a-z0-9][a-z0-9-]*$'

if re.match(pattern, branch_name):
    sys.exit(0)

# Reject
reason = f"""Branch name rejected: {branch_name}

All Sifututor projects use the same branch pattern:
  type/description

Valid types:
  feat/     - New features
  fix/      - Bug fixes
  refactor/ - Code refactoring
  hotfix/   - Critical production fixes
  chore/    - Maintenance, config, dependencies
  docs/     - Documentation only
  perf/     - Performance improvements
  test/     - Test additions or fixes
  ci/       - CI/CD changes

Description rules:
  - Lowercase letters, numbers, and hyphens only
  - No spaces or underscores
  - Must start with a letter or number

Examples:
  feat/add-login-screen
  fix/null-crash-on-payment
  refactor/simplify-auth-flow
  docs/update-api-reference
  chore/upgrade-dependencies

Also allowed (no validation):
  - Base branches: main, master, develop, staging, dev, integration, live-qa,
                   sifu-staging, sifu-backport
  - Deployment: sifu-*, lls-*, learnest-*, nakngaji-*
  - Release: release/* or release-*

Invalid:
  {branch_name}"""

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason
    }
}
print(json.dumps(output))
sys.exit(0)
