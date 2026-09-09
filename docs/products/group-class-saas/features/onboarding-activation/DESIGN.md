# Kelasapp Onboarding & Activation: Design & Build Plan

> **Status:** Discussed and locked with Hafiz, 2026-07-05 (chat-based product discussion, decision-by-decision). Not yet implemented.
> **Scope owner:** this doc is the "how we build onboarding/activation" reference. Module 8 in `PRD.md` is the "what". The live schema in `kelas/src/models/Schema.ts` is the source of truth for tables (none new are added by this feature).
> **Decision protocol:** every choice below was decided one at a time (plain options, how reputable SaaS do it, recommendation, Hafiz decides), same protocol as `features/m4-billing/DESIGN.md`.
> **Correction, 2026-07-05 (found during implementation start):** the dashboard checklist and dismissible banner described below were designed in this discussion without checking the codebase first. A getting-started checklist already shipped on 2026-07-02/07-03 (`src/features/onboarding/service.ts` + `GettingStartedChecklist.tsx`, commits `9a397ce`/`63c3365`/`8da4c9e`, tagged CX12/CX16), already wired into `(operator)/page.tsx`, already tested, already bilingual. It uses 6 steps (payment, teacher, class, enrol, attendance, invoice), not the 4-step path below, and its dismiss mechanism (localStorage) already covers what Decision 5's "welcome banner" was meant to do. That existing implementation stays as-is. The only part of this design still being built is the **contextual spotlight tour** (Decisions 4 and 5's tour half), which genuinely does not exist yet. Sections below are kept for the tour's rationale; the checklist/banner portions are historical record of the (redundant) original plan, not a build item.

---

## 1. Locked decisions

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | Target audience | **Org admin/owner only, for now** | Slack/Notion pattern: the workspace creator is the one deciding whether the org keeps using the product; every golden-path step is an admin action anyway. Teacher/guardian onboarding is a separate, later decision. |
| 2 | Golden path | **Org setup → first class + teacher → first student/guardian → first invoice** (4 steps) | Matches Kelasapp's real route dependencies (`organization-profile`, `setup/levels`+`setup/programs`, `classes`, `teachers`, `students`, `guardians`, `billing`). Ends at the "money moment" (first invoice sent). Capped at 4 steps per current onboarding UX guidance (4-5 step ceiling before a checklist starts reading as nagging). |
| 3 | Content architecture | **Tooltip + checklist copy live together in one small structured config per step** (id, title, one-line tooltip copy, short "why", target element selector, i18n keys). **The longer guide is a separate linked document.** | Tour libraries expect a `{target, short title, short description}` shape natively; that's forced, not a free choice. Keeps the UI-critical strings small and easy to keep in lockstep with real DOM elements; guide content is free to be genuinely descriptive (numbered steps + screenshots) without bloating the tour config. |
| 4 | Onboarding library + checklist state | **Onborda + Framer Motion** for the spotlight/tour UI. **Checklist state derived live from real data** (does this org have ≥1 class / ≥1 student / ≥1 invoice); **no new DB table.** | Onborda is purpose-built for Next.js App Router and gives smoother, more polished animation out of the box than driver.js/Shepherd.js (which are functional but plain by default). Bundle-size cost matters far less here than it would on a public marketing page, since this only loads inside the authenticated dashboard. Derived checklist state can never drift from reality (e.g. a deleted class un-checks the box automatically) and needs no new schema to build or maintain. |
| 5 | Trigger / placement | **Light first-login welcome banner** pointing at a **checklist widget on the operator dashboard home** (`(operator)/page.tsx`), plus **contextual spotlight tooltips fired per-page by actual behavior** (e.g. land on Classes with zero classes → tooltip on "Add class"). **Not** a forced full-screen linear tour. | Current onboarding UX guidance: contextual-at-the-moment-of-need beats a forced linear walkthrough. A checklist/guide parked only behind a nav link mostly behaves like support deflection (only reached if someone goes looking); activation needs it to proactively reach the user instead. |
| 6 | Analytics / heatmaps | **Deferred: no PostHog or Microsoft Clarity for now.** | Hafiz's call. Means no drop-off/completion data on the golden path until this is turned back on. Worth remembering when judging whether onboarding "worked." |
| 7 | LLM content maintenance workflow | **Gate scoped narrowly to golden-path routes only** (org profile, levels/programs, classes, teachers, students, guardians, billing/invoicing). Any change touching those routes triggers a drafted content update (tooltip/checklist/guide); **Hafiz reviews and approves before merge; nothing is ever auto-published.** | Mirrors the pattern every mature implementation converges on (Intercom Fin Operator, Zendesk auto-assist, Mintlify docs-on-autopilot): AI proposes, human approves, always. Scoped narrowly so it's a targeted check, not a blanket "review docs" tax on every commit. No new enforcement tooling/hooks; stays a convention, since Kelasapp doesn't currently have a formal release-notes gate the way Ripple/sifu-tutor do. |
| 8 | Full Help Center (DB-backed search/taxonomy/editorial CMS) | **Stays deferred.** Re-evaluate when Hafiz notices he's **repeatedly answering the same non-golden-path question**, or once **meaningfully past public launch with real active orgs**, whichever comes first. | Signal-based rather than date/number-based, because analytics is off (Decision 6) so there's no dashboard metric to watch. The qualitative signal (repeating yourself on support) is one a solo founder doing his own support will actually notice. |

