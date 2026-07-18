#!/usr/bin/env python3
"""Privacy-conscious Claude/Codex transcript retrospective for Agent OS analysis.

The default report contains aggregate counts only. Raw conversation text is
never written. Optional diagnostic details contain short redacted excerpts and
must remain local and uncommitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SIFUTUTOR_ROOT_MARKERS = (
    "/Projects/Sifututor",
    "/Projects/Sifututor-worktrees",
)

MAX_JSON_RECORD_BYTES = 8 * 1024 * 1024
MAX_CAPTURE_CHARS = 100_000
EXCERPT_CHARS = 360
AGENT_OS_ROOT = Path(__file__).resolve().parents[2]

SYNTHETIC_USER_PREFIXES = (
    "<local-command-caveat>",
    "<local-command-stdout>",
    "<command-name>",
    "<system-reminder>",
    "Base directory for this skill:",
    "Sifututor workflow dispatcher:",
    "Relevant Koda memories (",
    "SessionStart:",
    "This session is being continued from a previous conversation",
    "<task-notification>",
    "Approach this as the design lead at a small studio",
    "# Update Config Skill",
    "Check Spotlight reindex progress:",
)

FORWARDED_CONTEXT_PREFIXES = (
    "Hi Hafiz",
    "LLS Hi Hafiz",
    "Subject:",
    "@Hafiz",
)

USER_SIGNAL_PATTERNS = {
    "explicit_correction": re.compile(
        r"\b(?:wrong|incorrect|contradiction|not what i|you (?:didn['’]?t|did not)|"
        r"u (?:didn['’]?t|did not)|you forgot|you missed|why did you|dont forget|"
        r"don['’]?t forget|not done|not finish(?:ed)?)\b",
        re.I | re.S,
    ),
    "repeat_friction": re.compile(
        r"\b(?:again|still|keep (?:asking|doing)|already (?:said|told|approved)|"
        r"how many times|same (?:thing|question|problem))\b",
        re.I | re.S,
    ),
    "autonomy_until_done": re.compile(
        r"(?:\b(?:proceed|continue|finish|handle|complete|do everything|go ahead)\b"
        r".{0,80}\b(?:until|end[- ]to[- ]end|fully|properly|done|finish(?:ed)?)\b)|"
        r"(?:\buntil (?:it is |it['’]?s )?(?:done|finish(?:ed)?)\b)",
        re.I | re.S,
    ),
    "asks_explanation": re.compile(
        r"\b(?:explain|simple terms?|plain (?:english|language)|non[- ]technical|"
        r"what does|what do you mean|why (?:do|does|is|are|need))\b",
        re.I,
    ),
    "asks_next": re.compile(
        r"\b(?:what(?:'s| is) next|what should (?:we|i) do next|go next|next step|"
        r"where (?:are we|were we))\b",
        re.I,
    ),
    "stop_or_redirect": re.compile(
        r"\b(?:stop|hold on|wait|pause|don['’]?t do|do not do|leave it|skip it)\b",
        re.I,
    ),
    "agent_os_improvement": re.compile(
        r"\b(?:agent os|workflow|future agents?|claude and codex|codex and claude)\b"
        r".{0,100}\b(?:improv|fix|better|parity|drift|behavior|behaviour|confus)",
        re.I | re.S,
    ),
    "comprehensive_scope": re.compile(
        r"\b(?:all|every|complete|comprehensive|deep|fully|end[- ]to[- ]end)\b",
        re.I,
    ),
    "commit_request": re.compile(r"\bcommit\b", re.I),
    "push_or_pr_request": re.compile(r"\b(?:push|pull request|open (?:a )?pr|pr)\b", re.I),
    "deploy_request": re.compile(r"\bdeploy(?:ment|ed|ing)?\b", re.I),
}

ASSISTANT_SIGNAL_PATTERNS = {
    "status_field": re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?status(?:\*\*)?\s*:"),
    "meaning_field": re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?meaning(?:\*\*)?\s*:"),
    "checked_field": re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?checked(?:\*\*)?\s*:"),
    "recommended_next_field": re.compile(
        r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?recommended next(?:\*\*)?\s*:"
    ),
    "decision_needed_field": re.compile(
        r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?decision needed(?:\*\*)?\s*:"
    ),
    "next_action_language": re.compile(
        r"\b(?:next (?:action|step|move)|recommend(?:ed|ation)?|what comes next)\b", re.I
    ),
    "check_language": re.compile(
        r"\b(?:checked|verified|tested|tests? pass(?:ed)?|lint|build|smoke|evidence)\b", re.I
    ),
    "done_claim": re.compile(r"\b(?:done|complete(?:d)?|finished|resolved|fixed)\b", re.I),
    "needs_decision": re.compile(
        r"\b(?:decision needed|need (?:your|hafiz['’]?s) (?:approval|decision|input)|"
        r"waiting for (?:your|hafiz['’]?s) (?:approval|decision)|please (?:approve|choose|confirm))\b",
        re.I,
    ),
    "hard_gate_language": re.compile(
        r"\b(?:production|deploy|critical|migration|payment|destructive|rollback|"
        r"exact file list|commit (?:rule|gate|approval)|push (?:rule|gate|approval))\b",
        re.I,
    ),
    "unverified_or_blocked": re.compile(
        r"\b(?:unverified|not verified|could not|couldn['’]?t|unable|blocked|unavailable|"
        r"not available|remaining gap|still need)\b",
        re.I,
    ),
    "koda_action": re.compile(r"\b(?:koda|memory_(?:search|store|update)|memory saved)\b", re.I),
    "workflow_jargon": re.compile(r"\b(?:PARTIAL|BLOCKER|Gate 2A|Gate 2B|Critical Save)\b"),
    "local_state": re.compile(r"\b(?:local(?:ly)?|working tree|worktree|dirty)\b", re.I),
    "commit_state": re.compile(r"\b(?:commit(?:ted)?|SHA)\b", re.I),
    "github_state": re.compile(r"\b(?:push(?:ed)?|pull request|PR\s*#|on GitHub|merged)\b", re.I),
    "live_state": re.compile(r"\b(?:deploy(?:ed|ment)?|production|live smoke|live)\b", re.I),
}

REVIEW_SIGNAL_WEIGHTS = {
    "explicit_correction": 10,
    "repeat_friction": 6,
    "asks_explanation": 4,
    "asks_next": 3,
    "stop_or_redirect": 4,
}

REVIEW_RISK_WEIGHTS = {
    "autonomy_may_have_been_reasked": 6,
    "short_approval_followed_by_decision": 2,
}

SHORT_APPROVALS = {
    "yes",
    "yes proceed",
    "proceed",
    "continue",
    "continue please",
    "go ahead",
    "do it",
    "ok",
    "okay",
    "approved",
}

SECRET_PATTERNS = (
    (
        re.compile(
            r"(?i)\b(?:[a-z0-9]+[_-])*(?:api[_ -]?key|access[_ -]?key|secret[_ -]?key|"
            r"token|secret|password|authorization)[\\\"'`]*\s*[:=]\s*[\\\"'`]*[^\s,;}]+"
        ),
        "[REDACTED_CREDENTIAL]",
    ),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"https?://[^\s)\]>]+"), "[REDACTED_URL]"),
    (re.compile(r"/Users/[^\s)\]>]+"), "[REDACTED_PATH]"),
    (re.compile(r"\b(?:ghp_|github_pat_|sk-|xox[baprs]-)[A-Za-z0-9_-]+\b"), "[REDACTED_TOKEN]"),
)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def redact_excerpt(text: str) -> str:
    redacted = normalize_text(text)
    for pattern, replacement in SECRET_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted[:EXCERPT_CHARS]


def message_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8", "ignore")).hexdigest()[:12]


def extract_text_blocks(content: Any, allowed_types: set[str]) -> str:
    if isinstance(content, str):
        return content[:MAX_CAPTURE_CHARS]
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    length = 0
    for item in content:
        if not isinstance(item, dict) or item.get("type") not in allowed_types:
            continue
        value = item.get("text")
        if not isinstance(value, str):
            continue
        remaining = MAX_CAPTURE_CHARS - length
        if remaining <= 0:
            break
        parts.append(value[:remaining])
        length += min(len(value), remaining)
    return "\n".join(parts)


def is_synthetic_user_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    return any(stripped.startswith(prefix) for prefix in SYNTHETIC_USER_PREFIXES)


def clean_user_intent_text(text: str) -> str:
    marker = "## My request for Codex:"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()


def is_forwarded_context(text: str) -> bool:
    stripped = text.lstrip()
    return any(stripped.startswith(prefix) for prefix in FORWARDED_CONTEXT_PREFIXES)


def is_short_approval(text: str) -> bool:
    normalized = re.sub(r"[^a-z ]+", "", normalize_text(text).lower()).strip()
    return normalized in SHORT_APPROVALS


def detect_signals(text: str, patterns: dict[str, re.Pattern[str]]) -> list[str]:
    signals = [name for name, pattern in patterns.items() if pattern.search(text)]
    if patterns is ASSISTANT_SIGNAL_PATTERNS and "needs_decision" in signals:
        if re.search(r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?decision needed(?:\*\*)?\s*:\s*no\b", text):
            signals.remove("needs_decision")
    if patterns is USER_SIGNAL_PATTERNS and is_short_approval(text):
        signals.append("short_approval")
    return sorted(signals)


def safe_json_load(line: bytes, session: dict[str, Any]) -> dict[str, Any] | None:
    if len(line) > MAX_JSON_RECORD_BYTES:
        session["oversized_records"] += 1
        return None
    try:
        value = json.loads(line)
    except Exception:
        session["malformed_records"] += 1
        return None
    return value if isinstance(value, dict) else None


def blank_session(agent: str, path: Path) -> dict[str, Any]:
    return {
        "agent": agent,
        "path": str(path),
        "session_id": path.stem,
        "title": "",
        "cwd": "",
        "branch": "",
        "model": "",
        "started_at": "",
        "ended_at": "",
        "bytes": path.stat().st_size,
        "records": 0,
        "record_counts": Counter(),
        "event_counts": Counter(),
        "tool_counts": Counter(),
        "tool_errors": 0,
        "hook_errors": 0,
        "hook_blocks": 0,
        "oversized_records": 0,
        "malformed_records": 0,
        "turns": [],
        "fallback_prompts": [],
    }


def new_turn(agent: str, timestamp: str, text: str) -> dict[str, Any]:
    intent_text = clean_user_intent_text(text)
    return {
        "agent": agent,
        "timestamp": timestamp,
        "user_text": intent_text[:MAX_CAPTURE_CHARS],
        "assistant_final_parts": [],
        "commentary_parts": [],
        "tool_calls": [],
        "first_action": "",
        "aborted": False,
        "compactions": 0,
    }


def finalize_turn(session: dict[str, Any], turn: dict[str, Any] | None) -> None:
    if not turn or not normalize_text(turn.get("user_text", "")):
        return
    user_text = turn.pop("user_text")
    final_text = "\n".join(turn.pop("assistant_final_parts"))[:MAX_CAPTURE_CHARS]
    commentary_text = "\n".join(turn.pop("commentary_parts"))[:MAX_CAPTURE_CHARS]
    forwarded_context = is_forwarded_context(user_text)
    user_signals = [] if forwarded_context else detect_signals(user_text, USER_SIGNAL_PATTERNS)
    assistant_signals = detect_signals(final_text, ASSISTANT_SIGNAL_PATTERNS)
    closeout_fields = {
        "status_field",
        "meaning_field",
        "checked_field",
        "recommended_next_field",
        "decision_needed_field",
    }
    risks: list[str] = []
    if not final_text and not turn.get("aborted"):
        risks.append("no_final_answer")
    if turn.get("first_action") == "tool":
        risks.append("tool_before_commentary")
    if (
        "autonomy_until_done" in user_signals
        and "needs_decision" in assistant_signals
        and "hard_gate_language" not in assistant_signals
    ):
        risks.append("autonomy_may_have_been_reasked")
    if "short_approval" in user_signals and "needs_decision" in assistant_signals:
        risks.append("short_approval_followed_by_decision")
    if "done_claim" in assistant_signals and "check_language" not in assistant_signals:
        risks.append("done_claim_without_check_language")
    if final_text and "next_action_language" not in assistant_signals and not closeout_fields.intersection(assistant_signals):
        risks.append("final_without_clear_next_action")
    if final_text and len(closeout_fields.intersection(assistant_signals)) == 5:
        assistant_signals.append("all_closeout_fields")

    session["turns"].append(
        {
            **turn,
            "user_hash": message_hash(user_text),
            "assistant_final_hash": message_hash(final_text) if final_text else "",
            "user_excerpt": redact_excerpt(user_text),
            "user_chars": len(user_text),
            "user_signals": user_signals,
            "assistant_final_excerpt": redact_excerpt(final_text),
            "assistant_final_chars": len(final_text),
            "assistant_signals": sorted(assistant_signals),
            "commentary_chars": len(commentary_text),
            "had_commentary": bool(normalize_text(commentary_text)),
            "forwarded_context": forwarded_context,
            "risks": sorted(risks),
        }
    )


def update_session_metadata(session: dict[str, Any], record: dict[str, Any]) -> None:
    for target, source in (("cwd", "cwd"), ("branch", "gitBranch"), ("started_at", "timestamp")):
        value = record.get(source)
        if isinstance(value, str) and value and not session[target]:
            session[target] = value
    timestamp = record.get("timestamp")
    if isinstance(timestamp, str) and timestamp:
        if not session["started_at"] or timestamp < session["started_at"]:
            session["started_at"] = timestamp
        if not session["ended_at"] or timestamp > session["ended_at"]:
            session["ended_at"] = timestamp


def parse_claude(path: Path) -> dict[str, Any]:
    session = blank_session("claude", path)
    current: dict[str, Any] | None = None

    with path.open("rb") as handle:
        for line in handle:
            session["records"] += 1
            prefix = line[:4096]
            relevant = any(
                marker in prefix
                for marker in (
                    b'"type":"user"',
                    b'"type":"assistant"',
                    b'"type":"system"',
                    b'"type":"last-prompt"',
                    b'"type":"ai-title"',
                )
            )
            if not relevant:
                continue
            record = safe_json_load(line, session)
            if not record:
                continue
            record_type = str(record.get("type", "missing"))
            session["record_counts"][record_type] += 1
            update_session_metadata(session, record)

            if record_type == "ai-title":
                title = record.get("aiTitle")
                if isinstance(title, str):
                    session["title"] = title[:300]
                continue
            if record_type == "last-prompt":
                prompt = record.get("lastPrompt")
                if isinstance(prompt, str) and not is_synthetic_user_text(prompt):
                    session["fallback_prompts"].append(prompt[:MAX_CAPTURE_CHARS])
                continue
            if record_type == "system":
                subtype = str(record.get("subtype", "system"))
                session["event_counts"][subtype] += 1
                errors = record.get("hookErrors")
                if isinstance(errors, list):
                    session["hook_errors"] += len(errors)
                if record.get("preventedContinuation") is True:
                    session["hook_blocks"] += 1
                continue

            message = record.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content")

            if record_type == "user":
                text = extract_text_blocks(content, {"text"})
                if not text and isinstance(content, str):
                    text = content
                origin = record.get("origin")
                prompt_source = record.get("promptSource")
                if (
                    prompt_source == "sdk"
                    and not (isinstance(origin, dict) and origin.get("kind") == "human")
                ):
                    continue
                if is_synthetic_user_text(text):
                    continue
                finalize_turn(session, current)
                current = new_turn("claude", str(record.get("timestamp", "")), text)
                continue

            if record_type != "assistant":
                continue
            model = message.get("model")
            if isinstance(model, str) and model:
                session["model"] = model
            if current is None:
                continue
            saw_text = False
            if isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("type")
                    if item_type == "tool_use":
                        name = str(item.get("name", "unknown"))
                        current["tool_calls"].append(name)
                        session["tool_counts"][name] += 1
                        if not current["first_action"]:
                            current["first_action"] = "tool"
                    elif item_type == "text":
                        text = item.get("text")
                        if not isinstance(text, str):
                            continue
                        saw_text = True
                        if not current["first_action"]:
                            current["first_action"] = "assistant_text"
                        if message.get("stop_reason") == "end_turn":
                            current["assistant_final_parts"].append(text[:MAX_CAPTURE_CHARS])
                        else:
                            current["commentary_parts"].append(text[:MAX_CAPTURE_CHARS])
            if message.get("stop_reason") == "end_turn" and saw_text:
                finalize_turn(session, current)
                current = None

    finalize_turn(session, current)
    if not session["turns"] and session["fallback_prompts"]:
        for prompt in session["fallback_prompts"]:
            fallback = new_turn("claude", session["started_at"], prompt)
            fallback["aborted"] = True
            finalize_turn(session, fallback)
    return session


def parse_codex(path: Path) -> dict[str, Any]:
    session = blank_session("codex", path)
    current: dict[str, Any] | None = None

    with path.open("rb") as handle:
        for line in handle:
            session["records"] += 1
            prefix = line[:4096]
            relevant = any(
                marker in prefix
                for marker in (
                    b'"type":"session_meta"',
                    b'"type":"turn_context"',
                    b'"type":"event_msg"',
                    b'"type":"response_item"',
                )
            )
            if not relevant:
                continue
            record = safe_json_load(line, session)
            if not record:
                continue
            record_type = str(record.get("type", "missing"))
            session["record_counts"][record_type] += 1
            update_session_metadata(session, record)
            payload = record.get("payload")
            if not isinstance(payload, dict):
                continue

            if record_type == "session_meta":
                value = payload.get("cwd")
                if isinstance(value, str):
                    session["cwd"] = value
                session_id = payload.get("id")
                if isinstance(session_id, str):
                    session["session_id"] = session_id
                git = payload.get("git")
                if isinstance(git, dict) and isinstance(git.get("branch"), str):
                    session["branch"] = git["branch"]
                continue

            if record_type == "turn_context":
                model = payload.get("model")
                if isinstance(model, str) and model:
                    session["model"] = model
                cwd = payload.get("cwd")
                if isinstance(cwd, str) and cwd:
                    session["cwd"] = cwd
                continue

            if record_type == "event_msg":
                event_type = str(payload.get("type", "missing"))
                session["event_counts"][event_type] += 1
                if event_type == "user_message":
                    text = payload.get("message")
                    if not isinstance(text, str):
                        text = ""
                    if is_synthetic_user_text(text):
                        continue
                    finalize_turn(session, current)
                    current = new_turn("codex", str(record.get("timestamp", "")), text)
                elif event_type == "context_compacted" and current is not None:
                    current["compactions"] += 1
                elif event_type == "turn_aborted" and current is not None:
                    current["aborted"] = True
                elif event_type == "task_complete":
                    finalize_turn(session, current)
                    current = None
                continue

            if record_type != "response_item":
                continue
            item_type = str(payload.get("type", "missing"))
            if item_type == "message" and payload.get("role") == "assistant":
                if current is None:
                    continue
                text = extract_text_blocks(payload.get("content"), {"output_text", "text"})
                if not text:
                    continue
                phase = str(payload.get("phase", ""))
                if not current["first_action"]:
                    current["first_action"] = "commentary" if phase == "commentary" else "assistant_text"
                if phase == "final_answer":
                    current["assistant_final_parts"].append(text[:MAX_CAPTURE_CHARS])
                else:
                    current["commentary_parts"].append(text[:MAX_CAPTURE_CHARS])
            elif item_type in {"function_call", "custom_tool_call"}:
                name = str(payload.get("name", "unknown"))
                session["tool_counts"][name] += 1
                if current is not None:
                    current["tool_calls"].append(name)
                    if not current["first_action"]:
                        current["first_action"] = "tool"
            elif item_type in {"function_call_output", "custom_tool_call_output"}:
                output = payload.get("output")
                if isinstance(output, str):
                    lower = output[:100_000].lower()
                    nonzero_exit = re.search(r'"exit_code"\s*:\s*(?!0\b)\d+', lower)
                    if nonzero_exit or '"is_error":true' in lower or '"success":false' in lower:
                        session["tool_errors"] += 1

    finalize_turn(session, current)
    return session


def is_project_relevant(session: dict[str, Any]) -> bool:
    cwd = session.get("cwd", "")
    path = session.get("path", "")
    return any(marker in cwd or marker.replace("/", "-") in path for marker in SIFUTUTOR_ROOT_MARKERS)


def unique_turn_records(sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate replayed history across Codex rollovers and copied transcripts."""
    selected: dict[tuple[str, str, str], dict[str, Any]] = {}
    for session in sessions:
        for turn in session["turns"]:
            if turn["assistant_final_hash"]:
                # Rollovers/forks can replay the same completed turn with a new
                # record timestamp or even a new rollout session ID.
                key = (session["agent"], turn["user_hash"], turn["assistant_final_hash"])
            else:
                timestamp_key = turn["timestamp"] or session["session_id"]
                key = (session["agent"], timestamp_key, turn["user_hash"])
            record = {
                "agent": session["agent"],
                "session_id": session["session_id"],
                "file_name": Path(session["path"]).name,
                "title": session["title"],
                "cwd": session["cwd"],
                "project_relevant": is_project_relevant(session),
                "turn": turn,
            }
            existing = selected.get(key)
            if existing is None:
                selected[key] = record
                continue
            existing_turn = existing["turn"]
            existing_score = (
                bool(existing_turn["assistant_final_chars"]),
                not existing_turn["aborted"],
                existing_turn["assistant_final_chars"] + existing_turn["commentary_chars"],
                len(existing_turn["tool_calls"]),
            )
            candidate_score = (
                bool(turn["assistant_final_chars"]),
                not turn["aborted"],
                turn["assistant_final_chars"] + turn["commentary_chars"],
                len(turn["tool_calls"]),
            )
            if candidate_score > existing_score:
                selected[key] = record
    return sorted(
        selected.values(),
        key=lambda record: (record["turn"]["timestamp"], record["agent"], record["session_id"]),
    )


