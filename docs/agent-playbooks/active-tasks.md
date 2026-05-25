# Active Task Review

Last checked: 2026-05-26

## `sifu-tutor`

- Active task: `bugfix-20260524-4023`
- Route: `bugfix`
- Current step: `fix`
- Plane item: `ST-40`
- Scope: fix five E2E failures blocking Phase 3.3 sign-off:
  - `EC-CLS-002`
  - `PM-CLS-005`
  - `AT-027`
  - `TC-FIN-008`
  - `SM-AIR-E03`
- Critical note: includes `financial` test scope, so human review is required
  before commit if the fix touches financial module behavior.
- Next action: continue the `fix` step or explicitly park the task before
  starting unrelated `sifu-tutor` work.

## `sifututor_tutor`

- Active task: `tut-auth-firstrun-rebuild`
- Route: `feature`
- Current step: `generate_tests`
- Branch: `feat/tut-auth-firstrun-rebuild`
- Next action: write failing tests for the auth first-run rebuild before
  implementation continues.

## All Other Projects

No active task at last check:

- `ripple-suite`
- `sifututor_parent`
- `lls`
- `lls-frontend`
- `lls-mobile`
- `creative-hub`
- `team-inbox`
- `finch-inbox`

Run `quick-check.md` commands to refresh this list.
