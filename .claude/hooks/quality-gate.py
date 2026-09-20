#!/usr/bin/env python3
"""Umbrella dispatcher wrapper for the sub-project `quality-gate.py` hook.

AGENT-OS-CLAUDE-HOOK-DISPATCHER

Issue 96. Sub-project settings run this hook as:

    cd "$CLAUDE_PROJECT_DIR" && python3 .claude/hooks/quality-gate.py

When a session is launched from the umbrella workspace, `CLAUDE_PROJECT_DIR`
stays on the umbrella even after work moves into a sub-project worktree, so that
command looks here for a script that only exists inside the sub-project. Without
this wrapper python exits 2 and a PreToolUse exit 2 cancels every Bash call.

All behaviour lives in scripts/agent-checks/claude_hook_dispatch.py. Keep this
file thin: it only names the hook and hands over.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "agent-checks"))

try:
    from claude_hook_dispatch import wrapper_main
except ImportError:
    # Missing shared dispatcher is missing infrastructure, not a gate rejection.
    sys.stderr.write(
        "[agent-os] claude hook dispatch: shared dispatcher unavailable for "
        "quality-gate.py; skipped without blocking\n"
    )
    raise SystemExit(0)

raise SystemExit(wrapper_main("quality-gate.py", __file__))
