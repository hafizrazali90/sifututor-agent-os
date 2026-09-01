#!/usr/bin/env python3
"""Compatibility entry point for Codex's approved direct Koda helper.

The connection implementation lives in ``codex-lifecycle-hook.py``. Keeping
this file as a small process-level forwarder preserves the historical
``koda-direct.py`` entry point without duplicating credential or MCP logic.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys


CANONICAL_HELPER = Path(__file__).resolve().with_name("codex-lifecycle-hook.py")


def main() -> int:
    if not CANONICAL_HELPER.is_file():
        print(
            f"KODA DIRECT FAIL: canonical helper missing: {CANONICAL_HELPER}",
            file=sys.stderr,
        )
        return 1

    os.execv(
        sys.executable,
        [sys.executable, str(CANONICAL_HELPER), *sys.argv[1:]],
    )
    return 1  # pragma: no cover - os.execv replaces this process on success.


if __name__ == "__main__":
    raise SystemExit(main())
