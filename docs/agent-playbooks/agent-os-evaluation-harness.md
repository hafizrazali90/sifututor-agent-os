# Agent OS Evaluation Harness

Use this when changing or reviewing the tests that protect Agent OS behavior.

Plain meaning:

```text
This is how we test whether the agents follow the Agent OS, not whether the
Sifututor product works.
```

The harness should protect Hafiz from repeated workflow mistakes:

- the agent says "done" without saying what state is actually true
- the agent commits locally but forgets to say the work is not pushed
- the agent asks Hafiz to verify something it could safely check itself
- the agent treats Koda, Planner, GitHub, git, deploy records, and QA evidence
  as the same kind of truth
- Claude and Codex drift apart for the same workflow
- short replies such as `approve`, `proceed`, and `go next` are interpreted
  without visible context

## Core Rule

Do not add random tests just because a mistake is annoying.

Use this order:

```text
mistake -> expected behavior -> owner -> honest test layer -> runner/check
```

In normal words:

```text
First say what behavior went wrong. Then decide which rule owns it. Then choose
the lightest test that can honestly catch the mistake if it returns.
```

## Harness Layers

| Layer | What it proves | Good for | Not good for |
| --- | --- | --- | --- |
| Markdown eval | The expected behavior is written down. | New rules, scenarios, and teaching examples. | Proving the agent will obey it automatically. |
| Router eval | The prompt selects the right route and required action text. | Commit, push, QA, blocked paths, critical lanes, short commands. | Full natural-language answer quality. |
| Response-shape fixture | The close-out includes useful human information. | What changed, checks, state, remaining risk, next action. | Judging every nuance of tone. |
| State fixture | The wording does not confuse local, pushed, PR, merged, deployed, or live. | Preventing false "done/live" claims. | Proving real GitHub/deploy state. |
| Conversation fixture | Short replies resolve against the prior visible request. | `approve`, `proceed`, `what next`, `go next`. | Long multi-session reasoning. |
| Koda fixture | Memory payloads and stale-memory behavior are safe. | Memory quality and fallback discipline. | Live retrieval relevance by itself. |
| Capability fixture | Tool availability and approval claims stay honest. | Unknown, not connected, blocked, critical, and staff capability states. | Deep live connector behavior. |
| Parity fixture | Claude and Codex wiring does not drift. | Shared playbook and adapter coverage. | Full side-by-side LLM response quality. |
| Health/doctor | The installed Agent OS wiring is present and runnable. | Required docs, scripts, skills, baseline checks. | Whether the workflow design is good. |

## Test Depth

Use three depths.

| Depth | Meaning | Example |
| --- | --- | --- |
| Local fixture | Deterministic and safe to run on every health check. | A close-out without next action fails. |
| Evidence fixture | Needs current repo, GitHub, deploy, Koda, Planner, or logs. | PR open but not merged; deployed but not smoke checked. |
| Human review | Requires judgment, product context, or risk acceptance. | Whether an explanation is too formal for Hafiz. |

Default to local fixtures when the mistake is repeatable without external
systems. Use evidence fixtures only when fake data would teach the wrong lesson.
Keep human review when the answer depends on judgment.

## What To Automate First

Prioritize mistakes that are:

1. repeated in real sessions
2. expensive or frustrating for Hafiz
3. safe to test locally
4. clear enough to fail deterministically

Recommended order for the current Agent OS:

1. **Repo-state wording**: local, committed, pushed, PR open, merged, deployed,
   live smoke passed.
2. **Response shape**: plain-language close-outs with next action and decision
   needed.
3. **Conversation state**: short replies tied to the last exact visible request.
4. **Koda and capability discipline**: memory and tool claims stay honest.
5. **Behavior parity**: Claude and Codex produce the same workflow decision for
   the same prompt.

## What Not To Automate Yet

Avoid premature automation for:

- subjective tone beyond a few clear response-shape checks
- production deploy safety without a safe read-only evidence source
- live connector checks that are flaky or require broad credentials
- full LLM-vs-LLM answer comparison before the shared playbook is stable
- hook changes for behavior that still needs human judgment

Plain meaning:

```text
Do not make the Agent OS stricter than our understanding.
```

## Repo-State Fixture Standard

A repo-state fixture should name:

- the highest proven state
- the evidence that proves that state
- what is explicitly not true yet
- the recommended next action

Examples:

```text
Status: committed locally. Commit abc123 exists on this machine. It is not
pushed, not PR open, not merged, not deployed, and not live smoke checked.
Recommended next: approve push if you want this on GitHub.
```

```text
Status: merged. PR #18 is merged into main. It is not deployed and not live
smoke checked. Recommended next: approve deploy or continue with another local
task.
```

Do not let "done" hide the state. The useful question is not only "did we do
work?" It is "what is true now?"

## Response Fixture Standard

A response fixture should check that a meaningful close-out gives Hafiz:

- what changed
- how it was checked
- current state
- what remains unverified or not applicable
- recommended next action
- whether a decision is needed when the next action crosses a gate

Good:

```text
Committed locally. The governance playbook is saved as 077c204. Checks passed:
health, workflow doctor, eval self-test, and pre-commit guard. This is not
pushed yet, and nothing remains unverified for this docs commit. Recommended
next: approve push if you want GitHub to have it.
```

Bad:

```text
Done. Not pushed.
```

## Maintenance Workflow

When adding or changing a harness case:

1. Add or update `agent-os-evals.md` if the behavior is a named Agent OS
   scenario.
2. Update `agent-os-eval-coverage-map.md` so the case is not a random one-off.
3. Add the local runner case only when the check is deterministic.
4. Add health or workflow-doctor wiring when the runner becomes part of the
   baseline.
5. Run:

```bash
scripts/agent-checks/agent-os-eval-runner.py --self-test
scripts/agent-checks/agent-os-response-shape-runner.py
scripts/agent-checks/agent-os-workflow-example-runner.py
scripts/agent-checks/agent-os-state-fixture-runner.py
scripts/agent-checks/agent-os-health.sh
scripts/agent-checks/workflow-doctor.sh
```

For docs-only harness changes, also run:

```bash
git diff --check
python3 -m json.tool docs/agent-playbooks/agent-os-install-manifest.json >/dev/null
```

Before commit, run:

```bash
scripts/agent-checks/pre-commit-guard.sh
```

## Close-Out Shape

After changing the harness, report:

- which behavior is now better protected
- which runner or doc owns the protection
- which checks passed
- what is still only manual/future harness
- whether the change is local, committed, pushed, or adopted
- the next recommended action
