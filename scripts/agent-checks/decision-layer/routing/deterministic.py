#!/usr/bin/env python3
"""Bundle 2's own deterministic pre-policy layer for routing decisions.

Built the same way as Bundle 1's `pre_policy.py` (pure lookup / pattern
matching, always overrides, zero risk, zero latency, never touches a
provider) but scoped to concerns Bundle 1's generic module does not know
about: which project a request names, and whether the request's subject
matter lands in a critical lane. This module is a new, separate file
rather than an edit to Bundle 1's already-merged `pre_policy.py`, so
Bundle 2 stays an independently reviewable addition.

`shadow_router.py` runs every rule in this module before it constructs a
provider request. A critical-lane hit is a hard stop: the router answers
deterministically and never calls Bundle 1's `engine.decide()` at all.
"High sensitivity" is not permission to transmit; critical lanes are never
delegated to any provider, fake or real.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

import catalog

# The eight critical lanes. Each entry is (lane code, pattern). The first
# lane whose pattern matches wins, in this order, so a request touching
# two lanes reports the earlier one. Reason codes are short and stable
# (`critical_lane:<lane>`) so they can be asserted on and logged without
# ever carrying request text.
#
# These lanes cite AGENTS.md's Universal Safety Rule ("payments,
# commission, auth, migrations, or mobile API contracts ... halt for human
# review") plus the review finding on PR #172: destructive actions, secrets
# or credentials, private production data, and explicit approval decisions
# must also never be delegated to a provider.
#
# Deliberate scoping notes:
# - "session" is only an auth signal in an auth context ("login session",
#   "session expiry", "session token"). A bare "session" would make every
#   save-session request critical.
# - "role" is only an auth signal as "user roles", "role-based", "roles and
#   permissions"; a bare "role" reads as ordinary English.
# - "deploy to production" is the approval phrase; "deploy to staging" is
#   an ordinary deployment route with its own (high) default risk.
CRITICAL_LANES: tuple[tuple[str, str], ...] = (
    (
        "payments",
        r"\bpayments?\b|\bcommissions?\b|\binvoices?\b|\binvoicing\b|\brefunds?\b|"
        r"\brefunded\b|\bpayouts?\b|\bbilling\b",
    ),
    (
        "auth",
        r"\bauth\b|\bauthentication\b|\bauthori[sz]ation\b|\blogin\b|\blog[- ]in\b|"
        r"\blogout\b|\bsign[- ]in\b|\bpasswords?\b|"
        r"\b(?:login|auth\w*|user|tutor|parent|staff|admin) sessions?\b|"
        r"\bsessions? (?:expir\w*|tokens?|cookies?|timeouts?|hijack\w*|management|handling)\b|"
        r"\b(?:user|admin|staff|tutor|parent|owner) roles?\b|\brole[- ]based\b|"
        r"\broles?\s+(?:and|&|or)\s+permissions?\b|\bpermissions?\b|\btokens?\b",
    ),
    (
        "production_migration",
        r"\bmigrations?\b|\bmigrate\b|\bschema changes?\b|\bchange the schema\b|"
        r"\balter table\b|\badd column\b|\bdrop column\b|\brename column\b|"
        r"\b(?:db|database|production) schema\b",
    ),
    (
        "destructive_action",
        r"\bdeletes?\b|\bdeleting\b|\bdeleted\b|\bdrop\b|\btruncate\b|\brm -rf\b|\brm -fr\b|"
        r"\bforce[- ]push\w*\b|\bpush --force\b|\b--force-with-lease\b|\breset --hard\b|"
        r"\bpurge\b|\bwipe\b",
    ),
    (
        "mobile_api_contract",
        r"\bmobile api\b|\bapi contract\b|\bapp contract\b|\bbreaking api change\b|"
        r"\bendpoints?\b|\bresponse shape\b|\bapi version(?:ing)?\b|\bapi v\d+\b",
    ),
    (
        "secrets_credentials",
        r"\bapi[ _-]?keys?\b|\bsecrets?\b|\bcredentials?\b|\.env\b|\benv file\b|"
        r"\bprivate keys?\b",
    ),
    (
        "private_production_data",
        r"\b(?:customer|parent|tutor|student|user) (?:records?|data)\b|\bic numbers?\b|"
        r"\bic\b|\bnric\b|\bphone\b|\bpii\b|\b(?:prod|production|db|database) dumps?\b|"
        r"\bproduction data\b|\bpersonal data\b",
    ),
    (
        "approval_decision",
        r"\bapprove\b|\bapproval\b|\bapproved\b|\bauthori[sz]e\b|\bsign[- ]off\b|"
        r"\bgrant permission\b|\bmerge\b|\bmerged\b|\bmerging\b|"
        r"\bdeploy(?:ing|ment|s)?\s+(?:\w+\s+){0,2}to\s+prod(?:uction)?\b",
    ),
)

CRITICAL_LANE_CODES: tuple[str, ...] = tuple(lane for lane, _ in CRITICAL_LANES)


def critical_lane_reason(lane: str) -> str:
    """The short reason code for one lane, shared by keyword detection and
    the secret-filter path in `shadow_router.py`."""
    return f"critical_lane:{lane}"


@dataclass(frozen=True)
class ProjectDecision:
    project: str | None
    source: str  # "declared_param" | "declared_in_text" | "none"


@dataclass(frozen=True)
class RiskOverride:
    risk_level: str
    reason: str
    lane: str


# Phrases matching the CLAUDE.md/AGENTS.md declared-intent convention:
# "This is sifu-tutor work - ...", "sifu-tutor work - ...",
# "ripple-suite bug - ...", "Working on ripple-suite - ...". Tried in
# order; each candidate name is only accepted once it canonicalizes to a
# KNOWN_PROJECTS entry (see resolve_project), so an unrelated "will work -"
# style false match is silently skipped rather than accepted.
_DECLARED_INTENT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bthis is\s+(?P<name>[a-z][a-z0-9 _-]{1,40}?)\s+(?:work|bug)\s*[-:]", re.IGNORECASE),
    # Terminator requires whitespace before a bare "-" (not just "\s*[-:]")
    # so a hyphen that is *part of* a compound project name like
    # "ripple-suite" cannot itself terminate the lazy name match early.
    re.compile(r"\bworking on\s+(?P<name>[a-z][a-z0-9 _-]{1,40}?)(?:\s+-|\s*:)", re.IGNORECASE),
    re.compile(r"(?<![a-z0-9_-])(?P<name>[a-z][a-z0-9_-]{1,40}?)\s+(?:work|bug)\s*[-:]", re.IGNORECASE),
)


def _canonicalize_project_name(raw_name: str) -> str | None:
    name = raw_name.strip().lower()
    if name in catalog.PROJECT_ALIASES:
        return catalog.PROJECT_ALIASES[name]
    for project in catalog.KNOWN_PROJECTS:
        if name == project.lower() or name == project.lower().replace("_", " ").replace("-", " "):
            return project
    return None


def resolve_project(text: str, declared_project: str | None) -> ProjectDecision:
    """Resolve which project a request belongs to, deterministically.

    Priority (build spec: "if a request explicitly names a project, that
    overrides any inferred project"):
      1. `declared_project` passed explicitly by the caller.
      2. An explicit declared-intent phrase inside the text itself
         ("This is X work - ...", "Working on X - ...").
      3. None -- this module does not do fuzzy/weak inference; a merely
         mentioned project name that is not declared this way is left for
         the classifier, not decided here.
    """
    if declared_project:
        canonical = _canonicalize_project_name(declared_project) or declared_project
        return ProjectDecision(project=canonical, source="declared_param")

    for pattern in _DECLARED_INTENT_PATTERNS:
        for match in pattern.finditer(text or ""):
            canonical = _canonicalize_project_name(match.group("name"))
            if canonical is not None:
                return ProjectDecision(project=canonical, source="declared_in_text")

    return ProjectDecision(project=None, source="none")


def detect_critical_risk(text: str) -> RiskOverride | None:
    """Force a critical risk level when the text lands in any of the eight
    critical lanes. Returns the first lane that matches, in CRITICAL_LANES
    order, with a short `critical_lane:<lane>` reason code.

    This intentionally runs on the *raw* text, including any quoted or
    pasted spans -- a safety rule must stay conservative even when the
    trigger word appears inside a pasted log, so this is not routed
    through `strip_quoted_and_pasted_spans` first.
    """
    haystack = text or ""
    for lane, pattern in CRITICAL_LANES:
        if re.search(pattern, haystack, re.IGNORECASE):
            return RiskOverride(risk_level="critical", reason=critical_lane_reason(lane), lane=lane)
    return None


# A quoted span: text between a matching pair of straight or curly double
# quotes. Deliberately simple (no nested-quote handling) -- good enough to
# keep a pasted command/log out of the classifier's live-instruction
# scoring, which is all this is used for.
_QUOTED_SPAN_PATTERN = re.compile(r"[\"“][^\"“”]*[\"”]")

_PASTED_REPORT_FRAMING_PATTERN = re.compile(
    r"\b(pasted|a teammate (sent|pasted)|here is the log|here's the log|log output|"
    r"stack trace|error report)\b",
    re.IGNORECASE,
)


def strip_quoted_and_pasted_spans(text: str) -> str:
    """Remove quoted spans so a quoted "commit"/"push" inside pasted
    content is not read as a live instruction by the classifier.

    Per AGENTS.md's GitHub Issue Automation section: "A quoted phrase such
    as 'commit' or 'push' inside a pasted report, log, or someone else's
    message is not, by itself, an instruction to create, change, or act on
    an issue; only a direct instruction from Hafiz in the current session
    does that." This function is the routing-classifier-facing enforcement
    of that same rule.
    """
    return _QUOTED_SPAN_PATTERN.sub(" ", text or "")


def is_pasted_report(text: str) -> bool:
    """True when the text reads as a pasted report/log rather than a
    direct instruction: it contains a quoted span AND report-ish framing
    language (e.g. "here is the log", "a teammate pasted")."""
    haystack = text or ""
    return bool(_QUOTED_SPAN_PATTERN.search(haystack)) and bool(
        _PASTED_REPORT_FRAMING_PATTERN.search(haystack)
    )


_TASK_TYPE_OVERRIDE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("hotfix", r"\burgent\b|\bhotfix\b|\bproduction is down\b|\bsite is down\b"),
    ("docs", r"\bdocumentation\b|\breadme\b|\bchangelog\b"),
    ("refactor", r"\brefactor\b|\bclean ?up\b|\bdead code\b"),
)


def detect_task_type_override(text: str) -> str | None:
    """A deterministic task_type override for a few unambiguous signal
    words. Returns None (defer to the catalog's default-per-route table)
    when nothing matches."""
    haystack = text or ""
    for task_type, pattern in _TASK_TYPE_OVERRIDE_PATTERNS:
        if re.search(pattern, haystack, re.IGNORECASE):
            return task_type
    return None
