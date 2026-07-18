# Verify Playbook

Use this for Gate 2A, `/verify`, or any request to prove the implementation
works before QA or commit.

Use [agent-os-evidence-model.md](agent-os-evidence-model.md) as the source of
truth for the agent-as-tester rule: the agent should gather the same practical
evidence a capable human tester would gather before asking Hafiz to verify what
only he can judge.

Use the Evidence By Work Type matrix in
[agent-os-evidence-model.md](agent-os-evidence-model.md) before reporting that
work is ready. Plain meaning: "ready" must name the evidence level reached, such
as docs evidence, backend evidence, UI evidence, deploy evidence, or live-check
evidence. Do not say ready without saying ready for what.

Use the Proof Standard in
[agent-os-evidence-model.md](agent-os-evidence-model.md) when summarizing
verification. Plain meaning: say whether you have code proof, journey proof,
release proof, or only part of that stack. Always name the highest proven state
instead of saying "done" generically.

Use the Evidence Gap Stop Rules in
[agent-os-evidence-model.md](agent-os-evidence-model.md) when expected proof is
missing. Plain meaning: missing proof must be reported as a named gap, not
hidden inside "ready" or pushed onto Hafiz as a vague manual check.

Use [related-impact-audit.md](related-impact-audit.md) for bugfix, hotfix, and
user-facing small-change verification. Plain meaning: proving the exact fix is
not enough if the same root-cause pattern or adjacent regression risk is obvious
and unchecked.

## Rules

- Run verification in the project directory, not the umbrella root.
- Use fresh command output from the current session.
- If the project has `TESTING.md`, identify the affected feature row and run
  the manifest check from [test-coverage.md](test-coverage.md) when the shared
  script is available.
- If baseline failures exist before your change, report them separately from
  failures caused by your change.
- A failing verify blocks commit unless the user explicitly changes the scope.
- For critical-lane or AI-handoff work, use
  [ai-implementation-readiness.md](ai-implementation-readiness.md) as an
  additional acceptance lens. Green tests are not enough when the tests prove a
  weaker behavior than the PRD/build prompt required.
- Do not delegate verification that the agent can safely perform. For UI-visible
  changes, use Playwright or an equivalent browser smoke before asking for human
  QA. For deployed changes, prove the changed behavior against the deployed
  environment when safe credentials and representative data are available.
- Before counting browser, screenshot, staging, or production evidence, prove
  the checked target identity. For local UI work, name the URL, serving process,
  worktree/checkout, branch, commit or local-dirty state, and restart/rebuild
  state. For deployed work, confirm the deployed SHA/version. A stale port or
  wrong checkout cannot prove the intended implementation.
- For `sifu-tutor` UI-visible changes, verify against
  `sifu-tutor/docs/ui-ux/quality-gate.md` in addition to tests. Report which
  SIMS UI/UX docs were followed when the work changes page layout, components,
  visual styling, staff-facing copy, or browser interaction.
- Verification for `sifu-tutor` UI-visible work is not commit-ready until the
  later QA/review evidence includes screenshot-backed UI/UX checks or an
  explicit blocker. Machine checks alone prove the code compiles; they do not
  prove the page matches the SIMS UI system.
- Verification should prove both the machine part and the human journey when a
  real user depends on the behavior. Unit/API tests prove the engine; browser,
  mobile, API smoke, screenshots, or read-only state checks prove the workflow
  behaves like a user would experience it.
- For user-facing feature, bugfix, hotfix, or small-change work, verify is not
  complete until the permanent E2E regression decision is recorded: added,
  updated, or not feasible with a concrete blocker and follow-up.
- For bugfix/hotfix work, verify must state the related-impact audit strength
  used, what was checked, and whether any related finding was fixed, excluded,
  or needs Hafiz's decision.
- For any staff/admin/parent/tutor/student/customer workflow, the expected
  outcome is a permanent E2E test file, not only an E2E "decision". Treat
  missing E2E as a verify failure unless the exact workflow is not safely
  automatable and the exception is explicitly documented.
- When verification cannot reach the evidence level required for the next
  state, say the highest state actually proven. Example: "backend verified,
  UI workflow still unproven" instead of "ready".
- Verification is not a release claim. Passing local tests does not prove a PR
  is merged, a deploy happened, or production users can complete the changed
  workflow.

## Project Command Matrix

| Project | Minimum verify commands |
| --- | --- |
| `sifu-tutor` | `./vendor/bin/pest`, `npm run build`; add `npx playwright test --grep @smoke` for bugfix/hotfix or UI work |
| `ripple-suite` | `npx tsc --noEmit`, `npx @biomejs/biome ci .`, `npx playwright test --grep @smoke` |
| `sifututor_tutor` | `npm run lint`, `npm run typecheck`, `npm test` |
| `sifututor_parent` | project `AGENTS.md`/`CLAUDE.md` commands; at minimum lint, typecheck, and tests |
| `lls` | `composer validate --strict`, `php artisan test`; if API contracts changed, also verify `lls-frontend` |
| `lls-frontend` | project lint/build/test commands; check paired `lls` API contracts when RTK Query or generated types change |

When project-specific `CODEX-WORKFLOW.md` or `CLAUDE.md` gives stricter
commands, use the stricter command set.

## Evidence Report

Report in this shape:

```text
VERIFY - PASS | FAIL | PARTIAL

Commands:
- <command>: <pass/fail, key counts or exact failure>

Gate 2A:
- implementation works: yes/no/partial
- highest proven state: <changed locally | committed locally | ready for commit | ready for PR | deployed to staging | deployed to production | live checked | accepted / closed>
- proof layers reached: <code proof | journey proof | release proof>
- target identity: <URL/environment, process, worktree/branch, commit/version, restart/rebuild>
- TESTING.md row checked: yes/no/not applicable
- permanent E2E regression: added/updated/not feasible/not user-facing
- changed user workflows and their permanent E2E files: <list or explicit exception>
- related impact: <local related check | same-pattern sweep | critical impact audit; checked/found/fixed/follow-up>
- SIMS UI/UX docs checked: <paths or not applicable>
- baseline failures: none | listed
- task-caused failures: none | listed
- readiness gaps: none | listed, especially where tests prove a weaker behavior
  than the acceptance rule

Next:
- <qa/review/blocked action>
```

## Stop Conditions

Stop and report before continuing when:

- required test database or external service is unavailable
- command failure is unrelated but blocks trust in the result
- critical lane verification would require destructive data changes
- financial or mobile API behavior changed and no reviewer has approved it
- the only remaining check needs human judgment/sign-off; include the agent-run
  evidence already completed and the exact reason the rest cannot be automated
- a required evidence gap would make the next state misleading, such as saying
  ready for commit, PR, deploy, or live-check without the proof required by the
  work type
