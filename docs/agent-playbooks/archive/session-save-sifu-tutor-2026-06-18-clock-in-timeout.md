# Session Save — sifu-tutor clock-in notification timeout

- **Date:** 2026-06-18
- **Project:** sifu-tutor
- **Save level:** Critical Save
- **Reason:** Mobile API behavior, production permission repair, migration, deploy, smoke, and monitoring.

## What Happened

- Planner issue `TREQ-739898` reported tutors seeing "Server is taking too long to respond" during clock-in.
- Root cause was confirmed in `ClassService::addClassAttendance()`: attendance was saved first, then Pusher/realtime notification failures were re-thrown as API errors.
- PR `Sifututor/sifu-tutor#1602` was updated, reviewed, merged, and deployed.
- Production permission preflight initially failed because `classes.list`, `classes.view`, and `classes.export` were missing from production permissions. They were repaired with a targeted production update for `Admin` and `Super Admin`; no broad seeder was run.

## Durable Lesson

Attendance persistence must not depend on realtime notification delivery. For tutor clock-in/out, Pusher/push failures should be logged as non-fatal warnings after the class state is saved. Regression tests should simulate broadcast failure and assert the API still returns `responseCode = 100` and persists `clock_in` / status.

## Evidence

- PR `#1602` merged at `6103fb7c1`.
- Regression test file: `tests/Feature/Regression/ClockInNotificationTimeoutRegressionTest.php`.
- Focused tests passed:
  - `php artisan test tests/Feature/Regression/ClockInNotificationTimeoutRegressionTest.php`
  - `php artisan test tests/Feature/Class/AttendanceTest.php`
  - `php artisan test tests/Feature/Security/ApiAuthTest.php --filter='attendance|class attendance|class_attendance|class/attendance'`
- Production backup completed before deploy.
- Production deploy steps completed: pull, Composer install, npm install, build, migration, optimize, queue restart.
- Migration completed: `2026_06_18_000001_backfill_tutor_consents`.
- Public smoke passed:
  - `/login` returned `200`
  - `/` returned `302`
  - `/api/tutor/class/attendance` without token returned API envelope `responseCode = 101`
- Authenticated production smoke passed across 9 routes after one transient `/user/role` retry.
- Post-deploy log scan after the deploy window found no new production error or critical entries.
- Production route permission preflight passed after targeted repair: 157 route permissions checked.

## Current Production State

- Current production `main` head at save time: `696cb0704`.
- `origin/main` also points to `696cb0704`.
- `696cb0704` is a later merge commit after `#1602` (`Merge pull request #1609 from Sifututor/fix/fiuu-ordering-guard`).
- No pending migrations at save time.
- Production tracked working tree is clean.
- Production still has 5 pre-existing untracked backup artifacts, including `.env` and `.htaccess` backup files. They were not read or modified.
- `failed_jobs` remained at `56`; latest failed job timestamp stayed `2026-06-18 10:13:21`.

## Remaining Work

- Monitor tutor/staff feedback for clock-in/out behavior after PR `#1602`.
- Handle production failed notification jobs via the existing queue hygiene follow-up; do not retry/delete blindly.
- Separately clean production untracked backup artifacts with an approved housekeeping task.
- Separately investigate the npm audit high-severity warning.

## Koda Status

Koda health check passed, but Koda memory search/store timed out during save-session. This file is the fallback save note.
