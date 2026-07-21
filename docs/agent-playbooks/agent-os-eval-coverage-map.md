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
| Commit and push gates | AO-002, AO-005, AO-019, AO-026, AO-102 | Committing, pushing, deploying, merging, or releasing without review, risk checks, state clarity, and approval. |
| Approval bundle scope | AO-022, AO-023, AO-024 | Treating `approve` as permission to do more than the previous exact approval request. |
| Forbidden boundaries | AO-006, AO-007, AO-020 | Reading secrets, touching `live/`, or bypassing hooks/tests with `--no-verify`. |
| Critical lanes | AO-008, AO-009, AO-010 | Editing payment, invoice, migration, auth, or mobile API contract work before read-only diagnosis. |
| Staff and reported context | AO-011, AO-071, AO-075, AO-101 | Treating staff reports or capability requests as verified implementation permission, creating GitHub issue noise too early, or starting coding before quick diagnosis and task-state routing. |
| Context authority and state ownership | AO-012, AO-013, AO-096, AO-097, AO-098, AO-108 | Trusting Koda, prior memories, chat, commits, PRs, deploy records, Planner, GitHub, or QA evidence as the wrong kind of truth; storing new information in the wrong home; ignoring stale-context conflicts. |
| Verify, QA, UI audit, and evidence | AO-016, AO-017, AO-028, AO-059, AO-060, AO-099, AO-100, AO-107, AO-186 | Asking Hafiz to check what the agent can safely test, calling machine proof enough for a human workflow, saying ready without naming evidence level reached, mixing up code proof, journey proof, and release proof, routing SIMS visual QA into generic review instead of the first-class UI audit, or hiding a missing-proof gap inside a vague manual check. |
| Short commands | AO-021, AO-076 | Treating `proceed next` or `go next` as trivial instead of routing through visible chat context. |
| Smart resume | AO-093 | Starting cold when an active Session Map, Reference Pack, or local Git state clearly shows the user is continuing existing work. |
| Planning bundles | AO-015, AO-027 | Turning safe docs/planning work into product implementation without confirmed scope. |
| Implementation readiness | AO-104 | Starting code from a weak brief, guessing the entry point, skipping the plain-English implementation explanation, or handing another builder an incomplete prompt. |
| Enforcement and drift detection | AO-105 | Over-automating every preference in hooks, under-enforcing dangerous actions, or fixing drift in the wrong layer. |
| State truth | AO-018, AO-065, AO-067, AO-095 | Confusing drafted, changed locally, committed locally, pushed to GitHub, PR open, merged, deployed, live checked, or accepted / closed states. |
| Readiness checks | AO-072 | Answering readiness questions without running the health/doctor path. |
| Response shape | RS-001 through RS-012 | Closing work with vague "done" instead of changed, checked, state, remaining risk, next action, decision needed, practical meaning, easier explanation, formal-label translation, blocked-work clarity, and technical detail in natural language. |
| Explanation and walkthrough shape | EX-001 through EX-004 | Starting technical findings before the user/workflow story, or ignoring a one-by-one walkthrough request by dumping later items. |
| Implementation preview shape | PB-001 and PB-002 | Starting a non-trivial build before explaining the intended user behavior, real options, recommendation, and evidence plan in English. |
| Evidence target identity | TI-001 and TI-002; AO-185 | Trusting browser or screenshot evidence without proving the URL/environment, serving process, worktree/branch, and commit/version. |
| Copy-ready outbound messages | WM-001, WM-002, WM-003, WM-004 | Returning WhatsApp or other send-ready text as rendered Markdown links, blockquotes, or split copy blocks instead of one copy-safe plain-text message with bare URLs and channel-native formatting. |
| Recipient-specific release handoff | RH-001, RH-002, RH-003, RH-004, RH-005; AO-187, AO-188, AO-189 | Sending a generic incident report instead of an integrated developer PR continuation, omitting independent verification/evidence, sending two disconnected messages to one developer, mixing distinct audiences into one message, or inventing an unconfirmed report channel. |
| State fixtures | ST-001, ST-002, ST-003, ST-004, ST-005, ST-006, ST-007, ST-008, ST-009, ST-010, ST-011, ST-012, ST-013, ST-014 | Saying local, committed, pushed, PR-open, merged, deployed, or smoke-passed work is further along than evidence proves; claiming PR/deploy state without a PR/link, commit, release, or deployment evidence. |
| Koda fixtures | KO-001, KO-002, KO-003, KO-004, KO-005, KO-006, KO-007, KO-008, KO-009, KO-010, KO-011, KO-012, KO-013, KO-014, KO-015 | Storing unsafe, vague, unscoped, duplicate, or invalid memories; trusting stale memory without current evidence; silently dropping memory work when CLI fallback is healthy; using wrong correction source; mutating Koda during bulk cleanup before a read-only audit. |
| Koda retrieval quality | KR-001 through KR-004 | Important Agent OS memories can be found again by future sessions using the direct Koda helper. Checked on demand by `scripts/agent-checks/agent-os-koda-retrieval-quality.py`; health checks syntax only because live retrieval depends on current Koda service state. |
| Capability fixtures | CP-001, CP-002, CP-003, CP-004, CP-005, CP-006, CP-007, CP-008, CP-009, CP-010, CP-011, CP-012, CP-013, CP-014, CP-015, CP-016, CP-017 | Claiming unverified tools, using blocked tools without approval, asking again for task-relevant approved auto-read evidence, using auto-read as broad/unrelated access, granting staff unsafe capability, or treating forbidden boundaries as workaroundable. |
| Capability probe | Local capability report | Claiming local filesystem, git, Koda, agent-access wrapper, commit, push, deploy, secret, or live-write capability without checking current-session state first. Checked by `scripts/agent-checks/agent-os-capability-probe.py` and health. |
| GitHub probe | GitHub CLI read probe | Claiming GitHub repo metadata access without checking `gh` auth and a tiny read-only repo metadata call first. Checked on demand by `scripts/agent-checks/agent-os-github-probe.py`; health checks file presence only to stay fast. |
| Planner probe | Microsoft Graph read probe | Claiming Teams Planner intake access without checking Graph auth, the `Development & Support` group, the `Task Management Board` plan, and task metadata visibility first. Checked on demand by `scripts/agent-checks/agent-os-planner-probe.py`; output avoids Planner card content. |
| Google Drive probe | Connector metadata probe | Claiming Google Drive live read access when only plugin metadata is installed, or fetching Drive file contents before a tiny search/list/metadata read proves the target. Checked by `scripts/agent-checks/agent-os-google-drive-probe.py`; live reads still require exposed connector tools. |
| Production logs probe | Sentry and BetterStack read probe | Claiming production monitoring/log evidence without checking approved read-only Sentry and BetterStack access first, or printing noisy issue/log details during a capability check. Checked by `scripts/agent-checks/agent-os-production-logs-probe.py`; output is status/counts only. |
| Conversation fixtures | CV-001, CV-002, CV-003, CV-004, CV-005, CV-006, CV-007, CV-008, CV-009 | Treating short replies such as `approve`, `proceed`, `go next`, or `what next` as isolated text instead of resolving them against visible prior context. |
| Parity fixtures | Structural parity runner | Losing the shared playbook, Claude adapter, Codex adapter, Product Design phase mapping, Plane exception rule, or parity health wiring. |
| Behavior traces | BT-001 through BT-004 | Codex chooses the expected workflow route, first move, approval boundary, and evidence language for common Hafiz prompts; optional live Claude mode can compare Claude's structured trace without making normal health depend on live LLM output. Checked by `scripts/agent-checks/agent-os-behavior-trace-runner.py` and the validation loop. |
| Adapter readiness | SH, CX, and CL readiness checks | Claiming Codex or Claude is set up without proving the shared core, Codex config/skills, Claude settings/hooks, adapter markers, and deterministic behavior checks. Checked by `scripts/agent-checks/agent-os-adapter-readiness.py`; live Claude behavior remains optional evidence because extension/CLI limits can be external. |
| Workflow example structure | AO-138 | Leaving a workflow section without scenario examples or a scenario matrix. Checked by `scripts/agent-checks/agent-os-workflow-example-runner.py` and health. |
| Validation loop | Executable harness score | Hiding scattered Agent OS failures across separate scripts. Checked by `python3 scripts/agent-checks/agent-os-validation-loop.py --target 0.90 --max-rounds 3`, which combines executable checks into one readiness score. |
| Scenario Lab | RW-001 through RW-018 | Realistic Hafiz work moments across commit, push, critical lane, staff intake, agent-as-tester, memory, session map, production, forbidden secrets, validation target, readiness, product design, GitHub PR readiness, Planner read-only intake, production monitoring, stale Koda conflict, Claude/Codex behavior comparison, and live evidence probe reporting. Checked by `python3 scripts/agent-checks/agent-os-scenario-lab-runner.py --target 0.90`. |

