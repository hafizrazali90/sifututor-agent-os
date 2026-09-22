#!/usr/bin/env python3
"""Deterministic keyword/pattern scorer that ranks the 11 workflow routes
for a piece of free text.

This is *not* the "classifier answer" itself in the decision-layer sense.
`shadow_router.py` hands the ranked list this module produces to Bundle 1's
`engine.decide()` as the request's `options`, in ranked order, and lets
`engine.decide()` dispatch to FakeProvider as normal -- FakeProvider's "ok"
scenario always answers `options[0]`, so this module's top pick is what
comes back as the shadow decision. A future live classifier (Jev) would
plug into that same `engine.decide()` call and this module's calling
contract would not need to change; only which provider a caller configures
would.

Scoring is a simple keyword-hit count per route, computed on the caller's
already quote-stripped text (see `deterministic.strip_quoted_and_pasted_
spans`) so pasted/quoted content cannot swing the score. Ties fall back to
a fixed priority order, and an all-zero score falls back to "question" --
the least presumptuous route when nothing else signals anything.
"""

from __future__ import annotations

import re

import catalog
import deterministic

# Keyword/phrase signals per workflow route. Order inside a tuple does not
# matter; each match adds one point to that route's score.
_ROUTE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "continuation": (
        r"\bgo next\b",
        r"\bwhat'?s next\b",
        r"\bkeep going\b",
        r"\bcontinue where\b",
        r"\bproceed to the next\b",
        r"\bnext unblocked\b",
    ),
    "save_session": (
        r"\bsave session\b",
        r"\bsave-session\b",
        r"\bwrap up\b",
        r"\bend session\b",
        r"\bend the session\b",
        r"\bpersist what we learned\b",
    ),
    "handoff": (
        r"\bhandoff\b",
        r"\bhand off\b",
        r"\bhand this off\b",
        r"\bcontinuation pack\b",
        r"\bprepare a handoff\b",
        r"\banother agent\b",
    ),
    "deployment": (
        r"\bdeploy\b",
        r"\bdeployment\b",
        r"\brelease to production\b",
        r"\bpush to staging\b",
        r"\bgo live\b",
        r"\bship to prod\b",
    ),
    "qa": (
        r"\brun qa\b",
        r"\brun the tests\b",
        r"\bsmoke test\b",
        r"\bregression test\b",
        r"\bare tests passing\b",
        r"\bcheck tests\b",
    ),
    "review": (
        r"\breview this\b",
        r"\bcode review\b",
        r"\bplease review\b",
        r"\breview the pr\b",
        r"\bsecond opinion on\b",
        r"\breview my\b",
    ),
    "diagnosis": (
        r"\bwhy is\b",
        r"\bwhy does\b",
        r"\bbroken\b",
        r"\bbug\b",
        r"\bnot working\b",
        r"\bdoesn'?t work\b",
        r"\bcrash\w*\b",
        r"\berror\b",
        r"\bdiagnose\b",
        r"\bfailing\b",
    ),
    "implementation": (
        r"\bbuild\b",
        r"\bimplement\b",
        r"\badd a feature\b",
        r"\bcreate a\b",
        r"\badd support for\b",
        r"\bwrite the code\b",
        r"\bnew endpoint\b",
    ),
    "research": (
        r"\bresearch\b",
        r"\bexplore\b",
        r"\bevaluate\b",
        r"\binvestigate\b",
        r"\bwhat are our options\b",
        r"\bcompare\b",
        r"\bdeep analysis\b",
        r"\bshould we\b",
    ),
    "new_side_task": (
        r"\bseparately,",
        r"\bone more thing\b",
        r"\bunrelated\b",
        r"\bwhile you'?re at it\b",
        r"\balso, can you\b",
    ),
    "question": (r"\?",),
}

# When every route scores zero, or scores tie, this order breaks the tie.
# Deliberately puts the most consequential/specific routes ahead of the
# safest default ("question" last, "new_side_task" also low priority since
# it requires an active task to even be considered -- see below).
_TIE_BREAK_ORDER: tuple[str, ...] = (
    "deployment",
    "handoff",
    "save_session",
    "continuation",
    "qa",
    "review",
    "diagnosis",
    "implementation",
    "research",
    "new_side_task",
    "question",
)


def _score_text(text: str) -> dict[str, int]:
    scores = {route: 0 for route in catalog.WORKFLOW_ROUTES}
    for route, patterns in _ROUTE_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores[route] += 1
    return scores


def rank_workflow_routes(text: str, *, has_active_task: bool = False) -> list[str]:
    """Return every workflow route, ranked highest-signal first.

    `has_active_task` gates "new_side_task": the same "separately" /
    "while you're at it" phrasing means something different depending on
    whether there is already an active task in progress this session (a
    genuine mid-session interruption) versus it just being how someone
    phrased their very first message (not a side task of nothing).
    """
    cleaned = deterministic.strip_quoted_and_pasted_spans(text or "")
    scores = _score_text(cleaned)

    if not has_active_task:
        scores["new_side_task"] = 0

    ranked = sorted(
        catalog.WORKFLOW_ROUTES,
        key=lambda route: (-scores[route], _TIE_BREAK_ORDER.index(route)),
    )

    if scores[ranked[0]] == 0:
        # No signal at all: the safest, least presumptuous default.
        ranked = ["question"] + [route for route in ranked if route != "question"]

    return ranked