def summarize_session(session: dict[str, Any]) -> dict[str, Any]:
    turns = session["turns"]
    user_signals = Counter(signal for turn in turns for signal in turn["user_signals"])
    assistant_signals = Counter(signal for turn in turns for signal in turn["assistant_signals"])
    risks = Counter(risk for turn in turns for risk in turn["risks"])
    return {
        "agent": session["agent"],
        "session_id": session["session_id"],
        "file_name": Path(session["path"]).name,
        "title": session["title"],
        "cwd": session["cwd"],
        "branch": session["branch"],
        "model": session["model"],
        "started_at": session["started_at"],
        "ended_at": session["ended_at"],
        "bytes": session["bytes"],
        "records": session["records"],
        "project_relevant": is_project_relevant(session),
        "turns": len(turns),
        "final_answers": sum(bool(turn["assistant_final_chars"]) for turn in turns),
        "aborted_turns": sum(bool(turn["aborted"]) for turn in turns),
        "compactions": sum(int(turn["compactions"]) for turn in turns),
        "tool_calls": sum(session["tool_counts"].values()),
        "tool_errors": session["tool_errors"],
        "hook_errors": session["hook_errors"],
        "hook_blocks": session["hook_blocks"],
        "oversized_records": session["oversized_records"],
        "malformed_records": session["malformed_records"],
        "record_counts": dict(session["record_counts"].most_common()),
        "event_counts": dict(session["event_counts"].most_common()),
        "tool_counts": dict(session["tool_counts"].most_common()),
        "user_signals": dict(user_signals.most_common()),
        "assistant_signals": dict(assistant_signals.most_common()),
        "risks": dict(risks.most_common()),
    }


