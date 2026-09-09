# Tutor App Mission Ledger

Use this for tutor mobile app missions, child tasks, adjacent ideas, and paused
follow-ups.

## Missions

### STT-AUTH-001 — Tutor auth first-run rebuild

- **Project:** sifututor_tutor
- **Status:** paused
- **Type:** mission
- **Parent:** none
- **End goal:** Complete and verify the tutor app first-run/auth rebuild before it becomes part of a mobile release.
- **Why it matters:** The Phase 4 mobile QA task was closed out, but its task state still referenced this auth rebuild as paused; keeping it in the ledger makes the remaining release-readiness work visible.
- **Source:** `.claude/tasks/phase4-mobile-qa-sims-update-1.json`, 2026-05-28 Phase 4 QA closeout
- **Next action:** Decide whether the auth rebuild should resume now, become a GitHub issue, or stay paused until the next tutor app release cycle.
- **Promote to:** GitHub issue
- **Links:** none

### STT-QA-001 — Review old Phase 4 Maestro suite after tutor app E2E restructure

- **Project:** sifututor_tutor
- **Status:** triaged
- **Type:** task
- **Parent:** STT-AUTH-001
- **End goal:** Decide whether the Phase 4 Maestro improvements in `.workflow-rollout/sifututor_tutor/e2e/maestro/` should be ported into the current E2E structure, or explicitly retired.
- **Why it matters:** The real `sifututor_tutor/e2e/maestro/` was restructured after the rollout clone was made (May 28). The rollout has 4 unported changes — `ensure-logged-out.yaml` and `t14-logout.yaml` (new helpers) plus hardened selectors in `t1-session-persist.yaml` and `t7-payment.yaml` — that have not been evaluated against the new structure (`class-schedule.yaml`, `home.yaml`, `login.yaml`). Until this is resolved, `.workflow-rollout/sifututor_tutor` must not be deleted.
- **Source:** Agent OS housekeeping session, 2026-06-12
- **Next action:** Compare the 4 changed rollout files against the current `class-schedule.yaml`, `home.yaml`, `login.yaml` and determine coverage overlap. Port any missing coverage, then delete the rollout dir.
- **Promote to:** GitHub issue if porting requires significant work
- **Links:** `.workflow-rollout/sifututor_tutor/e2e/maestro/`

### STT-NAK-001 — Nakngaji unified flow: release phase and blocked proofs

- **Project:** sifututor_tutor
- **Status:** triaged
- **Type:** mission
- **Parent:** none
- **End goal:** PR #61 (unified Nakngaji/Sifututor flow) independently reviewed by Codex, then merged and released with Hafiz's approval.
- **Why it matters:** The build phase is complete and cross-platform verified (02/09/2026), but two proofs stay blocked outside the branch: real-backend smoke needs the staging Nakngaji flags on plus sifu-tutor #2389 fixed, and the Android external assessment handoff needs go.nakngaji.my to resolve.
- **Source:** Nakngaji unification session, 02/09/2026
- **Next action:** Codex independent review of b3d0537..a82b6a5 against docs/features/nakngaji-unified-flow-handoff.md, then fix sifu-tutor #2389.
- **Promote to:** stays on GitHub (PR #61 + sifu-tutor #2389)
- **Links:** sifututor_tutor PR #61, sifu-tutor issue #2389, docs/features/nakngaji-unified-flow-handoff.md

### STT-DESIGN-002 — Distance/proximity on in-person job cards (parked)

- **Project:** sifututor_tutor (+ sifu-tutor backend)
- **Status:** paused
- **Type:** adjacent
- **Parent:** STT-DESIGN-001
- **End goal:** Tutors see how far an in-person job is before opening it, without exposing a family's exact home location.
- **Why it matters:** Travel drives whether a tutor takes an in-person job; today the card shows only area/city, costing wasted taps and mismatched applications. Raised 03/09/2026 during the component walkthrough; Hafiz asked to keep it in the pipeline rather than build it now.
- **What already exists:** latitude/longitude on `tutor_request_addresses` AND on the tutor profile; another payload in `TutorRequestService` already exposes request coordinates.
- **Open decisions:** privacy (coarse band like "about 8 km" vs exact; round coordinates server-side), straight-line vs routing distance (maps API cost), server-side vs client-side computation, graceful fallback when coordinates are null, and whether "nearest first" sorting follows.
- **Source:** Tutor app design program R1 planning, 03/09/2026
- **Next action:** Product decision with Hafiz on privacy + precision, then size the backend work.
- **Promote to:** GitHub issue exists: sifu-tutor #2406
- **Links:** sifu-tutor issue #2406, design/specs/request-card.md (location MetaRow)

### STT-DESIGN-001 — Tutor app design program (theme, design system, UX revamp)

- **Project:** sifututor_tutor
- **Status:** active
- **Type:** mission
- **Parent:** none
- **End goal:** The signed 2026 refresh executed: design system built (R0 components), then screens migrated phase by phase (Jobs, Home, tracker order), Nakngaji included, everything gate-checked, Codex final review at the very end.
- **Why it matters:** Hafiz explicitly separated structural work from design work on 02/09/2026; the full design conversation then happened the same day and is COMPLETE.
- **Source:** Design program sessions, 02/09/2026
- **Progress 02/09/2026:** Design discussion DONE end to end: component inventory + verified visual catalog, batch keep/kill/migrate decisions, avoid-list research, all SIX foundations decided one by one by Hafiz (Inter deliberately treated; 7-role type scale; SOFT shape set; 4pt spacing + 6 slots density-preserving; color system one-family-per-meaning + neutral ramp + gradient ban; elevation flat + one floating shadow). Design contract SIGNED (artifact e8585ac9). Agent-facing docs generated mechanically on branch feat/refresh-2026 (commit eb4ef07): design/DESIGN.md, design/components.md registry, 13 specs, CLAUDE.md UI CONTRACT, ESLint contract enforcement (verified firing).
- **Progress 03/09/2026:** R0 BUILT and fully approved component by component. Tokens carry all six foundations; app migrated to Inter (found + fixed: iOS never actually bundled the old font); 16 components built or restyled with 2,466 tests green. Every piece walked through with Hafiz one at a time and approved: job card (commission hero + info sheet, brand tiles, TREQ ids, middots), EarningsSummary, Field/DateTimeTriggerRow, Select + BottomSheet header, Buttons, Toast (quiet success, loud failure), ConfirmDialog (facts box + consequences callout), SuccessScreen (Shop-style summary, no scroll, optically matched wordmarks). Governance added: design/review-checklist.md (agent QAs, owner approves), design/asset-sources.md (reference-only libraries; we generate our own with fal.ai), brand assets (official marks, wordmarks, app icons).
- **Next action:** Phase R1 walkthrough for Hafiz's go: wire the approved components into the real Jobs screens (open + applied), then Home. Codex only at program end.
- **Promote to:** GitHub issue(s) at build start
- **Links:** sifututor_tutor design/DESIGN.md + design/components.md; docs/design-system/refresh-2026/direction.md (all decisions); branch feat/refresh-2026 stacked on PR #61
