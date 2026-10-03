#!/usr/bin/env python3
"""PreToolUse guard: deny over-long AskUserQuestion boxes.

Limits mirror "Decision Questions" in docs/agent-playbooks/agent-os-communication.md
and DECISION_BOX_* in agent-os-response-shape-runner.py.
"""

from __future__ import annotations

import json
import re
import sys

MAX_QUESTION_WORDS = 35
MAX_QUESTION_SENTENCES = 2
MIN_OPTIONS = 2
MAX_OPTIONS = 4
MAX_LABEL_WORDS = 5
MAX_DESCRIPTION_WORDS = 14

REASON = (
    "This question box is too long to read. Put the explanation in chat as short bullets, "
    "then ask again with a question of at most 35 words and 2 sentences, 2 to 4 options, "
    "labels up to 5 words and descriptions up to 14 words. If it cannot be that brief, "
    "ask in chat with numbered options instead. Problems: {problems}."
)


def violations(tool_input: object) -> list[str]:
    found: set[str] = set()
    questions = tool_input.get("questions") if isinstance(tool_input, dict) else None
    if not isinstance(questions, list):
        return []
    for item in questions:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question") or "")
        if len(question.split()) > MAX_QUESTION_WORDS:
            found.add("question_too_long")
        if len(re.findall(r"[.?!](?:\s|$)", question.strip())) > MAX_QUESTION_SENTENCES:
            found.add("too_many_sentences")
        options = item.get("options")
        if not isinstance(options, list):
            continue
        if not MIN_OPTIONS <= len(options) <= MAX_OPTIONS:
            found.add("option_count")
        for option in options:
            if not isinstance(option, dict):
                continue
            if len(str(option.get("label") or "").split()) > MAX_LABEL_WORDS:
                found.add("label_too_long")
            if len(str(option.get("description") or "").split()) > MAX_DESCRIPTION_WORDS:
                found.add("description_too_long")
    return sorted(found)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0
    if (payload.get("tool_name") or payload.get("toolName")) != "AskUserQuestion":
        return 0
    problems = violations(payload.get("tool_input") or payload.get("toolInput"))
    if problems:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": REASON.format(problems=", ".join(problems)),
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
