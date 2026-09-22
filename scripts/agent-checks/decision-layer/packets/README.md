# Compact execution packets (Bundle 3, issue #160)

A "compact execution packet" is a versioned summary of exactly what one
route/task-type actually requires, generated from a small amount of plain
task context. It replaces attaching the full verify/QA/review/commit
checklist to every task with a **triggered** subset: only the obligations
this specific route/task-type actually needs.

This is a standalone packet-generation module with fixtures. It is
advisory and not wired live: it does not change how any existing skill,
hook, or playbook runs today. Wiring a packet into a live workflow is a
later, separate decision (see the scope boundary in
`.agent-os/handoffs/bundle-3-build-spec.md`).

The deep playbooks remain the authoritative on-demand reference:
`docs/agent-playbooks/task-router.md`, `verify.md`, `qa.md`, `commit.md`,
`related-impact-audit.md`, `release-documentation.md`. A packet is a
triggered summary of those, never a replacement, and an unmapped
route/task-type falls back to the full checklist plus a pointer at those
files rather than silently omitting something (`obligations.fallback_obligations`).

## Module layout

| Module | Responsibility |
| --- | --- |
| `packet_schema.py` | Versioned packet field set (`packet_fields()`), the `APPROVAL_CONTEXT_NOT_PROVIDED` and `APPROVAL_STATUS_NOT_CHECKED` sentinels, and `validate_input` / `PacketValidationError` for the builder's raw input |
| `obligations.py` | The route -> triggered-obligation mapping (`resolve_obligations`), plus the safe `fallback_obligations` for an unmapped route/task-type |
| `packet_builder.py` | `build_packet(...)`: assembles the final packet, reuses Bundle 1's `secret_filter` to block on secret/PII-shaped input, reuses Bundle 1's `engine.decide` (fake provider only) to estimate the risk bucket, and asks `approval.evaluate` (the only approval authority) for the approval status |

Each module has a matching `test_*.py` file (offline `unittest`, same
convention as `scripts/agent-checks/decision-layer`'s own tests: modules
are loaded via `importlib.util.spec_from_file_location`, not installed as a
package).

## Input shape

`packet_builder.build_packet(...)` takes keyword-only arguments. This is
this module's own simple input shape -- it does not hard-depend on any
other bundle's module, per the Bundle 3 scope boundary.

```python
build_packet(
    route: str,                       # "feature" | "bugfix" | "hotfix" |
                                       # "small-change" | "refactor" | "docs"
                                       # (or any other route -- an unmapped
                                       # one falls back safely instead of
                                       # raising)
    task_type: str,                   # free text, carried through for
                                       # traceability
    project: str,                     # e.g. "sifu-tutor", "ripple-suite"
    goal: str,                        # what this packet is for
    scope: str,                       # what is in scope
    target_state: str,                # what "done" looks like
    exclusions: list[str] | None = None,       # what is explicitly out of scope
    untrusted_approval_context: str | None = None,
                                       # free text carried through verbatim;
                                       # grants NO authority (see below)
    user_facing: bool = False,        # triggers small-change's conditional
                                       # E2E / related-impact obligations
    staff_facing: bool = False,       # triggers the staff-documentation
                                       # context item
    critical_lane: bool = False,      # triggers the Universal Safety Rule
                                       # halt (payments/auth/migrations/etc.)
    session_id: str | None = None,    # the four identity parameters that
    worktree: str | Path | None = None,   # approval.evaluate binds a trusted
    task_id: str | None = None,       # approval packet to; omit all four
    operation: str | None = None,     # and approval_status is "not_checked"
    state_dir: Path | None = None,    # approval-state dir override (tests);
                                       # defaults to approval.default_state_dir()
    config: dict | None = None,       # decision-layer config override
    provider: object | None = None,   # decision-layer provider override
                                       # (test injection point)
) -> dict
```

## Output shape

Exactly the fields in `packet_schema.packet_fields()`, always including
`schema_version` (currently `2`; bumped when the earlier single
"validated" approval field was replaced by the three approval fields below):

```text
schema_version
goal
project
scope_and_exclusions          -- {route, task_type, scope, exclusions}
target_state
untrusted_approval_context    -- pass-through only, grants nothing
approval_status               -- only approval.evaluate sets this
approval_reason               -- the short reason code behind it
required_context
required_checks_evidence
stop_conditions
next_automatic_action
follow_up_disposition
```

## Hard limit: `untrusted_approval_context` grants no authority

