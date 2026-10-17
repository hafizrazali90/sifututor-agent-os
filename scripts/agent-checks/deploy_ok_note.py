#!/usr/bin/env python3
"""Record Hafiz's typed "deploy ok" for the current session.

This runs as a prompt hook, so it only ever sees what Hafiz typed. The phrase
must be the whole message or its last words, and must not follow "not", "never"
or "without". The agent cannot write this note, because the agent never types
Hafiz's prompt. The shared command guard (secret_output_guard.py) lets a
production deploy or a merge into main pass only while this note exists for the
same session.

Agreed with Hafiz on 17/10/2026.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import time

TTL_SECONDS = 12 * 3600
PHRASE_AT_END = re.compile(r"(?:^|[\s,;:.])deploy\s+ok[\s.!]*$", re.I)
NEGATED = re.compile(r"\b(?:do not|don't|dont|never|not|without)\b[^.\n]{0,40}\bdeploy\s+ok\b", re.I)
SESSION_ID = re.compile(r"[A-Za-z0-9_-]{1,100}")


def approval_dir() -> Path:
    override = os.environ.get("AGENT_OS_APPROVAL_DIR")
    return Path(override) if override else Path.home() / ".agent-os" / "approvals" / "deploy-ok"


def _note_file(session: str) -> Path | None:
    # Real session ids are UUIDs. Anything with other characters is refused, never cleaned up.
    if not isinstance(session, str) or not SESSION_ID.fullmatch(session):
        return None
    return approval_dir() / f"{session}.json"


def write_note(session: str, now: float | None = None) -> bool:
    path = _note_file(session)
    if path is None:
        return False
    stamp = time.time() if now is None else now
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"session_id": session, "at": stamp, "expires": stamp + TTL_SECONDS}), encoding="utf-8")
    path.chmod(0o600)
    return True


def note_active(session: str) -> bool:
    path = _note_file(session or "")
    if path is None or not path.is_file():
        return False
    try:
        expires = float(json.loads(path.read_text(encoding="utf-8")).get("expires", 0))
    except (OSError, ValueError, TypeError):
        return False
    return expires > time.time()


def handle(payload: dict) -> bool | None:
    session = payload.get("session_id") or payload.get("sessionId")
    prompt = payload.get("prompt")
    if not session or not isinstance(prompt, str):
        return None
    text = prompt.strip()
    if NEGATED.search(text) or not PHRASE_AT_END.search(text):
        return None
    return True if write_note(str(session)) else None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, TypeError):
        return 0
    if isinstance(payload, dict) and handle(payload):
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": "Hafiz typed deploy ok: production deploy and merge into main are allowed in this session.",
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