---

## 2. Background

Kelasapp's only help surface today is a single static FAQ page (`kelas/src/app/[locale]/(auth)/dashboard/help/page.tsx`): contact email, a flat Q&A accordion, legal links. That's a support-deflection tool, it helps someone who's already stuck and already knows to look for help.

This design covers a different, additional job: **activation**, getting a newly registered org admin, who gets no personal walkthrough from Hafiz, from "just registered" to "actually using the product." Two framing decisions came out of the discussion that shape everything below:

1. **Activation content is sequenced and proactive** (a golden path shown to the user), not a searchable reference library the user has to go find.
2. **Content quality is a hard constraint, not a nice-to-have**: every piece of copy at every depth is capped short; nothing here should ever read as a wall of text.

A full Ripple-Suite-style Help Center (DB-backed articles, real search, editorial pipeline, feedback capture; see `ripple-suite/docs/features/help/help-prd.md` for what that actually involves) was considered and explicitly deferred (Decision 8): it's a support-deflection tool for a taxonomy Kelasapp doesn't have real usage data for yet, and it doesn't solve the activation problem this design targets.

---

## 3. Scope

**Already shipped, no build needed (found 2026-07-05):**
- Dashboard checklist widget on `(operator)/page.tsx`, `GettingStartedChecklist.tsx`, state derived live via `getOnboardingProgress()`, no new table
- Dismissible banner behavior (the checklist card itself, localStorage-backed)
- EN + BM copy for the checklist (`Onboarding` namespace in `src/locales/en.json`/`ms.json`)

**In scope, build now:**
- Onborda-based spotlight tour wired to real DOM elements on Classes/Teachers/Students/Guardians/Billing, triggered by the org's actual state (e.g. zero classes)
- Tooltip copy at the one-sentence depth (separate from the existing checklist copy, which stays as-is)

**Deferred (not part of this build):**
- Existing `/dashboard/help` FAQ page reframed as task-based: a separate decision from the earlier part of this discussion
- Full DB-backed Help Center (search, taxonomy, editorial CMS, feedback, analytics): per Decision 8's trigger
- PostHog / Clarity: per Decision 6, revisit whenever drop-off data is wanted
- Teacher- and guardian-specific onboarding: Decision 1, a separate later decision
- Any enforcement tooling (hooks/gates) for the LLM content workflow beyond a manual convention: per Decision 7, only build if the convention proves insufficient in practice

---

## 4. The golden path, step by step

