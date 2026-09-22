#!/usr/bin/env python3
"""Read-only aggregation over a batch of classifier.ClassificationResult.

`aggregate()` and `render_summary()` are pure report functions: they take
a batch of already-classified entries and produce counts/text. Neither
performs, requests, or is wired to any deletion, park, or close action --
that authority stays exclusively with `worktree-lifecycle.py`'s own,
unmodified mechanisms, called only by a human or by that tool directly,
never by this module.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

_MAX_EXAMPLES_PER_BUCKET = 3


@dataclass(frozen=True)
class BucketSummary:
    bucket: str
    count: int
    examples: tuple[str, ...]


def aggregate(results) -> list[BucketSummary]:
    """Group classified entries by bucket. Read-only; no side effects."""
    grouped: dict[str, list] = defaultdict(list)
    for result in results:
        grouped[result.classification].append(result)

    ordered_buckets = sorted(grouped, key=lambda bucket: (-len(grouped[bucket]), bucket))
    return [
        BucketSummary(
            bucket=bucket,
            count=len(grouped[bucket]),
            examples=tuple(r.worktree for r in grouped[bucket][:_MAX_EXAMPLES_PER_BUCKET]),
        )
        for bucket in ordered_buckets
    ]


def render_summary(results) -> str:
    """A short, human-readable report grouped by classification bucket,
    with counts and named examples. Read-only: this function performs no
    deletion, park, or close action of its own."""
    results = list(results)
    if not results:
        return "worktree triage: no entries classified."

    lines = [f"worktree triage: {len(results)} entries classified"]
    for summary in aggregate(results):
        example_text = ", ".join(summary.examples)
        suffix = f" (e.g. {example_text})" if example_text else ""
        lines.append(f"  - {summary.bucket}: {summary.count}{suffix}")
    return "\n".join(lines)
