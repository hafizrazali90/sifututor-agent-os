#!/usr/bin/env python3
"""Single source for the Koda MCP endpoint used by every umbrella helper.

Resolution order, first hit wins:

1. `KODA_MCP_URL` in the process environment (per-shell override).
2. `KODA_MCP_URL=<url>` in the shared conf file `~/.config/sifututor/koda.conf`
   (the same non-secret conf-lane layout the agent-access wrappers use).
   This is the one place a machine-wide change is made; the sub-project
   `memory-flush.py` hooks read the same variable and the same file, so
   nothing needs re-editing in five repositories when the endpoint moves.
3. The canonical production endpoint below, as a last-resort default.

The API key is deliberately not handled here; each caller keeps its own
`KODA_API_KEY` handling and nothing in this module reads or prints it.
"""

from __future__ import annotations

import os
from pathlib import Path

CANONICAL_KODA_MCP_URL = "https://koda.tutorla.tech/mcp"
ENV_VAR = "KODA_MCP_URL"
SHARED_CONF = Path.home() / ".config" / "sifututor" / "koda.conf"


def _read_conf_value(path: Path, key: str) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, _, value = stripped.partition("=")
        if name.strip() == key:
            return value.strip().strip("'\"")
    return ""


def resolve_koda_mcp_url(env: dict | None = None, conf_path: Path | None = None) -> str:
    """Return the Koda MCP endpoint per the resolution order in the docstring."""
    resolved_env = os.environ if env is None else env
    value = (resolved_env.get(ENV_VAR) or "").strip()
    if value:
        return value
    value = _read_conf_value(SHARED_CONF if conf_path is None else conf_path, ENV_VAR)
    if value:
        return value
    return CANONICAL_KODA_MCP_URL


KODA_MCP_URL = resolve_koda_mcp_url()