## Manual Scenario Coverage

These are important but not honest as simple router-classifier tests yet.

| Area | Eval IDs | Why manual for now |
| --- | --- | --- |
| Communication style | AO-032, AO-033, AO-034, AO-035, AO-064, AO-070, AO-104, AO-175, AO-181, AO-183, AO-184, AO-187, AO-188, AO-189 | Partly covered by the response-shape runner and shared adapter reminders, including practical meaning, pre-build explanation, explanation order, one-by-one pacing, state, next action, decision needed, formal-label translation, deterministic copy-ready formatting, audience-specific PR/release handoffs, developer verification, and confirmed source wording. Full tone, current real-session quality, and content judgment still need human review. |
| Browser evidence target identity | AO-185 | Response fixtures reject screenshot/browser proof that omits target identity; real process-to-checkout mapping and deployed SHA evidence remain environment-dependent. |
| Transcript privacy and interpretation | AO-176, AO-181, AO-182 | The retrospective self-test proves human/injected filtering, rollover deduplication, redaction, and aggregate-only default output. Docs/evals distinguish complete file processing from representative semantic review. Deciding which high-signal turns represent a real workflow failure still needs manual review. |
| Credential-free active adapters | AO-177 | Adapter readiness scans active global Claude instructions for credential-shaped assignments without printing content. Rotation of a previously exposed credential remains a separate approved operational action. |
| Operational content contracts | AO-178 | Requires current safe evidence from the owning product/API/mobile surfaces and human judgment when sources conflict. |
| Visual completeness and acceptance state | AO-179, AO-180 | QA/evidence owners define embedded-control coverage and distinguish technical journey proof from Hafiz/business-owner acceptance; real UI and owner acceptance remain evidence-dependent. |
| Context conflicts with live repo state | AO-036, AO-037, AO-038, AO-039, AO-040, AO-044, AO-066, AO-068, AO-069, AO-160, AO-161, AO-162 | Needs current git, Mission Ledger, Planner, Koda, Session Map, PR, QA, or production/deploy evidence. AO-098 documents the shared stale-context behavior; AO-160 through AO-162 define the conflict-handling routine. Richer automation needs repo-state and session-state fixtures. |
| Memory quality and safety | AO-041, AO-042, AO-043, AO-045, AO-046, AO-051, AO-052, AO-053 | Partly covered by Koda fixtures and the on-demand live Koda retrieval-quality runner. Live write/read behavior still needs careful non-polluting test design before it becomes routine automation. |
| Capability inventory | AO-047, AO-048, AO-049, AO-050 | Local capability state is covered by the capability probe and capability fixtures. GitHub read capability is covered by an on-demand `gh` probe. Planner read capability is covered by an on-demand Microsoft Graph probe. Google Drive connector readiness is covered by a metadata probe, but live Drive reads still need exposed connector tools. Production monitoring capability is covered by an on-demand Sentry/BetterStack probe. |
| Lane escalation | AO-055, AO-056, AO-057, AO-058, AO-061, AO-062, AO-063 | Needs task details, product surface, and sometimes test data or credentials. |
| Build handoff quality | AO-104 | Needs real feature/bug context, codebase entry points, risks, and evidence plan. A simple router fixture cannot prove a build-ready brief is complete. |
| Enforcement layer choice | AO-105, AO-157 | Needs the specific rule, repeated-failure history, danger level, and automation feasibility. A simple router fixture cannot honestly choose the best enforcement strength. The enforcement promotion path defines the manual decision now. |
| Agent OS improvement loop | AO-109, AO-110, AO-111 | Needs the specific workflow mistake, owning source, connected docs/skills/hooks/evals/Koda state, and Hafiz-approved behavior change. A simple router fixture can help later, but full correctness needs context-aware review. |
| Related impact audit | AO-112, AO-113, AO-114 | Needs the actual root cause, related code surface, risk lane, and scope boundary. A simple router fixture cannot prove whether the related search was sufficient. |
| Bugfix and feature scenario quality | AO-133, AO-134 | Needs real task context, risk lane, user impact, product surface, and available evidence. A simple router fixture cannot honestly decide whether the agent chose the right workflow weight. |
| Verify, QA, and review scenario quality | AO-135, AO-136, AO-137 | Needs real work type, changed surface, available tools/data, evidence already gathered, release state, and next-state boundary. A simple router fixture cannot honestly prove whether the agent gathered enough proof for the claimed state. |
| Master workflow example quality | AO-138 | Structural presence is checked by the workflow example runner. Human/agent review uses the Scenario Example Quality Standard in `agent-os-workflows.md` to judge whether each example has a real trigger, first move, evidence/source, stop point, and "do not do" warning. |
| Doc routing and context loading | AO-145, AO-146, AO-147 | Needs real route context and current task triggers. The doc routing playbook defines the matrix now; future automation can warn when required route docs, Agent OS improvement docs, TESTING.md, or UI/UX docs are skipped. |
| Skill quality and pruning | AO-148, AO-149, AO-150 | Needs real docs, references, and route ownership. The pruning playbook and owner index define the decision now; future automation can warn when new active docs lack index entries or a proposed skill duplicates an existing owner. |
| Runtime reliability | AO-151, AO-152, AO-153, AO-154, AO-155 | Partly covered by response-shape and conversation fixtures. Full checks need real session state, active Session Map, route context, and current Git evidence. The runtime playbook defines the behavior now, including daily operating examples for common Hafiz phrases. |
| Workflow execution depth | AO-158, AO-159 | Needs the actual task, risk lane, current Git/PR/deploy state, and approved boundary. The workflow lanes playbook now defines finish states such as local proof, committed, PR ready, merged, deployed, live checked, monitored, and accepted/closed. Future automation can warn when `done` or `production` is used without a named finish state. |
| Acceptance and closure criteria | AO-163, AO-164, AO-165 | Needs real current state, Hafiz/business acceptance, parked-topic reason, Git/check evidence, and current Session Map context. The workflow lanes and state model now define when a packet is merely pushed/adopted, intentionally parked, or truly accepted/closed. |
| Agent OS completion map and validation target | AO-166, AO-167, AO-168 | Completion/rollout claims need current roadmap state, health/check evidence, project-profile adoption state, access profile readiness, pilot state, and Hafiz/business acceptance. The 90% validation-target prompt is executable: it must route to workflow improvement, run the validation loop, explain what the score proves, and fix failing Agent OS layers if below target. |
| Session Map lifecycle | AO-106, AO-156 | Needs real parallel sessions, side paths, compaction, branch state, handoff context, and Git state changes. A simple fixture can catch obvious over-creation, but not whether two maps should be merged, parked, split, or updated after a commit/push. The live update loop defines the manual behavior now. |
| Developer staff rollout details | AO-073, AO-074 | Needs generated developer-staff onboarding artifacts, and must preserve the rule that ordinary staff use Teams Planner only. |
| Claude/Codex behavioral parity | AO-082, AO-083, AO-084 | Structural parity and the Behavior Parity Review Standard are executable through the parity runner. Adapter readiness now proves shared core, Codex, and Claude wiring. The behavior trace runner checks Codex route/first move/action markers and can optionally ask Claude CLI for a structured live trace. Full response-quality comparison still needs human review because different wording is allowed. |
| Multi-agent and adapter workflow | AO-129, AO-130, AO-131 | Needs real stage context, available tools, handoff state, and worker capability evidence. The playbook defines the stage-first rule now; richer automation needs trace fixtures from real multi-agent sessions. |
| Pre-push batch completion | AO-094 | Needs real local commit context, current Session Map state, check output, and human-readable package review. A simple router fixture cannot honestly tell whether a batch tells one complete story. |
| PR/CI automation and efficiency audit | AO-115, AO-116, AO-117 | Needs real GitHub PR state, CI state, branch protection, approval identity, and friction history. The playbooks define the behavior now; richer automation needs GitHub fixtures and workflow-friction logs. |
| Release/deploy/live monitoring | AO-118, AO-119, AO-120 | Needs real deploy records, production SHA, smoke evidence, monitoring output, and multi-fix release inventory. The playbook defines the state ladder now; richer automation needs safe deploy and observability fixtures. |
| Incident workflow | AO-121, AO-122, AO-123 | Needs real symptoms, monitoring evidence, severity, mitigation choices, rollback/fix-forward options, deploy state, and postmortem quality. The playbook defines the triage path now; richer automation needs incident trace fixtures. |
| Project adoption | AO-124, AO-125, AO-126 | Needs real target repo docs, installer output, project command evidence, and readiness profile review. The playbook defines the adoption path now; richer automation needs per-project fixtures. |
| Governance and versioning | AO-127, AO-128 | Needs real changed files, source ownership, checks, Koda state, and Git state. The playbook defines the path now; richer automation needs change-set fixtures. |
| Save-session and handoff continuity | AO-103 | Needs real session length, Session Map state, local Git state, evidence gaps, and target receiver context. A simple router fixture cannot honestly prove the restart pack is useful. |
| Work intake scenario quality | AO-132 | Needs current Session Map state and existing-doc awareness. A simple router fixture can catch the route, but a human/agent review must judge whether the agent continued from settled intake rules or restarted the topic. |

