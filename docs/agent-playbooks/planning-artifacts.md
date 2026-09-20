# Planning Artifacts

Use this playbook when a task needs thinking before implementation, but Hafiz
should not be forced to read code or a rigid PRD to understand what will happen.

Plain meaning:

```text
Before building something complex, create the smallest useful thinking board.
It should help Hafiz understand the goal, options, recommendation, risk, proof,
and next decision before the agent starts changing code.
```

## Why This Exists

The Agent OS already has Session Maps, Product Design artifacts, Koda, GitHub,
and workflow playbooks. The missing rule is how to choose the right planning
artifact before implementation.

This playbook prevents two bad extremes:

- building too fast from a vague prompt
- creating heavy documents for small safe work

## Source Of Truth

Markdown is the source of truth. HTML is a generated or review-only view.

Plain version:

```text
Update one readable Markdown source.
Generate a visual HTML view only when Hafiz needs to scan or review it.
Do not maintain two separate truths.
```

If an HTML view is manually annotated, copy the accepted decision back into the
Markdown source before treating it as final.

## Artifact Choices

Use the lightest artifact that makes the work understandable and safe.

| Artifact | Use when | What Hafiz should understand |
| --- | --- | --- |
| Chat only | Tiny question, learning, or no implementation yet. | The answer or recommendation. |
| Quick Brief | Small safe edit, typo, narrow bug, simple docs/tooling change, or obvious behavior. | What is wrong, what will change, what will not change, and how it will be checked. |
| Product Shape | User workflow, staff process, unclear expected behavior, multiple options, or multi-file change. | Current behavior, options, recommendation, tradeoff, evidence plan, and decision needed. |
| Build-Ready Pack | Major workflow, critical lane, multi-role/module work, backend/frontend contract, mobile/API contract, or handoff to another builder. | Full workflow, rules, contracts, edge cases, risks, build slices, proof plan, and stop point. |
| Session Map | Long-running session, side paths, many decisions, parallel agents, or unclear return path. | Where we are, why we are here, what changed, what is waiting, and what happens next. |
| Markdown + HTML view | Complex plan or long session where visual scanning matters. | Same truth as Markdown, easier to inspect as a board or dashboard. |

Do not use numeric labels such as `level 1`, `level 2`, or `level 3` when
talking to Hafiz. Say the practical artifact name and explain why.

## Required Content

Every planning artifact should answer only what is relevant for the task.

### Quick Brief

- What is wrong or requested?
- What will change?
- What will not be touched?
- How will the agent check it?
- Where will the agent stop?

### Product Shape

- What problem are we solving?
- What is the current behavior or current workflow?
- Who is affected?
- What options exist?
- What does the agent recommend, and why?
- What will change?
- What will not change?
- What are the risks or tradeoffs?
- How will it be proven?
- What decision does Hafiz need to make?

### Build-Ready Pack

- Goal and practical finish state.
- Users, roles, permissions, and affected workflows.
- Current workflow and target workflow.
- Business rules and edge cases.
- Entry points, state transitions, data/API/backend contracts, and
  compatibility requirements.
- Options, recommendation, and rejected alternatives.
- Out-of-scope list.
- Implementation slices.
- Evidence plan: tests, E2E, smoke, screenshots, API checks, monitoring, or
  manual business acceptance.
- Stop conditions and approval gates.
- Final build prompt or handoff instructions if another agent or developer will
  implement.

## Visual Review

Generate or open a visual view when Hafiz needs to scan the artifact quickly.
This applies especially to Session Maps, module redesigns, big workflow
decisions, release boards, and multi-session work.

Good visual view:

- starts with the goal and current state
- shows the recommended next action near the top
- separates decisions, risks, evidence, and waiting items
- uses cards, columns, flow, or tables so it is not a wall of text
- avoids decorative layouts that hide the actual work

When the visual artifact is local and safe to inspect, open it automatically:

```bash
open <path>
```

Do not auto-open files that contain secrets, credentials, raw tokens, `.env*`
content, or production-sensitive private payloads.

## Governed Deliverable Artifacts

Planning decides what to make. When the requested output is the deliverable
itself, route to the maintained artifact capability that is actually installed
in the current agent instead of recreating a Sifututor-specific generator.

| Deliverable | Preferred capability | Required evidence |
| --- | --- | --- |
| Word/DOCX or Google Docs-targeted document | Installed document skill or connected Google Docs skill | Source/fact review, privacy check, rendered-page inspection, and final-file openability. |
| PowerPoint or Google Slides deck | Installed presentation skill or connected Google Slides skill | Source/fact review, template/brand check, editable content where required, rendered-slide inspection, and export/openability. |
| Product identity, visual direction, or interface system | `product-design.md`; use installed image/design tools only for the assets they own | Confirmed audience and brand direction, project design-system fit, source/licence record for external assets, and visual review. |
| Security validation | Normal `verify.md`, `qa.md`, and `review.md` for task-scoped checks | Exact scope, non-destructive evidence, findings by severity, and honest residual risk. A penetration test is a separate explicitly scoped engagement. |

