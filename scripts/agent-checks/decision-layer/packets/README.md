# Compact execution packets (Bundle 3, issue #160)

A "compact execution packet" is a versioned summary of exactly what one
route/task-type actually requires, generated from a small amount of plain
task context. It replaces attaching the full verify/QA/review/commit
checklist to every task with a **triggered** subset: only the obligations
this specific route/task-type actually needs.

This is a standalone packet-generation module with fixtures. It does not
change how any existing skill, hook, or playbook runs today; wiring a
packet into a live workflow is a later, separate decision (see the scope
boundary in `.agent-os/handoffs/bundle-3-build-spec.md`).

The deep playbooks remain the authoritative on-demand reference:
`docs/agent-playbooks/task-router.md`, `verify.md`, `qa.md`, `commit.md`,
`related-impact-audit.md`, `release-documentation.md`. A packet is a
triggered summary of those, never a replacement, and an unmapped
route/task-type falls back to the full checklist plus a pointer at those
files rather than silently omitting something (`obligations.fallback_obligations`).

## Module layout

| Module | Responsibility |
| --- | --- |
| `packet_schema.py` | Versioned packet field set (`packet_fields()`), the `APPROVAL_REFERENCE_NOT_PROVIDED` sentinel, and `validate_input` / `PacketValidationError` for the builder's raw input |
| `obligations.py` | The route -> triggered-obligation mapping (`resolve_obligations`), plus the safe `fallback_obligations` for an unmapped route/task-type |
| `packet_builder.py` | `build_packet(...)`: assembles the final packet, reuses Bundle 1's `secret_filter` to block on secret/PII-shaped input, and reuses Bundle 1's `engine.decide` (fake provider only) to estimate the risk bucket |

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
    approval_reference: str | None = None,     # see hard limit below
    user_facing: bool = False,        # triggers small-change's conditional
                                       # E2E / related-impact obligations
    staff_facing: bool = False,       # triggers the staff-documentation
                                       # context item
    critical_lane: bool = False,      # triggers the Universal Safety Rule
                                       # halt (payments/auth/migrations/etc.)
    config: dict | None = None,       # decision-layer config override
    provider: object | None = None,   # decision-layer provider override
                                       # (test injection point)
) -> dict
```

## Output shape

Exactly the fields in `packet_schema.packet_fields()`, always including
`schema_version`:

```text
schema_version
goal
project
scope_and_exclusions          -- {route, task_type, scope, exclusions}
target_state
validated_approval_reference
required_context
required_checks_evidence
stop_conditions
next_automatic_action
follow_up_disposition
```

## Hard limit: `validated_approval_reference`

This module can never populate this field on its own authority. It is
always exactly the `approval_reference` string the caller supplied, or the
`APPROVAL_REFERENCE_NOT_PROVIDED` sentinel when none was supplied -- never
invented, never inferred from risk bucket, route, or a decision-layer
answer. See `test_packet_builder.ApprovalReferenceHardLimitTest`.

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

Before assembling a packet, every free-text input field is scanned with
Bundle 1's `secret_filter.scan` (reused, not rebuilt). Any finding blocks
the packet: the flagged field(s) are redacted in the returned packet,
`next_automatic_action` halts, and the decision layer is never dispatched
to (`test_packet_builder.SecretBlockedTest`).
