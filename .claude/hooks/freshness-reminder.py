#!/usr/bin/env python3
"""AGENT-OS-CLAUDE-HOOK-DISPATCHER"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "agent-checks"))
from claude_hook_dispatch import wrapper_main
raise SystemExit(wrapper_main(Path(__file__).name, __file__, sys.argv[1:]))
