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
