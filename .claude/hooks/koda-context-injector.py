#!/usr/bin/env python3
"""
koda-context-injector.py — UserPromptSubmit hook
Searches Koda Memory for relevant context based on the user's prompt and injects
top memories as additionalContext before Claude processes the message.

Hard constraints (memory failures are silent and never block the user's prompt):
- 2s network timeout — if Koda is slow, skip memory context
- Skip memory context if KODA_API_KEY is missing or a response is malformed
- Still emit the shared communication reminders for a non-trivial human prompt
- Silent skip if prompt is short (< 10 chars) — likely not a real task
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

AGENT_CHECKS = Path(__file__).resolve().parents[2] / "scripts" / "agent-checks"
if str(AGENT_CHECKS) not in sys.path:
    sys.path.insert(0, str(AGENT_CHECKS))

from secret_output_guard import prompt_requests_secret_reveal, sync_secret_visual_boundary

KODA_URL = "https://koda.tutorla.tech/mcp"
TIMEOUT = 2  # seconds — hard cap, Koda must respond quickly or we skip
MIN_PROMPT_LEN = 10
CLOSEOUT_REMINDER = (
    "Agent OS close-out reminder: after meaningful work, make the final answer "
    "self-contained with what changed, how it was checked, the highest proven "
    "state, what remains, one recommended next action, and whether Hafiz needs "
    "to decide anything."
)
EXPLANATION_REMINDER = (
    "Agent OS explanation-first reminder: for bugs, PRs, features, or unfamiliar "
    "technical topics, explain who uses the workflow, what happens now, what "
    "should happen, and why it matters before findings or code. Before non-trivial "
    "implementation, explain the intended build, real options, recommendation, and "
    "evidence plan in English once; after approval, continue inside the agreed "
    "boundary without re-asking. If Hafiz asks "
    "to go one by one, cover one item with its effect, improvement, evidence, "
    "and decision, then stop before the next item unless he approved an "
    "autonomous walkthrough."
)
SECRET_SAFETY_REMINDER = (
    "Agent OS secret-safety boundary: do not take screenshots, accessibility "
    "snapshots, DOM captures, or copied text from a provider page that displays "
    "a complete key, token, password, or private credential. Use owner-only "
    "hidden entry and verify only non-secret status or a boolean match through "
    "an approved wrapper."
)


def _emit_context(memory_context="", safety_context=""):
    sections = [
        section
        for section in (memory_context, safety_context, EXPLANATION_REMINDER, CLOSEOUT_REMINDER)
        if section
    ]
    print(json.dumps({
        "hookSpecificOutput": {
            "additionalContext": "\n\n".join(sections)
        }
    }))


# All 9 Sifututor project names + aliases — used to detect project intent in
# user prompts. Order: longer/more-specific names first to avoid substring
# collision (sifututor_parent contains "sifu" — we want to match the longer
# name). Aliases match the dispatcher patches in ~/.claude/skills/*/SKILL.md.
#
# Removed "rn" alias — too short, false-positive risk in natural language
# (turn, earn, learn, error, etc.). For explicit /save-session rn invocations,
# the dispatcher skill still accepts it — that's a different code path.
# For Koda search, users should write "sifututor_tutor" or "tutor-app" or
# the explicit project name. This hook is for NL prompt detection, where
# precision > recall.
PROJECT_NAMES = [
    "kelasapp", "kelas-app", "kelas",
    "sifututor_parent", "sifututor-parent", "parent-app",
    "sifututor_tutor", "sifututor-tutor", "tutor-app",
    "ripple-suite", "ripple", "dashboard",
    "sifu-tutor", "sifu",
    "lls-frontend", "lls-mobile", "lls",
    "creative-hub",
    # issue 103: team-inbox is retired; finch-inbox replaced it. Keep this
    # list identical in meaning to codex-lifecycle-hook.py PROJECT_ALIASES.
    "finch-inbox", "finch",
    "cx-call-capture-android", "cx-call-capture",
    "sims-owner-analytics",
]

# Normalized project tags (what's actually stored in Koda)
PROJECT_TAG_MAP = {
    "kelasapp": "kelas", "kelas-app": "kelas", "kelas": "kelas",
    "sifututor_parent": "sifututor_parent", "sifututor-parent": "sifututor_parent",
    "parent-app": "sifututor_parent",
    "sifututor_tutor": "sifututor_tutor", "sifututor-tutor": "sifututor_tutor",
    "tutor-app": "sifututor_tutor",
    "ripple-suite": "ripple-suite", "ripple": "ripple-suite",
    "dashboard": "ripple-suite",
    "sifu-tutor": "sifu-tutor", "sifu": "sifu-tutor",
    "lls-frontend": "lls-frontend",
    "lls-mobile": "lls-mobile",
    "lls": "lls",
    "creative-hub": "creative-hub",
    "finch-inbox": "finch-inbox", "finch": "finch-inbox",
    "cx-call-capture-android": "cx-call-capture-android",
    "cx-call-capture": "cx-call-capture-android",
    "sims-owner-analytics": "sims-owner-analytics",
}


def _detect_project_intent(prompt: str) -> str:
    """Return the canonical project tag if the prompt mentions a project, else empty string.

    Algorithm: find ALL project names that appear in the prompt, return the
    canonical tag for the EARLIEST OCCURRENCE in the prompt. This handles
    cross-project prompts correctly (e.g., "lls and sifu-tutor" → returns lls).

    Substring collisions (e.g., "sifu" inside "sifututor_parent") are handled
    by iterating PROJECT_NAMES in long-first order — when we find "sifututor_parent"
    at position N, we record it; "sifu" later in the string at position N+k won't
    override it for the EARLIEST_POSITION lookup since both compete on position.
    """
    p = prompt.lower()
    matches = []  # list of (position, canonical_tag)
    for name in PROJECT_NAMES:
        idx = p.find(name)
        if idx >= 0:
            matches.append((idx, PROJECT_TAG_MAP[name]))
    if not matches:
        return ""
    # Sort by position; first match wins. Ties broken by iteration order
    # (which is long-first, so substring collisions resolve correctly).
    matches.sort(key=lambda m: m[0])
    return matches[0][1]


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    user_prompt = data.get("user_prompt", "")
    sync_secret_visual_boundary(data, user_prompt)
    if len(user_prompt.strip()) < MIN_PROMPT_LEN:
        sys.exit(0)
    safety_context = (
        SECRET_SAFETY_REMINDER if prompt_requests_secret_reveal(user_prompt) else ""
    )

    api_key = os.environ.get("KODA_API_KEY", "")
    if not api_key:
        _emit_context(safety_context=safety_context)
        return

    # Detect project intent — if user mentioned a specific project, we'll
    # boost relevance by running an additional tag-filtered search.
    detected_project = _detect_project_intent(user_prompt)

    base_headers = {
        "Content-Type": "application/json",
        # Streamable HTTP MCP transport requires BOTH json + SSE accept.
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {api_key}",
    }

    def _post(payload_dict, extra_headers=None):
        """POST to Koda MCP; return (body_str, content_type, session_id, status). All exceptions are caught -> None tuple."""
        headers = dict(base_headers)
        if extra_headers:
            headers.update(extra_headers)
        try:
            req = urllib.request.Request(
                KODA_URL,
                data=json.dumps(payload_dict).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                body = resp.read().decode("utf-8")
                ctype = resp.headers.get("Content-Type", "")
                sid = resp.headers.get("Mcp-Session-Id", "")
                return body, ctype, sid, resp.status
        except Exception:
            return None, None, None, None

    def _unwrap_sse(body, ctype):
        """If SSE response, extract the first data line as JSON body."""
        if body and "text/event-stream" in (ctype or ""):
            for line in body.splitlines():
                if line.startswith("data:"):
                    return line[len("data:"):].strip()
        return body

    # Step 1: initialize the MCP session
    init_body, init_ctype, session_id, init_status = _post({
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "koda-context-injector", "version": "1.0"},
        },
        "id": 1,
    })
    if not init_body or not session_id:
        _emit_context(safety_context=safety_context)
        return

    # Step 2: send the initialized notification (some MCP servers require it)
    _post(
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        extra_headers={"Mcp-Session-Id": session_id},
    )

    # Step 3: call memory_search — cross-project (no tag filter) by default.
    # If user mentioned a specific project, we'll do an ADDITIONAL tag-filtered
    # search and merge results to boost project-specific relevance.
    body, content_type, _, _ = _post(
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "memory_search",
                "arguments": {"query": user_prompt[:500], "limit": 5},
            },
            "id": 2,
        },
        extra_headers={"Mcp-Session-Id": session_id},
    )

    if not body:
        _emit_context(safety_context=safety_context)
        return

    body = _unwrap_sse(body, content_type)

    # If user mentioned a project, also do a project-tag-filtered search to
    # boost relevance for that project. Merge into one bullet list.
    project_body = None
    if detected_project:
        pbody, pctype, _, _ = _post(
            {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "memory_search",
                    "arguments": {
                        "query": user_prompt[:500],
                        "limit": 3,
                        "tags": [detected_project],
                    },
                },
                "id": 3,
            },
            extra_headers={"Mcp-Session-Id": session_id},
        )
        if pbody:
            project_body = _unwrap_sse(pbody, pctype)

    def _parse_memories(raw_body):
        """Parse Koda's MCP response → list of memory dicts. Returns [] on any failure."""
        try:
            r = json.loads(raw_body)
            inner = r.get("result", {})
            content_arr = inner.get("content", []) if isinstance(inner, dict) else []
            if not content_arr:
                return []
            text_payload = ""
            for c in content_arr:
                if isinstance(c, dict) and c.get("type") == "text" and c.get("text"):
                    text_payload = c["text"]
                    break
            if not text_payload:
                return []
            mems = json.loads(text_payload)
            return mems if isinstance(mems, list) else []
        except Exception:
            return []

    cross_memories = _parse_memories(body)
    project_memories = _parse_memories(project_body) if project_body else []

    # Merge + dedupe by memory ID (project-tagged results first to boost them)
    seen_ids = set()
    merged = []
    for mem in project_memories + cross_memories:
        if not isinstance(mem, dict):
            continue
        mid = mem.get("id", "")
        if mid and mid in seen_ids:
            continue
        if mid:
            seen_ids.add(mid)
        merged.append(mem)

    if not merged:
        _emit_context(safety_context=safety_context)
        return

    # Format top 5 (or 7 if we had a project boost — more cross-project signal)
    limit = 7 if project_memories else 5
    bullets = []
    for mem in merged[:limit]:
        if not isinstance(mem, dict):
            continue
        content = (mem.get("content") or "").strip()
        mem_id = mem.get("id", "")
        tags = mem.get("tags", [])
        tag_str = f" [{','.join(tags[:3])}]" if tags else ""
        snippet = content.split("\n")[0][:180]
        if snippet:
            bullets.append(f"- ({mem_id}{tag_str}) {snippet}")

    if not bullets:
        _emit_context(safety_context=safety_context)
        return

    header = "Relevant Koda memories (search-injected — verify before relying on):"
    if detected_project:
        header = f"Relevant Koda memories (detected project: {detected_project}; cross-project + tag-boosted):"
    context = header + "\n" + "\n".join(bullets)
    _emit_context(context, safety_context)


if __name__ == "__main__":
    main()
