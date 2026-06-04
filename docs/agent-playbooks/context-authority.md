# Context Authority

Use this playbook when an agent needs to decide whether context is accurate
enough to act on.

The Agent OS must not trust context just because it exists. Every important
claim needs a source, freshness check, confidence level, and owner.

## Core Rule

Before acting on important context, identify:

1. Where did this context come from?
2. Is it current?
3. Who owns this truth?
4. Was it verified against code, docs, tests, logs, or official sources?
5. What confidence level applies?
6. What should happen if sources conflict?

If sources conflict, stop and report the conflict before editing.

In practical terms:

```text
Current verified evidence beats old memory.
Approved rules beat agent assumptions.
Reported symptoms must be investigated before code changes.
Hafiz owns business/product truth.
Code, tests, logs, and runtime evidence prove technical truth.
```

## Context Authority Ladder

Use this ladder when deciding what to trust first.

| Rank | Authority | Practical Meaning |
| --- | --- | --- |
| 1 | Forbidden boundaries | `.env*`, secrets, `live/`, destructive git history changes, and hook bypasses are not normal context decisions; they are safety boundaries. |
| 2 | Hafiz decision | Hafiz owns product direction, business rules, risk tolerance, and scope changes. |
| 3 | Current verified evidence | Current code, tests, logs, command output, screenshots, browser evidence, and production-safe evidence prove what is happening now. |
| 4 | Approved docs | `AGENTS.md`, project `AGENTS.md`, `CLAUDE.md`, and playbooks define workflow rules. |
| 5 | Task systems | GitHub issues, Plane cards, Planner cards, and active task files show work state and intake context. Cross-check when they disagree. |
| 6 | Memory and history | Koda, handoffs, snapshots, commit notes, and prior chat are useful leads, but must be checked against current state. |
| 7 | Agent assumption | Weakest source. Verify it or label it clearly. |

This ladder does not mean code always beats Hafiz. Code proves current
behavior; Hafiz can define the desired behavior. When those differ, call it a
change request or business-rule change instead of pretending it is already true.

## Confidence Levels

| Level | Meaning | Agent behavior |
| --- | --- | --- |
| `verified` | Checked against current source code, docs, command output, runtime evidence, or official sources. | Safe to act, subject to normal risk gates. |
| `trusted` | Comes from approved docs, `AGENTS.md`, `CLAUDE.md`, GitHub, Plane, active task state, or Koda, but was not rechecked yet. | Use for low-risk work; verify before high-risk work. |
| `reported` | Comes from Hafiz, staff, support, Planner, customer report, or a screenshot. | Treat as symptom or requirement; investigate before code changes. |
| `historical` | Comes from old Koda memories, handoffs, snapshots, commit notes, or prior chat summaries. | Useful lead only; check current files before relying. |
| `unverified` | Model assumption, unclear source, stale internet claim, or unsourced statement. | Do not present as fact; verify or label clearly. |

## Source Of Truth Map

| Context type | Source of truth | Accuracy owner |
| --- | --- | --- |
| Product/business rule | Hafiz, approved PRD, approved business docs | Hafiz |
| Current code behavior | source code, tests, runtime evidence | agent verifies; Hafiz/product confirms user impact when needed |
| Workflow rule | `AGENTS.md`, project `AGENTS.md`, playbooks | Hafiz approves; agents follow |
| Past lesson | Koda, save-session, handoff, snapshot, commit note | agent verifies against current state before relying |
| Staff-reported issue | Planner/support report, screenshot, reproduction steps | staff reports symptom; agent verifies cause |
| Engineering task state | GitHub issue, Plane, active task file | task source plus agent cross-check |
| Production truth | logs, monitoring, production-safe evidence | production evidence; Hafiz approves risky action |
| Test truth | command output, CI, screenshots, QA evidence | evidence determines result |
| External best practice | official docs, reputable primary sources | source quality and current date |

## Promotion Rules

Important context should move upward before action:

- `reported` -> `verified` by reproducing, checking code, logs, or tests.
- `historical` -> `verified` by checking current files or current tooling.
- `trusted` -> `verified` when the work is high-risk or user-facing.
- `unverified` -> `trusted` or `verified` only after source lookup.

## Conflict Rules

Stop and report the conflict when:

- user brief, `AGENTS.md`, and `CLAUDE.md` disagree
- Koda memory disagrees with current repo files
- active task state disagrees with GitHub or Plane
- staff report disagrees with reproduction evidence
- documentation disagrees with code behavior
- external source disagrees with official docs

Report:

```text
I found conflicting context:
- Source A says: ...
- Source B says: ...
- Practical meaning: ...
- Recommended resolution: ...
```

Do not silently choose the convenient source.

## Task Start Checklist

For non-trivial work, classify the important context before editing:

- What is the user asking for?
- Which project is active?
- What files/docs/memories/task states matter?
- Which claims are verified versus historical or reported?
- Does any high-risk lane require stricter verification?

## Examples

### Staff Report

Planner says a staff member cannot assign a tutor.

Classification: `reported`.

Agent action: treat the report as a symptom. Reproduce or inspect browser
behavior, network calls, permissions, and current code before changing
anything.

Truth ownership:

- staff owns the symptom
- current evidence owns the technical cause
- Hafiz owns whether the intended behavior should change

### Koda Memory

Koda says a workaround was accepted last month.

Classification: `historical`.

Agent action: check current code/docs before relying. If still true, promote to
`verified`.

If Hafiz gives a newer instruction that changes the old decision, treat Koda as
history and Hafiz's current decision as the target direction.

### Old Chat Says Done

A prior chat or compacted summary says a task is complete, but `git status`
shows dirty files or tests are failing.

Classification: prior chat is `historical`; current repo/test output is
`verified`.

Agent action: explain that the work may have been attempted, but it is not
safely complete yet. Use current repo state and checks before reporting done.

### Staff Bug Report

Planner says a staff member cannot open a modal.

Classification: `reported`.

Agent action: reproduce or inspect current code before changing anything.

### `AGENTS.md` Rule

Root `AGENTS.md` says never modify `live/`.

Classification: `trusted`; effectively mandatory. It does not need routine
verification, but if another file says to edit `live/`, report the conflict.

If Hafiz asks to cross a forbidden boundary, propose a safe alternative instead
of reading secrets or modifying protected paths.

### Hafiz Changes A Business Rule

Current code pays a tutor commission at 70%. Hafiz says it should now be 75%.

Classification: code is `verified` for current behavior; Hafiz's instruction is
the desired product/business target.

Agent action: explain that this is a business-rule change, not merely a bug.
Because commissions are critical-lane work, diagnose impact first and ask for
implementation approval before editing.

### GitHub And Plane Disagree

GitHub issue says "fix login validation message." Plane says "improve full
login and onboarding experience."

Classification: both are `trusted` task context, but their scope conflicts.

Agent action: keep the implementation scoped to the GitHub issue unless Hafiz
approves expanding scope. Report the mismatch in plain language.

### Official Docs

A tool behavior changed recently.

Classification: `unverified` until checked against official docs or current
tool output.

Agent action: browse or inspect the local tool before making the rule.

External blogs or examples are useful for options, but official docs and the
current repo architecture are stronger sources for implementation decisions.

## Close-Out

When context accuracy mattered, include:

- which context was verified
- which context remains reported, historical, or unverified
- what source of truth was used
- whether any conflict remains

Good close-out:

```text
I treated the Planner note as a reported symptom, then verified the current
behavior in the browser. The issue is in the frontend filter, not the backend
assignment API. The next best step is to add a regression test and patch the
filter.
```
