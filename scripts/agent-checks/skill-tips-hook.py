#!/usr/bin/env python3
"""Skill tips and suggestions for Hafiz (issue #331, step of #312).

Two modes, both reading docs/agent-playbooks/skill-tips.json:

  --tip      PostToolUse on the Skill tool. After a skill is used, print
             `Tip: /name: <sentence>` once per skill per session.
  --suggest  UserPromptSubmit. When the prompt matches a skill's trigger
             phrases and that skill was not used or suggested yet, print
             `Suggestion: /name could help here: <reason>`.

Rules (the point is to stay quiet):
  * At most one suggestion per prompt and three per session; never the same
    skill twice; never on very short prompts, prompts that already name a
    skill, injected system text, or replies to a question.
  * Fail-open: any error prints nothing and exits 0. No network, no secret
    files, no blocking. The only file read besides the tips file is the tail of
    the session's own transcript, to see whether the last assistant message
    was a question.
  * `SIFUTUTOR_SKILL_TIPS=0` turns both modes off.

Environment overrides (tests): SIFUTUTOR_SKILL_TIPS_FILE,
SIFUTUTOR_SKILL_TIPS_STATE_DIR.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TIPS_FILE = ROOT / "docs" / "agent-playbooks" / "skill-tips.json"
DEFAULT_STATE_DIR = Path.home() / ".local" / "state" / "sifututor-agent-os" / "skill-tips"

MAX_SUGGESTIONS_PER_SESSION = 3
MIN_PROMPT_CHARS = 25
MIN_PROMPT_WORDS = 5
MATCH_WINDOW_CHARS = 400
TRANSCRIPT_TAIL_BYTES = 131072
STATE_MAX_AGE_SECONDS = 14 * 24 * 3600

# A prompt that begins like this is an answer, not a new request.
ANSWER_START = re.compile(
    r"^\s*(yes|yep|yeah|yup|no|nope|ok|okay|sure|proceed|approve|approved|continue|"
    r"go ahead|go on|do it|option\b|the first|the second|the third|first one|second one|"
    r"third one|both|neither|[1-9][.)]?(\s|$)|[a-d][.)]\s)",
    re.IGNORECASE,
)
SESSION_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")

PROJECT_ALIASES = {
    "sifu-tutor": ("sifu-tutor", "sifu_tutor", "sims"),
    "ripple-suite": ("ripple-suite", "ripple"),
    "kelas": ("kelas", "kelasapp"),
}


def enabled() -> bool:
    return os.environ.get("SIFUTUTOR_SKILL_TIPS", "1") != "0"


def tips_path() -> Path:
    override = os.environ.get("SIFUTUTOR_SKILL_TIPS_FILE")
    return Path(override) if override else DEFAULT_TIPS_FILE


def state_dir() -> Path:
    override = os.environ.get("SIFUTUTOR_SKILL_TIPS_STATE_DIR")
    return Path(override) if override else DEFAULT_STATE_DIR


def load_entries(path: Path, agent: str = "claude") -> list[dict]:
    """Return usable entries for this agent. Any problem returns an empty list."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        raw = data["skills"]
    except Exception:
        return []
    entries: list[dict] = []
    if not isinstance(raw, list):
        return entries
    for item in raw:
        try:
            name = item["name"]
            tip = item["tip"]
            triggers = item["triggers"]
            agents = item.get("agents", ["claude", "codex"])
            if not (isinstance(name, str) and isinstance(tip, str) and tip.strip()):
                continue
            if not (isinstance(triggers, list) and triggers):
                continue
            if agent not in agents:
                continue
            entries.append(item)
        except Exception:
            continue
    return entries


def compile_trigger(phrase: str) -> re.Pattern:
    pieces = [re.escape(part) for part in phrase.lower().split()]
    return re.compile(r"(?<![\w])" + r"\s+".join(pieces) + r"(?![\w])")


def normalise(text: str) -> str:
    return text.replace("’", "'").replace("‘", "'").lower()


