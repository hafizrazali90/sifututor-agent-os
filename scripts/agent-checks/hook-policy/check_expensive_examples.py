#!/usr/bin/env python3
"""Two representative expensive/network-or-model-backed checks.

Nothing in the surveyed hooks (SURVEY.md section 6) calls a network service
or a model directly today. These two checks are the shapes such a check
would take once one exists -- a REQUIRED one (a remote policy verdict that
must gate the action) and an ADVISORY one (a non-blocking status lookup,
modeled on the documented-but-currently-silent Koda health check in
docs/agent-playbooks/agent-os-hook-dispatcher.md's SessionStart row). Both
take their "backend" as an injected callable so tests never make a real
network call; dispatcher.py's timeout/fail-safe wrapper is what turns a
slow or raising backend into the required block-vs-degrade behavior, not
these classes themselves -- see test_dispatcher.py for that contract.
"""
from __future__ import annotations

from typing import Callable

from models import Decision, HookRequest, Severity


class RemotePolicyCheck:
    """REQUIRED, expensive: a hypothetical remote policy verdict on a push.

    `backend(request)` returns True (allowed) or False (rejected) — or
    raises/blocks past the dispatcher's timeout, in which case the
    dispatcher denies with a "required check unavailable" reason (never
    silently passes; see dispatcher.py::_unavailable_decision).
    """

    name = "remote_policy_check"
    severity = Severity.REQUIRED
    expensive = True

    def __init__(self, backend: Callable[[HookRequest], bool]):
        self._backend = backend

    def applies(self, request: HookRequest) -> bool:
        return request.tool_name == "Bash" and "git push" in request.command

    def run(self, request: HookRequest) -> Decision:
        if self._backend(request):
            return Decision.allow(self.name)
        return Decision.deny(
            self.name,
            reason="Remote policy service rejected this push.",
            guidance="Review the policy service's dashboard for the exact rule "
            "that failed, address it, and retry the push.",
        )


class StaffNoticeCheck:
    """ADVISORY, expensive: a non-blocking status/notice lookup.

    `backend(request)` returns a note string to surface (e.g. a Koda health
    warning) or None/empty for "nothing to say". A failure here degrades
    visibly via the dispatcher's timeout/fail-safe wrapper; it never blocks.
    """

    name = "staff_notice_check"
    severity = Severity.ADVISORY
    expensive = True

    def __init__(self, backend: Callable[[HookRequest], str | None]):
        self._backend = backend

    def applies(self, request: HookRequest) -> bool:
        return request.tool_name == "Bash" and "git commit" in request.command

    def run(self, request: HookRequest) -> Decision:
        note = self._backend(request)
        if note:
            return Decision.allow(self.name, note=note)
        return Decision.allow(self.name)
