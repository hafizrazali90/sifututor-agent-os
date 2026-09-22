#!/usr/bin/env python3
"""Signal 2 of 8: whether changes look unrelated to the stated task
(scope-creep signal).

Deterministic only. Two sources of evidence, in priority order:

  1. An explicit `related_to_task: False` on a changed-file entry -- the
     caller (a diff-aware hook, a human, or a future provider upstream of
     this module) already knows the file is unrelated; this module trusts
     that explicit fact and flags it with high confidence.
  2. When no explicit flag is given, a plain keyword-overlap heuristic
     between the task description and the file path -- weak evidence, so
     it is flagged at lower confidence (`possibly_unrelated`, not
     `unrelated`) and never raises priority past "medium" on its own.

Test-kind files (`kind == "test"`) are never flagged by the heuristic path,
since adding or extending tests for the stated task is expected even when
the test file's own name does not share task-description words.
"""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from contract import build_signal  # noqa: E402
import text_tokens  # noqa: E402

SIGNAL_NAME = "scope_creep"

_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with",
    "is", "are", "this", "that", "it", "so", "be", "by", "at", "as",
}


def _significant_words(text: str) -> set[str]:
    words = {word for word in text_tokens.tokens(text) if len(word) > 3}
    return words - _STOPWORDS


def classify(payload: dict) -> dict:
    """Return the scope_creep signal record for one change payload."""
    changed_files = payload.get("changed_files") or []
    task_words = _significant_words(str(payload.get("task_description", "")))

    explicit_unrelated: list[str] = []
    possibly_unrelated: list[str] = []

    for entry in changed_files:
        path = str(entry.get("path", ""))
        related = entry.get("related_to_task")

        if related is False:
            explicit_unrelated.append(path)
            continue
        if related is True:
            continue

        # No explicit signal: fall back to the weak keyword-overlap
        # heuristic, skipping test files (see module docstring).
        if entry.get("kind") == "test":
            continue
        if not task_words:
            continue
        path_words = _significant_words(path)
        if not (path_words & task_words):
            possibly_unrelated.append(path)

    if explicit_unrelated:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="high",
            flags=[f"unrelated_file:{path}" for path in explicit_unrelated],
            reason="one or more changed files are marked unrelated to the stated task",
            decision_source="deterministic",
        )

    if possibly_unrelated:
        return build_signal(
            signal=SIGNAL_NAME,
            priority="medium",
            flags=[f"possibly_unrelated_file:{path}" for path in possibly_unrelated],
            reason="one or more changed files share no keywords with the stated task description (weak signal, worth a human glance)",
            decision_source="deterministic",
        )

    return build_signal(
        signal=SIGNAL_NAME,
        priority="low",
        flags=[],
        reason="every changed file looks related to the stated task",
        decision_source="deterministic",
    )
