#!/usr/bin/env python3
"""Static reference data for the routing/context shadow-decision module.

Pure data only -- project names/aliases, the workflow-route vocabulary, and
the deterministic playbook/document lookup tables. Nothing here calls a
provider or does pattern matching; see `deterministic.py` and
`classifier.py` for that.

Every value here is a citation of an existing documented fact rather than
an invented vocabulary (per this repo's "No Invented Terms" convention):

- The project list mirrors this repo's own `AGENTS.md` "Active projects"
  table.
- The playbook paths mirror `AGENTS.md`'s "Shared Workflow Playbooks"
  table -- this module never names a playbook that table does not list.
- The Koda project tags mirror the parent Sifututor workspace's
  `CLAUDE.md` "Project tagging convention" table.
"""

from __future__ import annotations

# AGENTS.md "Active projects" table.
KNOWN_PROJECTS: tuple[str, ...] = (
    "kelas",
    "sifu-tutor",
    "ripple-suite",
    "sifututor_tutor",
    "sifututor_parent",
    "lls",
    "lls-frontend",
    "lls-mobile",
    "creative-hub",
    "finch-inbox",
    "cx-call-capture-android",
    "sims-owner-analytics",
)

# Extra spellings people actually type for a known project, mapped to the
# canonical AGENTS.md project slug above. Lookup keys are lowercase.
PROJECT_ALIASES: dict[str, str] = {
    "kelasapp": "kelas",
    "sims": "sifu-tutor",
    "sifu tutor": "sifu-tutor",
    "tutor app": "sifututor_tutor",
    "parent app": "sifututor_parent",
    "finch": "finch-inbox",
    "learnest": "lls",
}

# Umbrella/cross-project work that is not any single sub-project (CLAUDE.md
# Koda tagging convention: "umbrella Agent OS work" -> tag "sifututor").
UMBRELLA_PROJECT = "sifututor"

# The 11 workflow/skill routes named explicitly in the Bundle 2 build spec.
WORKFLOW_ROUTES: tuple[str, ...] = (
    "question",
    "research",
    "diagnosis",
    "implementation",
    "review",
    "qa",
    "deployment",
    "handoff",
    "save_session",
    "continuation",
    "new_side_task",
)

# A bounded task-type vocabulary. Distinct from workflow_route: workflow
# route is "what kind of session move is this", task type is closer to
# AGENTS.md's branch-type vocabulary ("what kind of change is this").
TASK_TYPES: tuple[str, ...] = (
    "question",
    "research",
    "bugfix",
    "hotfix",
    "feature",
    "docs",
    "refactor",
    "operational",
)

# A bounded risk scale. Distinct from the decision-layer schema's
# "sensitivity" (low/medium/high, an input hint) -- this is an output
# judgment with a fourth, deterministic-only rung: "critical" is reachable
# only through a forced override, never through the classifier alone.
RISK_LEVELS: tuple[str, ...] = ("low", "medium", "high", "critical")

# AGENTS.md "Shared Workflow Playbooks" table.
PLAYBOOKS: dict[str, str] = {
    "task_router": "docs/agent-playbooks/task-router.md",
    "verify": "docs/agent-playbooks/verify.md",
    "qa": "docs/agent-playbooks/qa.md",
    "monitor_production_logs": "docs/agent-playbooks/monitor-production-logs.md",
    "mission_ledger": "docs/agent-playbooks/mission-ledger.md",
    "commit": "docs/agent-playbooks/commit.md",
    "save_session": "docs/agent-playbooks/save-session.md",
}

# Deterministic workflow_route -> required playbooks. An empty tuple is a
# real answer ("no playbook needed for a plain question"), not a
# placeholder -- this is the "only the playbooks this specific request
# actually needs, not the full always-loaded set" bullet from the build
# spec.
REQUIRED_PLAYBOOKS_BY_ROUTE: dict[str, tuple[str, ...]] = {
    "question": (),
    "research": (PLAYBOOKS["mission_ledger"],),
    "diagnosis": (PLAYBOOKS["task_router"], PLAYBOOKS["verify"], PLAYBOOKS["qa"]),
    "implementation": (PLAYBOOKS["task_router"], PLAYBOOKS["verify"], PLAYBOOKS["commit"]),
    "review": (PLAYBOOKS["verify"],),
    "qa": (PLAYBOOKS["qa"],),
    "deployment": (PLAYBOOKS["verify"], PLAYBOOKS["monitor_production_logs"]),
    "handoff": (PLAYBOOKS["save_session"],),
    "save_session": (PLAYBOOKS["save_session"],),
    "continuation": (PLAYBOOKS["task_router"],),
    "new_side_task": (PLAYBOOKS["task_router"], PLAYBOOKS["mission_ledger"]),
}

# Deterministic default risk per workflow_route, used only when nothing in
# `deterministic.py` forces an override.
DEFAULT_RISK_BY_ROUTE: dict[str, str] = {
    "question": "low",
    "research": "low",
    "diagnosis": "medium",
    "implementation": "medium",
    "review": "medium",
    "qa": "medium",
    "deployment": "high",
    "handoff": "low",
    "save_session": "low",
    "continuation": "low",
    "new_side_task": "low",
}

# Deterministic default task_type per workflow_route, used only when
# nothing in `deterministic.py` overrides it (e.g. an explicit "hotfix"
# signal in the text).
DEFAULT_TASK_TYPE_BY_ROUTE: dict[str, str] = {
    "question": "question",
    "research": "research",
    "diagnosis": "bugfix",
    "implementation": "feature",
    "review": "operational",
    "qa": "operational",
    "deployment": "operational",
    "handoff": "operational",
    "save_session": "operational",
    "continuation": "operational",
    "new_side_task": "operational",
}

# CLAUDE.md "Project tagging convention" Koda tag table. Only the projects
# with a documented tag are listed here; UMBRELLA_PROJECT above is its own
# valid tag for cross-project work.
KODA_PROJECT_TAGS: dict[str, str] = {
    "kelas": "kelasapp",
    "sifu-tutor": "sifu-tutor",
    "ripple-suite": "ripple-suite",
    "sifututor_tutor": "sifututor_tutor",
    "sifututor_parent": "sifututor_parent",
    "lls": "lls",
    "lls-frontend": "lls-frontend",
    "lls-mobile": "lls-mobile",
    "creative-hub": "creative-hub",
    "finch-inbox": "finch-inbox",
    "cx-call-capture-android": "cx-call-capture-android",
    "sims-owner-analytics": "sims-owner-analytics",
}
