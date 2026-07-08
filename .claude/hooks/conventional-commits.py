#!/usr/bin/env python3
"""
Validate git commit messages follow Conventional Commits format.
Format: [emoji] type(scope): description

IMPORTANT: This hook validates the raw command string BEFORE the shell expands it.
This means HEREDOC-style commit messages like:
  git commit -m "$(cat <<'EOF' ... EOF)"
will NOT be parsed correctly -- the hook sees '$(cat <<' as the message.

Always use direct -m flags:
  git commit -m "emoji type(scope): title" -m "Body." -m "Co-Authored-By: ..."

Also avoid emojis with variation selectors (U+FE0F) as they can cause regex issues.
Stick to simple emojis without modifiers.
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

# Only validate git commit commands
if tool_name != "Bash" or "git commit" not in command:
    sys.exit(0)

# Skip if --no-verify is passed
if "--no-verify" in command:
    sys.exit(0)

# Extract commit message from the FIRST -m flag
# Handle both -m "message" and -m 'message' formats
match = re.search(r'git commit.*?-m\s+["\']([^"\']+)["\']', command)
if not match:
    # If we can't extract a message, allow it (could be --amend with no -m, etc.)
    sys.exit(0)

commit_msg = match.group(1)

# Get first line only (ignore body/co-author lines)
first_line = commit_msg.split('\n')[0].strip()

# Check if message follows Conventional Commits format
# Allow optional emoji prefix before the type keyword
# Format: [emoji] type(scope)?: description
# Types: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert, wip
#
# Emoji range: covers most common emojis used in conventional commits
# We use a permissive pattern that allows any non-ASCII characters before the type
conventional_pattern = r'^[^\x00-\x7F\s]*\s*?(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert|wip)(\(.+\))?:\s.+'

if not re.match(conventional_pattern, first_line):
    reason = f"""Invalid commit message format.

Your message: {first_line}

Commit messages must follow Conventional Commits:
  [emoji] type(scope): description

Types:
  feat:     New feature
  fix:      Bug fix
  docs:     Documentation changes
  style:    Code style changes (formatting)
  refactor: Code refactoring
  perf:     Performance improvements
  test:     Adding or updating tests
  chore:    Maintenance tasks
  ci:       CI/CD changes
  build:    Build system changes
  revert:   Revert previous commit
  wip:      Work in progress

Examples:
  feat: add user authentication
  feat(auth): implement JWT tokens
  fix: resolve memory leak in parser
  fix(api): handle null responses
  docs: update API documentation

With emoji:
  ✨ feat: add user authentication
  🐛 fix: resolve memory leak
  📝 docs: update API reference

IMPORTANT:
  - Use -m flags directly, not HEREDOC
  - Use multiple -m flags for multi-line commits:
    git commit -m "✨ feat: title" -m "Body text." -m "Co-Authored-By: ..."
  - Avoid emojis with variation selectors (like the lightning bolt with modifier)"""

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }
    print(json.dumps(output))
    sys.exit(0)

# Allow the command
sys.exit(0)