def names_in_prompt(prompt: str, entries: list[dict]) -> set[str]:
    """Skill names the prompt already mentions as /name, $name or a hyphenated name."""
    found: set[str] = set()
    text = normalise(prompt)
    for item in entries:
        name = item["name"].lower()
        if re.search(r"(?<![\w/])[/$]" + re.escape(name) + r"(?![\w-])", text):
            found.add(item["name"])
        elif "-" in name and re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", text):
            found.add(item["name"])
    return found


def project_allows(item: dict, prompt: str, cwd: str) -> bool:
    project = item.get("project")
    if not project:
        return True
    aliases = PROJECT_ALIASES.get(project, (project,))
    haystack = normalise(prompt[:MATCH_WINDOW_CHARS]) + " " + (cwd or "").lower()
    return any(alias in haystack for alias in aliases)


def best_match(prompt: str, entries: list[dict], blocked: set[str], cwd: str = "") -> dict | None:
    text = normalise(prompt)[:MATCH_WINDOW_CHARS]
    best: tuple[int, int] | None = None
    best_item: dict | None = None
    for item in entries:
        if item["name"] in blocked or not project_allows(item, prompt, cwd):
            continue
        hits = [t for t in item["triggers"] if isinstance(t, str) and t.strip() and compile_trigger(t).search(text)]
        if not hits:
            continue
        score = (len(hits), max(len(t) for t in hits))
        if best is None or score > best:
            best, best_item = score, item
    return best_item


def looks_like_reply(prompt: str, asked_question: bool) -> bool:
    return asked_question or bool(ANSWER_START.match(prompt[:200]))


def is_injected_text(prompt: str) -> bool:
    head = prompt.lstrip()[:1]
    return head in ("<", "[", "/", "$", "!")


def long_enough(prompt: str) -> bool:
    stripped = prompt.strip()
    return len(stripped) >= MIN_PROMPT_CHARS and len(stripped.split()) >= MIN_PROMPT_WORDS


def decide_suggestion(
    prompt: str,
    entries: list[dict],
    state: dict,
    *,
    asked_question: bool = False,
    cwd: str = "",
) -> dict | None:
    """Pure decision. Updates `state` (used / suggested) and returns the entry to suggest."""
    if not isinstance(prompt, str) or not entries:
        return None
    named = names_in_prompt(prompt, entries)
    if named:
        for name in named:
            if name not in state["used"]:
                state["used"].append(name)
        return None
    if is_injected_text(prompt) or not long_enough(prompt):
        return None
    if looks_like_reply(prompt, asked_question):
        return None
    if len(state["suggested"]) >= MAX_SUGGESTIONS_PER_SESSION:
        return None
    blocked = set(state["used"]) | set(state["suggested"])
    item = best_match(prompt, entries, blocked, cwd)
    if item is None:
        return None
    state["suggested"].append(item["name"])
    return item


def suggestion_line(item: dict) -> str:
    reason = (item.get("reason") or item["tip"]).strip()
    return f"Suggestion: /{item['name']} could help here: {reason}"


def tip_line(item: dict) -> str:
    return f"Tip: /{item['name']}: {item['tip'].strip()}"


def resolve_skill_name(raw: str, entries: list[dict]) -> dict | None:
    names = {item["name"]: item for item in entries}
    candidate = raw.strip().lstrip("/")
    if candidate in names:
        return names[candidate]
    tail = candidate.split(":")[-1]
    return names.get(tail)


def decide_tip(skill_name: str, entries: list[dict], state: dict) -> dict | None:
    item = resolve_skill_name(skill_name, entries) if isinstance(skill_name, str) else None
    if item is None:
        return None
    if item["name"] not in state["used"]:
        state["used"].append(item["name"])
    if item["name"] in state["tipped"]:
        return None
    state["tipped"].append(item["name"])
    return item


# ---------------------------------------------------------------- state ----

def empty_state() -> dict:
    return {"used": [], "tipped": [], "suggested": []}


