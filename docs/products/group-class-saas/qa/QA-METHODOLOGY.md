# Kelasapp QA Methodology + Implementation Plan

> How we produce an exhaustive, human-runnable, E2E-convertible test catalog for Kelasapp,
> and the plan to turn this method into a reusable `qa-plan` skill later. This is the "brain":
> the canonical format, the exhaustiveness engine, the risk model, and the manual->E2E bridge.
>
> Status: applied to Kelasapp first (the per-module catalogs under this folder); the skill is
> formalised afterwards from what works here. Last updated: 2026-07-04 (full catalog revision
> against feat/finish-mvp-polish: Better Auth migration + 43-commit MVP polish re-grounded,
> import module added; see README.md for the revision record).

---

## 1. The goal (what we are testing for)

Kelasapp is heading to ~100 active organisations and ~10,000 users. We need the test asset a
professional QA would build if she understood the whole product: **every flow, every option,
every scenario, every edge case**, written so:

1. A **human** (even non-technical) can run each case top to bottom and get a clear Pass/Fail.
2. A **robot** can run the same list non-stop (the cases convert ~1:1 to Playwright E2E that
   behaves like a human: it navigates, types, clicks, and *looks* at what a human would look at).
3. Coverage is **risk-tiered** so the critical paths (money, auth, tenant isolation) are tested
   first and hardest, and a smoke subset gives a fast go/no-go.

This is bigger than [FLOWS.md](../FLOWS.md): FLOWS is one line per scenario (orientation). This
catalog is one *executable case* per scenario-variant, across the full technique matrix below.

## 2. How professionals do this (research summary)

- **Test-design techniques**, applied per feature, are what make coverage exhaustive instead of
  guesswork: equivalence partitioning + boundary value analysis (inputs), decision tables
  (business logic), state-transition (lifecycles), use-case (flows), error-guessing + negative
  (failure paths). Combine the techniques that fit each field/action.
- **Risk-based prioritisation:** P0/T1 = money, auth, billing, tenant isolation (run every build);
  P1/T2 = important (nightly / pre-release); P2/T3 = nice-to-have (full regression). For
  multi-tenant SaaS, PII / financial / auth / cross-tenant paths are tested first and hardest.
- **Manual -> E2E bridge:** write each case in a structured Given/When/Then-flavoured form, then
  bind it to Playwright with the Page Object Model and stable semantic locators
  (`getByRole`/`getByLabel`), Arrange-Act-Assert, auto-waiting. Playwright MCP lets an agent drive
  the browser via the accessibility tree, i.e. it perceives and acts on what a human sees. The
  structured manual catalog is the single artifact that is both human-runnable and ~80-90%
  auto-convertible.

Sources: test design techniques (aqua-cloud, accelq); risk-based prioritisation (testwheel,
testrigor multi-tenant); manual->Playwright + LLM/BDD bridge (hungdoan, GenTestCase, Playwright MCP).

## 3. What we already have (reuse, do not rebuild)

| Asset | Role we reuse |
|---|---|
| `testcases` skill + `sifu-tutor-1375-tests/docs/manual-qa-standard.md` | The canonical **case format** + self-explanatory quality rules |
| `qa-audit` skill + `qa-framework.md` | The **risk model** (RPN) + US<->Risk<->TC traceability matrix |
| `browser-test` skill | The **human-like Playwright runner** (consumes YAML, `getByRole`, screenshots, self-heal) |

The missing middle this method fills: the **exhaustiveness engine** (walk the technique matrix to
enumerate every case) and the **manual catalog -> `browser-test.yaml` converter**.

## 4. Canonical test-case format (house standard)

Field set from `manual-qa-standard.md §1`; layout from `manual-qa-testcases.md`. Every case:

