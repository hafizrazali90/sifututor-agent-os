#!/usr/bin/env python3
"""The one shared command-safety dispatcher (bundle spec, build item 2).

`HookDispatcher.dispatch()` runs every check that `applies()` to a request,
cheap-safe checks before expensive ones, and enforces the bundle's central
fail-safe contract for a check that cannot run:

- Severity.REQUIRED: block with a clear, actionable reason. Never pass.
- Severity.ADVISORY: degrade visibly (a non-blocking note in the result).
  Never silently drop the failure.

A cheap check's own exception is treated the same way as an expensive
check's failure (same `_unavailable_decision` path) -- "cheap" only means
"no timeout wrapper is needed to bound its running time", not "assumed
infallible".

This module does not know about Claude or Codex payload shapes; see
adapter_claude.py and adapter_codex.py for that translation.
"""
from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass, field

from models import Decision, HookRequest, Outcome, Severity

DEFAULT_EXPENSIVE_TIMEOUT_S = 5.0


@dataclass(frozen=True)
class DispatchResult:
    request: HookRequest
    decisions: list[Decision] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(d.blocks for d in self.decisions)

    @property
    def blocking_decision(self) -> Decision | None:
        for d in self.decisions:
            if d.blocks:
                return d
        return None

    @property
    def ask_user_decisions(self) -> list[Decision]:
        return [d for d in self.decisions if d.outcome == Outcome.ASK_USER]

    @property
    def degraded_decisions(self) -> list[Decision]:
        return [d for d in self.decisions if d.outcome == Outcome.DEGRADED]


class HookDispatcher:
    def __init__(self, checks, *, expensive_timeout_s: float = DEFAULT_EXPENSIVE_TIMEOUT_S):
        self._checks = list(checks)
        self._expensive_timeout_s = expensive_timeout_s

    def dispatch(self, request: HookRequest) -> DispatchResult:
        decisions: list[Decision] = []
        cheap = [c for c in self._checks if not getattr(c, "expensive", False)]
        expensive = [c for c in self._checks if getattr(c, "expensive", False)]

        for check in cheap:
            if not check.applies(request):
                continue
            decision = self._run_cheap(check, request)
            decisions.append(decision)
            if decision.blocks:
                return DispatchResult(request, decisions)

        for check in expensive:
            if not check.applies(request):
                continue
            decision = self._run_expensive(check, request)
            decisions.append(decision)
            if decision.blocks:
                return DispatchResult(request, decisions)

        return DispatchResult(request, decisions)

    def _run_cheap(self, check, request: HookRequest) -> Decision:
        try:
            return check.run(request)
        except Exception as exc:  # noqa: BLE001 - any check failure must degrade/block, not crash the caller
            return self._unavailable_decision(check, exc)

    def _run_expensive(self, check, request: HookRequest) -> Decision:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(check.run, request)
            try:
                return future.result(timeout=self._expensive_timeout_s)
            except concurrent.futures.TimeoutError:
                return self._unavailable_decision(check, TimeoutError("check did not respond in time"))
            except Exception as exc:  # noqa: BLE001
                return self._unavailable_decision(check, exc)

    @staticmethod
    def _unavailable_decision(check, exc: Exception) -> Decision:
        if check.severity == Severity.REQUIRED:
            return Decision.deny(
                check.name,
                reason=f"Required check '{check.name}' could not run: {exc}",
                guidance=f"'{check.name}' is a required check; a required check "
                "that cannot run must block, never silently pass. Retry once its "
                "dependency is reachable, or get explicit human approval before "
                "proceeding without it.",
            )
        return Decision.degraded(
            check.name,
            note=f"Could not verify '{check.name}' ({exc}); proceed with caution.",
        )