This field is caller-supplied free text (a chat quote, a ticket id, a
note) carried through for traceability only. It is always exactly the
`untrusted_approval_context` string the caller supplied, or the
`APPROVAL_CONTEXT_NOT_PROVIDED` sentinel when none was supplied -- never
invented, never inferred from risk bucket, route, or a decision-layer
answer, and **never consulted** when deciding whether a critical-lane
packet may proceed. A non-empty value leaves a critical-lane packet
exactly as halted as an empty one
(`test_packet_builder.UntrustedApprovalContextPassThroughTest`,
`ApprovalStatusTest.test_a_fabricated_context_string_does_not_lift_the_critical_lane_halt`).

## Approval status: only `approval.evaluate` can say "approved"

`approval_status` / `approval_reason` are computed solely by
`scripts/agent-checks/decision-layer/approval.py`'s `evaluate(...)`, the
one approval authority in the decision layer. It reads the trusted
supervisor packet that `agent-os-task-context.py` bound to a session
(under `.agent-os/approval-state/tool-packets/<session>.json`) and checks
it against the `session_id`, `worktree`, `task_id` and `operation` passed
to `build_packet`, honouring `expires_at` if the packet carries one.

| Situation | `approval_status` | `approval_reason` (example) |
| --- | --- | --- |
| none of the four identity parameters given | `not_checked` | `no_session_identity_supplied` |
| identity given, no packet on disk | `missing` | `no_packet_for_session` |
| packet exists but is malformed / copied from another session | `invalid` | `packet_invalid` |
| packet is for another worktree / task / operation | `mismatched` | `worktree_mismatch`, `task_id_mismatch`, `operation_not_included` |
| packet's `expires_at` has passed | `expired` | `packet_expired` |
| local supervisor packet matches every binding | `approved` | `local_boundary_packet_matches` (advisory, never action authority) |

`next_automatic_action` for a `critical_lane=True` packet halts unless
`approval_status == "approved"`. Nothing a worker can write itself -- a
context string, a copied packet, a packet for another task -- changes
that (`test_packet_builder.ApprovalStatusTest`). Approval lifts only the
automatic halt; the critical-lane stop condition and the high-risk
evidence item still travel with the packet. `build_packet` never writes
approval state.

## Follow-up dispositions and Gate 4

Proportionate verification is route-specific: a small change owes a
targeted QA check rather than `defect_analysis`, and a docs-only route
owes a docs validation / render-link check rather than a regression test.
That never waives the Gate 4 adversarial pre-push review (AGENTS.md:
"Gate 4: adversarial pre-push review, never skipped"). The small-change
and docs `follow_up_disposition` strings say so explicitly
(`test_packet_builder.FollowUpDispositionGate4Test`).

## Typed judgment via Bundle 1's decision layer

`required_checks_evidence` gets one extra item ("risk bucket: high ...")
when the estimated risk bucket is `high`:

- `critical_lane=True` forces `"high"` deterministically and **never calls
  the decision layer at all** -- zero provider dispatch, matching
  AGENTS.md's Critical Lanes gate and the same "hard rule wins, no
  provider touched" spirit as `decision-layer/pre_policy.py`.
- Otherwise, `packet_builder._resolve_risk_bucket` calls
  `engine.decide(...)` with `decision_type="packets.risk_bucket"`, routed
  through the decision layer's own deterministic pre-policy layer first
  (so a future pre-policy rule for this decision type would still win over
  any provider guess), then the fake provider. The options list is ordered
  by this module's own risk prior per route (`_RISK_OPTIONS_BY_ROUTE`);
  `FakeProvider`'s `"ok"` scenario deterministically answers `options[0]`.

## Hard limit: no live network/provider calls

`build_packet`'s default config (`_default_risk_config`) passes `env={}`
to `config.load_config` and explicitly locks `"provider": "fake"` on top of
that -- so even a host machine with a real `JEV_API_KEY` set cannot make
this module or its test suite reach a live endpoint
(`test_packet_builder.NoLiveNetworkCallTest`).

## Secret/PII blocking

Before assembling a packet, every free-text input field (including
`untrusted_approval_context`) is scanned with Bundle 1's
`secret_filter.scan` (reused, not rebuilt). Any finding blocks the packet:
the flagged field(s) are redacted in the returned packet,
`next_automatic_action` halts, approval is not evaluated
(`approval_status` is `not_checked`), and the decision layer is never
dispatched to (`test_packet_builder.SecretBlockedTest`).