Artifact governance is capability-based, not model-based. Claude, Codex, Kilo,
or a future agent may expose different tool names, but the output contract stays
the same:

1. Use supplied source material and templates as authority. Never invent facts,
   citations, brand rules, or approvals.
2. Minimize sensitive input. Do not send private or production data to an
   external artifact service unless that service and data scope are approved.
3. Record provenance and licence/usage rights for downloaded fonts, images,
   templates, or other third-party assets. A preview image is not a licensed
   deliverable.
4. Preserve editability when the audience needs to revise the artifact. Do not
   flatten evidence, charts, tables, or required text merely to make rendering
   easier.
5. Inspect the rendered output, not only the source file. Automated checks can
   find overflow or missing files, but they do not prove good writing, visual
   quality, accessibility, or audience fit.
6. Prefer adaptable source formats and include headings, meaningful reading
   order, alternative text or an equivalent explanation for important visuals,
   readable contrast, and sufficiently large text where the format supports
   them. W3C advises providing adaptable formats, alternative text, consistent
   design, clear language, and readable presentation material.
7. Treat a real pilot as evidence only for the tested artifact, audience,
   environment, and reviewer. One successful output does not establish a
   universal autonomous workflow.

Authoritative references:

- [W3C: Making Events and Presentations Accessible](https://www.w3.org/WAI/teach-advocate/accessible-presentations/)
- [NIST SP 800-218: Secure Software Development Framework](https://www.nist.gov/publications/secure-software-development-framework-ssdf-version-11-recommendations-mitigating-risk)
- [OWASP Web Security Testing Guide](https://owasp.org/projects/web-security-testing-guide)

### Legacy Package Disposition (2026-09-20)

This closes the five package proposals recorded as CP-17, CP-18, CP-19,
CP-20, and CP-24. Their untracked proposal files are absent from the canonical
repository, so they are not recoverable active sources of truth.

| Proposal | Disposition | Reason and current owner |
| --- | --- | --- |
| CP-17 governed document production | **Replace** | Maintained installed document tooling already owns DOCX/Google Docs-targeted creation and render verification. This playbook owns Sifututor source, privacy, provenance, accessibility, and evidence rules. Do not recreate the missing custom skill or templates. |
| CP-18 HTML presentation workflow | **Replace** | Maintained presentation tooling owns editable decks and render/export checks. HTML may be a review view when useful, but it is not a second source of truth or the default deck format. Do not recreate the missing slide skill. |
| CP-19 identity design | **Adapt** | `product-design.md` owns identity decisions; installed image/design capabilities own asset creation or sourcing; project design systems and visual QA own implementation proof. A future dedicated skill needs repeated use and independent pilot evidence first. |
| CP-20 security testing research | **Retire as a workflow** | Routine secure-development checks belong in verify, QA, review, secret guards, and project rules. OWASP WSTG may inform an explicitly scoped web security assessment, but a broad penetration test must not be implied by ordinary QA. The old research package had no reconciled scope or accepted pilot. |
| CP-24 design autopilot | **Retire as a universal workflow; absorb proven parts** | Keep evidence-first design, surface/state inventory, deterministic preflight, rendered visual review, and learning from false positives. Reject fixed five-round loops, “never stop” behavior, universal quality claims, and tool-specific assumptions. `product-design.md`, `sims-ui-audit.md`, `qa.md`, and `review.md` own the live route. |

No follow-up skill is required by this review. Open a new issue only when real
use exposes a specific capability gap that the installed tools and current
owner playbooks cannot cover.

## Implementation Boundary

Before coding starts, the agent must be able to explain the intended
implementation in plain English:

```text
What will change, what will not change, why this approach is recommended, how
it will be proven, and where the agent will stop.
```

If the agent cannot explain that clearly, keep planning. Do not start coding
just because a document exists.

## Where To Save

| Information | Save to |
| --- | --- |
| Current session story and return path | Session Map |
| Confirmed product or UX artifact | Project feature docs |
| Durable workflow lesson or correction | Koda |
| Future goal or parked idea | Mission Ledger |
| Execution-ready coding work | GitHub issue or project active task |
| Exact changed files | Git commit |

Plain version:

```text
Planning artifacts explain the work.
They do not replace Koda, GitHub, Session Map, Mission Ledger, tests, or commits.
```

## Common Failure Modes

Avoid these:

- turning every small task into a heavy artifact
- building from vague agreement without naming the finish state
- making HTML the only truth
- copying the same decision into many docs without naming the source
- leaving Hafiz with options but no recommendation
- asking Hafiz to approve code he has not understood in plain English
- saying "done" when the artifact is only drafted and not approved, checked, or
  connected to implementation

## Recommended Close-Out

End a planning step with:

```text
Status:
Meaning:
Recommended next:
Decision needed:
```

Keep it natural. The goal is that Hafiz knows what just became clearer and what
the agent recommends next.