```
### TC-[MODULE]-[NNN]: [behaviour validated, one line]
**Tags**: @smoke @regression @security @ai-check @data-integrity   (pick applicable)
**Severity**: S1 Critical | **Priority**: P1     (set independently; S1-S4 / P1-P4)
**Tier**: T1 | **Linked**: US-xxx  **Risk**: R-xxx     **Type**: Feature | E2E | API

**Before you start**: exact runnable state (role, credentials, how to FIND data, never a hardcoded id).
**Test Data**: exact values only (RM 100.00, `Ahmad bin Razali`, `920101-14-5567`, `<script>alert(1)</script>`).

| Step | Action |   (one imperative action per row)
|------|--------|
| 1 | ... |

**What you should see**: observable, specific (name the exact banner / message / status / row count).
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked / Skipped
**Notes**: bug id / screenshot / regression provenance (REGRESSION: <bug> + commit SHA)
```

Rules: Severity (impact) and Priority (urgency) are set independently. Test data is exact, never
"a valid X". No hardcoded IDs: tell the tester how to obtain one ("go to X, note the number in the
URL"). Expected results name the exact thing to look for (anti false-pass). Bilingual note where a
string is user-facing (verify EN + BM).

## 5. The exhaustiveness engine (technique matrix)

For **every** action / input field / state in a module, walk this matrix and emit a case wherever a
row applies. This is the checklist that turns a flow into its full set of cases.

| # | Technique | What to enumerate |
|---|---|---|
| 1 | Happy path | The intended success flow, realistic data |
| 2 | Equivalence + boundary | min, max, zero, negative, just-over-max, max-length+1, empty, whitespace |
| 3 | Negative / validation | malformed, wrong type, missing required, and **server-side bypass** (call the API directly with the UI rule violated) |
| 4 | Format / locale | Malaysian IC/passport, phone, RM money (<=2dp), DD/MM/YYYY date; EN + BM strings |
| 5 | Permissions / role | each role (operator / staff / teacher); "control hidden in UI but server must still 403" |
| 6 | Cross-tenant / IDOR | org A's record accessed/edited as org B (URL id, POST body, query) -> not-found, never leak |
| 7 | State transition | every lifecycle edge + illegal transition (e.g. pay a draft, void a void, mark-paid twice) |
| 8 | Concurrency / idempotency | rapid double-submit, re-run generation, double-pay -> exactly one effect |
| 9 | Empty / loading / error states | empty list message, slow/failed load, 404-not-500 |
| 10 | Data integrity | totals reconcile, snapshots frozen, soft-deleted excluded, audit row written |
| 11 | Accessibility (UI) | keyboard reach, labels, focus, contrast (axe/Lighthouse spot) |
| 12 | Security (where input hits render/store/SQL) | XSS payload, SQLi string, path traversal, mass-assignment |
| 13 | Non-functional (opt-in, flagged) | perf SLA, N+1, fan-out at scale |

Not every row applies to every field; applicability is a judgement, but the matrix must be
*walked* and a row only skipped with reason. That is the difference between "wrote some tests" and
"a QA designed the suite".

## 6. Risk model + what runs when

- **RPN = Severity (1-5) x Likelihood (1-5) x Detectability (1-5)**. Tier: RPN >= 36 -> **T1**
  (blocking), 20-35 -> **T2**, < 20 -> **T3**.
- Tag `@smoke` on the thin happy-path-per-module subset (fast go/no-go, runs every build);
  `@regression` on everything (nightly + pre-release); `@security`, `@data-integrity`, `@ai-check`
  (cross-check a claim that could false-pass).
- Kelasapp risk lens: **money** (billing, payments, refunds, teacher pay), **auth/roles**, and
  **tenant isolation** are T1 by default; pure display is T2/T3.

## 7. Manual -> E2E conversion plan (the robot)

Each manual case maps to a `browser-test` YAML case so the runner executes it human-like:

| Manual element | E2E (`browser-test.yaml`) |
|---|---|
| Before you start (role) | `role:` + `setup:` (login as operator/teacher) |
| Step "Go to X" | `NAVIGATE /x` |
| Step "Enter / pick Y" | `FILL`/`SELECT` via `getByLabel`/`getByRole` (never brittle CSS) |
| Step "Click Z" | `CLICK` via `getByRole('button', name: 'Z')` |
| What you should see | `VERIFY` text/role/count + `SCREENSHOT` for visual judgement |
| TC-ID | the e2e case `id` (1:1 traceability manual <-> automated) |

Conversion priority: T1 smoke first (the money/auth/tenant paths), then T1 regression, then T2.
Mobile flows (none in Kelasapp web today) would hand off to Maestro, not Playwright. Playwright MCP
(accessibility-tree driving) is the mechanism that makes "checks what a human checks" literal.

## 8. Kelasapp module + risk inventory (the build list)

Catalog files in this folder, one per area, highest risk first:

| File | Area | Default tier | Why |
|---|---|---|---|
| `test-plan-billing.md` | Invoices, payments, refunds, public page, verification | **T1** | Money + payer + lifecycle |
| `test-plan-teacher-pay.md` | Payroll: generate, mark-paid, void, payslip | **T1** | Money out + immutability |
| `test-plan-auth-tenancy.md` | Sign-in, roles, route/API gating, cross-tenant | **T1** | Auth + isolation across 100 orgs |
| `test-plan-classes.md` | Classes + taxonomy (programs/levels) | T2 | Config; feeds money via fee/rate |
| `test-plan-people.md` | Students, guardians, enrolments | T2 | PII + family links + fee override |
| `test-plan-attendance.md` | Attendance + reports | T2 | Drives pay + alerts; 7-day window |
| `test-plan-teachers.md` | Teacher profiles + detail | T2 | PII (IC, bank) masking |
| `test-plan-import.md` | CSV import wizard + migration hub | T2 | Bulk data entry; enrolment rows can double-bill (T1) |
| `test-plan-dashboard.md` | Operator dashboard | T3 | Aggregations, display |
| `test-plan-crosscutting.md` | Validation, i18n, PII masking, responsive, a11y | mixed | Applies to all forms |

Grounding: every case is reconciled to real behaviour (the service code, the unit/integration
tests: 151 as of 2026-07-04, FLOWS.md, the PRD). A case asserting a behaviour the code does not have is a defect in the case, not a found bug.

## 9. Coverage, traceability, exit criteria

- `README.md` (this folder) holds the **coverage matrix** (module -> case count by tier) and the
  **smoke subset** list.
- Release exit: all **T1 @smoke** pass = deployable to staging; all **T1** pass = production gate;
  T2/T3 tracked, not blocking. New bug found -> add a `REGRESSION:` case (append-only) before the fix.

## 10. Learnings (feeds the future `qa-plan` skill)

- The three existing skills cover format, risk, and execution; the reusable value to add is the
  **technique-matrix walk + the YAML converter**. Keep the skill thin and composing.
- The house format is already excellent and self-explanatory; standardise on
  `manual-qa-standard` fields + `manual-qa-testcases` layout, do not invent a new one.
- Cases must be **grounded in code/tests**, or an agent will hallucinate plausible-but-wrong
  expected results. Always cite the source behaviour (test name / service function).
- Set Severity and Priority independently; testers conflate them otherwise.
- "Expected result" must name the exact observable (banner text, status code, row count), or a
  tester false-passes (the real lesson behind the gate-test convention).

## 11. Future skill blueprint (`qa-plan`, build later)

- **Trigger:** "write a test plan / QA cases / regression suite / E2E coverage for <module>".
- **Inputs:** `[module|route|PRD] [--scope smoke|full] [--emit manual|e2e|both]`.
- **Process:** read+ground the target -> walk the §5 technique matrix -> risk-tier (§6) -> emit
  manual cases in the §4 format -> convert to `browser-test.yaml` (§7) -> update coverage matrix.
- **Outputs:** `docs/.../qa/test-plan-<module>.md` + `.claude/browser-test.yaml` + matrix rows.
- **Composes:** `testcases` (format), `qa-audit` (risk/matrix), `browser-test` (runner). Authored
  per `write-a-skill` (<=100-line SKILL.md + `TECHNIQUE-MATRIX.md` + `FORMAT.md`).
