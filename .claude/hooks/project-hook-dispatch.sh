#!/usr/bin/env bash
# AGENT-OS-CLAUDE-HOOK-DISPATCHER
set -u
HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd -P)"
ROOT="$(cd -- "$HOOK_DIR/../.." && pwd -P)"
exec python3 "$ROOT/scripts/agent-checks/claude_hook_dispatch.py" \
  --dispatch-hook "$(basename -- "$0")" --self-path "$HOOK_DIR/$(basename -- "$0")" -- "$@"
