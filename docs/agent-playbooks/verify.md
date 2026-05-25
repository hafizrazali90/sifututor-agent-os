# Verify Playbook

Use this for Gate 2A, `/verify`, or any request to prove the implementation
works before QA or commit.

## Rules

- Run verification in the project directory, not the umbrella root.
- Use fresh command output from the current session.
- If baseline failures exist before your change, report them separately from
  failures caused by your change.
- A failing verify blocks commit unless the user explicitly changes the scope.

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
- baseline failures: none | listed
- task-caused failures: none | listed

Next:
- <qa/review/blocked action>
```

## Stop Conditions

Stop and report before continuing when:

- required test database or external service is unavailable
- command failure is unrelated but blocks trust in the result
- critical lane verification would require destructive data changes
- financial or mobile API behavior changed and no reviewer has approved it
