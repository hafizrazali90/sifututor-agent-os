# Session Save: Tutor Students Missing

Date: 2026-06-04

## Summary

Backend fix for the tutor app missing-students issue was merged, deployed to
production, and backported to staging. The remaining work is the separate tutor
mobile app pagination release.

## Backend

- Issue: https://github.com/Sifututor/sifu-tutor/issues/1387
- Production PR: https://github.com/Sifututor/sifu-tutor/pull/1388
- Production merge commit: `6f131bc17973d1cc0aa762098e03121aad557723`
- Production SHA after deploy: `6f131bc17`
- Rollback anchor before deploy: `135052002`
- Staging backport PR: https://github.com/Sifututor/sifu-tutor/pull/1390
- Staging backport merge commit: `7f0446ecf67360661cd6e78448268b0e4525d178`

Root cause: `StudentService::getTutorStudents` used
`getTutorStudentCandidateIds()` to include active request students OR verified
class students, but then applied a second verified-class filter. This removed
newly assigned active-request students that did not have verified classes yet.
`getStudentSubjects` had the same verified-class dependency.

Fix: remove the extra verified-class filters so the returned list matches the
candidate set already scoped to the tutor.

## Mobile

- Mobile PR: https://github.com/Sifututor/sifututor_tutor/pull/7
- State: open and mergeable
- Base: `feat/tut-auth-firstrun-rebuild`
- Head: `fix/6-tutor-student-pagination`

Mobile still needs to ship the pagination fix so tutors with more than 20
students load page 2+ in the app.

## Verification

Backend focused tests passed:

```bash
php artisan test tests/Feature/API/TutorStudentsApiTest.php tests/Feature/API/TutorApiContractTest.php --filter='get_students|student_subjects|tutor_students'
```

Production deploy checks passed:

- `/login` returned HTTP 200.
- `/api/tutor/students` returned HTTP 200 with expected unauthenticated body.
- Production SHA was `6f131bc17`.
- Maintenance mode was off.
- Debug was false.
- No pending migrations.
- Failed jobs count was 0.
- Production log marker worked.
- No new `production.ERROR` or `production.CRITICAL` entries after deploy.

Production issue evidence:
https://github.com/Sifututor/sifu-tutor/issues/1387#issuecomment-4621930325

## Important Lesson

Do not use `php artisan down --status` as a maintenance status check in this
Laravel app. It enables maintenance mode. Check maintenance safely with
`[ -f storage/framework/down ]` or another read-only method, then verify
`/login` externally.

## Remaining Work

1. Mobile dev reviews, merges, builds, and releases PR #7.
2. Smoke test tutor app with `TUT-973079` Fatnin Khalilah, `TUT-109996` Diana
   Atiqah, or any tutor with 21+ active students.
3. Confirm Calendar > Add Class > Student shows page 2+ students, newly
   assigned active-request students, and dropdown search across the full list.