## Future Harness Targets

1. Add non-polluting Koda live write/read checks only when the harness can
   create, find, and clean up test memories without polluting durable memory.
2. Add an app-tool live-read fixture for Google Drive when Codex can call the
   Google Drive connector from the fixture harness.
3. Extend live Claude/Codex behavior comparison into a richer response-quality
   review once trace output is stable enough and cost/noise are acceptable.
4. Add a real Claude extension transcript check if the extension exposes a safe
   non-interactive way to run prompts without loading unrelated project context.

## Maintenance Rule

When adding or changing an eval:

1. Add or update the Markdown eval table.
2. Add executable coverage when the behavior can be tested honestly by the
   runner.
3. Add Scenario Lab coverage when the behavior needs a realistic Hafiz work
   moment rather than only a small route eval.
4. If it cannot be executable yet, record it under manual scenario or future
   harness coverage here.
5. Keep every executable `AO-*` case listed in this coverage map; the runner
   fails when a code case is missing from the map.
6. Run `scripts/agent-checks/agent-os-eval-runner.py --self-test`.
7. Run `python3 scripts/agent-checks/agent-os-scenario-lab-runner.py --target 0.90`.
8. Run `python3 scripts/agent-checks/agent-os-validation-loop.py --target 0.90 --max-rounds 3`.
9. Run `scripts/agent-checks/agent-os-health.sh`.

Use [agent-os-evaluation-harness.md](agent-os-evaluation-harness.md) when
deciding which layer should own a new harness case.