def rank_manual_review_candidates(
    records: list[dict[str, Any]], limit: int = 25
) -> list[dict[str, Any]]:
    """Rank deduplicated sessions for manual review without copying chat text."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in records:
        if not record["project_relevant"]:
            continue
        grouped.setdefault((record["agent"], record["session_id"]), []).append(record)

    candidates: list[dict[str, Any]] = []
    for (agent, session_id), session_records in grouped.items():
        user_signals = Counter(
            signal
            for record in session_records
            for signal in record["turn"]["user_signals"]
        )
        risks = Counter(
            risk for record in session_records for risk in record["turn"]["risks"]
        )
        score = sum(
            user_signals[signal] * weight
            for signal, weight in REVIEW_SIGNAL_WEIGHTS.items()
        ) + sum(risks[risk] * weight for risk, weight in REVIEW_RISK_WEIGHTS.items())
        if score == 0:
            continue
        first = session_records[0]
        candidates.append(
            {
                "agent": agent,
                "session_id": session_id,
                "friction_score": score,
                "turns": len(session_records),
                "started_at": min(record["turn"]["timestamp"] for record in session_records),
                "ended_at": max(record["turn"]["timestamp"] for record in session_records),
                "file_name": first["file_name"],
                "title": first["title"],
                "cwd": first["cwd"],
                "user_signals": dict(user_signals.most_common()),
                "risks": dict(risks.most_common()),
            }
        )
    return sorted(
        candidates,
        key=lambda candidate: (
            -candidate["friction_score"],
            -candidate["turns"],
            candidate["agent"],
            candidate["session_id"],
        ),
    )[:limit]


def aggregate(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    by_agent: dict[str, Any] = {}
    all_unique_turns = unique_turn_records(sessions)
    for agent in ("claude", "codex"):
        selected = [session for session in sessions if session["agent"] == agent]
        relevant = [session for session in selected if is_project_relevant(session)]
        relevant_turns = [
            record["turn"]
            for record in all_unique_turns
            if record["agent"] == agent and record["project_relevant"]
        ]
        top_tools = Counter(tool for turn in relevant_turns for tool in turn["tool_calls"])
        by_agent[agent] = {
            "files": len(selected),
            "distinct_session_ids": len({session["session_id"] for session in selected}),
            "project_relevant_files": len(relevant),
            "bytes": sum(session["bytes"] for session in selected),
            "project_relevant_bytes": sum(session["bytes"] for session in relevant),
            "records": sum(session["records"] for session in selected),
            "raw_turns": sum(len(session["turns"]) for session in relevant),
            "turns": len(relevant_turns),
            "final_answers": sum(bool(turn["assistant_final_chars"]) for turn in relevant_turns),
            "aborted_turns": sum(bool(turn["aborted"]) for turn in relevant_turns),
            "compactions": sum(int(turn["compactions"]) for turn in relevant_turns),
            "tool_calls": sum(len(turn["tool_calls"]) for turn in relevant_turns),
            "tool_error_records_raw": sum(session["tool_errors"] for session in relevant),
            "hook_errors": sum(session["hook_errors"] for session in relevant),
            "hook_blocks": sum(session["hook_blocks"] for session in relevant),
            "oversized_records": sum(session["oversized_records"] for session in selected),
            "malformed_records": sum(session["malformed_records"] for session in selected),
            "user_signals": dict(Counter(signal for turn in relevant_turns for signal in turn["user_signals"]).most_common()),
            "assistant_signals": dict(Counter(signal for turn in relevant_turns for signal in turn["assistant_signals"]).most_common()),
            "risks": dict(Counter(risk for turn in relevant_turns for risk in turn["risks"]).most_common()),
            "top_tools": dict(top_tools.most_common(25)),
        }
    period_rows: list[dict[str, Any]] = []
    for period_name, period_test in (
        ("through_2026-06", lambda timestamp: timestamp[:7] <= "2026-06"),
        ("2026-07-01_to_12", lambda timestamp: "2026-07-01" <= timestamp[:10] <= "2026-07-12"),
        ("2026-07-13_plus", lambda timestamp: timestamp[:10] >= "2026-07-13"),
    ):
        for agent in ("claude", "codex"):
            turns = [
                record["turn"]
                for record in all_unique_turns
                if record["agent"] == agent
                and record["project_relevant"]
                and period_test(record["turn"]["timestamp"])
            ]
            period_rows.append(
                {
                    "period": period_name,
                    "agent": agent,
                    "turns": len(turns),
                    "final_answers": sum(bool(turn["assistant_final_chars"]) for turn in turns),
                    "aborted_turns": sum(bool(turn["aborted"]) for turn in turns),
                    "compactions": sum(int(turn["compactions"]) for turn in turns),
                    "tool_calls": sum(len(turn["tool_calls"]) for turn in turns),
                    "user_signals": dict(
                        Counter(signal for turn in turns for signal in turn["user_signals"]).most_common()
                    ),
                    "assistant_signals": dict(
                        Counter(signal for turn in turns for signal in turn["assistant_signals"]).most_common()
                    ),
                    "risks": dict(Counter(risk for turn in turns for risk in turn["risks"]).most_common()),
                }
            )

    return {
        "scope": {
            "all_files": len(sessions),
            "project_relevant_files": sum(is_project_relevant(session) for session in sessions),
            "all_bytes": sum(session["bytes"] for session in sessions),
            "project_relevant_bytes": sum(session["bytes"] for session in sessions if is_project_relevant(session)),
        },
        "by_agent": by_agent,
        "by_period": period_rows,
    }


def run_self_test() -> int:
    """Prove human filtering, rollover deduplication, and redaction."""
    with tempfile.TemporaryDirectory(prefix="agent-os-transcript-test-") as temp_dir:
        root = Path(temp_dir)
        claude_path = root / "claude.jsonl"
        codex_one = root / "codex-one.jsonl"
        codex_two = root / "codex-two.jsonl"

        claude_records = [
            {
                "type": "user",
                "timestamp": "2026-07-18T00:00:00Z",
                "promptSource": "sdk",
                "message": {"content": "Sifututor workflow dispatcher: injected"},
            },
            {
                "type": "user",
                "timestamp": "2026-07-18T00:00:01Z",
                "promptSource": "sdk",
                "origin": {"kind": "human"},
                "message": {"content": "Please explain what is next"},
            },
            {
                "type": "assistant",
                "timestamp": "2026-07-18T00:00:02Z",
                "message": {
                    "content": [{"type": "text", "text": "Checked. Recommended next action: continue."}],
                    "stop_reason": "end_turn",
                    "model": "fixture",
                },
            },
        ]
        claude_path.write_text(
            "".join(json.dumps(record, separators=(",", ":")) + "\n" for record in claude_records),
            encoding="utf-8",
        )

        codex_records = [
            {
                "type": "session_meta",
                "timestamp": "2026-07-18T00:00:00Z",
                "payload": {"id": "fixture", "cwd": "/Projects/Sifututor"},
            },
            {
                "type": "event_msg",
                "timestamp": "2026-07-18T00:00:01Z",
                "payload": {"type": "user_message", "message": "Please explain what is next"},
            },
            {
                "type": "response_item",
                "timestamp": "2026-07-18T00:00:02Z",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "phase": "final_answer",
                    "content": [{"type": "output_text", "text": "Checked. Recommended next action: continue."}],
                },
            },
        ]
        encoded = "".join(json.dumps(record, separators=(",", ":")) + "\n" for record in codex_records)
        codex_one.write_text(encoded, encoding="utf-8")
        codex_two.write_text(encoded, encoding="utf-8")

        claude = parse_claude(claude_path)
        codex_sessions = [parse_codex(codex_one), parse_codex(codex_two)]
        failures: list[str] = []
        if len(claude["turns"]) != 1:
            failures.append("Claude injected/human filtering")
        if len(unique_turn_records(codex_sessions)) != 1:
            failures.append("Codex rollover deduplication")
        ranked = rank_manual_review_candidates(unique_turn_records([claude, *codex_sessions]))
        if sum(
            candidate["agent"] == "codex" and candidate["session_id"] == "fixture"
            for candidate in ranked
        ) != 1:
            failures.append("manual review ranking rollover deduplication")

        sensitive = "password=fixture-secret-123 user@example.test https://example.test/private"
        redacted = redact_excerpt(sensitive)
        for marker in ("fixture-secret-123", "user@example.test", "https://example.test/private"):
            if marker in redacted:
                failures.append(f"redaction leaked {marker}")

        aggregate_only = {"aggregate": aggregate([claude, *codex_sessions])}
        serialized = json.dumps(aggregate_only)
        if "Please explain what is next" in serialized or "fixture-secret-123" in serialized:
            failures.append("aggregate report contains conversation text")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("agent-os-transcript-retrospective self-test: 4/4 passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claude-root",
        type=Path,
        default=Path.home() / ".claude" / "projects",
    )
    parser.add_argument(
        "--codex-root",
        type=Path,
        default=Path.home() / ".codex" / "sessions",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--include-redacted-details",
        action="store_true",
        help="include local-only session metadata and short redacted excerpts",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.include_redacted_details:
        if not args.output:
            parser.error("--include-redacted-details requires --output")
        try:
            args.output.resolve().relative_to(AGENT_OS_ROOT.resolve())
        except ValueError:
            pass
        else:
            parser.error("redacted detail reports must be written outside the Agent OS repository")

    claude_files = sorted(args.claude_root.glob("*/*.jsonl"))
    codex_files = sorted(args.codex_root.rglob("*.jsonl"))
    sessions: list[dict[str, Any]] = []
    total_files = len(claude_files) + len(codex_files)

    for index, path in enumerate(claude_files, 1):
        sessions.append(parse_claude(path))
        if index % 10 == 0:
            print(f"parsed {index}/{total_files}: Claude", file=sys.stderr, flush=True)
    offset = len(claude_files)
    for index, path in enumerate(codex_files, 1):
        sessions.append(parse_codex(path))
        completed = offset + index
        if index % 10 == 0 or completed == total_files:
            print(f"parsed {completed}/{total_files}: Codex", file=sys.stderr, flush=True)

    unique_turns = unique_turn_records(sessions)
    output: dict[str, Any] = {"aggregate": aggregate(sessions)}
    if args.include_redacted_details:
        output["privacy_notice"] = (
            "Local diagnostic data only: excerpts are redacted but may still contain context. "
            "Do not commit this report."
        )
        output["sessions"] = [summarize_session(session) for session in sessions]
        output["manual_review_ranking"] = {
            "method": {
                "unit": "deduplicated agent/session",
                "user_signal_weights": REVIEW_SIGNAL_WEIGHTS,
                "risk_weights": REVIEW_RISK_WEIGHTS,
                "note": (
                    "Ranking selects manual review candidates; a high score is not proof "
                    "that the agent failed. Read the session evidence in context."
                ),
            },
            "candidates": rank_manual_review_candidates(unique_turns),
        }
        output["high_signal_turns"] = [
            {
                "agent": record["agent"],
                "session_id": record["session_id"],
                "file_name": record["file_name"],
                "title": record["title"],
                "cwd": record["cwd"],
                "project_relevant": record["project_relevant"],
                **record["turn"],
            }
            for record in unique_turns
            if record["project_relevant"]
            and (record["turn"]["user_signals"] or record["turn"]["risks"])
        ]
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output["aggregate"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
