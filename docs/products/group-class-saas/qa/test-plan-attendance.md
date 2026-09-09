# Test plan: Attendance & Reports (M3)

> Exhaustive manual catalog for attendance + reports. Format + method: [QA-METHODOLOGY.md](QA-METHODOLOGY.md).
> Grounded in `src/features/attendance/{schema,service,service.test}.ts`, `src/features/reports/{service,service.test,format,export-data}.ts`,
> the attendance + report pages/API routes, and [FLOWS.md](../FLOWS.md) §3.
> Default tier T2 (attendance drives teacher pay + absence alerts; the 7-day window and the frozen pay snapshot are the high-risk edges, lifted to T1).
> Roles (Better Auth: role is ASSIGNED on the org membership, never inferred from email): operator (org owner, full),
> staff (member without the teacher role: same attendance + report access as operator here), teacher (member with the
> teacher role, linked to a teachers record: attendance + own classes only, no reports).
> Dev logins: operator = operator@kelastest.local / newpassword6789; teacher = teacher@kelastest.local / password12345 (linked to teacher Ustazah Fatimah).
>
> Updated 2026-07-04 against branch feat/finish-mvp-polish: roster guard (f31491a), touch-size + AA contrast (4580941),
> save-button wrap fix (031eb53), dark mode (2a7804c), shared status tones (a9737aa), export/date-picker localization (e86b941),
> Better Auth migration + teacher self-service (b175d3e). 65 cases (43 TC-ATT, 22 TC-RPT).
>
> Smoke subset (@smoke): TC-ATT-001, TC-ATT-003, TC-ATT-010, TC-ATT-020, TC-ATT-030, TC-ATT-060, TC-ATT-064, TC-RPT-001, TC-RPT-010, TC-RPT-040, TC-RPT-052.

---

## A. Marking attendance: happy path