Superseded by the real, shipped checklist. The tour hooks onto the **existing 6 steps** (`src/features/onboarding/GettingStartedChecklist.tsx`'s `STEPS` array), not the 4-step path originally imagined here:

| Existing step key | Route it links to | "Done" check (already implemented) | Tour tooltip needed? |
|---|---|---|---|
| `setup` (payment) | `billing/settings` | `orgSettings` has bank details or a DuitNow QR | Yes: spotlight on the payment method field |
| `teacher` | `teachers/new` | `teachers` table has ≥1 row | Yes: spotlight on "Add teacher" |
| `class` | `classes/new` | `classes` table has ≥1 row | Yes: spotlight on "Add class" |
| `enroll` | `classes/[id]` (first class) | `enrollments` table has ≥1 row | Yes: spotlight on the enrol action inside a class |
| `attendance` | `dashboard/attendance` | `attendanceRecords` table has ≥1 row | Optional: lower priority, daily habit not one-time setup |
| `invoice` | `dashboard/billing` | `invoices` table has ≥1 non-draft row | Yes: spotlight on "Run billing" / send action |

The original 4-step table (org setup, class+teacher, student, invoice) is kept below for historical reference only; it does not match what's live and should not be built against.

<details>
<summary>Original 4-step table (superseded, kept for record)</summary>

| Step | Triggered on | Anchors to (route) | Checklist "done" check | Notes |
|---|---|---|---|---|
| 1. Set up your center | First login | `organization-profile`, `setup/levels`, `setup/programs` | Required org profile fields filled | **Confirmed 2026-07-05** (live browser check): `levels`/`programs` are optional on the New Class form ("No programs yet" / "No levels yet", class still saves). Not a hard prerequisite. |
| 2. Add your first class + teacher | After step 1 | `classes/new`, `teachers/new` | `classes` table has ≥1 row for this org | Merges two entities (class, teacher) into one checklist item since they're typically created together. |
| 3. Enrol your first student | After step 2 | `students/new`, `guardians/new` | `students` (or enrolments) table has ≥1 row for this org | **Unverified:** whether student creation requires a guardian to exist first, or either order works. Needs confirming against actual code. |
| 4. Send your first invoice | After step 3 | `billing` | `billing`/invoices table has ≥1 row for this org | The activation "aha moment": the tool visibly doing the thing it's for (getting the center paid). |

</details>

---

## 5. Content depths, worked example (illustrative copy, not final)

Using Step 2 as the concrete example so whoever picks this up has a template to match, not just an abstract spec:

- **Tooltip** (fires on the Classes page when the org has zero classes): *"Add your first class here."* One sentence, one action, anchored to the "Add class" button.
- **Checklist item**: *"Add a class, so you can assign a teacher and start enrolling students."* Label plus one short "why" clause.
- **Guide page section**: 3-4 numbered steps ("1. Go to Classes → New Class. 2. Fill in name, schedule, fee. 3. Assign a teacher. 4. Save.") with one screenshot per step, no prose paragraphs.
- **Full reference article** (deferred, would only exist if the Full Help Center is ever built): the only place dense edge-case detail belongs, e.g. every field's validation rules, bulk import via CSV, archiving a class. Not needed for this design.

All copy exists as `next-intl` translation keys (EN + BM), matching Decision 3.

---

## 6. LLM content maintenance workflow (Decision 7, detailed)

1. **Trigger**: a task/change touches one of the golden-path routes (`organization-profile`, `setup/levels`, `setup/programs`, `classes`, `teachers`, `students`, `guardians`, `billing`/`settings/invoicing`).
2. **Draft**: the same session that makes the change drafts the affected tooltip/checklist/guide content update.
3. **Readiness check before requesting approval**: does the draft match the *current* UI; is EN/BM parity intact; does it stay within the depth caps from Section 5; does it avoid promising anything not actually built yet.
4. **Gate**: Hafiz reviews and approves. **Never auto-published or auto-merged.**
5. No new hooks/enforcement tooling for this now; it's a convention applied at the point of change, not a blocking CI check. Revisit only if content visibly drifts despite the convention.

---

## 7. Open items for the build phase

These are deliberately not decided here, they're implementation-time questions, not product-scope questions:

- Exact tooltip anchor selectors (may need `data-testid` additions on target elements in Classes/Teachers/Students/Guardians/Billing pages)
- Final copy for every tooltip, checklist label, and guide step (drafted then reviewed per Decision 7, once build starts)
- Confirm whether `levels`/`programs` gate class creation (Step 1 note above)
- Confirm student-vs-guardian creation order dependency (Step 3 note above)
- Screenshot capture/maintenance approach for the guide pages
