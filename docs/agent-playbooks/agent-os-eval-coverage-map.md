# Agent OS Eval Coverage Map

This map keeps Agent OS eval work from becoming random one-off tests.

Plain meaning: the eval suite should prove the expensive mistakes are guarded,
while the map records what is automated, what is still manual, and what should
be automated next.

## Coverage Levels

| Level | Meaning | Current proof |
| --- | --- | --- |
| Executable | Checked by `scripts/agent-checks/agent-os-eval-runner.py` and health. | Router skill, reason text, and required action text. |
| Manual scenario | Covered by the Markdown eval table but not yet automated. | Human/agent review using `docs/agent-playbooks/agent-os-evals.md`. |
| Future harness | Needs conversation state, repo state, browser/mobile action, or external tools before automation is honest. | Coverage map only until the harness exists. |

## Executable Coverage

| Area | Eval IDs | Protects against |
| --- | --- | --- |
| Discussion stays light | AO-001, AO-014, AO-054 | Over-triggering workflow ceremony during thinking, learning, or architecture discussion. |
| Commit and push gates | AO-002, AO-005, AO-019, AO-026 | Committing, pushing, deploying, merging, or releasing without review and approval. |
| Approval bundle scope | AO-022, AO-023, AO-024 | Treating `approve` as permission to do more than the previous exact approval request. |
| Forbidden boundaries | AO-006, AO-007, AO-020 | Reading secrets, touching `live/`, or bypassing hooks/tests with `--no-verify`. |
| Critical lanes | AO-008, AO-009, AO-010 | Editing payment, invoice, migration, auth, or mobile API contract work before read-only diagnosis. |
| Staff and reported context | AO-011, AO-071, AO-075 | Treating staff reports or capability requests as verified implementation permission. |
| Context authority | AO-012, AO-013 | Trusting Koda, prior memories, or conflicting docs without checking current source of truth. |
| Verify, QA, and evidence | AO-016, AO-017, AO-028, AO-059, AO-060 | Asking Hafiz to check what the agent can safely test, or calling machine proof enough for a human workflow. |
| Short commands | AO-021, AO-076 | Treating `proceed next` or `go next` as trivial instead of routing through visible chat context. |
| Planning bundles | AO-015, AO-027 | Turning safe docs/planning work into product implementation without confirmed scope. |
| State truth | AO-018, AO-065, AO-067 | Confusing saved, local, committed, pushed, deployed, or live-smoke-passed states. |
| Readiness checks | AO-072 | Answering readiness questions without running the health/doctor path. |
| Response shape | RS-001, RS-002, RS-003, RS-004 | Closing work with vague "done" instead of changed, checked, state, remaining risk, and next action. |
| State fixtures | ST-001, ST-002, ST-003, ST-004, ST-005 | Saying local or committed work is live, deployed, or smoke-passed without evidence. |
| Koda fixtures | KO-001, KO-002, KO-003, KO-004, KO-005, KO-006, KO-007, KO-008, KO-009 | Storing unsafe, vague, unscoped, or invalid memories; trusting stale memory without current evidence; silently dropping memory work when CLI fallback is healthy. |

## Manual Scenario Coverage

These are important but not honest as simple router-classifier tests yet.

| Area | Eval IDs | Why manual for now |
| --- | --- | --- |
| Communication style | AO-032, AO-033, AO-034, AO-035, AO-064, AO-070 | Partly covered by the response-shape runner; still needs full assistant response review for tone and layered explanations. |
| Context conflicts with live repo state | AO-036, AO-037, AO-038, AO-039, AO-040, AO-044, AO-066, AO-068, AO-069 | Needs current git, Plane, Planner, Koda, or production/deploy evidence. |
| Memory quality and safety | AO-041, AO-042, AO-043, AO-045, AO-046, AO-051, AO-052, AO-053 | Partly covered by Koda fixtures; still needs live write/read behavior and retrieval quality evidence. |
| Capability inventory | AO-047, AO-048, AO-049, AO-050 | Needs session tool availability and permission state. |
| Lane escalation | AO-055, AO-056, AO-057, AO-058, AO-061, AO-062, AO-063 | Needs task details, product surface, and sometimes test data or credentials. |
| Staff kit details | AO-073, AO-074 | Needs generated staff/developer onboarding artifacts, not only routing. |

## Future Harness Targets

1. Add conversation-state fixtures so `approve`, `proceed`, and `what next`
   can be tested with real previous-message context instead of synthetic
   prompt text.
2. Add richer response fixtures for practical meaning, easier explanation,
   technical detail, and formal-label translation.
3. Add richer repo-state fixtures for PR open, merged, deployed, and
   live-smoke-passed scenarios with external evidence links.
4. Add richer Koda integration fixtures for live memory retrieval quality,
   duplicate detection, correction updates, and read-only memory audits.
5. Add tool-capability fixtures for GitHub, Plane, Planner, Google Drive, and
   production-log availability.

## Maintenance Rule

When adding or changing an eval:

1. Add or update the Markdown eval table.
2. Add executable coverage when the behavior can be tested honestly by the
   runner.
3. If it cannot be executable yet, record it under manual scenario or future
   harness coverage here.
4. Keep every executable `AO-*` case listed in this coverage map; the runner
   fails when a code case is missing from the map.
5. Run `scripts/agent-checks/agent-os-eval-runner.py --self-test`.
6. Run `scripts/agent-checks/agent-os-health.sh`.