### TC-ATT-001: Open Attendance and see today's scheduled classes with status
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 **Linked**: M3 **Type**: Feature
**Before you start**: Log in as operator. Ensure at least one active (not archived) class is scheduled to meet today (open Classes, confirm a class whose weekly schedule includes today's weekday). "Today" is computed in Asia/Kuala_Lumpur.
| Step | Action |
|------|--------|
| 1 | Go to Dashboard > Attendance |
| 2 | Read the date picker value and the list |
**What you should see**: The date picker shows today's date (day-first, Malaysia time). A summary line "{N} classes · {C} complete · {P} pending". Each class that meets today appears as a card with its slot time, "{count} students", and a status badge from the shared status tones (a9737aa): "Pending" as an amber-tinted outline badge (BM: "Belum diambil"), "Complete" as a green-tinted one (BM: "Selesai"). An unstarted class shows a filled "Take attendance" button (BM: "Ambil kehadiran"); a complete one shows an outline "Review" (BM: "Semak").
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-ATT-002: Class that does not meet today is not listed
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; an active class whose weekly schedule does NOT include today's weekday (note its name).
| Step | Action |
|------|--------|
| 1 | Go to Attendance for today |
**What you should see**: That class is absent from the list (only classes scheduled on today's weekday appear). No empty rows.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-003: Open a class roster (read-only, no session created yet)
**Tags**: @smoke @regression @data-integrity **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a class that meets today with 2+ active enrolled students that has NOT been marked yet (status Pending on the list).
| Step | Action |
|------|--------|
| 1 | On Attendance, click Take attendance for that class |
| 2 | Look at every student's current status |
**What you should see**: A roster row per active enrolled student, each starting Unmarked (no status button highlighted). Opening the roster alone does NOT create a session row (the list still shows Pending until you save).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-010: Toggle each status, add a note, save once; session materialises and list flips to Complete
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: Feature
**Before you start**: Operator; an unmarked class meeting today with at least 4 active students (note the names).
**Test Data**: student 1 = Present, student 2 = Absent, student 3 = Late, student 4 = Excused; note on student 2 = "Sick, mother called".
| Step | Action |
|------|--------|
| 1 | Open the class roster for today |
| 2 | Tap Present on student 1, Absent on student 2, Late on student 3, Excused on student 4 |
| 3 | Type "Sick, mother called" in student 2's note field |
| 4 | Click Save attendance |
**What you should see**: Each tapped button takes its selected fill (4580941): Present = white text on dark green, Absent = white on dark red, Excused = white on dark sky-blue, and Late = DARK text on an amber fill (not white; changed for AA contrast). After save, a green "Saved" (BM: "Disimpan") appears. Back on Attendance the class badge is Complete and the meta reads "4 of 4 marked". Re-opening the roster shows the same four statuses and the saved note on student 2.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-011: Mark all present sets every roster row to Present in one click
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; an unmarked class meeting today with 3+ students.
| Step | Action |
|------|--------|
| 1 | Open the roster |
| 2 | Click Mark all present |
| 3 | Click Save attendance |
**What you should see**: Every student row turns green (Present) immediately. After save the list shows "{n} of {n} marked", status Complete.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-012: Per-student note is optional and trimmed; blank note stores nothing
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; an unmarked class meeting today with 2 students.
**Test Data**: student 1 note = "   " (only spaces); student 2 note = "Left early at 10".
| Step | Action |
|------|--------|
| 1 | Mark both Present |
| 2 | Type three spaces into student 1's note; type "Left early at 10" into student 2's note |
| 3 | Save, then re-open the roster |
**What you should see**: Student 1 has no note (whitespace-only is sent as no note). Student 2 shows "Left early at 10".
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-013: Saving with no student marked is blocked client-side
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; an unmarked class meeting today (leave every row Unmarked).
| Step | Action |
|------|--------|
| 1 | Open the roster but tap no status buttons |
| 2 | Click Save attendance |
**What you should see**: The error "Mark at least one student." (BM: "Tandakan sekurang-kurangnya seorang pelajar.") is shown; no save request is sent; the class stays Pending.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## B. Lazy session materialisation + frozen pay snapshot

### TC-ATT-020: Session is created only on the first save, with teacher pay frozen onto it
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: Feature
**Before you start**: Operator; an unmarked class meeting today set to pay **per session** with a known per-session rate (e.g. RM 30.00) and an assigned primary teacher. No session exists for today yet (status Pending).
**Test Data**: 3 students, all Present.
| Step | Action |
|------|--------|
| 1 | Open the roster (confirm status still Pending on the list, i.e. no session yet) |
| 2 | Mark all present and Save |
| 3 | Go to Teacher pay, run/open this teacher's payout for the current month, find this session's line |
**What you should see**: After save a session exists and the class is Complete. The payout line for this session shows the frozen amount = the rate (RM 30.00 for per-session), dated today, attributed to the assigned teacher.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-021: Per-student class freezes pay = rate x students present (present + late count)
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: Feature
**Before you start**: Operator; an unmarked class meeting today set to pay **per student** with a known rate (e.g. RM 10.00) and a primary teacher; 4 active students.
**Test Data**: 2 Present, 1 Late, 1 Absent.
| Step | Action |
|------|--------|
| 1 | Mark 2 Present, 1 Late, 1 Absent; Save |
| 2 | Open this teacher's payout line for the session |
**What you should see**: Frozen pay = rate x (present + late) = RM 10.00 x 3 = RM 30.00 (the Absent student is excluded; Late counts toward pay). The session records 3 as its pay-basis count.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-022: Re-marking within the window upserts statuses and recomputes the frozen pay
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: Feature
**Before you start**: A per-student class (rate RM 10.00) already marked today (from TC-ATT-021: pay RM 30.00). Still within 7 days of the session.
| Step | Action |
|------|--------|
| 1 | Re-open the same class roster (status Complete) |
| 2 | Change the Absent student to Present; Save again |
| 3 | Re-open the teacher's payout line for that session |
**What you should see**: No duplicate session or duplicate records; the changed student is now Present; recomputed frozen pay = RM 10.00 x 4 = RM 40.00. The marked count reflects the new statuses.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-023: Editing the class rate after marking does NOT change an already-frozen session's pay
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: Feature
**Before you start**: A per-session class marked today with pay frozen at RM 30.00 (note the payout line amount).
| Step | Action |
|------|--------|
| 1 | Go to Classes, open the class, change the per-session teacher rate to RM 50.00, save |
| 2 | Re-open the teacher's payout line for today's already-marked session |
**What you should see**: The session's frozen pay stays RM 30.00 (the rate was snapshotted at mark time). The new RM 50.00 applies only to sessions marked after the change.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-024: Class with no rate set freezes pay at RM 0.00 (no crash)
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a class meeting today with NO teacher rate set (per-session rate blank, no per-teacher override).
| Step | Action |
|------|--------|
| 1 | Mark all present; Save |
| 2 | Open the session's payout line |
**What you should see**: Attendance saves successfully (Complete); the frozen pay is RM 0.00 (rate null = 0), not an error.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## C. Window, no-meeting-day, and date rules

### TC-ATT-030: Marking on a day the class does not meet is rejected (no_session_day)
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: Feature
**Before you start**: Operator; a class that meets on one specific weekday only (note the name). Pick a recent date (within the last 7 days) that is a DIFFERENT weekday from its meeting day.
| Step | Action |
|------|--------|
| 1 | On Attendance, change the date picker to that non-meeting date |
| 2 | Confirm the class is not in the list; open it directly via /dashboard/attendance/<classId>?date=<that-date> |
| 3 | Bypass the UI: POST to /api/attendance with that classId, that date, and one mark |
**What you should see**: The roster page shows "This class does not meet on the selected day." (BM: "Kelas ini tidak diadakan pada hari yang dipilih.") with no save sheet. The API returns 422 with error `no_session_day`; no session and no records are created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-031: Editing a session older than 7 days is rejected (window_closed)
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: Feature
**Before you start**: Operator; a weekly class. Set the date picker to a meeting date that is 14 days ago (same weekday, outside the 7-day window).
| Step | Action |
|------|--------|
| 1 | Open that class's roster for the 14-days-ago date |
| 2 | Observe the sheet state; try to Save anyway |
| 3 | Bypass the UI: POST to /api/attendance with that classId + the 14-days-ago date |
**What you should see**: The roster shows the window-closed notice "Attendance can only be edited within 7 days of the session." (BM: "Kehadiran hanya boleh disunting dalam tempoh 7 hari dari sesi.") and the status buttons + Save are disabled. The API returns 422 with error `window_closed`; nothing is written.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-032: Exactly 7 days ago is still editable (boundary)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a class whose meeting weekday lands exactly 7 days ago (use a class that meets on today's weekday and pick the date 7 days back).
| Step | Action |
|------|--------|
| 1 | Set the date to exactly 7 days ago (a meeting day) |
| 2 | Open the roster, mark a student, Save |
**What you should see**: The sheet is editable (window is "within 7 days", i.e. days difference <= 7). Save succeeds; status Complete. (Contrast TC-ATT-031 at 14 days, which is rejected.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-033: "Today" is computed in Asia/Kuala_Lumpur near midnight
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator. Set the test machine clock to a time where UTC and Kuala_Lumpur fall on different calendar dates (e.g. 23:30 KL on date D = 15:30 UTC same day; or 07:30 KL = 23:30 UTC previous day). Have a class meeting on the KL date.
| Step | Action |
|------|--------|
| 1 | Open Attendance with no date in the URL |
| 2 | Read the date picker default and which classes are listed |
**What you should see**: The default date is the Kuala_Lumpur calendar date (UTC+8), not the UTC date; classes for the KL day are listed. The 7-day window is also measured from the KL "today".
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-034: Picking a future meeting date is allowed and editable
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a weekly class. Pick its next future meeting date (e.g. 7 days from now, same weekday).
| Step | Action |
|------|--------|
| 1 | Set the date picker to that future meeting date |
| 2 | Open the roster |
**What you should see**: The sheet is editable (the 7-day rule blocks only dates MORE than 7 days in the past, not future dates); a mark can be saved for the future meeting day.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## D. Unmarked, empty, and roster-edge states

### TC-ATT-040: A student left unmarked is never counted as absent
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: Feature
**Before you start**: Operator; a class meeting today with 3 active students (note names).
**Test Data**: student 1 = Present, student 2 = Present, student 3 = leave Unmarked.
| Step | Action |
|------|--------|
| 1 | Mark students 1 and 2 Present, leave student 3 untouched; Save |
| 2 | Re-open the roster |
| 3 | Open the class report for today (Classes > class > report, range = today) |
**What you should see**: Student 3 still shows Unmarked (not Absent). The class report counts only the 2 marked students; the unmarked student is excluded from present/absent/late/excused and from the rate.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-041: Class meeting today with no enrolled students shows the empty-roster state
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 **Type**: Feature
**Before you start**: Operator; an active class meeting today with zero active enrolments (note its name).
| Step | Action |
|------|--------|
| 1 | Open that class's roster for today |
**What you should see**: "No students enrolled in this class yet." (BM: "Belum ada pelajar didaftarkan dalam kelas ini."); no save sheet.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-042: No classes scheduled today shows the empty-day state
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 **Type**: Feature
**Before you start**: Operator; pick a date on which no active class meets (e.g. a weekday with no scheduled classes).
| Step | Action |
|------|--------|
| 1 | Set the date picker to that date |
**What you should see**: "No classes scheduled for this day." (BM: "Tiada kelas dijadualkan untuk hari ini."); no summary line, no cards.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-043: Only active enrolments of active students appear on the roster for the date
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a class meeting today with: one active student, one paused/ended enrolment, and one dropped student (set these up on the class roster + student status first).
| Step | Action |
|------|--------|
| 1 | Open the roster for today |
**What you should see**: Only the active student (active enrolment, started on/before today, not ended before today) appears. The paused/ended enrolment and the dropped student are excluded from the roster.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## E. Absence alerts + class attendance rate

### TC-ATT-050: 3+ consecutive absences surface as an absence alert
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Linked**: M3-US4 **Type**: Feature
**Before you start**: Operator; a class with a student marked Absent in its 3 most recent marked sessions (mark 3 recent meeting days Absent for that student; mark another student Present on the same days as a control). All within the last 30 days.
| Step | Action |
|------|--------|
| 1 | Go to Attendance and read the "Absence alerts" section |
**What you should see**: The absentee appears with "{count} in a row" = 3 (BM: "3 berturut-turut") under the class name and a View link to the student. The Present control student does NOT appear. Alerts are sorted by count (highest first).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-051: A run broken by a non-absent mark does not alert
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a student whose 3 most recent marked sessions are Absent, Present, Absent (the most recent is Absent but the run is broken by a Present).
| Step | Action |
|------|--------|
| 1 | Open Attendance and read Absence alerts |
**What you should see**: The student does NOT appear (the consecutive run counts back from the newest marked session and stops at the first non-absent; the run is 1, below the threshold of 3).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-052: Unmarked sessions do not break or count toward an absence run
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a student marked Absent on 3 meeting days, with another meeting day in between where that student was left Unmarked (not marked at all).
| Step | Action |
|------|--------|
| 1 | Open Attendance and read Absence alerts |
**What you should see**: The student still alerts with 3 in a row: unmarked sessions are skipped entirely (an unmarked session never counts as an absence and never breaks the run of marked absences).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-053: No absence alerts shows the empty state
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 **Type**: Feature
**Before you start**: Operator in an org with no student at 3+ consecutive absences.
| Step | Action |
|------|--------|
| 1 | Open Attendance and read the Absence alerts section |
**What you should see**: "No students with 3 or more absences in a row." (BM: "Tiada pelajar dengan 3 atau lebih ketidakhadiran berturut-turut.").
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-054: Class attendance rate excludes unmarked and excused
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a class with recent (last 30 days) marks totalling, across its sessions: 3 Present, 3 Absent, 1 Late, 2 Excused, 2 Unmarked.
| Step | Action |
|------|--------|
| 1 | Open Attendance; on the class card read the rate (operator only, shown when Complete) |
| 2 | Cross-check on the class report overall rate |
**What you should see**: Rate = (present + late) / (present + late + absent) = (3+1)/(3+1+3) = 4/7 = 57%. The 2 Excused and the 2 Unmarked are excluded from both numerator and denominator.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-055: Class with no marked sessions shows no rate (null), not 0%
**Tags**: @regression @data-integrity **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; an active class meeting today that has never been marked.
| Step | Action |
|------|--------|
| 1 | Open Attendance (the class is Pending) |
**What you should see**: No rate percentage is shown for that class (rate is null when present+late+absent = 0; it is not displayed as 0%). The card shows time and student count only.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## F. Permissions + tenant isolation (attendance)

### TC-ATT-060: Teacher sees and marks only their own classes
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: Feature
**Before you start**: Log in as a teacher (teacher@kelastest.local / password12345, a Better Auth org member with the teacher role, linked to teacher Ustazah Fatimah) who is assigned to class X but NOT class Y (both meet today). Note class Y's id (from an operator session URL).
| Step | Action |
|------|--------|
| 1 | Open Attendance as the teacher |
| 2 | Confirm class X is listed and class Y is not |
| 3 | Mark class X present and Save |
**What you should see**: Only the teacher's own classes (class X) are listed (no absence-alerts section, no per-class rate %, which are operator-only). Marking class X succeeds.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-061: Teacher opening a class they do not teach is blocked (page redirect + API 403)
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: API
**Before you start**: Teacher from TC-ATT-060; class Y's id (a class they do NOT teach).
| Step | Action |
|------|--------|
| 1 | Navigate directly to /dashboard/attendance/<classY-id>?date=<today> |
| 2 | GET /api/attendance?classId=<classY-id>&date=<today> while authed as the teacher |
| 3 | POST /api/attendance with classY-id and a mark |
**What you should see**: The page redirects back to /dashboard/attendance (not the roster). Both API calls return 403 Forbidden; no roster data is returned and no marks are written for class Y.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-062: Teacher-role member with no linked teacher record is blocked from all attendance writes
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: API
**Before you start**: A Better Auth member whose org-membership role is teacher but who has NO linked teachers record (teacherId null). Beware the auto-link: on first login the app links a teacher-role member to the active teacher record whose email matches theirs, so use a login whose email matches no active teacher record in the org. If unreachable in the UI, exercise the API directly.
| Step | Action |
|------|--------|
| 1 | POST /api/attendance for any class while authed as that user |
**What you should see**: 403 Forbidden (a teacher context with no teacherId is treated as blocked for every class). No marks written.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-063: Unauthenticated / no-org request to attendance is 401, page redirects to onboarding
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: API
**Before you start**: A signed-out browser (or a signed-in user with no active organisation).
| Step | Action |
|------|--------|
| 1 | Open /dashboard/attendance with no session/org |
| 2 | Call GET and POST /api/attendance with no session/org |
**What you should see**: The page redirects to /onboarding/organization-selection. The API returns 401 with the exact error "Not authenticated" (signed out) or "No active organisation selected" (signed in, no org); a signed-in user removed from the org gets "Not a member of this organisation". No data is returned.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-064: Cross-tenant: org B cannot read or mark org A's class
**Tags**: @smoke @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: API
**Before you start**: Two orgs (A and B). As operator of org B, obtain a class id belonging to org A (from a known fixture or another session).
| Step | Action |
|------|--------|
| 1 | As org B, open /dashboard/attendance/<org-A-classId>?date=<today> |
| 2 | GET /api/attendance?classId=<org-A-classId>&date=<today> as org B |
| 3 | POST /api/attendance with org A's class id as org B |
**What you should see**: The page shows not-found. GET returns 404 Not found (the class is not in org B's scope). POST returns 404 `class_not_found`; no session/records are created against org A's class. Org A's data never renders or returns.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## G. API input validation (attendance)

### TC-ATT-070: Malformed mark payload is rejected (422 Invalid input)
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: API
**Before you start**: Operator; a valid class meeting today (note classId).
**Test Data**: (a) classId not a UUID; (b) date = "30-06-2026" (wrong format); (c) marks = [] (empty); (d) a mark with status = "tardy" (not present/absent/late/excused); (e) a note 501 characters long.
| Step | Action |
|------|--------|
| 1 | POST /api/attendance for each malformed body in turn |
**What you should see**: Each returns 422 "Invalid input" with field issues (date must match YYYY-MM-DD; marks must have at least 1; status must be one of the four; notes max 500). No session or records created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-071: GET roster without classId or date returns 400
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 **Type**: API
**Before you start**: Operator.
| Step | Action |
|------|--------|
| 1 | GET /api/attendance with classId only (no date) |
| 2 | GET /api/attendance with date only (no classId) |
**What you should see**: Both return 400 "Provide classId and date". No roster is returned.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-ATT-072: Note with a script payload is stored and rendered escaped, not executed
**Tags**: @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a class meeting today with a student.
**Test Data**: note = `<script>alert('xss')</script>`.
| Step | Action |
|------|--------|
| 1 | Mark the student Present, type the payload into the note, Save |
| 2 | Re-open the roster (and any place the note renders) |
**What you should see**: The note text appears literally as typed (escaped); no alert pops in the roster or anywhere it is shown. No script executes.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## H. Attendance accessibility (UI)

### TC-ATT-080: Status buttons and note field are keyboard reachable and labelled
**Tags**: @regression @a11y **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 **Type**: Feature
**Before you start**: Operator; an editable roster open.
| Step | Action |
|------|--------|
| 1 | Tab through the sheet without a mouse |
| 2 | Activate Present with the keyboard, type a note, Tab to Save and activate it |
**What you should see**: Each status button and each note input is reachable by Tab with a visible focus ring; status buttons show readable text (Present/Absent/Late/Excused). The selected button carries aria-pressed="true" (the other three aria-pressed="false"), and the selected state meets WCAG AA 4.5:1: white text on the dark green/red/sky fills, dark text on the amber Late fill (4580941). Save is reachable and operable by keyboard.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## I. Roster guard (server-side, REGRESSION: f31491a)

### TC-ATT-081: A mark for a same-org student not enrolled in the class rejects the whole request (pay-inflation guard)
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: API
**Before you start**: Operator; an unmarked class meeting today set to pay **per student** with rate RM 10.00, a primary teacher, and exactly 1 active enrolled student (get their studentId from GET /api/attendance?classId=...&date=today). Also note the studentId of a student in the SAME org who is NOT enrolled in this class (open a different class's roster response).
**Test Data**: marks = [enrolled student Present, non-enrolled student Present].
| Step | Action |
|------|--------|
| 1 | POST /api/attendance with the classId, today's date, and BOTH marks |
| 2 | GET /api/attendance?classId=<classId>&date=<today> |
| 3 | POST again with only the enrolled student marked Present |
| 4 | Open the teacher's payout line for this session (Teacher pay, current month) |
**What you should see**: Step 1 returns 422 with error `not_on_roster` and the request is rejected WHOLE: the valid mark is not saved either. Step 2 shows sessionId null and the student still Unmarked (no session was materialised, no pay snapshot). Step 3 succeeds; step 4 shows frozen pay = RM 10.00 x 1 = RM 10.00, never RM 20.00.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: crafted marks could inflate a per-student session's frozen pay; roster guard added in commit f31491a (unit test "rejects marks for students not on the class roster (pay-inflation guard)" in service.test.ts).

### TC-ATT-082: A foreign-org or unknown student id in the marks payload is rejected (no orphan rows)
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: API
**Before you start**: Operator of org A with an unmarked class meeting today (1+ enrolled student). Obtain a real student UUID belonging to org B (from a fixture or another session), plus one made-up UUID.
**Test Data**: (a) marks = [enrolled student Present, org-B student Present]; (b) marks = [enrolled student Present, random-UUID Present].
| Step | Action |
|------|--------|
| 1 | POST /api/attendance with payload (a) |
| 2 | POST /api/attendance with payload (b) |
| 3 | GET the roster for the class and date |
**What you should see**: Both POSTs return 422 with error `not_on_roster` (the roster check runs before any write). The roster still shows sessionId null and every student Unmarked; no attendance row referencing the foreign or fake id exists anywhere.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: before commit f31491a such ids inserted as orphan attendance rows.

### TC-ATT-083: A student whose enrolment ended or paused before the date cannot be marked via the API
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: API
**Before you start**: Operator; a class meeting today with one active student and one student whose enrolment in this class you end dated yesterday (class roster > end enrolment). Note both studentIds.
| Step | Action |
|------|--------|
| 1 | Open the roster page for today and confirm only the active student is listed (see TC-ATT-043) |
| 2 | POST /api/attendance with marks for BOTH students |
| 3 | POST /api/attendance with only the active student marked Present |
**What you should see**: Step 2 returns 422 `not_on_roster` and writes nothing: the roster is evaluated as of the session date (active enrolment + active student, started on/before the date, not ended before it), so the ended enrolment fails the guard even though the id was recently valid. Step 3 succeeds.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Server-side counterpart of the UI-only TC-ATT-043; guard from commit f31491a.

## J. Attendance UI regressions: layout, touch size, dark mode

### TC-ATT-084: Sheet header wraps at phone width; the save button stays inside its card
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T3 **Type**: Feature
**Before you start**: Operator with the app language set to Bahasa Malaysia (the longest labels); an editable roster. Set the browser viewport to 375 x 812 (DevTools device toolbar).
| Step | Action |
|------|--------|
| 1 | Open the class roster at 375px width in BM |
| 2 | Mark one student Present, then Save, so the saved note appears |
| 3 | Inspect the header row ("Tandakan semua hadir" + "Disimpan" + "Simpan kehadiran") against the card border |
**What you should see**: The header row wraps: the save group ("Disimpan" + the "Simpan kehadiran" button) drops to a second line inside the card. No horizontal scrollbar appears and no part of the save button crosses the card border.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: at 375px the non-wrapping flex row pushed the save button 11px past the card border; fixed with flex-wrap in commit 031eb53.

### TC-ATT-085: Status buttons meet the 44px touch size on phones and AA contrast when selected
**Tags**: @regression @a11y **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; an editable roster. Test once at 375px viewport width and once at 1280px.
| Step | Action |
|------|--------|
| 1 | At 375px, measure a status button's rendered height (DevTools computed style) |
| 2 | Tap each of the four statuses on one student and inspect the selected button's aria-pressed attribute |
| 3 | Repeat the height measurement at 1280px |
**What you should see**: At 375px each status button is 44px tall; at 1280px, 36px. Exactly one button per student has aria-pressed="true" (the rest "false"). Selected fills read at WCAG AA 4.5:1 or better: white text on dark green (Present), dark red (Absent), dark sky (Excused), and dark text on the amber Late fill.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: buttons were 32px and Late was white-on-amber at 2.3:1; fixed in commit 4580941 (CX8).

### TC-ATT-086: Dark mode keeps the selected status fills visible on the attendance sheet
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 **Type**: Feature
**Before you start**: Operator; an editable roster. Theme picker is in the account menu (header or sidebar): Theme > Light / Dark / Follow device (BM: Tema > Cerah / Gelap / Ikut peranti).
| Step | Action |
|------|--------|
| 1 | Switch the theme to Dark via the account menu |
| 2 | Open the roster and tap each of the four statuses on one student |
| 3 | Switch back to Light and compare |
**What you should see**: In dark mode the selected buttons keep the same explicit solid fills as in light mode (dark green / dark red / amber / dark sky) and stand out clearly from the unselected outline buttons. The default theme for a user who never touched the picker stays Light.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: the outline button's dark-mode overrides washed out the selected attendance colours; fixed with explicit dark-variant fills in commit 2a7804c (CX14).

## K. Teacher self-service (my-classes)

### TC-ATT-087: My classes lists only the teacher's classes; non-teachers are redirected away
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: The teacher dev login (teacher@kelastest.local / password12345, linked to Ustazah Fatimah) assigned to at least one class; the operator login for step 3.
| Step | Action |
|------|--------|
| 1 | Log in as the teacher and read the sidebar |
| 2 | Open /dashboard/my-classes |
| 3 | Log in as the operator and navigate directly to /dashboard/my-classes |
**What you should see**: The teacher sidebar shows "My classes" (BM: "Kelas saya") and "My pay" (BM: "Bayaran saya"). The page (title "My classes", description "Classes you teach and their schedule.") lists ONLY classes this teacher is assigned to, each with its schedule (short weekday + 12-hour time + duration in minutes) and program/level line; a teacher with no classes sees "You're not assigned to any classes yet." (BM: "Anda belum ditugaskan ke mana-mana kelas."). The operator in step 3 is redirected to /dashboard (teacher-only guard).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Added with the teacher self-service in commit b175d3e (post Better Auth migration). Attendance-marking gating itself is unchanged and covered by TC-ATT-060/061.

---

## R. Reports: per-student + per-class over a range

### TC-RPT-001: Per-student report computes totals + per-class breakdown for the range
**Tags**: @smoke @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T2 **Type**: Feature
**Before you start**: Log in as operator. Pick a student with marks in the current month (e.g. 2 Present + 1 Late + 0 Absent in one class). Open Students > the student > report (or /dashboard/students/<id>/report).
| Step | Action |
|------|--------|
| 1 | Confirm the default range is the 1st of this month to today |
| 2 | Read the on-screen "By class" table and its Total row |
**What you should see**: The student name as the heading and the period line. A By class table: one row per class with Present/Absent/Late/Excused counts and a Rate column, plus a bold Total summary row. For 2 Present + 1 Late + 0 Absent the rate = (2+1)/(2+1+0) = 100%.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-002: Per-class report computes overall + per-student breakdown
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a class with this-month marks for 2 students (e.g. overall 3 Present, 1 Late, 2 Absent across sessions). Open Classes > the class > report.
| Step | Action |
|------|--------|
| 1 | Read the By student table: the bold Overall summary row, then one row per student |
**What you should see**: Heading = class name + period. Overall rate = (3+1)/(3+1+2) = 67%. Each student row shows their own Present/Absent/Late/Excused + rate; students are listed alphabetically by name.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-003: Rate excludes unmarked + excused; "-" shown when nothing counts
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a class in a range where one student has only Excused marks (no present/absent/late) and another has Present + Absent.
| Step | Action |
|------|--------|
| 1 | Open the class report for that range |
**What you should see**: The Excused-only student's Rate shows "-" (denominator is 0 because excused is excluded), with the Excused count still displayed. The other student's rate is computed from present/absent/late only. Unmarked records never appear in any count.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-004: Custom date range and the This month / Last month presets re-scope the report
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a class with marks spread across this month and last month (note one mark only in last month).
| Step | Action |
|------|--------|
| 1 | On the report, click Last month |
| 2 | Then set a custom From/To that includes only one specific session day |
**What you should see**: Last month re-loads the report scoped to the previous calendar month (the from/to in the URL change). The custom range shows only marks whose session falls within from 00:00 to to 23:59 (Malaysia time), inclusive of both endpoints.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-005: Range boundary: a session exactly on the To date (KL midnight edge) is included
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a class with a marked session on a known date D. Set the report range From = D, To = D.
| Step | Action |
|------|--------|
| 1 | Load the report for that single-day range |
**What you should see**: The session on D is included (the range is from D 00:00:00 to D 23:59:59.999 Malaysia time). Counts match that day's marks.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## S. Reports: empty + not-found states

### TC-RPT-010: Empty range shows a zeros summary row and hides the trend chart (on-screen)
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a valid student or class, but a date range with no marks (e.g. a future month, or a past month before any attendance existed).
| Step | Action |
|------|--------|
| 1 | Open the report and set the range to the empty period |
| 2 | Read the By class / By student table and look below it for the trend card |
**What you should see**: The table renders with exactly one bold summary row (Total on a student report, Overall on a class report) showing 0 in every count column and "-" in Rate; there are no per-class/per-student rows. The Weekly trend card is absent entirely (it is hidden when there are no points).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: The string "No attendance recorded in this period." (BM: "Tiada kehadiran direkodkan dalam tempoh ini.") exists in the locale files but is currently unreachable on these reports, because the summary row is always emitted (reports/format.ts always appends Total/Overall). If you see that text instead of the zeros row, record it: the rendering path changed.

### TC-RPT-011: Report for a non-existent / wrong-org id is not-found, not a 500
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator of org B. A made-up UUID, and a real student/class id belonging to org A.
| Step | Action |
|------|--------|
| 1 | Open /dashboard/students/<random-uuid>/report |
| 2 | Open /dashboard/classes/<org-A-classId>/report as org B |
**What you should see**: Both render the application not-found page (the service returns undefined for a missing or cross-org id), never a 500 and never another org's data.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## T. Reports: PDF + CSV export

### TC-RPT-020: Student PDF export matches the on-screen tables
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator on a student report with data (note the on-screen Total counts + rate).
| Step | Action |
|------|--------|
| 1 | Click Download PDF |
| 2 | Open the downloaded file (filename like attendance-student-<from>_<to>.pdf) |
**What you should see**: The PDF shows the org's display name (brand) as a header/footer, the report title "Attendance report", the student name, the period, and the By class table with the same counts, the same Total row, and the same rate% as on screen. Rate cells show "%" (or "-" where null).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-021: Class PDF export matches the on-screen tables
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator on a class report with data (note the Overall row).
| Step | Action |
|------|--------|
| 1 | Click Download PDF (filename like attendance-class-<from>_<to>.pdf) |
**What you should see**: The PDF By student table leads with the bold Overall row, then one row per student alphabetically, counts + rate matching the screen; brand + title + class name + period present.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-022: Student CSV export has the exact header + Total row
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator on a student report with data.
| Step | Action |
|------|--------|
| 1 | Click Download CSV (filename like attendance-student-<from>_<to>.csv) |
| 2 | Open it in a text editor / spreadsheet |
**What you should see**: First row = Class,Present,Absent,Late,Excused,Rate (EN labels for an EN locale). One row per class, then a final Total row. Counts + rate% (or "-") match the on-screen table.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-023: Class CSV export has the exact header + Overall row
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator on a class report with data.
| Step | Action |
|------|--------|
| 1 | Click Download CSV (filename like attendance-class-<from>_<to>.csv) |
**What you should see**: First row = Student,Present,Absent,Late,Excused,Rate. Next row = Overall (the summary first), then one row per student. Values match the screen.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-024: CSV escapes a name containing a comma / quote (injection-safe cells)
**Tags**: @regression @security @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator; a student named `Ahmad, "Aman"` (comma + quote) with marks in the range.
| Step | Action |
|------|--------|
| 1 | Download the class CSV for a class that includes that student |
| 2 | Open the raw CSV file |
**What you should see**: That student's name cell is wrapped in quotes with the inner quote doubled, e.g. `"Ahmad, ""Aman"""`, so the comma does not split into extra columns; the row still has 6 fields.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-025: PDF/CSV export with an empty range still produces a valid file
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 **Type**: Feature
**Before you start**: Operator on a report with an empty range (no marks).
| Step | Action |
|------|--------|
| 1 | Download the PDF, then the CSV |
**What you should see**: A valid PDF (header + table with only the Total/Overall row of zeros, rate "-") and a valid CSV (header + the Total/Overall row of 0,0,0,0,-) download; neither errors.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-026: Export with bad/missing parameters returns 400, missing record returns 404
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: API
**Before you start**: Operator.
| Step | Action |
|------|--------|
| 1 | GET /api/reports/pdf with type=invalid (or no id/from/to) |
| 2 | GET /api/reports/csv?type=student&id=<random-uuid>&from=...&to=... |
**What you should see**: Bad/missing params return 400 "Invalid parameters". A valid request for a non-existent (or cross-org) record returns 404 Not found. No file is produced in either case.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

## U. Reports: locale (EN + BM) + dates

### TC-RPT-040: Switching app language to BM translates labels in screen, PDF, and CSV
**Tags**: @smoke @regression **Severity**: S2 High | **Priority**: P1 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator on a class report with data.
| Step | Action |
|------|--------|
| 1 | View the report in EN and note the column labels |
| 2 | Switch app language to Bahasa Malaysia and reload the report |
| 3 | Download the BM PDF and BM CSV (the locale travels in the export URL) |
| 4 | Read the footer of the BM PDF |
**What you should see**: BM labels everywhere: title "Laporan kehadiran", columns Hadir / Tidak hadir / Lewat / Dikecualikan / Kadar, Pelajar / Kelas, Keseluruhan, Jumlah. The PDF and CSV use the same BM labels (the locale param drives the export). The BM PDF footer reads "Dikuasakan oleh Kelasapp" (localized in e86b941; EN: "Powered by Kelasapp"). The period line under the heading also renders BM month names since 17cc0ed (2026-07-04); see TC-RPT-041.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-041: Period line uses the canonical day-first long date; app screens stay DD/MM/YYYY
**Tags**: @regression @data-integrity **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Operator on a report with a known range (e.g. From = 1st of this month, To = today).
| Step | Action |
|------|--------|
| 1 | Read the period line on screen and in the PDF |
| 2 | Open the attendance roster page and read the date in its heading |
| 3 | Switch to BM and re-read the report period line |
**What you should see**: The period reads day-first with a short month and full year (e.g. "1 Jul 2026 - 4 Jul 2026"), never US "Jul 1, 2026". This split is INTENDED and documented (UI-CONVENTIONS.md): printed/exported documents use the long form via the shared formatDateLong helper, while on-screen app dates (step 2, the roster heading) use DD/MM/YYYY via formatDate. Both are day-first Malaysian formats. In BM (step 3) the period line shows BM month names (e.g. "1 Mac 2026 - 31 Mac 2026" for a March range); an English month name in BM (Aug for Ogo, Mar for Mac) is a FAIL.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: Catalog finding #4 re-triage 2026-07-04: the format was formalised as the canonical export format in commit 55f4251 (fmtDate replaced by the shared formatDateLong, documented in UI-CONVENTIONS.md). REGRESSION: the residual BM month-name gap (format.ts called formatDateLong without a locale) was fixed in 17cc0ed the same day, browser-verified with a March range in BM.

### TC-RPT-042: Trend chart bucket labels are day/month (DD/MM), domain 0-100%
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 **Type**: Feature
**Before you start**: Operator on a class report whose range spans 2+ weeks with marks in different weeks.
| Step | Action |
|------|--------|
| 1 | Scroll to the Weekly trend chart |
| 2 | Read the X-axis labels and Y-axis ticks; hover a bar |
**What you should see**: One bar per week with the range present, X labels in DD/MM form, Y axis 0% to 100%, and the hover tooltip showing "{rate}%" labelled "Attendance rate" (BM: "Kadar kehadiran"). Each week's rate uses (present+late)/(present+late+absent), with empty-mark weeks omitted.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: the tooltip label was hardcoded English in TrendChart.tsx; translated in 17cc0ed (2026-07-04). An English tooltip in a BM session is a regression of that fix.

### TC-RPT-054: Report From/To date pickers render month names in the active language
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 **Type**: Feature
**Before you start**: Operator on a class or student report with the app language set to Bahasa Malaysia.
| Step | Action |
|------|--------|
| 1 | Click the From date picker to open the calendar popover |
| 2 | Read the month/year header and navigate to July and August |
| 3 | Pick a date and read the label on the closed picker button |
**What you should see**: The calendar header shows BM month names ("Julai 2026", "Ogos 2026"), and the picker button shows a day-first short date in BM month form (e.g. "4 Jul 2026"; BM short months differ for Ogo, Mac, Mei, Dis). The weekday header row stays the two-letter Mo Tu We Th Fr Sa Su (hardcoded, not localized); record it as an i18n gap if it matters, not a case failure.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked
**Notes**: REGRESSION: pickers were hardcoded en-MY; localized via the shared intlLocale helper in commit e86b941. Applies to the same DatePicker used on the Attendance date filter.

## V. Reports: permissions + tenant isolation

### TC-RPT-050: Teacher cannot reach report pages or export routes
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: API
**Before you start**: Log in as a teacher. Have a valid student id and class id in the same org.
| Step | Action |
|------|--------|
| 1 | Navigate to /dashboard/students/<id>/report and /dashboard/classes/<id>/report |
| 2 | GET /api/reports/pdf and /api/reports/csv with valid params while authed as the teacher |
**What you should see**: The report pages redirect the teacher to /dashboard/attendance (operator-only route group). Both export APIs return 401 with the exact error "Forbidden: operators only"; no report data or file is returned.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-051: Staff (member without the teacher role) CAN view reports like an operator
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: Feature
**Before you start**: Log in as staff (a Better Auth org member whose membership role is NOT teacher and NOT owner/admin).
| Step | Action |
|------|--------|
| 1 | Open a student report and a class report |
| 2 | Download a PDF and a CSV |
**What you should see**: Staff are treated as operators for reports (the guard rejects only teachers); the report pages render and the exports download. (This confirms staff are not blocked here, unlike teachers.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-052: Cross-tenant export: org B cannot export org A's report
**Tags**: @smoke @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 **Type**: API
**Before you start**: Two orgs (A and B). As operator of org B, obtain a student id and class id belonging to org A.
| Step | Action |
|------|--------|
| 1 | GET /api/reports/pdf?type=class&id=<org-A-classId>&from=...&to=...&locale=en as org B |
| 2 | GET /api/reports/csv?type=student&id=<org-A-studentId>&from=...&to=...&locale=en as org B |
| 3 | Open /dashboard/classes/<org-A-classId>/report as org B |
**What you should see**: Each returns 404 Not found (the report service scopes by the signed-in org); no PDF/CSV is generated for org A's data; the page is not-found. Org A's attendance never leaks to org B.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-RPT-053: Unauthenticated / no-org export returns 401
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 **Type**: API
**Before you start**: A signed-out browser (or a user with no active org).
| Step | Action |
|------|--------|
| 1 | GET /api/reports/pdf and /api/reports/csv with otherwise-valid params |
**What you should see**: Both return 401 with the org-required message; no file is produced.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## Coverage note

Techniques walked (§5 matrix): happy path (ATT-001/003/010/011, RPT-001/002/020-023); equivalence + boundary
(ATT-032 the 7-day edge, ATT-034 future date, ATT-083 roster as-of-date, RPT-005 To-date KL midnight edge); negative /
validation incl. server-side bypass (ATT-013/030/031/070/071, ATT-081/082/083 roster guard, RPT-026); format / locale +
EN/BM (RPT-040/041/042/054, plus bilingual strings asserted throughout); permissions / role per role operator/staff/teacher
(ATT-060/061/062/063/087, RPT-050/051/053); cross-tenant / IDOR (ATT-064, ATT-082 foreign student id, RPT-052); state
transition incl. re-mark + window-closed + lazy materialisation (ATT-010/020/022/030/031); concurrency / idempotency
(ATT-022 upsert, no duplicate session); empty / loading / error states (ATT-041/042/053/055, RPT-010/011/025); data
integrity incl. frozen pay snapshot, unmarked-never-absent, rate exclusions, pay-inflation guard, CSV escaping
(ATT-020/021/023/024/040/052/054/081, RPT-003/024); accessibility incl. touch size + AA contrast + dark mode
(ATT-080/084/085/086); security XSS + injection-safe cells (ATT-072, RPT-024).

Deliberately not in this functional catalog: money/RM formatting (reports carry attendance counts + percentages only,
no currency, so no RM cases apply here, unlike billing); non-functional perf / N+1 (listSessionsForDate and the absence-
alert scan fan out per class/student and are flagged for the load pass, not functional QA); the on-screen attendance-rate
trend chart pixel rendering beyond labels/axis (visual QA via browser-test). Grounding: every expected result is reconciled
to `attendance/service.ts`, `reports/{service,format,export-data}.ts`, the route handlers, and the attendance/reports
unit suites (incl. the f31491a roster-guard test); a case asserting behaviour the code does not have is a defect in the
case, not a found bug.

Post-catalog update (2026-07-04, branch feat/finish-mvp-polish): rewrote in place TC-ATT-001 (a9737aa status tones),
TC-ATT-010/080 (4580941 selected-fill contrast + aria-pressed), TC-ATT-060/062 and TC-RPT-051 (Better Auth replaced
Clerk: roles assigned on the org membership), TC-ATT-063 and TC-RPT-050 (exact auth error strings), TC-RPT-010 (empty
range renders a zeros summary row, the no-data string is unreachable), TC-RPT-040 (Dikuasakan oleh Kelasapp footer,
e86b941), TC-RPT-041 (finding #4 re-triage: "1 Jun 2026" is the documented canonical export format via formatDateLong
since 55f4251; residual BM month-name gap because format.ts passes no locale), TC-RPT-042 (hardcoded EN tooltip note).
Appended TC-ATT-081/082/083 (f31491a roster guard: not_on_roster), TC-ATT-084 (031eb53 save-button wrap), TC-ATT-085
(4580941 44px touch targets), TC-ATT-086 (2a7804c dark mode), TC-ATT-087 (b175d3e teacher my-classes gating), and
TC-RPT-054 (e86b941 localized date pickers). Deletions: none (no covered feature was removed).

Case count: 65 (43 attendance TC-ATT, 22 reports TC-RPT). Smoke subset: 11, unchanged (TC-ATT-001, 003, 010, 020, 030, 060, 064; TC-RPT-001, 010, 040, 052).