def state_file(directory: Path, session_id: str) -> Path:
    return directory / f"{session_id}.json"


def load_state(directory: Path, session_id: str) -> dict:
    state = empty_state()
    try:
        data = json.loads(state_file(directory, session_id).read_text(encoding="utf-8"))
        for key in state:
            if isinstance(data.get(key), list):
                state[key] = [x for x in data[key] if isinstance(x, str)]
    except Exception:
        pass
    return state


def prune_old(directory: Path) -> None:
    cutoff = time.time() - STATE_MAX_AGE_SECONDS
    try:
        for entry in os.scandir(directory):
            if entry.name.endswith(".json") and entry.stat().st_mtime < cutoff:
                os.unlink(entry.path)
    except OSError:
        pass


def save_state(directory: Path, session_id: str, state: dict) -> bool:
    """Atomic write. Returns False when the state could not be stored."""
    try:
        directory.mkdir(parents=True, exist_ok=True)
        target = state_file(directory, session_id)
        fresh = not target.exists()
        temp = directory / f".{session_id}.{os.getpid()}.tmp"
        temp.write_text(json.dumps(state), encoding="utf-8")
        os.replace(temp, target)
        if fresh:
            prune_old(directory)
        return True
    except Exception:
        return False


# ----------------------------------------------------------- transcript ----

def last_assistant_asked_question(transcript_path: str) -> bool:
    """True when the newest assistant text message in the transcript ends with a question."""
    if not transcript_path:
        return False
    try:
        path = Path(transcript_path)
        size = path.stat().st_size
        with path.open("rb") as handle:
            handle.seek(max(0, size - TRANSCRIPT_TAIL_BYTES))
            tail = handle.read().decode("utf-8", errors="ignore")
        for line in reversed(tail.splitlines()):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("type") != "assistant":
                continue
            content = (row.get("message") or {}).get("content")
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = "\n".join(
                    block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
                )
            else:
                continue
            text = text.strip()
            if text:
                return text.endswith("?")
    except Exception:
        return False
    return False


# ----------------------------------------------------------------- main ----

def emit(event: str, message: str, agent: str) -> None:
    out: dict = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": message}}
    if agent == "codex":
        out["continue"] = True
    print(json.dumps(out))


SHOW_NOTE = "Show Hafiz this line once, as one short line at the end of your reply."


def run(mode: str, agent: str, payload: dict) -> str | None:
    if not enabled() or not isinstance(payload, dict):
        return None
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not SESSION_ID.match(session_id):
        return None
    entries = load_entries(tips_path(), agent)
    if not entries:
        return None
    directory = state_dir()
    state = load_state(directory, session_id)
    if mode == "tip":
        tool_input = payload.get("tool_input") or {}
        raw = tool_input.get("skill") or tool_input.get("name") or ""
        item = decide_tip(raw, entries, state)
        line = tip_line(item) if item else None
        message = f"{line}\n{SHOW_NOTE}" if line else None
    else:
        prompt = payload.get("prompt") or ""
        asked = False
        if isinstance(prompt, str) and long_enough(prompt) and not is_injected_text(prompt):
            asked = last_assistant_asked_question(payload.get("transcript_path") or "")
        item = decide_suggestion(prompt, entries, state, asked_question=asked, cwd=payload.get("cwd") or "")
        line = suggestion_line(item) if item else None
        message = f"{line}\n{SHOW_NOTE}" if line else None
    # Save first. If the state cannot be stored, stay silent: no way to keep the once-only rule.
    if not save_state(directory, session_id, state):
        return None
    return message


def main(argv: list[str]) -> int:
    try:
        mode = "tip" if "--tip" in argv else "suggest" if "--suggest" in argv else ""
        if not mode:
            return 0
        agent = "codex" if "--agent" in argv and argv[argv.index("--agent") + 1 : argv.index("--agent") + 2] == ["codex"] else "claude"
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        message = run(mode, agent, payload)
        if message:
            emit("PostToolUse" if mode == "tip" else "UserPromptSubmit", message, agent)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
